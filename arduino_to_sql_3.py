# work in "(venv)" virtual environment
# .\venv\Scripts\activate

from pyfirmata2 import Arduino, util
from time import sleep, time
from datetime import datetime, date
import psycopg2
from collections import deque
import matplotlib.pyplot as plt
import threading
import csv
from func import cal_rpm

arduino_param = {
    'digital': tuple(x for x in range(14)),
    'analog': tuple(x for x in range(16)),
    'pwm': (3, 5, 6, 9, 10, 11),
    'use_ports': True,
    'disabled': (0, 1)  # Rx, Tx, Crystal
}

class Daq:
    """read data from arduino, save to SQL, and plot instant curve"""
    def __init__(self, user_name, num_sensors, sr, max_runtime, *, com1, com2,
                 project_name, project_info, plot_second, save_to_csv=True):
        # Input values
        self.user_name = user_name.upper()
        self.num_sensors = num_sensors
        self.project_name = project_name
        self.project_info = project_info
        self.com1 = com1
        self.com2 = com2
        self.sr = sr
        self.save_to_csv = save_to_csv
        # postgresql & arduino connection
        self.conn = psycopg2.connect(database='plantar_data', user='postgres', password='3333', host='localhost')
        self.cursor = self.conn.cursor()
        self.uno1 = Arduino(self.com1)
        self.uno1.setup_layout(arduino_param)
        self.it1 = util.Iterator(self.uno1)
        # variables for class
        self.plot_second = plot_second
        self.dqs_len = plot_second * self.sr
        self.toDay = str(date.today()).replace('-', '')
        self.col_str = self.col_name(self.num_sensors, 'col')
        self.is_run = True
        self.interval = 1 / self.sr
        self.max_tb = 100
        self.pins1 = []
        self.pins2 = []
        self.dqs = []
        self.time_series = deque(maxlen=self.dqs_len)
        self.tableName = None
        self.t0 = None
        self.max_runtime = max_runtime
        self.fft_freq = 0.
        self.da_contain = None

    def init_arduino(self):
        """init arduino and dqs, and write information into into"""
        self.tableName = self.create_db_table()
        # write project information into 'info' table
        self.cursor.execute(f"""
            INSERT INTO {self.project_name}.info (table_name, timestamp, info, project_name, user_name,
                                                  number_of_sensors, sampling_rate, max_run_time)
            VALUES ('{self.tableName}', '{datetime.now()}', '{self.project_info}', '{self.project_name}', '{self.user_name}',
                    '{self.num_sensors}', '{self.sr}', '{self.max_runtime}');
        """)
        self.it1.start()
        # self.it2.start()
        for i in range(self.num_sensors):
            self.pins1.append(self.uno1.get_pin(f'a:{i}:i'))
            # self.pins2.append(self.uno2.get_pin(f'a:{i}:i'))
        for i in range(self.num_sensors*2 + 2):
            self.dqs.append(deque([0 for i in range(self.dqs_len)], maxlen=self.dqs_len))
        self.t0 = datetime.now()

        # create csv file
        if self.save_to_csv:
            with open(f'./data/{self.tableName}.csv', 'w') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'interval(s)'] + [f'volt_{i}' for i in range(self.num_sensors)])

    def read_arduino(self):
        """da_contain for sql and append to dqs"""
        da_contain = []
        t = datetime.now()
        p = (datetime.now() - self.t0).total_seconds()
        da_contain.append(t)
        da_contain.append(p)
        self.dqs[0].append(t)
        self.dqs[1].append(p)
        for i in range(self.num_sensors):
            da = self.pins1[i].read()
            if da is None:
                da = -1
            self.dqs[i + 2].append(da)
            da_contain.append(da)

        # save to csv file
        if self.save_to_csv:
            with open(f'./data/{self.tableName}.csv', 'a') as f:
                writer = csv.writer(f)
                writer.writerow(da_contain)

        return da_contain

    def save_to_db(self, da_contain):
        if len(da_contain) == self.num_sensors + 2:
            data = [str(s) for s in da_contain[2:]]  # list
            data = ', '.join(data)  # string
            t, p = da_contain[0:2]

            self.cursor.execute(f"""
                INSERT INTO {self.project_name}.{self.tableName} (timestamp, interval, {self.col_str})
                VALUES ('{t}', '{p}', {data});
            """)

    def start_read_and_save(self):
        self.init_arduino()
        i = 1
        time__ = time()
        while self.is_run:
            try:
                sleep(time__ - time())
            except ValueError:
                pass
            self.da_contain = self.read_arduino()
            if self.da_contain[1] >= self.max_runtime:
                self.close()
                break
            self.save_to_db(self.da_contain)
            if i % 100 == 0:
                self.conn.commit()
                print(f'i={i} has been saved')
                print(self.da_contain)

            time__ += self.interval
            i += 1

        else:
            self.close()

    def close(self, save=True):
        self.is_run = False
        exact_run_time = self.dqs[1][-1]
        self.cursor.execute(f"""
            UPDATE {self.project_name}.info
            SET exact_run_time = '{exact_run_time}'
            WHERE table_name = '{self.tableName}';
        """)
        if save:
            self.conn.commit()
            print('all data saved')

        self.cursor.close()
        self.conn.close()
        self.uno1.exit()

        print('uno exit')

    def create_db_table(self):
        """create table and return tableName"""
        sql_str = self.col_name(self.num_sensors, 'sql')
        # create info table
        self.cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.project_name}.info
            (table_name varchar(50),
             timestamp timestamp,
             info varchar(1000),
             project_name varchar(1000),
             user_name varchar(50),
             number_of_sensors int,
             sampling_rate real,
             max_run_time real,
             exact_run_time real);
        """)
        print('info has been created')

        if not self.user_name:
            user_name = 'user'
        else:
            user_name = self.user_name.lower()

        # create table
        for i in range(self.max_tb):
            tbn = f'{user_name}_{self.toDay}_{i+1:02d}'
            # check table exist or not
            self.cursor.execute(f"""
                SELECT EXISTS (
                    SELECT * FROM information_schema.tables
                    WHERE table_schema='{self.project_name}' AND table_name = '{tbn}'
                )
            """)
            b = self.cursor.fetchone()  # (True or False, )
            if b[0]:
                print(f"'{self.project_name}.{tbn}' has been used")
                continue
            elif not b[0]:
                try:
                    self.cursor.execute(f"""
                        CREATE TABLE {self.project_name}.{tbn} (timestamp timestamp,
                                                                interval real,
                                                                {sql_str});
                    """)

                    tableName = tbn
                    print(f"'{self.project_name}.{tableName}' has been created")
                    return tableName
                except Exception as e:
                    print('exception: ', e)
                    print('table is fulled...')

    def plot_dqs(self, axes, ylim=0.9):
        axes[0].clear()
        axes[1].clear()
        for plot_i in range(self.num_sensors // 2):
            axes[0].plot(self.dqs[1], self.dqs[plot_i+2], lw=1, label=f'a{plot_i}', marker=None)

        for plot_i in range(self.num_sensors // 2, self.num_sensors):
            axes[1].plot(self.dqs[1], self.dqs[plot_i+2], lw=1, label=f'a{plot_i}', marker=None)

        axes[0].legend(loc='upper left')
        axes[1].legend(loc='upper left')
        axes[0].set_ylim(0, ylim)
        axes[1].set_ylim(0, ylim)
        plt.pause(0.01)

    def start_plot(self):
        #end = self.t0.total_seconds + max_play_time
        fig, axes = plt.subplots(2, 1, figsize=(15, 6))
        plt.ion()
        while self.is_run:
            self.plot_dqs(axes)
        plt.ioff()
        plt.show()

    def main(self):
        """main program"""
        # 2 threading
        th1 = threading.Thread(target=self.start_read_and_save)  # read arduino and save to sql
        th2 = threading.Thread(target=self.start_plot)  # plot instant curve

        th1.start()
        th2.start()
        sleep(self.max_runtime)  # run_time
        self.is_run = False
        # th1.join()
        # th2.join()

    def real_time_rpm(self):
        sleep(3)
        while self.is_run:
            self.fft_freq = cal_rpm(self.dqs[2], self.plot_second)
            # self.rpm.set(round(f, 1))
            print('--', self.fft_freq, '--')
            sleep(2)

    @staticmethod
    def col_name(num_sensors, mode):
        """create column names for SQL"""
        col_str = [f'volt_{i}' for i in range(num_sensors)]
        if mode == 'col':
            col_str = ', '.join(col_str)
        elif mode == 'sql':
            col_str = ' real, '.join(col_str) + ' real'
        return col_str


class User:
    @classmethod
    def create_user(cls, user_name):
        """create user to user.csv"""
        exist_user = cls.check_user()
        if user_name.upper() not in exist_user:
            with open('user.csv', 'a') as f:
                f.write(f'{user_name.upper()}\n')
                print(f'{user_name} has been written to user.csv')
        else:
            print(f'{user_name} has been existed')

    @classmethod
    def check_user(cls):
        exist_user = set()
        with open('user.csv', 'r') as f:
            for line in f.readlines():
                l0 = line.strip('\n')
                exist_user.add(l0)
        return exist_user

class SqlCommand:
    # get schema and table names
    getSchemaAndTableNames = '''
        SELECT table_schema, table_name
        FROM information_schema.tables
        WHERE table_schema = 'resist_speed'
        ORDER BY table_schema, table_name;
    '''


    def __init__(self):
        pass


if __name__ == '__main__':
    # 測試SQL指令
    conn = psycopg2.connect(database='plantar_data', user='postgres', password='3333', host='localhost')
    cursor = conn.cursor()
#     cursor.execute(f"""
#         SELECT table_name
#   FROM information_schema.tables
#  WHERE table_schema='data'
#    AND table_type='BASE TABLE'
# ;
#     """)

    # # get schema names
    # cursor.execute('''
    #     SELECT datname
    #     FROM pg_database
    #     WHERE datistemplate = false
    #     ;
    # ''')

    # get schema and table names
    cursor.execute('''
    SELECT table_schema, table_name
    FROM information_schema.tables
    WHERE table_schema = 'resist_speed'
    ORDER BY table_schema, table_name
    ;''')

    b = cursor.fetchall()
    print(len(b))
    print(b)








