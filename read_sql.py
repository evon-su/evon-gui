# work in "(venv)" virtual environment
# .\venv\Scripts\activate

import psycopg2
import pandas as pd
import os

conn = psycopg2.connect(database='plantar_data', user='postgres', password='3333', host='localhost')
cursor = conn.cursor()

def load_tb(user, date, i=0):
    tableName = f'{user}_{date}_{i:02d}'
    cursor.execute(
        f'SELECT * FROM resist_speed.{tableName}'  # "resist_speed" is the project name
    )
    return cursor

def download_tb(user, date, i):
    if not i:
        i = 0
    data = []
    cursor = load_tb(user, date, i)
    for row in cursor:
        data.append(list(row))
    data = pd.DataFrame(data, columns=['timestamp', 'interval(s)','volt_0', 'volt_1', 'volt_2',
                                       'volt_3', 'volt_4', 'volt_5', 'volt_6', 'volt_7',
                                       'volt_8', 'volt_9', 'volt_10', 'volt_11'])
    return data

def download_bunch_db(user, date, max_i):
    if not os.path.isdir(f'data/{date}'):
        os.mkdir(f'data/{date}')
    for i in range(1, max_i+1):
        data = download_tb(user, date, i)
        data.to_csv(f'data/{date}/{user}_{date}_{i:02d}.csv', columns=data.columns, index=False)

if __name__ == '__main__':
    download_bunch_db(user='jy', date='20200804', max_i=20)

