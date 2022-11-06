import paramiko
from scp import SCPClient
import yaml
import cv2
import time
import threading
import os
import moviepy.editor as mp


'''Verifica a conexão com o servidor'''
def check_connection(ssh: paramiko.SSHClient) -> bool:
    active = False
    if ssh.get_transport():
        active = ssh.get_transport().is_authenticated()
    return active


'''Conecta com o servidor'''
def ssh_connection(server: dict) -> paramiko.SSHClient:
    max_try = 0
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    while not check_connection(ssh):
        max_try += 1
        try:
            ssh.connect(server['host'], server['port'], server['username'], server['password'])
            return ssh
        except (paramiko.BadHostKeyException,
                paramiko.AuthenticationException,
                paramiko.SSHException) as e:
            print(f'Erro na conexão com o servidor {server["host"]}:' + str(e))
        except BaseException as e:
            raise('Numero maximo de reconexões atingido.')
        if max_try == server['retry']:
            raise('Numero maximo de reconexões atingido.')


'''Função para enviar um arquivo via scp'''
def upload_file_scp(input_path: str, ssh: paramiko.SSHClient, remote_path: str) -> None:
    try:
        with SCPClient(ssh.get_transport()) as scp:
            scp.put(input_path, remote_path)
    except BaseException as e:
        print('Erro no envio do arquivo: ' + str(e))


'''Função para fazer download de um arquivo via scp'''
def download_file_scp(remote_path: str, ssh: paramiko.SSHClient, local_path: str) -> None:
    try:
        with SCPClient(ssh.get_transport()) as scp:
            scp.get(remote_path, local_path)
    except BaseException as e:
        print('Erro no download do arquivo: ' + str(e))


'''Função que retorna a quantidade de frames que serão processados por servidor'''
def get_video_frames(input_path: str, tam_server: int) -> int:
    video = cv2.VideoCapture(input_path)
    frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    return int(frame_count/tam_server)


'''Função que lê o terminal constantemente para identificar quando o processamento do vídeo esta pronto'''
def end_command(end_str, channel, ssh):
    channel_data = ''
    while True:
        if check_connection(ssh):
            # recv_ready() lê o conteúdo do terminal que não foi lido
            if channel.recv_ready():
                # channel_data guarda o conteúdo inteiro do terminal
                channel_data += channel.recv(9999).decode('UTF8', 'i')
                # verifica se a channel_data termina com uma string específica
                if channel_data.endswith(end_str):
                    break
            time.sleep(1)
        else:
            raise('erro')
    return channel_data


'''Função que será executada por uma thread para controlar o envio de um vídeo e o recebimento do mesmo processado'''
def server_execution(server: dict, input_path: str, count: int, get_frames: int, video_size: tuple):
    filename = input_path.split('\\')[-1]
    ssh = ssh_connection(server)
    try:
        # Upload do arquivo para o servidor
        upload_file_scp(input_path, ssh, server['remote_path'])
        # Envia o comando para executar o script que processa o arquivo
        channel = ssh.invoke_shell()
        channel.send(f'python3 server_video.py {filename} {video_size[0]} {video_size[1]} {get_frames * count} {get_frames * (count + 1)}\n')
        end_command(f"{server['username']}@{server['hostname']}:~# ", channel, ssh)
        # Ao termino do processamento basta baixar o arquivo
        download_file_scp(os.path.join(server['remote_path'], server['hostname'] + filename.split('.')[0] + '.avi'), ssh, 'output/')
    finally:
        channel.close()
        ssh.close()


'''Concatena todos os videos processados em um único'''
def concat_videos(filename: str):
    videos = [mp.VideoFileClip(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output', f)) for f in os.listdir("output/") if os.path.isfile(os.path.join("output/", f))]   
    final_video = mp.concatenate_videoclips(videos, method="compose")
    final_video.write_videofile(filename)


'''Função para ser chamada na main'''
def run_distribuida_processing(filename: str, video_size: tuple):
    inicio = time.time()
    file_input_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'input', filename)
    file_output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output', filename.split('.')[0] + '_distribuido_tratado.mp4')
    count = 0
    thread_list = []
    with open('addresses.yml') as f:
        servers_config = yaml.safe_load(f)['servers']
    get_frames = get_video_frames(file_input_path, len(servers_config))
    # Para cada servidor configurado no arquivo yaml, uma thread será criada para gerenciar o seu processo
    for server in servers_config: 
        insert_thread = threading.Thread(target=server_execution, args=(server, file_input_path, count, get_frames, video_size))
        thread_list.append(insert_thread)
        insert_thread.start()
        count += 1
    # Espera todas as threads terminarem
    for process in thread_list:
        process.join()
    concat_videos(file_output_path)
    print(f'Processamento em Memória Distribuída\nTempo de execução: {time.time() - inicio}')