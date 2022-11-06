import cv2
import os
import numpy as np
import threading
from time import time


'''Função que insere os frames prontos em um arquivo de vídeo de forma ordenada, ele é chamado apenas uma vez'''
def insert_frames(output_dict: list, filename: str, video_size: tuple, fps: int, frame_count: int):
    file_output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output', filename + '_compartilhada_tratado.avi')
    output = cv2.VideoWriter(file_output_path, cv2.VideoWriter_fourcc(*'MJPG'), fps, video_size, isColor=False)
    position = 0
    while position < frame_count:
        if position in output_dict:
            frame = output_dict.pop(position)
            output.write(frame)
            position += 1
    output.release()


'''Função para adicionar um frame a uma thread'''
def create_frame_process(video, output_dict, thread_list, position, video_size, mascara):
    ret, frame = video.read()
    if ret:
        process = threading.Thread(target=filter_frame, args=(frame, output_dict, position, video_size, mascara))
        process.start()
        thread_list.append(process)
        position += 1
    return position


'''Função para controlar o fluxo de execução'''
def execute_controller(thread: int, filename: str, video, video_size: tuple, mascara: np.ndarray, fps: int) -> None:
    output_dict = {}
    thread_list = []
    try:
        # Iniciar a thread que fara o controle da inserção dos frames no arquivo final. Existe gargalo de memória
        frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        insert_thread = threading.Thread(target=insert_frames, 
                                        args=(output_dict, filename, video_size, fps, frame_count))
        insert_thread.start()
        position = 0
        # Loop para executar n threads
        for _ in range(0, thread):
            position = create_frame_process(video, output_dict, 
                                            thread_list, position, video_size, mascara)
        # Loop para controlar o encerramento do processamento de cada thread, quando a thread terminar de executar ela ja coloca outro frame para processar (de forma ordenada)
        while len(thread_list) > 0:
            process = thread_list.pop(0)
            process.join()
            position = create_frame_process(video, output_dict, 
                                            thread_list, position, video_size, mascara)
        # Espera a thread de inserção terminar para finalizar a execução
        insert_thread.join()
    finally:
        video.release()


'''Função executada por n threads, no qual aplica-se as 3 transformações na imagem'''
def filter_frame(frame: np.ndarray, output_dict: list, position: int, video_size: tuple, mascara: np.ndarray) -> None:
    frame_input = cv2.resize(frame, video_size, fx = 0, fy = 0,
                            interpolation=cv2.INTER_CUBIC)   
    frame_input = cv2.cvtColor(frame_input, cv2.COLOR_BGR2GRAY)
    frame_output = cv2.filter2D(frame_input, ddepth=-1, kernel=mascara)
    # A primeira posição da tupla é o frame e a segunda a sua posição corresponde no vídeo
    output_dict[position] = frame_output


'''Função para ser chamada na main'''
def run_compartilhada_processing(thread: int, filename: str, video_size: tuple, mascara: np.ndarray) -> None:
    print(f'Iniciando processamento paralelo do vídeo {filename}...')
    file_input_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'input', filename)
    filename = filename.split('.')[0]
    video = cv2.VideoCapture(file_input_path)
    fps = video.get(cv2.CAP_PROP_FPS)
    inicio = time()
    execute_controller(thread, filename, video, video_size, mascara, fps)
    print(f'Processamento em Memória Compartilhada\nTempo de execução: {time() - inicio}')
