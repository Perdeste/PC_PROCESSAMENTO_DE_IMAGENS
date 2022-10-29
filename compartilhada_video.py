import cv2
import numpy as np
from joblib import Parallel
from joblib import delayed
from time import time


def image_processing(file_name: str, start: int, end: int, mascara: np.ndarray, video_size: tuple) -> list:
    print(f'start: {start}')
    output_list = []
    capture = cv2.VideoCapture(file_name)
    capture.set(cv2.CAP_PROP_POS_FRAMES, start)
    for _ in range(end):
        ret, frame = capture.read()
        if ret:
            frame_input = cv2.resize(frame, video_size, fx = 0, fy = 0,
                                interpolation=cv2.INTER_CUBIC)
            frame_input = cv2.cvtColor(frame_input, cv2.COLOR_BGR2GRAY)
            frame_output = cv2.filter2D(frame_input, ddepth=-1, kernel=mascara)
            output_list.append(frame_output)
    print(f'end: {end}')
    return output_list


if __name__ == '__main__':
    file_name = 'teste2.mp4'
    video_size = (540, 380)
    # mascara = np.array([[1, 1, 1],
    #                     [0, 0, 0],
    #                     [-1, -1, -1]])
    mascara = np.array([[-1, 0, 1],
                        [-1, 0, 1],
                        [-1, 0, 1]])
    video = cv2.VideoCapture(file_name)
    threads = 5
    inicio = time()
    count_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    valor = count_frames // threads 
    process_frames = Parallel(n_jobs=(threads), backend='multiprocessing')(delayed(image_processing)(file_name, start, (start + valor), mascara, video_size) for start in range(0, count_frames, valor))
    print(time() - inicio)
    # for bucket in process_frames:
    #     for frame_output in bucket:
    #         cv2.imshow('Output', frame_output)
    #         cv2.waitKey(40)
    #     if cv2.waitKey(0) == 27:
    #         break
    
