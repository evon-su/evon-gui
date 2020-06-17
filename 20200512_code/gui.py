import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from arduino_to_sql_3 import Daq
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import csv

class FootDataOperatingPlatform(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Healthy Data Operating Platform')
        self.geometry(self.gui_size())
        self.parameter_frame = tk.Frame(self, bg='white', pady=20)
        self.parameter_frame.pack()
        self.parameter_frame.grid_rowconfigure(0, weight=1)
        self.parameter_frame.grid_columnconfigure(1, weight=1)
        # Variable
        self.user_name = tk.StringVar(value='user')
        self.num_sensors = tk.IntVar(value=6)
        self.freq = tk.IntVar(value=20)
        self.runtime = tk.IntVar(value=60)
        self.start_button_text = tk.StringVar(value='START')
        # --Widget--
        self.user_label = ttk.Label(self.parameter_frame, text='User Name : ')
        self.user_label.config(font=('Arial', 12))
        self.user_label.grid(row=0, column=0, pady=(5, 5))
        self.user_dropdown = ttk.Combobox(self.parameter_frame, values=self.get_user_names(),
                                          textvariable=self.user_name)
        self.user_dropdown.grid(row=0, column=1, pady=10)

        self.num_sensors_label = ttk.Label(self.parameter_frame, text='Number of Sensors : ')
        self.num_sensors_label.config(font=('Arial', 12))
        self.num_sensors_label.grid(row=1, column=0, pady=(5, 5))
        self.num_sensors_entry = ttk.Entry(self.parameter_frame, textvariable=self.num_sensors)
        self.num_sensors_entry.grid(row=1, column=1, pady=(5, 5))

        self.freq_label = ttk.Label(self.parameter_frame, text='Frequency (Hz) : ')
        self.freq_label.config(font=('Arial', 12))
        self.freq_label.grid(row=2, column=0, pady=(5, 5))
        self.freq_entry = ttk.Entry(self.parameter_frame, textvariable=self.freq)
        self.freq_entry.grid(row=2, column=1, pady=(5, 5))

        self.runtime_label = ttk.Label(self.parameter_frame, text='RUN Time (s) : ')
        self.runtime_label.config(font=('Arial', 12))
        self.runtime_label.grid(row=3, column=0, pady=(5, 5))
        self.runtime_entry = ttk.Entry(self.parameter_frame, textvariable=self.runtime)
        self.runtime_entry.grid(row=3, column=1, pady=(5, 5))

        self.button = ttk.Button(self.parameter_frame, textvariable=self.start_button_text,
                                 command=self.start_command, padding=(10, 20))
        self.button.grid(row=4, column=0, columnspan=2, sticky='WE', pady=(50, 20))

        # figure
        #self.fig, self.axes = plt.subplots(1, 2, figsize=(20, 3))
        #self.graph = FigureCanvasTkAgg(self.fig, master=self)
        #self.graph.get_tk_widget().pack()

        # parameter
        self.is_start = False
        # instance
        self.d = None

    def start_command(self):

        if not self.is_start:
            print('getting start...')
            self.start_button_text.set('STOP')
            self.is_start = True
            # create instance
            self.d = Daq(user_name=self.user_name.get(),
                         num_sensors=self.num_sensors.get(),
                         com='COM10',
                         sr=self.freq.get(),
                         plot_second=5)
            # main program
            self.d.main(self.runtime.get())
            self.d.is_run = True
        else:
            print('going to stop...')
            self.start_button_text.set('START')
            self.is_start = False
            self.d.is_run = False
            try:
                self.d.close()
            except:
                print('there is no instance of Daq()')

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

