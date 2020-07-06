import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from func import projectName_list, get_YlOrRd, read_YlOrRd, get_user_names, get_project_names
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
from time import sleep
import pandas as pd


class TitleFrame(tk.Frame):
    def __init__(self, container):
        super().__init__(container)
        self.configure(bg='white')
        self.title_ = ttk.Label(self, text='Plantar Data Acquisition and Visualization',
                                padding=(10, 10, 10, 10), background='darkslategrey', foreground='white')
        self.title_.config(font=('Helvetica', 20, 'bold'), anchor='center')

        # title components pack
        self.title_.pack(side=tk.TOP, fill='x', expand=True)


class FrontFrame(tk.Frame):
    def __init__(self, container, frame_2, frame_3, line_plot_command, illustrated_plot_command, history_command):
        super().__init__(container)
        self.configure(bg='blue')

        self.frame_2 = frame_2
        self.frame_3 = frame_3

        # Setting Frames
        self.figFrame = tk.Frame(self, padx=0, pady=0, bg='white')
        self.buttonFrame = tk.Frame(self, bg='white')
        self.figFrame.pack(side=tk.LEFT, padx=0, pady=0)
        self.buttonFrame.pack(side=tk.LEFT, fill='y')

        # figFrame
        self.foot_image = Image.open('fig/300x250.png')
        self.foot_image = ImageTk.PhotoImage(self.foot_image)

        self.foot_label = ttk.Label(self.figFrame, image=self.foot_image)
        self.foot_label.config(padding=(0,0,0,0), background='white')
        self.foot_label.grid(row=0, column=0, padx=0, pady=0)

        # buttonFrame
        self.lineplot_button = ttk.Button(self.buttonFrame, text='Line Plot', command=line_plot_command, cursor='hand1')
        self.illustrate_button = ttk.Button(self.buttonFrame, text='Illustrated Plot', command=illustrated_plot_command, cursor='hand1')

        self.history_data = ttk.Button(self.buttonFrame, text='History', command=history_command, cursor='hand1')

        self.history_data.pack(side=tk.BOTTOM, padx=20, pady=50, fill='both', expand=0)
        self.lineplot_button.pack(side=tk.BOTTOM, padx=20, pady=10, fill='both', expand=0)
        self.illustrate_button.pack(side=tk.BOTTOM, padx=20, pady=10, fill='both', expand=0)


class ParamFrame(tk.Frame):
    def __init__(self, container, start_command_fn):
        super().__init__(container)
        self.configure(bg='white')

        # Tk variable
        self.user_name = tk.StringVar()
        self.project_label = tk.StringVar(value='data')
        self.num_sensors = tk.IntVar(value=12)
        self.freq = tk.IntVar(value=10)
        self.max_runtime = tk.IntVar(value=60)
        self.start_button_text = tk.StringVar(value='START')
        self.message_text = tk.StringVar(value=f'User Name: \n\n{self.user_name.get()}')
        self.rpm = tk.IntVar(value=0)

        # user
        self.user_label = ttk.Label(self, text='User Name : ',
                                    foreground='red', background='white')
        self.user_label.config(font=('Georgia 14 bold'))
        self.user_label.focus()
        self.user_dropdown = ttk.Combobox(self, values=get_user_names(),
                                          textvariable=self.user_name)
        self.user_dropdown.bind('<<ComboboxSelected>>', self.set_user_name)

        # project
        self.project_name = ttk.Label(self, text='Project : ',
                                      foreground='red', background='white')
        self.project_name.config(font=('Georgia 14 bold'))
        self.project_dropdown = ttk.Combobox(self, values=projectName_list,
                                             textvariable=self.project_label)

        # project information
        self.project_info_label = ttk.Label(self, text='Project Info : ', background='white')
        self.project_info_label.config(font=('Georgia 14'))
        self.project_info_text = tk.Text(self, height=2, width=30)

        # num_sensors
        self.num_sensors_label = ttk.Label(self, text='Number of Sensors : ', background='white')
        self.num_sensors_label.config(font=('Georgia', 14))
        self.num_sensors_entry = ttk.Entry(self, textvariable=self.num_sensors)

        # sampling rate
        self.sr_label = ttk.Label(self, text='Sampling Rate (Hz) : ', background='white')
        self.sr_label.config(font=('Georgia', 14))
        self.sr_entry = ttk.Entry(self, textvariable=self.freq)

        # max run time
        self.max_runtime_label = ttk.Label(self, text='Max Run Time (s) : ', background='white')
        self.max_runtime_label.config(font=('Georgia', 14))
        self.max_runtime_entry = ttk.Entry(self, textvariable=self.max_runtime)

        # Start/Stop button
        self.button = ttk.Button(self, textvariable=self.start_button_text,
                                 command=start_command_fn, padding=(10, 20), cursor='hand2',
                                 takefocus=True)

        # param components grid
        self.user_label.grid(row=0, column=0, pady=(5, 5), stick='E')
        self.user_dropdown.grid(row=0, column=1, pady=(5, 5), stick='WE')
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

    # @staticmethod
    # def get_user_names():
    #     user_names = []
    #     with open('user.csv', 'r') as f:
    #         for row in csv.reader(f):
    #             user_names.append(row[0].upper())
    #     return user_names

    def set_user_name(self, event):
        self.message_text.set(f'User Name: \n\n {self.user_name.get()}')


