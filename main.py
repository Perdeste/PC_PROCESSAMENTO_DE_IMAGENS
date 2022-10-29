import numpy as np
import os
from serial_video import run_serial_processing


if __name__ == '__main__':
    file_name = 'teste2.mp4'
    video_size = (1360, 720)
    # mascara = np.array([[1, 1, 1],
    #                     [0, 0, 0],
    #                     [-1, -1, -1]])
    mascara = np.array([[-1, 0, 1],
                        [-1, 0, 1],
                        [-1, 0, 1]])
    run_serial_processing(file_name, video_size, mascara)