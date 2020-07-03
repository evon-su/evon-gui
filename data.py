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

    def readOneTable_u(self, project, user=None, date=None, i=None):
        self.cursor.execute('SELECT * FROM {}.{}_{}_{}'.format(project, user, date, i))
        data = self.cursor.fetchall()
        return data

    def readOneTable_n(self, schema_tableName):
        self.cursor.execute('SELECT * FROM {}'.format(schema_tableName))
        data = self.cursor.fetchall()
        data = pd.DataFrame(data)
        return data

    def getBunchTables(self, project=None, user=None, dates=None):
        tableNames = []
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
        for tableName in tableNames:
            data = self.readOneTable_n(tableName)
            yield tableName, data


if __name__ == '__main__':
    database = DataBase()
    database.getBunchTables(project='test', user='USER', dates=['20200601', '20200605', '20200630'])

