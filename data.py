import psycopg2
import numpy as np
import pandas as pd
from func import cal_fft, cal_rpm


class DataBase:
    def __init__(self):
        self.conn = psycopg2.connect(database='plantar_data', user='postgres', password='3333', host='localhost')
        self.cursor = self.conn.cursor()

    def getAllDates(self, project, user):
        self.cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = '{}'    
            AND table_name LIKE '{}%'
        """.format(project.lower(), user.lower()))
        days_ls = [l[0].split('_')[1] for l in self.cursor.fetchall()]
        return sorted(list(set(days_ls)))

    def getAllUsers(self, project):
        self.cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = '{}'    
        """.format(project.lower()))
        user_ls = [l[0].split('_')[0].upper() for l in self.cursor.fetchall()]
        user_ls = set(user_ls)
        if 'INFO' in user_ls:
            user_ls.remove('INFO')
        return list(user_ls)

    def readOneTable_u(self, project, user=None, date=None, i=None):
        self.cursor.execute('SELECT * FROM {}.{}_{}_{}'.format(project, user, date, i))
        data = self.cursor.fetchall()
        return data

    def readOneTable_n(self, schema_tableName):
        self.cursor.execute('SELECT * FROM {}'.format(schema_tableName))
        data = self.cursor.fetchall()
        data = pd.DataFrame(data)
        data.index = data[1]
        return data

    def getBunchTables(self, project=None, user=None, dates=None, info=None):
        tableNames = []
        if info:
            try:
                self.cursor.execute("""
                    SELECT table_name FROM {}.info
                    WHERE info LIKE '%{}%'
                    AND table_name LIKE '{}%';
                """.format(project, info.lower(), user.lower()))
                tableNames = [project + '.' + l[0] for l in self.cursor.fetchall()]
            except Exception as e:
                print('info error : ', e)
        else:
            for date in dates:
                self.cursor.execute("""
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = '{}'    
                    AND table_name LIKE '{}_{}%'
                """.format(project, user.lower(), date))
                tableNames += [project + '.' + l[0] for l in self.cursor.fetchall()]

        return sorted(tableNames)  # list

    def readInfo(self, tableName):
        projectName, tableName = tableName.split('.')
        self.cursor.execute(
            '''
            SELECT info, exact_run_time FROM {}.info WHERE table_name = '{}'
            '''.format(projectName, tableName)
        )
        info = self.cursor.fetchall()
        if info:
            info, exact_run_time = info[0]
        else:
            info, exact_run_time = 'no info', 'NULL'

        return info, exact_run_time

    def readBunchTables_gen(self, tableNames):
        i = 0
        for tableName in tableNames:
            data = self.readOneTable_n(tableName)
            info, exact_run_time = self.readInfo(tableName)  # a string
            i += 1
            yield i, tableName, data, info, str(exact_run_time)

    def calculate_fft(self, data):
        # fft series
        # fft, phase, lower, amplitude
        # return values
        return data.apply(cal_fft, data.index[-1])


class Calculation:
    # get data and calculate


    pass


if __name__ == '__main__':
    database = DataBase()
    database.getBunchTables(project='test', user='USER', dates=['20200601', '20200605', '20200630'])

