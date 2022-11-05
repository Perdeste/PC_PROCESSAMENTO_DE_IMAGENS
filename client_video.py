import paramiko
from scp import SCPClient
import yaml


def check_connection(ssh: paramiko.SSHClient) -> bool:
    active = False
    if ssh.get_transport():
        active = ssh.get_transport().is_authenticated()
    return active


def ssh_connection(host: str, username: str, password: str,
ssh: paramiko.SSHClient, port: str, retry = 5) -> paramiko.SSHClient:
    max_try = 0
    while not check_connection(ssh):
        max_try += 1
        try:
            ssh.connect(host, port, username, password)
        except (paramiko.BadHostKeyException,
                paramiko.AuthenticationException,
                paramiko.SSHException) as e:
            print(f'Erro na conexão com o servidor {host}:' + str(e))
        except BaseException as e:
            raise('Numero maximo de reconexões atingido.')
        if max_try == retry:
            raise('Numero maximo de reconexões atingido.')


def upload_file_scp(input_path: str, ssh: paramiko.SSHClient, remote_path: str):
    try:
        with SCPClient(ssh.get_transport()) as scp:
            scp.put(input_path, remote_path=remote_path)
    except BaseException as e:
        print('Erro no envio do arquivo: ' + str(e))


def run_client_parallel():
    with open('addresses.txt') as f:
        servers_config = yaml.safe_load(f)
    for host in server_list:
        username = 'root'
        password = '123'
        port = 22
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_connection(host, username, password, ssh, port)
        upload_file_scp()
    