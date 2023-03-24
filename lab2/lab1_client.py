import socket
from time import sleep

# Hard coding serverA ip and port
SERVER = "0.0.0.0"
PORT = 6060
ADDRESS = (SERVER, PORT)
HEADER = 4096
FORMAT = 'utf-8'


# This establishes a socket in the Internet domain, and configures it for stream-oriented communication using
# the default TCP protocol.
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDRESS)


def send(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)
    # Receive the response returned by ServerA
    resp = client.recv(HEADER).decode(FORMAT)
    # Convert the string response received from serverA to list
    all_files_list = resp.strip('][').split(', ')
    # loop through each item in list and print to the console
    for each in all_files_list:
        print(each)


# Send a message to serverA
send("Get file list")



