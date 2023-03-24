import glob
import os
import time
import socket
import threading
from dirsync import sync
from time import sleep

SERVER = "0.0.0.0"
PORT = 6061
ADDRESS = (SERVER, PORT)
HEADER = 4096
FORMAT = 'utf-8'


# This establishes a socket in the Internet domain, and configures it for stream-oriented communication using
# the default TCP protocol.
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# This system call associates a socket with a particular address
server.bind(ADDRESS)

# Directory path from which the files are to be retrieved
dir_name_b = './directoryB/'
dir_name_a = './directoryA/'


def get_files():
    # Get list of all files only in the given directory
    list_of_files = filter(os.path.isfile, glob.glob(dir_name_b + '*'))
    # Sort list of files based on last modification time in ascending order
    list_of_files = sorted(list_of_files, key=os.path.basename)

    files_with_meta = []

    # Iterate over sorted list of files and print file path
    # along with last modification time of file
    for file_path in list_of_files:
        timestamp_str = time.strftime('%m/%d/%Y %H:%M:%S', time.gmtime(os.path.getmtime(file_path)))
        # append each file info to the above list
        files_with_meta.append(os.path.basename(file_path) + ' :: ' + timestamp_str + ' :: ' + str(os.path.getsize(file_path)) + ' bytes')
    return str(files_with_meta)


def handle_client(conn, address):
    print(f"[NEW CONNECTION] {address} connected")

    connected = True
    while connected:
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)
            print(f"[{address}] {msg}")
            conn.send(get_files().encode(FORMAT))

    conn.close()


def handle_sync(dir1, dir2):
    while True:
        # sync
        sync(dir1, dir2, 'sync', verbose=True)
        sync(dir2, dir1, 'sync', verbose=True)
        sleep(5)


def start_b():
    server.listen()
    print(f"[Listening] ServerB listening on {SERVER}:{PORT}")
    while True:
        #  wait for new connection to the server and store connection and ip address
        conn, address = server.accept()
        #  create a thread and pass the connection to the handle_client along with the args
        thread = threading.Thread(target=handle_client, args=(conn, address))
        # start the thread
        thread.start()


print("starting server B")
threading.Thread(target=handle_sync, args=(dir_name_a, dir_name_b)).start()
start_b()



