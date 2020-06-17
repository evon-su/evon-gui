import tkinter as tk
import numpy as np

projectName_list = ['test', 'resist_speed']


def cal_fft(series, period):
    N = len(series)
    fft_list = np.fft.fft(series)[:N // 2]
    fft_abs = abs(fft_list)
    fs = N / period
    fk = np.arange(N) / period

    return fft_list, fft_abs, fk, fs

def cal_rpm(series, period):
    fft_list, fft_abs, fk, fs = cal_fft(series, period)
    fft_freq = fk[fft_abs[1:].argmax()] * 60

    return fft_freq







