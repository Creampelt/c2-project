
from Crypto.Cipher import AES
from getpass import getpass
import bcrypt

PASSPHRASE = b"mainframe"
ENCRYPT_PASSPHRASE_1 = "i love computers"
ENCRYPT_PASSPHRASE_2 = "i slept 8 hours!"

ASK_PASS = "PASSWORD VERIFICATION"

def encrypt(message):
    obj = AES.new(ENCRYPT_PASSPHRASE_1, AES.MODE_CBC, ENCRYPT_PASSPHRASE_2)
    if len(message) % 16 != 0:
        message += "\0" * (16 - len(message) % 16)
    return obj.encrypt(message)

def decrypt(cipher):
    obj = AES.new(ENCRYPT_PASSPHRASE_1, AES.MODE_CBC, ENCRYPT_PASSPHRASE_2)
    message = obj.decrypt(cipher)
    return message.rstrip("\0")

def send(sock, message):
    msg = encrypt(message)
    sock.sendall(msg) # encrypt(message))

def receive(sock):
    received = sock.recv(2048)
    return decrypt(received)

def get_hashed_pass():
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(PASSPHRASE, salt)

def verify_client(client):
    for i in range(3):
        send(client, ASK_PASS)
        password = receive(client).rstrip("\n")
        hashed = get_hashed_pass()
        if bcrypt.hashpw(password, hashed) == hashed:
            return True
    return False

def is_ask_pass(message):
    return message == ASK_PASS

def ask_pass(sock):
    password = getpass("Enter password: ")
    send(sock, password)