class LinePlotFrame(tk.Frame):
    def __init__(self, container, d):
        super().__init__(container)
        self.configure(bg='paleturquoise', padx=1, pady=1)
        self.d = d

        # graph frame
        self.fig = Figure(figsize=(18.9, 3))
        self.ax1 = self.fig.add_subplot(121)
        self.ax2 = self.fig.add_subplot(122)
        self.fig.suptitle('Real Time Data Display Platform')
        self.ax1.set_ylabel('Amplitude')
        self.ax2.set_ylabel('Amplitude')
        self.color = ['maroon', 'indianred', 'goldenrod', 'gold', 'royalblue', 'darkblue',
                      'forestgreen', 'limegreen']
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(side=tk.LEFT, fill='x', expand=True, anchor='w')

    def update_(self, i):
        self.ax1.clear()
        self.ax2.clear()
        self.ax1.set_ylim(0, 0.8)
        self.ax2.set_ylim(0, 0.8)
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
            self.ax1.set_ylabel('Amplitude')
            self.ax2.set_ylabel('Amplitude')
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


class IllustratedFrame(tk.Frame):
    def __init__(self, container, d):
        super().__init__(container)
        self.configure(bg='red')
        self.d = d

        self.img = Image.open('fig/light.png')
        self.photo_img = ImageTk.PhotoImage(self.img)
        self.canvas_foot = tk.Canvas(self, width=self.img.size[0]+30, height=self.img.size[1]+20)
        self.canvas_foot.create_image(20,15, anchor='nw', image=self.photo_img)
        self.canvas_foot.grid(row=0, column=0)

        self.center_radius_list = [(240, 170, 20),
                                   (190, 172, 20),
                                   (140, 175, 20),
                                   (90, 180, 20),
                                   (170, 320, 20),
                                   (172, 350, 20)]
        self.init_circle_container = []

        for cx, cy, r in self.center_radius_list:
            left_ = self.canvas_foot.create_oval(cx - r, cy - r, cx + r, cy + r, fill='lightgrey', outline='white')
            right_ = self.canvas_foot.create_oval((640 - cx + r), cy - r, 640 - cx - r, cy + r, fill='lightgrey', outline='white')

            self.init_circle_container.append(left_)
            self.init_circle_container.append(right_)

    def animate(self):
        self.canvas_foot.delete(self.init_circle_container)
        sleep(0.2)
        count = 0

        time_ball = None

        while self.d.is_run:
            count += 1
            for i, (cx, cy, r) in enumerate(self.center_radius_list):
                left_ = self.canvas_foot.create_oval(
                    cx - r, cy - r, cx + r, cy + r,
                    #fill="#%02x%02x%02x" % (255 - int(255*self.d.da_contain[i+2]/0.8), 255 - int(255*self.d.da_contain[i+2]/0.8), 255), outline='white'
                    fill="#%02x%02x%02x" % self.get_rgb_from_cmap(self.d.da_contain[i+2]), outline='white'
                )
                right_ = self.canvas_foot.create_oval(
                    (640 - cx + r), cy - r, 640 - cx - r, cy + r,
                    #fill="#%02x%02x%02x" % (255 - int(255*self.d.da_contain[i+8]/0.8), 255 - int(255*self.d.da_contain[i+8]/0.8), 255), outline='white'
                    fill="#%02x%02x%02x" % self.get_rgb_from_cmap(self.d.da_contain[i+8]), outline='white'
                )

                self.init_circle_container.append(left_)
                self.init_circle_container.append(right_)

            # plot time_ball
            if count % 10 == 0:
                self.canvas_foot.delete(time_ball)
                time_ball = self.canvas_foot.create_rectangle(
                    0, 410, self.d.da_contain[1] * 640 / self.d.max_runtime + 10, 425,
                    #self.circle_to_coord(self.d.da_contain[1] * 640 / self.d.max_runtime, 410, 12),
                    fill='royalblue', outline='white'
                )
            sleep(0.1)

            # delete circle
            if count % 350 == 0:
                for item in self.init_circle_container:
                    self.canvas_foot.delete(item)
                self.init_circle_container = []

        else:
            self.canvas_foot.delete(time_ball)

    @staticmethod
    def circle_to_coord(center_x, center_y, radius):
        return center_x - radius, center_y - radius, center_x + radius, center_y + radius

    @staticmethod
    def get_rgb_from_cmap(weight_value):
        max_value = 1
        position = (weight_value / max_value) * 255
        c1, c2, c3 = read_YlOrRd()[int(position)]
        return c1, c2, c3


