import numpy as np
import os
import time
import sys
from serial_video import run_serial_processing
from compartilhada_video import run_compartilhada_processing
from client_video import run_distribuida_processing


def check_folder() -> None:
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')
    if not os.path.isdir(output_path):
        os.mkdir(output_path)


if __name__ == '__main__':
    check_folder()
    if len(sys.argv) > 0:
        filename = sys.argv[1]
        video_size = (1360, 720)
        mascara = np.array([[-1, 0, 1],
                            [-1, 0, 1],
                            [-1, 0, 1]])
        # run_serial_processing(filename, video_size, mascara)
        time.sleep(1)
        # run_compartilhada_processing(5, filename, video_size, mascara)
        time.sleep(1)
        run_distribuida_processing(filename, video_size)
    else:
        print('Nome do arquivo não foi passado como argumento. Ex.: python main.py teste.mp4')
