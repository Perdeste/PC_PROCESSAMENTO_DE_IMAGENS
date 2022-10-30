import cv2
import os
from time import time


def run_serial_processing(filename, video_size, mascara):
    print(f'Iniciando processamento serial do vídeo {filename}...')
    file_input_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'input', filename)
    filename = filename.split('.')[0]
    file_output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output', filename + '_serial_tratado.avi')
    video = cv2.VideoCapture(file_input_path)
    fps = video.get(cv2.CAP_PROP_FPS)
    output = cv2.VideoWriter(file_output_path, cv2.VideoWriter_fourcc(*'MJPG'), fps, video_size, isColor=False)
    try:
        inicio = time()
        while True:
            ret, frame = video.read()
            if not ret:
                break
            frame_input = cv2.resize(frame, video_size, fx = 0, fy = 0,
                                interpolation=cv2.INTER_CUBIC)
            frame_input = cv2.cvtColor(frame_input, cv2.COLOR_BGR2GRAY)
            frame_output = cv2.filter2D(frame_input, ddepth=-1, kernel=mascara)
            output.write(frame_output)
        print(f'Processamento em Série\nTempo de execução: {time() - inicio}')
    finally:
        video.release()
        output.release()