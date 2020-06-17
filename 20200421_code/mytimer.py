from threading import Timer
from datetime import datetime
from time import sleep

class MyTimer:
    def __init__(self, interval, callback_proc, args=None, kwargs=None):
        self.__timer = None
        self.__interval = interval
        self.__callback_pro = callback_proc
        self.__args = args if args is not None else []
        self.__kwargs = kwargs if kwargs is not None else {}

    def exec_callback(self, args=None, kwargs=None):
        self.__timer = Timer(self.__interval, self.exec_callback)
        self.__timer.start()
        self.__callback_pro(*self.__args, **self.__kwargs)

    def start(self):
        self.__timer = Timer(self.__interval, self.exec_callback)
        self.__timer.start()

    def cancel(self):
        self.__timer.cancel()
        self.__timer = None

def print_now():
    print(f'\ntime now is {datetime.now()}')

if __name__ == "__main__":
    tmr = MyTimer(0.1, print_now)
    tmr.start()
    sleep(3)
    print('tmr cancel')
    tmr.cancel()



