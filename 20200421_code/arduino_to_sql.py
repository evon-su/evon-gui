# work in "(venv)" virtual environment
# .\venv\Scripts\activate

from pyfirmata2 import Arduino, util
import time
from time import sleep
from datetime import datetime, date
import psycopg2
import pandas as pd
import numpy as np
from collections import deque
from threading import Thread
from mytimer import MyTimer, print_now
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


class ArduinoToSql:
    def __init__(self, sensors_number, user_name, com):
        self.sensors_number = sensors_number
        self.userName = user_name
        self.toDay = str(date.today()).replace('-', '')
        self.col_str = self.col_name(self.sensors_number)
        self.conn = psycopg2.connect(database='first_test', user='postgres', password='3333', host='localhost')
        self.cursor = self.conn.cursor()
        self.plot_len = 200
        self.tableName = None
        self.uno = Arduino(com)
        self.it = util.Iterator(self.uno)
        self.t00 = datetime.now()
        # other parm which haven't defined
        self.pins = None
        self.dqs = None

    def start(self):
        self.tableName = self.create_db_table(user_name=self.userName, to_date=self.toDay)
        self.it.start()
        self.pins, self.dqs = self.init_pins_dqs(max_len=self.plot_len)
        t0 = datetime.now()
        time_series = deque(maxlen=self.plot_len)
        # plot dqs
        print('create fig...?')
        fig, axes = plt.subplots(2, 1, figsize=(15, 6))
        plt.ion()
        while True:
            self.append_and_plot(t0, time_series, axes)

        # old codes
        # try:
        #     my_timer = MyTimer(0.1, self.append_and_plot, args=(t0, time_series, axes))
        #     my_timer.start()
        # except KeyboardInterrupt:
        #     my_timer.cancel()
        #     self.close()

        # while True:
        #     t = datetime.now()
        #     p = (t - t0).total_seconds()
        #     da_contain = []
        #     time_series.append(p)
        #     data = self.daq(self.sensors_number, self.pins, self.dqs, da_contain)
        #     self.save_to_sql(t, p, data)
        #     self.plot_dqs(time_series=time_series, dqs=self.dqs, axes=axes)

        # ax.clear()
        # ax2.clear()
        # for i in range(self.sensors_number//2):
        #     ax.plot(time_series, self.dqs[i], lw=1, label=i)
        # ax.legend(loc='right')
        #
        # for i in range(self.sensors_number//2, self.sensors_number):
        #     ax2.plot(time_series, self.dqs[i], lw=1, label=i)
        # ax2.legend(loc='right')

    def append_and_plot(self, t0, time_series, axes):
        t = datetime.now()
        p = (t - t0).total_seconds()
        da_contain = []
        time_series.append(p)
        data = self.daq(self.sensors_number, self.pins, self.dqs, da_contain)
        self.save_to_sql(t, p, data)
        #self.ani_plot(time_series, self.dqs)

        self.plot_dqs(time_series=time_series, dqs=self.dqs, axes=axes)

    def close(self):
        self.conn.commit()
        self.conn.close()
        self.uno.exit()
        print(f'saved in {self.tableName}')

    def save_to_sql(self, t, p, da_contain):
        """
        save data to PostgreSql
        :param da_contain: data from arduino -> list
        :param t: timestamp
        :param p: period from initial moment
        :return: None
        """
        if len(da_contain) == self.sensors_number:
            da_contain = [str(s) for s in da_contain]  # list
            da_contain = ', '.join(da_contain)  # string
            print(t)
            print(p)
            print(da_contain)

            self.cursor.execute(f"""
                INSERT INTO {self.tableName} (timestamp, period, {self.col_str})
                VALUES ('{t}', '{p}', {da_contain});
            """)

    @staticmethod
    def daq(sensors_number, pins, dqs, da_contain):
        """

        :param sensors_number:
        :param pins:
        :param dqs:
        :param da_contain:
        :return:
        """
        for i in range(sensors_number):
            da = pins[i].read()
            dqs[i].append(da)
            if da is not None:
                da_contain.append(da)
            else:
                break
        return da_contain

    # initialize "pins", "dqs"
    def init_pins_dqs(self, max_len=200):
        pins = []
        dqs = []
        for i in range(self.sensors_number):
            pins.append(self.uno.get_pin(f'a:{i}:i'))
            dqs.append(deque(maxlen=max_len))
        return pins, dqs

    # create new SQL table
    def create_db_table(self, user_name, to_date, max_tb=10):
        if not user_name:
            user_name = 'anonymous'
        else:
            user_name = user_name.lower()

        for i in range(max_tb):
            tbn = f'{user_name}_{to_date}_{i}'
            self.cursor.execute(f"""
                SELECT EXISTS (
                    SELECT * FROM information_schema.tables
                    WHERE table_name = '{tbn}'
                )
            """)
            b = self.cursor.fetchone()  # (True or False, )
            print(tbn)
            print('b: ', b)
            if b[0]:
                print(f"'{tbn}' has been used")
                continue
            elif not b[0]:
                print('tbn: ', tbn)
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
                break
        return tableName

    @staticmethod
    def col_name(sensors_number):
        col_str = [f'volt_{i + 1}' for i in range(sensors_number)]
        col_str = ', '.join(col_str)
        return col_str

    def plot_dqs(self, time_series, dqs, axes):
        axes[0].clear()
        axes[1].clear()
        for i in range(self.sensors_number // 2):
            axes[0].plot(time_series, dqs[i], lw=1, label=i)
            axes[0].legend(loc='right')

        for i in range(self.sensors_number // 2, self.sensors_number):
            axes[1].plot(time_series, dqs[i], lw=1, label=i)
            axes[1].legend(loc='right')
        plt.pause(0.01)




    # try:
    #     sensors_number = 6
    #     col_str = col_name(sensors_number)
    #     toDay = str(date.today()).replace('-', '')
    #     # connect to database
    #     conn = psycopg2.connect(database='first_test', user='postgres', password='3333', host='localhost')
    #     cursor = conn.cursor()
    #     # set arduino param
    #     uno = Arduino('COM10')
    #     it = util.Iterator(uno)
    #     it.start()
    #     # init pins, dqs, time_series
    #     pins, dqs, time_series = init_pins_dqs(sensors_number)
    #     # input userName
    #     userName = input('Input Your Name: ')
    #     # create table and get tableName
    #     tableName = create_db_table(user=userName, to_date=toDay)
    #     # initial time
    #     t0 = datetime.now()
    #
    #     while True:
    #         t = datetime.now()
    #         p = t - t0
    #         time_series.append(p)
    #         da_contain = []
    #         for i in range(sensors_number):
    #             da = pins[i].read()
    #             dqs[i].append(da)
    #             if da is not None:
    #                 da_contain.append(da)
    #             else:
    #                 break
    #         if da_contain:
    #             da_contain = [str(s) for s in da_contain]
    #             da_contain = ', '.join(da_contain)
    #
    #             cursor.execute(f"""
    #                 INSERT INTO {tableName} (timestamp, period, {col_str})
    #                 VALUES ('{t}', '{p}', {da_contain});
    #             """)
    #
    #         sleep(10)
    #
    # except KeyboardInterrupt:
    #     print('end...')
    #     conn.commit()
    #     conn.close()
    #     uno.exit()
