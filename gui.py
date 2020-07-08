import tkinter as tk
from arduino_to_sql_3 import Daq
import threading
from time import sleep
from frames import ParamFrame, FrontFrame, LinePlotFrame, InfoFrame, TitleFrame, \
                   BackFrame, IllustratedFrame, HistoryParamFrame, HistoryLinePlotFrame, ScrollableFrame
from data import DataBase
import pandas as pd


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
        self.frame_4 = tk.Frame(self)

        self.frame_1.configure(bg='white')
        self.frame_2.configure(bg='white')
        self.frame_3.configure(bg='white')
        self.frame_4.configure(bg='white')

        self.frame_0.place(relx=0, rely=0, relwidth=1, relheight=0.075)

        # frame_1
        self.frontFrame = FrontFrame(self.frame_1, self.frame_2, self.frame_3,
                                     self.line_plot_command, self.illustrated_plot_command, self.history_frame_command)
        self.frontFrame.pack(side=tk.TOP, expand=0, anchor='center', pady=150)

        # live plot frame objects
        self.back_frame = None
        self.param_frame = None
        self.info_frame = None
        self.lineplot_frame = None
        self.illustrated_frame = None

        # history frame objects
        self.history_param_frame = None
        self.history_lineplot_frame = None

        # Put big frames
        self.frame_1.place(relx=0, rely=0.07, relwidth=1, relheight=0.9)
        self.frame_2.place(relx=0, rely=0.07, relwidth=1, relheight=0.9)
        self.frame_3.place(relx=0, rely=0.07, relwidth=1, relheight=0.9)
        self.frame_4.place(relx=0, rely=0.00, relwidth=1, relheight=0.99)

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

    def history_start_command(self, show='Raw Plot'):
        def nextPageFn():
            try:
                for item in self.history_lineplot_frame.scrollableFrame.scrollable_frame.pack_slaves():
                    item.destroy()
            except Exception as ex:
                print('nothing to destroy ', ex)
            try:
                onePagePlot(num_figs=num_figs)
            except StopIteration:
                print('stopiteration')
                pass
            else:
                print('create another next btn')
                self.history_lineplot_frame.putNextPageButton(next_page_fn=nextPageFn)

        def onePagePlot(num_figs=10):
            #i = 1
            while True:
                n, tableName, data = next(self.data_gen)
                title = tableName + f'  ({n:02d})'
                # make and put figs
                fig = self.history_lineplot_frame.makeOneFig(title, data)
                self.history_lineplot_frame.putFig(fig)
                #i += 1
                if n % num_figs == 0:
                    break
        # clear previous slaves
        try:
            for item in self.history_lineplot_frame.scrollableFrame.scrollable_frame.pack_slaves():
                item.destroy()
        except Exception as ex:
            print('nothing to destroy ', ex)

        # filter tables
        projectName = self.history_param_frame.project.get()
        userName = self.history_param_frame.user_name.get()
        date = self.history_param_frame.date.get()
        info = self.history_param_frame.info.get()
        time_init = self.history_param_frame.time_init_value.get()
        time_end = self.history_param_frame.time_end_value.get()

        # setting value
        self.history_lineplot_frame.time_init = time_init
        self.history_lineplot_frame.time_end = time_end
        #self.history_lineplot_frame.time_end = time_end

        # number of figures per page
        num_figs = 10

        if date:
            dates = [date]
        else:
            dates = self.database.getAllDates(projectName, userName)
        print('dates: ', dates)

        tableNames = self.database.getBunchTables(project=projectName.lower(),
                                             user=userName.lower(), dates=dates, info=info)
        self.history_param_frame.page.set(f'TOTAL " {len(tableNames)} " FIGS')
        print('tableNames: ', tableNames)

        self.data_gen = self.database.readBunchTables_gen(tableNames)

        # Line Plot
        if show == 'Raw Plot':
            try:
                onePagePlot(num_figs=num_figs)
                self.history_lineplot_frame.putNextPageButton(next_page_fn=nextPageFn)
            except StopIteration:
                pass

        # Pressure Plot

        # fft plot

    def line_plot_command(self):
        self.state('normal')
        self.plot_way = 'line_plot'
        try:
            print('frame2 slaves', self.frame_2.grid_slaves())
            for item in self.frame_2.grid_slaves():
                item.destroy()

        except Exception as ex:
            print('nothing to destroy...', ex)

        self.is_ani = False
        self.create_liveFrame_elements(
            frame=self.frame_2, back_frame=BackFrame, param_frame=ParamFrame, plot_frame=LinePlotFrame,
            info_frame=InfoFrame, frame_1=self.frame_1, start_command=self.start_command
        )
        self.frame_2.tkraise()

    def illustrated_plot_command(self):
        self.state('normal')
        self.plot_way = 'illustrated_plot'
        try:
            for item in self.frame_3.grid_slaves():
                item.destroy()
        except Exception as ex:
            print('nothing to destroy ', ex)

        self.create_liveFrame_elements(
            frame=self.frame_3, back_frame=BackFrame, param_frame=ParamFrame, plot_frame=LinePlotFrame,
            info_frame=InfoFrame, frame_1=self.frame_1, start_command=self.start_command
        )
        self.frame_3.tkraise()

    def history_frame_command(self):
        self.state('zoomed')
        try:
            print('slaves', self.frame_4.grid_slaves())
            for item in self.frame_4.grid_slaves():
                item.destroy()
        except Exception as ex:
            print('nothing to destroy...', ex)

        # create self.frame_4
        self.create_historyFrame_elements()

        # tkraise frame_4
        self.frame_4.tkraise()

    def create_liveFrame_elements(self, *, frame, back_frame, param_frame, plot_frame, info_frame,
                                  frame_1, start_command):
        self.param_frame = ParamFrame(frame, start_command)
        self.info_frame = InfoFrame(frame, param_frame=self.param_frame)
        self.lineplot_frame = LinePlotFrame(frame, d=None)
        self.illustrated_frame = IllustratedFrame(frame, d=None)

        if self.plot_way == 'line_plot':
            self.back_frame = BackFrame(frame, frame_1, show_foot=True)

            self.back_frame.grid(row=0, column=0, sticky='W', padx=20)
            self.info_frame.grid(row=0, column=2, sticky='W')
            self.param_frame.grid(row=0, column=1, sticky='W')
            self.lineplot_frame.grid(row=1, column=0, columnspan=3)

        elif self.plot_way == 'illustrated_plot':
            self.back_frame = BackFrame(frame, frame_1, show_foot=False)

            self.back_frame.grid(row=0, column=0, sticky='W', padx=20, pady=100)
            self.param_frame.grid(row=0, column=1, sticky='W', padx=100, pady=100)
            self.illustrated_frame.grid(row=0, column=2, columnspan=2, padx=30, pady=100)
            self.info_frame.grid(row=0, column=4, padx=100, sticky='W', pady=100)

    def create_historyFrame_elements(self):
        def user_selec_cmd(event):
            projectName = self.history_param_frame.project.get()
            userName = self.history_param_frame.user_name.get()
            dates = self.database.getAllDates(projectName, userName)
            self.history_param_frame.date_dropdown['value'] = dates
            self.history_param_frame.date_dropdown.set('')

        def project_selec_cmd(event):
            projectName = self.history_param_frame.project.get()
            users = self.database.getAllUsers(projectName)
            self.history_param_frame.user_dropdown['value'] = users
            self.history_param_frame.user_dropdown.set('')
            self.history_param_frame.date_dropdown.set('')

        # create database class object
        self.database = DataBase()
        # create history param frame
        self.history_param_frame = HistoryParamFrame(self.frame_4, self.frame_1,
                                                     self.history_start_command, self.back)
        # bind
        self.history_param_frame.project_dropdown.bind("<<ComboboxSelected>>", project_selec_cmd)
        self.history_param_frame.user_dropdown.bind("<<ComboboxSelected>>", user_selec_cmd)
        self.history_lineplot_frame = HistoryLinePlotFrame(self.frame_4)

        # frame_4
        self.history_param_frame.place(relx=0.01, rely=0, relwidth=0.99, relheight=0.08)
        self.history_lineplot_frame.place(relx=0.01, rely=0.08, relwidth=0.99, relheight=0.99)

    def gui_size(self):
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        return f'{int(ws * 0.99)}x{int(hs * 2.1 // 3)}'

    def back(self):
        self.state('normal')
        self.frame_0.tkraise()
        self.frame_1.tkraise()

if __name__ == '__main__':
    root = tk.Tk()
    frame = tk.Frame(root)
    frame.pack()

    scrollbar = tk.Scrollbar(frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    lb=tk.Text(frame, yscrollcommand=scrollbar.set)
    lb.pack()
    scrollbar.config(command=lb.yview)

    root.mainloop()