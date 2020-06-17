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


class Daq:
    """read data from arduino, save to SQL, and plot instant curve"""
    def __init__(self, user_name, num_sensors, com, fq, plot_second=20, save_to_csv=True):
        # Input values
        self.user_name = user_name.upper()
        self.num_sensors = num_sensors
        self.com = com
        self.fq = fq
        self.save_to_csv = save_to_csv
        # postgresql & arduino connection
        self.conn = psycopg2.connect(database='first_test', user='postgres', password='3333', host='localhost')
        self.cursor = self.conn.cursor()
        self.uno = Arduino(self.com)
        self.it = util.Iterator(self.uno)
        # variables for class
        self.dqs_len = plot_second * self.fq
        self.toDay = str(date.today()).replace('-', '')
        self.col_str = self.col_name(self.num_sensors, 'col')
        self.is_run = True
        self.freq_ration = (-0.3 * math.log(self.fq, 10) + 1.2) / self.fq
        self.interval = 1 / self.fq
        self.max_tb = 30
        self.pins = []
        self.dqs = []
        self.time_series = deque(maxlen=self.dqs_len)
        self.tableName = None
        self.t0 = None

    def init_arduino(self):
        """init arduino and dqs"""
        self.tableName = self.create_db_table()
        self.it.start()
        for i in range(self.num_sensors):
            self.pins.append(self.uno.get_pin(f'a:{i}:i'))
        for i in range(self.num_sensors + 2):
            self.dqs.append(deque([0 for i in range(self.dqs_len)], maxlen=self.dqs_len))
        self.t0 = datetime.now()

        # create csv file
        if self.save_to_csv:
            with open(f'./data/{self.tableName}.csv', 'w') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'interval(s)'] + [f'volt_{i}' for i in range(self.num_sensors)])

    @staticmethod
    def cali_time():
        t = [5, 10, 20, 30]
        t_ivs = [1/i for i in t]
        real_t = []
        for item in t:
            t0 = datetime.now()
            sleep(1/item)
            real_t.append((datetime.now()-t0).total_seconds())
        plt.plot(t_ivs, real_t, marker='.')
        plt.grid(True)
        plt.show()

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
            da = self.pins[i].read()
            if da is None:
                da = -1
            self.dqs[i + 2].append(da)
            da_contain.append(da)
        print(da_contain)

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
            t = da_contain[0]
            p = da_contain[1]
            print(t, p)

            self.cursor.execute(f"""
                INSERT INTO {self.tableName} (timestamp, interval, {self.col_str})
                VALUES ('{t}', '{p}', {data});
            """)

    def start_read_and_save(self):
        self.init_arduino()
        i = 1
        start = time()
        while self.is_run:
            end = start + i * self.interval
            sleep_time = end - time()
            if sleep_time > 0:
                sleep(end - time())
            else:
                pass
            da_contain = self.read_arduino()
            self.save_to_db(da_contain)
            i += 1
            print(i)

        else:
            sleep(0.1)
            self.close()
            pass

    def close(self, save=True):
        if save:
            self.conn.commit()
            print('data saved')
        self.cursor.close()
        self.conn.close()
        self.uno.exit()
        print('uno exit')

    def create_db_table(self):
        """create table and return tableName"""
        sql_str = self.col_name(self.num_sensors, 'sql')
        if not self.user_name:
            user_name = 'user'
        else:
            user_name = self.user_name.lower()

        for i in range(self.max_tb):
            tbn = f'{user_name}_{self.toDay}_{i+1}'
            self.cursor.execute(f"""
                SELECT EXISTS (
                    SELECT * FROM information_schema.tables
                    WHERE table_name = '{tbn}'
                )
            """)
            b = self.cursor.fetchone()  # (True or False, )
            if b[0]:
                print(f"'{tbn}' has been used")
                continue
            elif not b[0]:
                try:
                    self.cursor.execute(f"""
                        CREATE TABLE {tbn} (timestamp varchar(30),
                                           interval varchar(10),
                                           {sql_str})
                    """)
                    tableName = tbn
                    print(f"'{tableName}' has been created")
                    return tableName
                except:
                    print('table is fulled...')

    def plot_dqs(self, axes, ylim=1):
        print('axes', axes)
        print('1', self.num_sensors // 2)
        axes[0].clear()
        axes[1].clear()
        print('2', self.num_sensors // 2)
        for plot_i in range(self.num_sensors // 2):
            print('plot axes0')
            axes[0].plot(self.dqs[1], self.dqs[plot_i+2], lw=1, label=plot_i, marker='.')
            axes[0].legend(loc='right')

        for plot_i in range(self.num_sensors // 2, self.num_sensors):
            axes[1].plot(self.dqs[1], self.dqs[plot_i+2], lw=1, label=plot_i, marker='.')
            axes[1].legend(loc='right')
        axes[0].set_ylim(0, ylim)
        axes[1].set_ylim(0, ylim)
        plt.pause(0.01)

    def start_plot(self):
        #end = self.t0.total_seconds + max_play_time
        fig, axes = plt.subplots(2, 1, figsize=(15, 6))
        plt.ion()
        print('start plot')
        while self.is_run:
            self.plot_dqs(axes)
        plt.ioff()
        plt.show()
        print('plt off')

    def main(self, run_time=60):
        """main program"""
        # 2 threading
        th1 = threading.Thread(target=self.start_read_and_save)  # read arduino and save to sql
        th2 = threading.Thread(target=self.start_plot)  # plot instant curve

        th1.start()
        th2.start()
        sleep(run_time)  # run_time
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
    pass