class InfoFrame(tk.Frame):
    def __init__(self, container, param_frame):
        super().__init__(container)
        self.param_frame = param_frame
        self.configure(padx=0, pady=2, bg='white')

        self.message = tk.Message(self, textvariable=self.param_frame.message_text,
                                  background='aliceblue', padx=50, pady=20, width=2000,
                                  font='Georgia 10', relief='raised')
        self.rpm_label1 = ttk.Label(self, text='RPM: ', background='white')
        self.rpm_label2 = ttk.Label(self, textvariable=self.param_frame.rpm, background='white')
        self.max_run_time_label1 = ttk.Label(self, text='Max Run Time: ', background='white')
        self.max_run_time_label2 = ttk.Label(self, textvariable=self.param_frame.max_runtime, background='white')

        self.rpm_label1.config(font=('Georgia', 20))
        self.rpm_label2.config(font=('Georgia', 50))
        self.max_run_time_label1.config(font=('Georgia', 20))
        self.max_run_time_label2.config(font=('Georgia', 30))
        # label components pack
        # self.message.pack(side=tk.TOP, fill='x', anchor='nw', expand=True, pady=50)
        # self.rpm_label1.pack(side=tk.LEFT)
        # self.rpm_label2.pack(side=tk.TOP)
        # self.max_run_time_label1.pack(side=tk.TOP)
        # self.max_run_time_label2.pack(side=tk.TOP)
        self.message.grid(row=0, column=0, columnspan=3)
        self.rpm_label1.grid(row=2, column=0, sticky='w')
        self.rpm_label2.grid(row=2, column=1, sticky='w')
        self.max_run_time_label1.grid(row=3, column=0, sticky='w', pady=10)
        self.max_run_time_label2.grid(row=3, column=1, sticky='w', pady=10)

    def get_real_time_rpm(self, d):
        while d.is_run:
            f = d.fft_freq
            self.param_frame.rpm.set(round(f, 1))
            sleep(2)


class BackFrame(tk.Frame):
    def __init__(self, container, frame_1, show_foot=True):
        super().__init__(container)
        self.configure(bg='white')
        self.frame_1 = frame_1

        self.frame_1_back_button = ttk.Button(self, text='←  BACK', command=self.back_button_fn, cursor='hand1')
        self.frame_1_back_button.pack(side=tk.LEFT)

        if show_foot:
            self.small_foot_image = ImageTk.PhotoImage(Image.open('fig/90x90.png'))
            self.foot_graph = ttk.Label(self, image=self.small_foot_image, background='white')
            self.foot_graph.pack(side=tk.LEFT)

    def back_button_fn(self):
        self.frame_1.tkraise()





