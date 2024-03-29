import tkinter as tk
import numpy as np
from matplotlib import cm
import csv


def cal_fft(series, period):
    N = len(series)
    fft_list = np.fft.fft(series)[:N//2]
    fft_abs = abs(fft_list)
    fs = N / period
    fk = np.arange(N) / period

    return fft_list, fft_abs, fk, fs

# def cal_fft_series(series):
#     N = len(series)
#     fft_list = np.fft.fft(series)[: N//2]
#     fft_abs = abs(fft_list)
#     # fs = N / series.index[-1]
#     # fk = np.arange(N) / period
#
#     return fft_abs

def cal_rpm(series, period):
    """
    Input: 壓力數列(series)與時間秒數(period)
    Output:  RPM
    """
    fft_list, fft_abs, fk, fs = cal_fft(series, period)
    fft_freq = fk[fft_abs[1:].argmax() + 1] * 60

    return fft_freq

def get_user_names():
    """從user.csv檔中取出user name"""
    user_names = []
    with open('files/user.csv', 'r') as f:
        for row in csv.reader(f):
            user_names.append(row[0].upper())

    return user_names

def get_project_names():
    """從projectName.csv檔中取出project name"""
    project_names = []
    with open('files/projectName.csv', 'r') as f:
        for row in csv.reader(f):
            project_names.append(row[0].upper())
    return project_names

def get_AB():
    """從AB.txt擷取A,B參數"""
    with open('files/AB.txt', 'r') as f:
        params = f.readline().strip('\n').split(',')
    return float(params[0]), float(params[1])

def get_YlOrRd():
    colormap_int = np.zeros((256, 3), np.uint8)
    colormap_float = np.zeros((256, 3), np.float)

    for i in range(0, 256, 1):
        colormap_float[i, 0] = cm.YlOrRd(i)[0]
        colormap_float[i, 1] = cm.YlOrRd(i)[1]
        colormap_float[i, 2] = cm.YlOrRd(i)[2]

        colormap_int[i, 0] = np.int_(np.round(cm.YlOrRd(i)[0] * 255.0))
        colormap_int[i, 1] = np.int_(np.round(cm.YlOrRd(i)[1] * 255.0))
        colormap_int[i, 2] = np.int_(np.round(cm.YlOrRd(i)[2] * 255.0))

    np.savetxt("YlOrRd_float.txt", colormap_float, fmt="%f", delimiter=' ', newline='\n')
    np.savetxt("YlOrRd_int.txt", colormap_int, fmt="%d", delimiter=' ', newline='\n')

    return colormap_int

def read_YlOrRd():
    data = np.loadtxt('files/YlOrRd_int.txt', dtype=int)
    return data





if __name__ == '__main__':
    get_AB()







