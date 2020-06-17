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


# from PIL import Image
# arr = ['fig/left.png', 'fig/right.png']
# toImage = Image.new('RGBA',(180,90))
# for i in range(2):
#     fromImge = Image.open(arr[i]).resize((90,90), Image.ANTIALIAS)
#     # loc = ((i % 2) * 200, (int(i/2) * 200))
#     loc = ((i % 2) * 90, (int(i/2) * 200))
#     print(loc)
#     toImage.paste(fromImge, loc)
# toImage.save('fig/90x90.png')

# img = data.coffee()
# # rr, cc = draw.circle(150, 150, 50)
# # draw.set_color(img, [rr, cc], [0, 255, 0])
# plt.imshow(img)
# plt.show()

if __name__ == '__main__':
    get_rgb_from_cmap(0.1)
    get_rgb_from_cmap(0.5)
    get_rgb_from_cmap(0.8)
    get_rgb_from_cmap(0.9)
    get_rgb_from_cmap(0.99)