class HistoryParamFrame(tk.Frame):
    def __init__(self, container, frame_1, input_command_fn, back_command):
        super().__init__(container)
        self.frame_1 = frame_1

        # Tk variable 暫時複製 ParmaFrame
        self.user_name = tk.StringVar()
        self.date = tk.StringVar()
        self.project = tk.StringVar()
        self.num_sensors = tk.IntVar(value=12)
        self.freq = tk.IntVar(value=10)
        self.max_runtime = tk.IntVar(value=60)
        self.start_button_text = tk.StringVar(value='START')
        self.message_text = tk.StringVar(value=f'User Name: \n\n{self.user_name.get()}')
        self.rpm = tk.IntVar(value=0)
        self.show = tk.StringVar(value='Raw Plot')
        self.info = tk.StringVar()

        # user
        self.user_label = ttk.Label(self, text='User Name* : ')
        self.user_label.config(font=('Georgia 13'))
        self.user_dropdown = ttk.Combobox(self, values=get_user_names(),
                                          textvariable=self.user_name)

        # date
        self.date_label = ttk.Label(self, text='Date : ')
        self.date_label.config(font=('Georgia 13'))
        self.date_dropdown = ttk.Combobox(self, values=self.get_dates(),
                                          textvariable=self.date)

        # project
        self.project_label = ttk.Label(self, text='Project* : ')
        self.project_label.config(font=('Georgia 13'))
        self.project_dropdown = ttk.Combobox(self, values=get_project_names(),
                                             textvariable=self.project)

        # info
        self.info_label = ttk.Label(self, text='Info : ')
        self.info_label.config(font=('Georgia 13'))
        self.info_dropdown = ttk.Combobox(self, values='',
                                             textvariable=self.info)

        # Show
        self.show_label = ttk.Label(self, text='Show : ')
        self.show_label.config(font=('Georgia 13'))
        self.show_dropdown = ttk.Combobox(self, values=['Raw Plot', 'Pressure Plot', 'fft'],
                                             textvariable=self.show)

        # button
        self.historyBackButton = ttk.Button(self, text='←  BACK', command=back_command, cursor='hand1')
        self.historyInputButton = ttk.Button(self, text='INPUT',
                                 command=input_command_fn, padding=(10, 20), cursor='hand2',
                                 takefocus=True)


        # grid
        self.historyBackButton.grid(row=0, column=0, padx=(10,100))
        self.project_label.grid(row=0, column=1)
        self.project_dropdown.grid(row=1, column=1)
        self.user_label.grid(row=0, column=2)
        self.user_dropdown.grid(row=1, column=2)
        self.date_label.grid(row=0, column=3)
        self.date_dropdown.grid(row=1, column=3)
        self.info_label.grid(row=0, column=4)
        self.info_dropdown.grid(row=1, column=4)
        self.show_label.grid(row=0, column=5)
        self.show_dropdown.grid(row=1, column=5)
        self.historyInputButton.grid(row=0, column=6, rowspan=2)

    def get_dates(self, user=None, project=None, info=None):
        pass

    def get_schema_names(self):
        '''
            SELECT datname
            FROM pg_database
            WHERE schema
            AND datistemplate = false
            ;
        '''


class HistoryLinePlotFrame(tk.Frame):
    def __init__(self, container):
        super().__init__(container)

        self.scrollableFrame = ScrollableFrame(self)

        self.color = ['maroon', 'indianred', 'goldenrod', 'gold', 'royalblue', 'darkblue',
                      'forestgreen', 'limegreen']
        self.fig = None
        self.canvas = None
        self.canvas_widget = None

        self.scrollableFrame.pack(fill=tk.X)

    def makeAndPutFigs(self, tableNames):
        for tableName in tableNames:
            self.fig = self.makeOneFig(tableName)
            self.putFig(self.fig)

    @staticmethod
    def makeOneFig(title, data, figsize=(20, 2.8)):
        num_sensors_per_foot = (data.shape[1] - 2) // 2

        fig = Figure(figsize=figsize)
        ax1 = fig.add_subplot(121)
        ax2 = fig.add_subplot(122)
        ax1.set_ylim(0, 0.8)
        ax2.set_ylim(0, 0.8)
        t = data.iloc[:300, 1]
        for i in range(0, num_sensors_per_foot):
            ax1.plot(t, data.iloc[:300, i+2])
            ax2.plot(t, data.iloc[:300, i+num_sensors_per_foot+2])
        fig.suptitle(title)
        ax1.set_ylabel('Amplitude')
        ax2.set_ylabel('Amplitude')
        return fig

    def putFig(self, fig):
        self.canvas = FigureCanvasTkAgg(fig, master=self.scrollableFrame.scrollable_frame)
        self.canvas.draw()
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side=tk.TOP, fill='x', expand=True, anchor='w')

    def putNextPageButton(self, next_page_fn):
        self.nextPageButton = ttk.Button(self.scrollableFrame.scrollable_frame, text='NEXT PAGE',
                                         command=next_page_fn, padding=(10,30))
        self.nextPageButton.pack(side=tk.TOP, anchor='e', expand=True, fill='x', pady=20)


class HistoryFftPlotFrame(tk.Frame):
    def __init__(self, container):
        super().__init__(container)


class HistoryTableFrame(tk.Frame):
    def __init__(self, container):
        super().__init__(container)


class ScrollableFrame(tk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tk.Canvas(self, width=200, height=920)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set, bg='darkblue')

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")


if __name__ == '__main__':

    root = tk.Tk()
    #frame = HistoryParamFrame(root, lambda: print('test command'))
    frame = HistoryLinePlotFrame(root)
    frame.pack()
    root.mainloop()

