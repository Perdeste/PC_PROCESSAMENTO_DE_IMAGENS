import numpy as np
import os
import time
from serial_video import run_serial_processing
from compartilhada_video import run_parallel_processing


def check_folder() -> None:
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')
    if not os.path.isdir(output_path):
        os.mkdir(output_path)


if __name__ == '__main__':
    check_folder()
    filename = 'teste2.mp4'
    video_size = (1360, 720)
    # mascara = np.array([[1, 1, 1],
    #                     [0, 0, 0],
    #                     [-1, -1, -1]])
    mascara = np.array([[-1, 0, 1],
                        [-1, 0, 1],
                        [-1, 0, 1]])
    run_serial_processing(filename, video_size, mascara)
    time.sleep(1)
    run_parallel_processing(5, filename, video_size, mascara)
