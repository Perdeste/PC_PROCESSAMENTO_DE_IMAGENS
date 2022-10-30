import cv2
import os
import numpy as np
import threading
from time import time


'''Função que insere os frames prontos em um arquivo de vídeo, ele é chamado apenas uma vez'''
def insert_frames(output_list: list, filename: str, video_size: tuple, fps: int):
    file_output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output', filename + '_parallel_tratado.avi')
    output = cv2.VideoWriter(file_output_path, cv2.VideoWriter_fourcc(*'MJPG'), fps, video_size, isColor=False)
    while True:
        if len(output_list) > 0:
            frame = output_list.pop(0)
            # Caso a flag seja atendida, então todos os frames ja foram processadas
            if frame[1] < 0:
                break
            output.set(cv2.CAP_PROP_POS_FRAMES, frame[1])
            output.write(frame[0])
    output.release()


'''Função para controlar o fluxo de execução'''
def execute_controller(thread: int, filename: str, video, video_size: tuple, mascara: list, fps: int) -> None:
    output_list = []
    try:
        # Iniciar a thread que fara o controle da inserção dos frames no arquivo final
        insert_thread = threading.Thread(target=insert_frames, args=(output_list, filename, video_size, fps))
        insert_thread.start()
        position = 0
        while True:
            thread_list = []
            # Execute a função de transformação nas n threads
            for _ in range(0, thread):
                ret, frame = video.read()
                if ret:
                    process = threading.Thread(target=filter_frame, args=(frame, output_list, position, video_size, mascara))
                    process.start()
                    thread_list.append(process)
                    position += 1
            # Espera todas as n threads terminarem
            for process in thread_list:
                process.join()
            if not ret:
                # Adiciona o flag -1 para indicar quando acabar o processamento de todas as imagens
                output_list.append((None,-1))
                break
        insert_thread.join()
    finally:
        video.release()


'''Função executada por n threads, no qual aplica-se as 3 transformações na imagem'''
def filter_frame(frame: np.ndarray, output_list: list, position: int, video_size: tuple, mascara: list) -> None:
    frame_input = cv2.resize(frame, video_size, fx = 0, fy = 0,
                            interpolation=cv2.INTER_CUBIC)   
    frame_input = cv2.cvtColor(frame_input, cv2.COLOR_BGR2GRAY)
    frame_output = cv2.filter2D(frame_input, ddepth=-1, kernel=mascara)
    # A primeira posição da tupla é o frame e a segunda a sua posição corresponde no vídeo
    output_list.append((frame_output, position))


'''Função para ser chamada na main'''
def run_parallel_processing(thread, filename, video_size, mascara) -> None:
    print(f'Iniciando processamento paralelo do vídeo {filename}...')
    file_input_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'input', filename)
    filename = filename.split('.')[0]
    video = cv2.VideoCapture(file_input_path)
    fps = video.get(cv2.CAP_PROP_FPS)
    inicio = time()
    execute_controller(thread, filename, video, video_size, mascara, fps)
    print(f'Processamento em Paralelo\nTempo de execução: {time() - inicio}')