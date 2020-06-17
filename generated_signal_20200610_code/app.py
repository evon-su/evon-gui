from arduino_to_sql_3 import User, Daq
from gui import FootDataOperatingPlatform
import tkinter as tk
from tkinter import ttk

# # INPUT user_name, numbers_of_sensors, COM, frequency, plot_time(seconds)
# d = Daq(user_name='JU',
#         num_sensors=6,
#         fq=20,
#         max_runtime=6000,
#         com1='COM10', com2='COM12',
#         plot_second=10)
#
# # main program
# d.main()


if __name__ == '__main__':
    app = FootDataOperatingPlatform()

    app.mainloop()
