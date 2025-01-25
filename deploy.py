"""
Боль - постоянное логиниться на сервер и перезапускать докер
для внесения изменений

1. зайти на сервер
2. перейти в папку /home/bot
3. запустить команду docker compose down
4. запустить команду docker compose up --build -d
5. выйти
"""
import paramiko
import time
import socket
import re
from pprint import pprint
import os
from dotenv import load_dotenv, dotenv_values 


def send_show_command(ip, username, password, enable, command, max_bytes=60000, short_pause=1, long_pause=5,):
    cl = paramiko.SSHClient()
    cl.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    cl.connect(
        hostname=ip,
        username=username,
        password=password,
        look_for_keys=False,
        allow_agent=False,
    )
    with cl.invoke_shell() as ssh:
        ssh.send("enable\n")
        ssh.send(f"{enable}\n")
        time.sleep(short_pause)
        ssh.send("terminal length 0\n")
        time.sleep(short_pause)
        ssh.recv(max_bytes)

        result = {}
        for command in commands:
            ssh.send(f"{command}\n")
            ssh.settimeout(5)

            output = ""
            while True:
                try:
                    part = ssh.recv(max_bytes).decode("utf-8")
                    # match = re.search('[A-Za-z]', part).group()
                    output += part
                    time.sleep(0.5)
                except socket.timeout:
                    break
            result[command] = output

        return result


if __name__ == "__main__":
    load_dotenv() 
 
    HOST = os.getenv("HOST")
    PORT = os.getenv("PORT")
    USERNAME = os.getenv("USER_NAME")
    PASSWORD = os.getenv("PASSWORD")
    BOT_PATH = os.getenv("BOT_PATH")

    commands = [
        f"cd {BOT_PATH}",
        "docker compose down",
        # "docker compose up --build -d"
    ]

    result = send_show_command(ip=HOST, username=USERNAME, password=PASSWORD, enable="root", command=commands)
    pprint(result, width=120)