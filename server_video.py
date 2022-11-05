import sys
import os
import cv2
import numpy as np


def run_serial_processing(filename: str, video_size: tuple, mascara: np.ndarray, start: int, end: int):
    print(f'Iniciando processamento serial do vídeo {filename}...')
    file_input_path = '/root/pc/input/' + filename
    file_output_path = '/root/pc/input/' + 'instance-1' + filename.split('.')[0] + '.avi'
    video = cv2.VideoCapture(file_input_path)
    fps = video.get(cv2.CAP_PROP_FPS)
    output = cv2.VideoWriter(file_output_path, cv2.VideoWriter_fourcc(*'MJPG'), fps, video_size, isColor=False)
    count = 0
    try:
        while True:
            ret, frame = video.read()
            if (not ret) or (count == end):
                break
            if (count >= start):
                frame_input = cv2.resize(frame, video_size, fx = 0, fy = 0,
                                interpolation=cv2.INTER_CUBIC)
                frame_input = cv2.cvtColor(frame_input, cv2.COLOR_BGR2GRAY)
                frame_output = cv2.filter2D(frame_input, ddepth=-1, kernel=mascara)
                output.write(frame_output)
            count += 1
    finally:
        video.release()
        output.release()


if __name__ == '__main__':
    filename = sys.argv[1]
    video_size = (int(sys.argv[2]), int(sys.argv[3]))
    start = int(sys.argv[4])
    end = int(sys.argv[5])
    mascara = np.array([[-1, 0, 1],
                    [-1, 0, 1],
                    [-1, 0, 1]])
    run_serial_processing(filename, video_size, mascara, start, end)
