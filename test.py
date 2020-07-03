import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk
from skimage import draw, data
import matplotlib.pyplot as plt
import numpy as np

from matplotlib import cm


def get_jet():
    colormap_int = np.zeros((256, 3), np.uint8)
    colormap_float = np.zeros((256, 3), np.float)

    for i in range(0, 256, 1):
        colormap_float[i, 0] = cm.jet(i)[0]
        colormap_float[i, 1] = cm.jet(i)[1]
        colormap_float[i, 2] = cm.jet(i)[2]

        colormap_int[i, 0] = np.int_(np.round(cm.jet(i)[0] * 255.0))
        colormap_int[i, 1] = np.int_(np.round(cm.jet(i)[1] * 255.0))
        colormap_int[i, 2] = np.int_(np.round(cm.jet(i)[2] * 255.0))

    return colormap_int


def get_rgb_from_cmap(weight_value):
    max_value = 1
    position = (weight_value / max_value) * 256
    color = get_jet()[int(position)]
    print(*color)
    return color


# root = tk.Tk()
#
# fig = Figure(figsize=(10, 3))
# ax1 = fig.add_subplot(111)
# ax1.set_xlabel('time (s)')
# canvas = FigureCanvasTkAgg(fig, master=root)
# canvas.get_tk_widget().pack(side=tk.TOP, fill='x', expand=True)
#
# root.mainloop()






class ScrollableFrame(tk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tk.Canvas(self)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")



if __name__ == '__main__':
    root = tk.Tk()

    frame = ScrollableFrame(root)

    for i in range(50):
        tk.Label(frame.scrollable_frame, text="Sample scrolling label").pack()

    frame.pack()
    root.mainloop()
