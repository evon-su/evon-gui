# work in "(venv)" virtual environment
# .\venv\Scripts\activate

import psycopg2
import pandas as pd

conn = psycopg2.connect(database='first_test', user='postgres', password='3333', host='localhost')
cursor = conn.cursor()

def load_tb(user, date, i=0):
    tableName = f'{user}_{date}_{i}'
    cursor.execute(
        f'SELECT * FROM {tableName}'
    )
    return cursor

def download_tb(user, date, i):
    if not i:
        i = 0
    data = []
    cursor = load_tb(user, date, i)
    for row in cursor:
        data.append(list(row))
    data = pd.DataFrame(data)
    return data

if __name__ == '__main__':
    pd.set_option('display.max_columns', 10)
    data = download_tb('YH', '20200416', i=1)
    data.to_csv('20200416.csv')
    print(data)
