import psycopg2
import numpy as np
import pandas as pd
from func import cal_fft, cal_rpm


class DataBase:
    """
      讀取歷史資料庫之相關操作
    """
    def __init__(self):
        self.conn = psycopg2.connect(database='plantar_data', user='postgres', password='3333', host='localhost')
        self.cursor = self.conn.cursor()

    def getAllDates(self, project, user):
        """資料庫中，讀取指定project與user之所有測試日期"""

        self.cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = '{}'    
            AND table_name LIKE '{}%'
        """.format(project.lower(), user.lower()))

        days_ls = [l[0].split('_')[1] for l in self.cursor.fetchall()]

        return sorted(list(set(days_ls)))

    def getAllUsers(self, project):
        """資料庫中，讀取指定project之所有users"""

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
        """讀取指定table之數據01 - 給定資訊"""

        self.cursor.execute('SELECT * FROM {}.{}_{}_{}'.format(project, user, date, i))
        data = self.cursor.fetchall()

        return data

    def readOneTable_n(self, schema_tableName):
        """讀取指定table之數據02 - 給定tableName"""

        self.cursor.execute('SELECT * FROM {}'.format(schema_tableName))
        data = self.cursor.fetchall()
        data = pd.DataFrame(data)
        data.index = data[1]

        return data

    def getBunchTables(self, project=None, user=None, dates=None, info=None):
        """get tableNames (list)"""
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
        """
          Input: tableName
          Output: 指定tableName的 "info"
        """
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
        """
          Input: tableNames (list)
          Output: i, tableName, data, info, exact run time
        """
        i = 0
        for tableName in tableNames:
            data = self.readOneTable_n(tableName)
            info, exact_run_time = self.readInfo(tableName)  # a string
            i += 1
            yield i, tableName, data, info, str(exact_run_time)

    @staticmethod
    def calculate_fft(data):
        return data.apply(cal_fft, data.index[-1])




if __name__ == '__main__':
    database = DataBase()
    database.getBunchTables(project='test', user='USER', dates=['20200601', '20200605', '20200630'])

