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
        self.num_sensors = tk.IntVar(value=12)
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

        self.fig = Figure(figsize=(20,6))
        self.ax1 = self.fig.add_subplot(211)
        self.ax2 = self.fig.add_subplot(212)
        self.ax1.set_ylim(0, 1)
        self.ax2.set_ylim(0, 1)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, padx=(1,1), pady=(1,1),
                                         sticky='WE')

        # parameter
        self.is_start = False
        # instance
        self.d = None

    def start_command(self):
        if not self.is_start:  # going to start
            print('getting start...')
            self.start_button_text.set('STOP')
            self.is_start = True
            # create DAQ instance
            self.d = Daq(user_name=self.user_name.get(),
                         num_sensors=self.num_sensors.get(),
                         sr=self.freq.get(),
                         max_runtime=self.runtime.get(),
                         com1='COM10',
                         com2='COM12',
                         plot_second=10)
            # main program
            th1 = threading.Thread(target=self.d.start_read_and_save)  # read arduino and save to sql
            # th2 = threading.Thread(target=self.animate)
            self.d.is_run = True

            th1.start()
            self.animate()
            # th2.start()
            # ani = animation.FuncAnimation(self.fig, self.update_, interval=100, blit=False)
            # self.canvas.draw()


        else:  # going to stop
            print('going to stop...')
            self.start_button_text.set('START')
            self.is_start = False
            self.d.is_run = False

    def update_(self, i):
        self.ax1.clear()
        self.ax2.clear()

        try:
            for plot_i in range(self.d.num_sensors // 2):
                self.ax1.plot(self.d.dqs[1], self.d.dqs[plot_i + 2], lw=1.5, label=f'a{plot_i}', marker=None)
            for plot_i in range(self.d.num_sensors // 2, self.d.num_sensors):
                self.ax2.plot(self.d.dqs[1], self.d.dqs[plot_i + 2], lw=1.5, label=f'a{plot_i}', marker=None)
            self.ax1.legend(loc='upper left')
            self.ax2.legend(loc='upper left')
        except AttributeError as e:
            print('Attributeerror:', e)
        except IndexError:
            print('Indexerror')

    def animate(self):
        self.ax1.set_ylim(0, 0.8)
        self.ax2.set_ylim(0, 0.8)
        ani = animation.FuncAnimation(self.fig, self.update_, interval=100, blit=False)
        self.canvas.draw()

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

