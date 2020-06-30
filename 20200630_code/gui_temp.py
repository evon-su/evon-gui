import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from arduino_to_sql_3 import Daq
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import csv
import threading
import numpy as np
from time import sleep
import matplotlib.animation as animation


class FootDataOperatingPlatform(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Healthy Data Operating Platform')
        self.geometry(self.gui_size())
        self.graph_frame = tk.Frame(self, bg='white', pady=20)
        self.graph_frame.pack()
        self.graph_frame.grid_rowconfigure(0, weight=1)
        self.graph_frame.grid_columnconfigure(1, weight=1)
        # Variable
        self.user_name = tk.StringVar()
        self.num_sensors = tk.IntVar(value=6)
        self.freq = tk.IntVar(value=20)
        self.runtime = tk.IntVar(value=60)
        self.start_button_text = tk.StringVar(value='START')
        # --Widget--
        self.user_label = ttk.Label(self.graph_frame, text='User Name : ')
        self.user_label.config(font=('Arial', 12))
        self.user_label.grid(row=0, column=0, pady=(5, 5))
        self.user_dropdown = ttk.Combobox(self.graph_frame, values=self.get_user_names(),
                                          textvariable=self.user_name)
        self.user_dropdown.grid(row=0, column=1, pady=10)

        self.num_sensors_label = ttk.Label(self.graph_frame, text='Number of Sensors : ')
        self.num_sensors_label.config(font=('Arial', 12))
        self.num_sensors_label.grid(row=1, column=0, pady=(5, 5))
        self.num_sensors_entry = ttk.Entry(self.graph_frame, textvariable=self.num_sensors)
        self.num_sensors_entry.grid(row=1, column=1, pady=(5, 5))

        self.freq_label = ttk.Label(self.graph_frame, text='Frequency (Hz) : ')
        self.freq_label.config(font=('Arial', 12))
        self.freq_label.grid(row=2, column=0, pady=(5, 5))
        self.freq_entry = ttk.Entry(self.graph_frame, textvariable=self.freq)
        self.freq_entry.grid(row=2, column=1, pady=(5, 5))

        self.runtime_label = ttk.Label(self.graph_frame, text='RUN Time (s) : ')
        self.runtime_label.config(font=('Arial', 12))
        self.runtime_label.grid(row=3, column=0, pady=(5, 5))
        self.runtime_entry = ttk.Entry(self.graph_frame, textvariable=self.runtime)
        self.runtime_entry.grid(row=3, column=1, pady=(5, 5))

        self.button = ttk.Button(self.graph_frame, textvariable=self.start_button_text,
                                 command=self.start_command, padding=(10, 20))
        self.button.grid(row=4, column=0, columnspan=2, sticky='WE', pady=(50, 20))

        # graph frame
        self.graph_frame = tk.Frame(self, bg='white')
        self.graph_frame.pack(side='top', fill='both', expand=True)
        self.graph_frame.grid_rowconfigure(0, weight=1)
        self.graph_frame.grid_columnconfigure(1, weight=1)

        self.fig = Figure(figsize=(20,3))
        self.ax1 = self.fig.add_subplot(121)
        self.ax2 = self.fig.add_subplot(122)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, padx=(1,1), pady=(1,1),
                                         sticky='WE')
        self.x, self.y1, self.y2 = [], [], []
        #ani = animation.FuncAnimation(self.fig, self.animate, interval=100, blit=False)
        self.ax1.plot(self.x, self.y1, color='r')
        self.ax2.plot(self.x, self.y2, color='b')

        # parameter
        self.is_start = False
        # instance
        self.d = None

    def start_command(self, mode='2'):
        if not self.is_start:  # going to start
            print('getting start...')
            self.start_button_text.set('STOP')
            self.is_start = True
            # create instance
            self.d = Daq(user_name=self.user_name.get(),
                         num_sensors=self.num_sensors.get(),
                         com='COM10',
                         sr=self.freq.get(),
                         plot_second=10)
            # main program
            if mode == '1':  # plot on new interface (old program)
                self.d.main(self.runtime.get())
            if mode == '2':  # plot on the gui
                th1 = threading.Thread(target=self.d.start_read_and_save)  # read arduino and save to sql
                ani = animation.FuncAnimation(self.fig, self.animate, interval=100, blit=False)

                # self.x.append(6)
                # self.y1.append(10)
                # self.y2.append(10)
                # self.ax1.clear()
                # self.ax2.clear()
                # self.ax1.plot(self.x, self.y1, color='g')
                # self.ax2.plot(self.x, self.y2, color='y')

                self.canvas.draw()

                th1.start()

            self.d.is_run = True

        else:  # going to stop
            print('going to stop...')
            self.start_button_text.set('START')
            self.is_start = False
            self.d.is_run = False
            #self.d.close()


    def animate(self, i):
        self.ax1.clear()
        self.ax2.clear()
        try:
            print(self.d.dqs[1])
            print('-----------')
            xx, yy = self.d.dqs[1], self.d.dqs[2]
            print(xx,'and', yy)
            print(self.x)
            print(self.y1)
            if xx is not None and yy is not None:
                self.x.append(xx)
                self.y1.append(yy)
                print('animate', i)
                print(self.x)
                print(self.y1)
            self.ax1.plot(xx, yy, color='r')
        except AttributeError as e:
            print('attributeerror:', e)
        except IndexError:
            print('indexerror')


    # def init_plot(self):
    #     line, = self.ax1.plot(self.x, self.y1)
    #
    #     print('init plot')
    #     #self.canvas.draw()

    def get_xy_series(self):
        pass

    # def ani_plot(self):
    #     # self.ax1.clear()
    #     # self.ax2.clear()
    #     # self.ax1.plot(np.arange(10), np.arange(10), color='b')
    #     # self.ax2.plot(np.arange(10), np.arange(10), color='r')
    #     # self.canvas.draw()
    #     # sleep(3)
    #     # self.ax1.clear()
    #     # self.ax2.clear()
    #     # self.ax1.plot(np.arange(10), np.arange(10), color='r')
    #     # self.ax2.plot(np.arange(10), np.arange(10), color='b')
    #     # self.canvas.draw()
    #     #self.ax1.plot(x, y)
    #     print('ani plot')
    #     ani = animation.FuncAnimation(self.fig, self.animate, interval=1000, blit=False)

    @staticmethod
    def get_user_names():
        user_names = []
        with open('user.csv', 'r') as f:
            for row in csv.reader(f):
                user_names.append(row[0].upper())
        return user_names

    def gui_size(self):
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        return f'{ws}x{hs}'


if __name__ == '__main__':
    app = FootDataOperatingPlatform()

    app.mainloop()

