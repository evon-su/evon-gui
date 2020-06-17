import os
import datetime as dt

t0 = dt.datetime.now()

print(dt.date.today())
t = dt.datetime.now() - t0



print(type(dt.datetime.now().time()))
print(type(t))