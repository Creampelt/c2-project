import socket
import subprocess
import os
from getpass import getuser
from encrypt import send, receive, verify_client

PORT = 1337
HOST = socket.gethostname()

def prompt_prefix():
    user = getuser()
    return "[{}@{} {}]{} ".format(getuser(), HOST, os.getcwd().split("/")[-1], "#" if user == "root" else "$")

def format_address(address):
    return "{}:{}".format(address[0], address[1])

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(1)

while True:
    client, address = server.accept()
    str_address = format_address(address)
    print "Verifying client {}...".format(str_address)
    try:
        if not verify_client(client):
            print "Invalid authentication. Terminating connection."
            send(client, "TERMINATE")
            client.close()
            continue
    except socket.error as e:
        continue
    print "Connected to client {}".format(str_address)
    send(client, prompt_prefix())
    while True:
        try:
            data = receive(client)
            if not data:
                break
            elif data.startswith("cd"):
                try:
                    new_dir = data[2:].strip().rstrip("\n")
                    os.chdir(new_dir)
                    out = ""
                except OSError as e:
                    out = e.strerror + "\n"
            else:
                try:
                    out = subprocess.check_output(data, shell=True, stderr=subprocess.STDOUT)
                    prefix_len = len(prompt_prefix())
                    if len(out) > 2048 - prefix_len:
                        msg = "Output is longer than 2048 bytes and is truncated below. Try piping to a file instead.\n"
                        out = msg + out[0:2048 - prefix_len - len(msg) - 1] + "\n"
                except subprocess.CalledProcessError as e:
                    out = e.output
            out += prompt_prefix()
            send(client, out)
        except socket.error as e:
            break
    client.close()
    print "Connection terminated"
