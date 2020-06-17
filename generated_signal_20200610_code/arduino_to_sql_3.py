# work in "(venv)" virtual environment
# .\venv\Scripts\activate
# using threading

from pyfirmata2 import Arduino, util
from time import sleep, time
from datetime import datetime, date
import psycopg2
from collections import deque
import matplotlib.pyplot as plt
import math
import threading
import csv


# arduino_param = {
#     'digital': tuple(x for x in range(14)),
#     'analog': tuple(x for x in range(16)),
#     'pwm': (3, 5, 6, 9, 10, 11),
#     'use_ports': True,
#     'disabled': (0, 1)  # Rx, Tx, Crystal
# }

class Daq:
    """read data from arduino, save to SQL, and plot instant curve"""
    def __init__(self, user_name, num_sensors, sr, max_runtime, *, com1, com2, project_name, project_info, plot_second, save_to_csv=True):
        # Input values
        self.user_name = user_name.upper()
        self.num_sensors = num_sensors
        self.project_name = project_name
        self.project_info = project_info
        # self.com1 = com1
        # self.com2 = com2
        self.sr = sr
        self.save_to_csv = save_to_csv
        # postgresql & arduino connection
        self.conn = psycopg2.connect(database='plantar_data', user='postgres', password='3333', host='localhost')
        self.cursor = self.conn.cursor()
        # self.uno1 = Arduino(self.com1)
        # self.uno1.setup_layout(arduino_param)
        # # self.uno2 = Arduino(self.com2)
        # # self.uno2.setup_layout(arduino_param)
        # self.it1 = util.Iterator(self.uno1)
        # # self.it2 = util.Iterator(self.uno2)
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

    def init_arduino(self):
        """init arduino and dqs, and write information into into"""
        self.tableName = self.create_db_table()
        # write project information into 'info' table
        self.cursor.execute(f"""
            INSERT INTO {self.project_name}.info (table_name, info)
            VALUES ('{self.tableName}', '{self.project_info}');
        """)
        # self.it1.start()
        # self.it2.start()
        # for i in range(self.num_sensors):
        #     self.pins1.append(self.uno1.get_pin(f'a:{i}:i'))
            # self.pins2.append(self.uno2.get_pin(f'a:{i}:i'))
        for i in range(self.num_sensors*2 + 2):
            self.dqs.append(deque([0 for i in range(self.dqs_len)], maxlen=self.dqs_len))
        self.t0 = datetime.now()

        # # create csv file
        # if self.save_to_csv:
        #     with open(f'./data/{self.tableName}.csv', 'w') as f:
        #         writer = csv.writer(f)
        #         writer.writerow(['timestamp', 'interval(s)'] + [f'volt_{i}' for i in range(self.num_sensors)])

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
            da = math.sin((2 * math.pi * p * 1000)/6 + i*0.3)
            self.dqs[i + 2].append(da)
            da_contain.append(da)

        # # save to csv file
        # if self.save_to_csv:
        #     with open(f'./data/{self.tableName}.csv', 'a') as f:
        #         writer = csv.writer(f)
        #         writer.writerow(da_contain)

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
        start = time()
        while self.is_run:
            end = start + i * self.interval
            try:
                sleep(end - time())
            except ValueError:
                pass
            da_contain = self.read_arduino()
            if da_contain[1] >= self.max_runtime:
                self.close()
                break
            self.save_to_db(da_contain)
            if i % 100 == 0:
                self.conn.commit()
                print(f'i={i} has been saved')
                print(da_contain)
            i += 1

        else:
            self.close()

    def close(self, save=True):
        self.is_run = False
        if save:
            self.conn.commit()
            print('all data saved')

        self.cursor.close()
        self.conn.close()
        # self.uno1.exit()

        print('uno exit')

    def create_db_table(self):
        """create table and return tableName"""
        sql_str = self.col_name(self.num_sensors, 'sql')

        # create 'project_name.info' table
        self.cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.project_name}.info
            (table_name varchar(50),
             info varchar(1000));
        """)
        print('info has been created')

        if not self.user_name:
            user_name = 'user'
        else:
            user_name = self.user_name.lower()

        # create 'userName_date_i' table
        for i in range(self.max_tb):
            tbn = f'{user_name}_{self.toDay}_{i+1}'
            self.cursor.execute(f"""
                SELECT EXISTS (
                    SELECT * FROM information_schema.tables
                    WHERE table_schema = '{self.project_name}' AND table_name = '{tbn}'
                )
            """)
            b = self.cursor.fetchone()  # (True or False, )
            if b[0]:
                print(f"'{self.project_name}.{tbn}' has been used")
                continue
            elif not b[0]:
                try:
                    print('project name')
                    print(self.project_name)
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


class Calculation:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def cal_fft(self):
        # return fft list
        pass

    def cal_rpm(self):
        pass






