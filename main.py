import numpy as np
import time
from serial_video import run_serial_processing
from teste_compartilhada import run_parallel_processing


if __name__ == '__main__':
    filename = 'teste2.mp4'
    video_size = (1360, 720)
    # mascara = np.array([[1, 1, 1],
    #                     [0, 0, 0],
    #                     [-1, -1, -1]])
    mascara = np.array([[-1, 0, 1],
                        [-1, 0, 1],
                        [-1, 0, 1]])
    # run_serial_processing(filename, video_size, mascara)
    # time.sleep(1)
    run_parallel_processing(5, filename, video_size, mascara)
