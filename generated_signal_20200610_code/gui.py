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
from func import cal_rpm, projectName_list
import pandas as pd


class FootDataOperatingPlatform(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Healthy Data Operating Platform')
        #self.geometry(self.gui_size())
        # self.state('zoomed')
        self.configure(bg='white')

        # self.graph_frame.grid_rowconfigure(0, weight=1)
        # self.graph_frame.grid_columnconfigure(0, weight=1)

        # Variable
        self.user_name = tk.StringVar()
        self.project_label = tk.StringVar(value='data')
        self.num_sensors = tk.IntVar(value=12)
        self.freq = tk.IntVar(value=10)
        self.max_runtime = tk.IntVar(value=60)
        self.start_button_text = tk.StringVar(value='START')
        self.message_text = tk.StringVar(value=f'User Name: \n\n{self.user_name.get()}')
        self.rpm = tk.DoubleVar(value=0.)

        # create frame
        self.title_frame = tk.Frame(self, bg='white')
        self.param_frame = tk.Frame(self, bg='white', pady=10)
        self.graph_frame = tk.Frame(self, bg='white', padx=0, pady=10)
        self.label_frame = tk.Frame(self, bg='white', padx=0, pady=2)

        # frame pack
        self.title_frame.grid(row=0, column=0, columnspan=3, sticky='WE')
        self.param_frame.grid(row=1, column=1)
        self.label_frame.grid(row=1, column=2, sticky='N')
        self.graph_frame.grid(row=2, column=0, columnspan=3, sticky='WE')

        # --Widget--
        # param frame components
        # user
        self.user_label = ttk.Label(self.param_frame, text='User Name : ',
                                    foreground='red', background='white')
        self.user_label.config(font=('Times 14 bold'))
        self.user_label.focus()
        self.user_dropdown = ttk.Combobox(self.param_frame, values=self.get_user_names(),
                                          textvariable=self.user_name)
        self.user_dropdown.bind('<<ComboboxSelected>>', self.set_user_name)

        # project
        self.project_name = ttk.Label(self.param_frame, text='Project : ',
                                      foreground='red', background='white',)
        self.project_name.config(font=('Times 14 bold'))
        self.project_dropdown = ttk.Combobox(self.param_frame, values=projectName_list,
                                             textvariable=self.project_label)

        # project information
        self.project_info_label = ttk.Label(self.param_frame, text='Project Info : ',
                                            background='white')
        self.project_info_label.config(font=('Times 14'))
        self.project_info_text = tk.Text(self.param_frame, height=2, width=30)

        # num_sensors
        self.num_sensors_label = ttk.Label(self.param_frame, text='Number of Sensors : ',
                                           background='white')
        self.num_sensors_label.config(font=('Times', 14))
        self.num_sensors_entry = ttk.Entry(self.param_frame, textvariable=self.num_sensors)

        # sampling rate
        self.sr_label = ttk.Label(self.param_frame, text='Sampling Rate (Hz) : ',
                                    background='white')
        self.sr_label.config(font=('Times', 14))
        self.sr_entry = ttk.Entry(self.param_frame, textvariable=self.freq)

        # max run time
        self.max_runtime_label = ttk.Label(self.param_frame, text='Max Run Time (s) : ',
                                           background='white')
        self.max_runtime_label.config(font=('Times', 14))
        self.max_runtime_entry = ttk.Entry(self.param_frame, textvariable=self.max_runtime)

        # Start/Stop button
        self.button = ttk.Button(self.param_frame, textvariable=self.start_button_text,
                                 command=self.start_command, padding=(10, 20), cursor='hand2',
                                 takefocus=True)

        # param components grid
        self.user_label.grid(row=0, column=0, pady=(5, 5), stick='E')
        self.user_dropdown.grid(row=0, column=1, pady=(5,5), stick='WE')
        self.project_name.grid(row=1, column=0, pady=(5, 5), stick='E')
        self.project_dropdown.grid(row=1, column=1, pady=10, stick='WE')
        self.project_info_label.grid(row=2, column=0, pady=(5, 5), stick='E')
        self.project_info_text.grid(row=2, column=1, pady=(5, 5), stick='WE')
        self.num_sensors_label.grid(row=3, column=0, pady=(5, 5), stick='E')
        self.num_sensors_entry.grid(row=3, column=1, pady=(5, 5), stick='WE')
        self.sr_label.grid(row=4, column=0, pady=(5, 5), stick='E')
        self.sr_entry.grid(row=4, column=1, pady=(5, 5), stick='WE')
        self.max_runtime_label.grid(row=5, column=0, pady=(5, 5), stick='E')
        self.max_runtime_entry.grid(row=5, column=1, pady=(5, 5), stick='WE')
        self.button.grid(row=6, column=0, columnspan=2, sticky='WE', pady=(20, 20), stick='WE')

        # title frame components
        self.title_ = ttk.Label(self.title_frame, text='Plantar Data Acquisition and Visualization',
                                padding=(10,10,10,10), background='darkslategrey', foreground='white')
        self.title_.config(font=('Helvetica', 20, 'bold'), anchor='center')

        # title components pack
        self.title_.pack(fill='x')

        # graph frame
        self.graph_frame.grid_rowconfigure(0, weight=1)
        self.graph_frame.grid_columnconfigure(0, weight=1)

        self.fig = Figure(figsize=(20,3))
        self.ax1 = self.fig.add_subplot(121)
        self.ax2 = self.fig.add_subplot(122)
        self.fig.suptitle('Real Time Data Display Platform')
        self.ax1.set_xlabel('time (s)')
        self.ax2.set_xlabel('time (s)')
        self.color = ['maroon', 'indianred', 'goldenrod', 'gold', 'royalblue', 'darkblue',
                      'forestgreen', 'limegreen']
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill='x')

        # label frame component
        self.message = tk.Message(self.label_frame, textvariable=self.message_text,
                                  background='aliceblue', padx=50, pady=20, width=2000,
                                  font='Georgia 10'
                                  )
        self.rpm_label1 = ttk.Label(self.label_frame, text='RPM: ', background='white')
        self.rpm_label2 = ttk.Label(self.label_frame, textvariable=self.rpm)
        self.rpm_label1.config(font=('Georgia', 20))
        self.rpm_label2.config(font=('Georgia', 50))

        # label components pack
        self.message.pack(side=tk.TOP, fill='x', anchor='nw', expand=True, pady=50)
        self.rpm_label1.pack(side=tk.LEFT)
        self.rpm_label2.pack(side=tk.LEFT)

        # parameter
        self.is_start = False
        # instance
        self.d = None

        self.is_ani = False

    def set_user_name(self, event):
        self.message_text.set(f'User Name: \n\n {self.user_name.get()}')

    def start_command(self):
        if not self.is_start:  # going to start

            print('getting start...')
            self.start_button_text.set('STOP')
            self.is_start = True
            # create DAQ instance
            self.d = Daq(user_name=self.user_name.get(),
                         num_sensors=self.num_sensors.get(),
                         sr=self.freq.get(),
                         max_runtime=self.max_runtime.get(),
                         project_name=self.project_label.get(),
                         project_info=self.project_info_text.get(1.0, 'end'),
                         com1='COM10',
                         com2='COM12',
                         plot_second=10)

            # main program
            th1 = threading.Thread(target=self.d.start_read_and_save)  # read arduino and save to sql
            th2 = threading.Thread(target=self.real_time_rpm)
            th1.start()

            self.d.is_run = True

            if not self.is_ani:
                print('animating...')
                self.animate()
            self.is_ani = True
            th2.start()
            sleep(2)
            self.message_text.set(f'Table Name : \n\n{self.d.tableName}')

        else:  # going to stop
            print('going to stop...')
            self.start_button_text.set('START')
            self.is_start = False
            self.d.is_run = False

    def update_(self, i):
        if self.is_start:
            self.ax1.clear()
            self.ax2.clear()
            self.ax1.set_ylim(-1, 1)
            self.ax2.set_ylim(-1, 1)
            try:
                for plot_i, color in zip(range(self.d.num_sensors // 2), self.color):
                    self.ax1.plot(self.d.dqs[1], self.d.dqs[plot_i + 2], lw=1.5,
                                  label=f'a{plot_i}', marker=None, color=color)
                for plot_i, color in zip(range(self.d.num_sensors // 2, self.d.num_sensors), self.color):
                    self.ax2.plot(self.d.dqs[1], self.d.dqs[plot_i + 2], lw=1.5, label=f'a{plot_i}',
                                  marker=None, color=color)
                self.ax1.legend(loc='upper left')
                self.ax2.legend(loc='upper left')
                self.ax1.grid()
                self.ax2.grid()
                self.ax1.set_xlabel('time (s)')
                self.ax2.set_xlabel('time (s)')
            except AttributeError as e:
                print('Attributeerror:', e)
            except IndexError as e:
                print('Indexerror: ', e)

    def animate(self):
        self.ax1.clear()
        self.ax2.clear()
        ani = animation.FuncAnimation(self.fig, self.update_, interval=100,
                                      blit=False, repeat=False)
        self.canvas.draw()

    def real_time_rpm(self):
        sleep(5)
        while self.is_start:
            f = cal_rpm(self.d.dqs[2], self.d.plot_second)
            self.rpm.set(round(f, 1))
            print('---', f, '---')
            sleep(2)

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




