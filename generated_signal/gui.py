import tkinter as tk
from arduino_to_sql_3 import Daq
import threading
from time import sleep
from frames import ParamFrame, FrontFrame, LinePlotFrame, InfoFrame, TitleFrame, BackFrame, IllustratedFrame


class FootDataOperatingPlatform(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Healthy Data Operating Platform')
        self.geometry(self.gui_size())
        self.configure(bg='white')

        # create 1st_frame
        self.frame_0 = TitleFrame(self)  # Title Frame
        self.frame_1 = tk.Frame(self)  # Greeting Frame
        self.frame_2 = tk.Frame(self)  # Line Plot Frame
        self.frame_3 = tk.Frame(self)  # Foot Plot Frame

        self.frame_1.configure(bg='white')
        self.frame_2.configure(bg='white')
        self.frame_3.configure(bg='white')

        self.frame_0.place(relx=0, rely=0, relwidth=1, relheight=0.075)

        # frame_1
        self.frontFrame = FrontFrame(self.frame_1, self.frame_2, self.frame_3,
                                     self.line_plot_command, self.illustrated_plot_command)
        self.frontFrame.pack(side=tk.TOP, expand=0, anchor='center', pady=150)

        # objects in frames
        self.back_frame = None
        self.param_frame = None
        self.info_frame = None
        self.lineplot_frame = None
        self.illustrated_frame = None

        self.frame_1.place(relx=0, rely=0.08, relwidth=1, relheight=0.9)
        self.frame_2.place(relx=0, rely=0.08, relwidth=1, relheight=0.9)
        self.frame_3.place(relx=0, rely=0.08, relwidth=1, relheight=0.9)

        # frames
        self.frame_1.tkraise()

        # parameter
        self.is_start = False
        self.is_ani = False
        self.plot_way = None

        # instance
        self.d = None


    def start_command(self):
        if not self.is_start:  # going to start

            print('getting start...')
            self.param_frame.start_button_text.set('STOP')
            self.is_start = True
            # create DAQ instance
            self.d = Daq(user_name=self.param_frame.user_name.get(),
                         num_sensors=self.param_frame.num_sensors.get(),
                         sr=self.param_frame.freq.get(),
                         max_runtime=self.param_frame.max_runtime.get(),
                         project_name=self.param_frame.project_label.get(),
                         project_info=self.param_frame.project_info_text.get(1.0, 'end'),
                         com1='COM10',
                         com2='COM12',
                         plot_second=10)

            # main program
            th1 = threading.Thread(target=self.d.start_read_and_save)  # read arduino and save to sql
            th2 = threading.Thread(target=self.d.real_time_rpm)
            th3 = threading.Thread(target=self.info_frame.get_real_time_rpm, args=(self.d,))

            th1.start()

            self.d.is_run = True

            # Line Plot for first animate:
            if self.plot_way == 'line_plot':
                print('animating...')
                self.lineplot_frame.d = self.d
                if not self.is_ani:
                    print('line plot')
                    self.lineplot_frame.animate()
            # Illustrated Plot:
            if self.plot_way == 'illustrated_plot':
                th4 = threading.Thread(target=self.illustrated_frame.animate)
                self.illustrated_frame.d = self.d
                th4.start()
                print('illustrated plot')
            self.is_ani = True
            self.is_start = self.d.is_run
            th2.start()
            sleep(2)
            th3.start()
            print('tableName', self.d.tableName)
            self.param_frame.message_text.set(f'Table Name : \n\n{self.d.tableName}')
            self.back_frame.frame_1_back_button.config(state=tk.DISABLED)

        else:  # going to stop
            print('going to stop...')
            self.param_frame.start_button_text.set('START')
            self.back_frame.frame_1_back_button.config(state=tk.NORMAL)
            self.is_start = False
            self.d.is_run = False

    def gui_size(self):
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        return f'{int(ws*0.99)}x{int(hs*2.1//3)}'

    def back(self):
        self.frame_1.tkraise()

    def create_frame_elements(self, *, frame, back_frame, param_frame, plot_frame, info_frame,
                              frame_1, start_command):
        self.param_frame = ParamFrame(frame, start_command)
        self.info_frame = InfoFrame(frame, param_frame=self.param_frame)
        self.lineplot_frame = LinePlotFrame(frame, d=None)
        self.illustrated_frame = IllustratedFrame(frame, d=None)

        if self.plot_way == 'line_plot':
            self.back_frame = BackFrame(frame, frame_1, show_foot=True)

            self.back_frame.grid(row=0, column=0, sticky='W', padx=20)
            self.info_frame.grid(row=0, column=2)
            self.param_frame.grid(row=0, column=1, sticky='W')
            self.lineplot_frame.grid(row=1, column=0, columnspan=3)

        elif self.plot_way == 'illustrated_plot':
            self.back_frame = BackFrame(frame, frame_1, show_foot=False)

            self.back_frame.grid(row=0, column=0, sticky='W', padx=20, pady=100)
            self.param_frame.grid(row=0, column=1, sticky='W', padx=100, pady=100)
            self.illustrated_frame.grid(row=0, column=2, columnspan=2, padx=80, pady=100)
            self.info_frame.grid(row=0, column=4, padx=100, sticky='E', pady=100)

    def line_plot_command(self):
        self.plot_way = 'line_plot'
        try:
            for item in self.frame_2.grid_slaves():
                item.destroy()

        except Exception as ex:
            print('nothing to destroy...', ex)

        self.is_ani = False
        self.create_frame_elements(
            frame=self.frame_2, back_frame=BackFrame, param_frame=ParamFrame, plot_frame=LinePlotFrame,
            info_frame=InfoFrame, frame_1=self.frame_1, start_command=self.start_command
        )
        self.frame_2.tkraise()

    def illustrated_plot_command(self):
        self.plot_way = 'illustrated_plot'
        try:
            for item in self.frame_3.grid_slaves():
                item.destroy()
        except Exception as ex:
            print('nothing to destroy ', ex)

        self.create_frame_elements(
            frame=self.frame_3, back_frame=BackFrame, param_frame=ParamFrame, plot_frame=LinePlotFrame,
            info_frame=InfoFrame, frame_1=self.frame_1, start_command=self.start_command
        )
        self.frame_3.tkraise()






