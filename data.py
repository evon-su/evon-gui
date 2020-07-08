import psycopg2
import numpy as np
import pandas as pd


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
            print('info ', project)
            self.cursor.execute("""
                SELECT table_name FROM {}.info
                WHERE info LIKE '%{}%'
                AND table_name LIKE '{}%';
            """.format(project, info.lower(), user.lower()))
            tableNames = [project + '.' + l[0] for l in self.cursor.fetchall()]
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

    def readBunchTables_gen(self, tableNames):
        i = 0
        for tableName in tableNames:
            data = self.readOneTable_n(tableName)
            i += 1
            yield i, tableName, data


if __name__ == '__main__':
    database = DataBase()
    database.getBunchTables(project='test', user='USER', dates=['20200601', '20200605', '20200630'])

