# work in "(venv)" virtual environment
# .\venv\Scripts\activate
# using threading

from pyfirmata2 import Arduino, util
from time import sleep
from datetime import datetime, date
import psycopg2
from collections import deque
import matplotlib.pyplot as plt
import math
import threading


class Daq:
    """read data from arduino. output: [d0,d1,d2...]"""
    def __init__(self, user_name, num_sensors, com, fq, plot_second=20):
        # Input values
        self.user_name = user_name.upper()
        self.num_sensors = num_sensors
        self.com = com
        self.fq = fq
        # postgresql & arduino connection
        self.conn = psycopg2.connect(database='first_test', user='postgres', password='3333', host='localhost')
        self.cursor = self.conn.cursor()
        self.uno = Arduino(self.com)
        self.it = util.Iterator(self.uno)
        # variables for class
        self.dqs_len = plot_second * self.fq
        self.to_date = str(date.today()).replace('-', '')
        self.col_str = self.col_name(self.num_sensors, mode='col')
        self.is_run = True
        self.freq_ration = (-0.3 * math.log(self.fq, 10) + 1.2) / self.fq
        self.toDay = str(date.today()).replace('-', '')
        self.t00 = datetime.now()  # haven't used
        self.max_tb = 10
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
            self.dqs[i+2].append(da)
            if da is not None:
                da_contain.append(da)
        print(da_contain)
        return da_contain

    def save_to_db(self):
        da_contain = self.read_arduino()

        if len(da_contain) == self.num_sensors + 2:
            data = [str(s) for s in da_contain[2:]]  # list
            data = ', '.join(data)  # string
            t = da_contain[0]
            p = da_contain[1]
            print(t, p)

            self.cursor.execute(f"""
                INSERT INTO {self.tableName} (timestamp, period, {self.col_str})
                VALUES ('{t}', '{p}', {data});
            """)

    def start(self):
        self.init_arduino()
        while self.is_run:
            self.save_to_db()
            sleep(self.freq_ration)
        else:
            self.close()

    def close(self, save=True):
        if save:
            self.conn.commit()
        self.cursor.close()
        self.conn.close()
        self.uno.exit()
        print('data saved')

    def create_db_table(self):
        """create table and return tableName"""
        if not self.user_name:
            user_name = 'anonymous'
        else:
            user_name = self.user_name.lower()

        for i in range(self.max_tb):
            tbn = f'{user_name}_{self.to_date}_{i}'
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
                        CREATE TABLE {tbn} (timestamp varchar(50),
                                           period varchar(30),
                                           volt_1 real, 
                                           volt_2 real, 
                                           volt_3 real, 
                                           volt_4 real, 
                                           volt_5 real, 
                                           volt_6 real)
                    """)
                    tableName = tbn
                    print(f"'{tableName}' has been created")
                    return tableName
                except:
                    print('table is fulled...')

    def plot_dqs(self, axes, ylim=1):
        axes[0].clear()
        axes[1].clear()
        for i in range(self.num_sensors // 2):
            axes[0].plot(self.dqs[1], self.dqs[i+2], lw=1, label=i, marker='.')
            axes[0].legend(loc='right')

        for i in range(self.num_sensors // 2, self.num_sensors):
            axes[1].plot(self.dqs[1], self.dqs[i+2], lw=1, label=i, marker='.')
            axes[1].legend(loc='right')
        axes[0].set_ylim(0, ylim)
        axes[1].set_ylim(0, ylim)
        plt.pause(0.01)

    def plot_start(self):
        fig, axes = plt.subplots(2, 1, figsize=(15, 6))
        plt.ion()
        while self.is_run:
            self.plot_dqs(axes)
        else:
            plt.ioff()
            #plt.close(fig)

    def main(self, run_time=60):
        """main program"""
        # 2 threading
        th1 = threading.Thread(target=self.start)  # read arduino and save to sql
        th2 = threading.Thread(target=self.plot_start)  # plot instant curve

        th1.start()
        th2.start()
        sleep(run_time)  # run_time
        self.is_run = False
        # th1.join()
        # th2.join()

    @staticmethod
    def col_name(num_sensors, mode):
        """create column names for SQL"""
        col_str = [f'volt_{i + 1}' for i in range(num_sensors)]
        if mode == 'col':
            col_str = ', '.join(col_str)
        elif mode == 'save':
            col_str = ' real, '.join(col_str) + 'real'
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






