import cv2
import os
import numpy as np
import threading
from time import time


def process_image(frame, mascara, video_size, output_list, pos):
    frame_input = cv2.resize(frame, video_size, fx = 0, fy = 0,
                              interpolation=cv2.INTER_CUBIC)
    frame_input = cv2.cvtColor(frame_input, cv2.COLOR_BGR2GRAY)
    frame_output = cv2.filter2D(frame_input, ddepth=-1, kernel=mascara)
    output_list[pos] = frame_output


def run_serial_processing(file_name, video_size, mascara):
    threads = 5
    output_list = [None for _ in range(0, threads)]
    file_output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output', file_name.replace('.mp4','') + '_serial_tratado.avi')
    file_input_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'input', file_name)
    video = cv2.VideoCapture(file_input_path)
    fps = video.get(cv2.CAP_PROP_FPS)
    output = cv2.VideoWriter(file_output_path, cv2.VideoWriter_fourcc(*'MJPG'), fps, video_size, isColor=False)
    try:
        inicio = time()
        while True:
            count = 0
            for _ in range(0, threads):
                ret, frame = video.read()
                if not ret:
                    break
                else:
                    threading.Thread(target=process_image(frame, mascara, video_size, output_list, count)).start()
                    count += 1
            if type(output_list[0]) != np.ndarray:
                break
            pos = 0
            while pos < count:
                if type(output_list[pos]) == np.ndarray:
                    output.write(output_list[pos])
                    output_list[pos] = None
                    pos += 1          
        print(f'Processamento em Série\nTempo de execução: {time() - inicio}')
    finally:
        video.release()
        output.release()


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