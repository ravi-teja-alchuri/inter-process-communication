import glob
import os
import time
import socket
import threading
from dirsync import sync
from time import sleep


SERVER = "0.0.0.0"
PORT = 6060
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

locked_files = []


def get_files():
    # Get list of all files only in the given directory
    list_of_files = filter(os.path.isfile, glob.glob(dir_name_a + '*'))
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


def send(msg):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Make a call to serverB running on port 6061
    client.connect((SERVER, 6061))
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    # Make it byte representation of the string
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)
    return client.recv(HEADER).decode(FORMAT)


def lock_file(file):
    locked_files.append(file)


def unlock_file(file):
    locked_files.remove(file)


def handle_client(conn, address):
    connected = True
    while connected:
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)

            print(f"[{address}] {msg}")

            # Get the files from directoryA
            dir1_files = get_files()
            # Convert the str to list
            dir1_files_list = dir1_files.strip('][').split(', ')

            # Establish a connection to serverB and get the files from directoryB also synchronizes both the directories
            dir2_files = send("Get file list form serverB")
            # Convert the str to list
            dir2_files_list = dir2_files.strip('][').split(', ')

            # Combine the files of directoryA and directoryB
            all_files = dir1_files_list + dir2_files_list
            # Remove duplicates form the composite list
            all_files = list(dict.fromkeys(all_files))
            # Sort the file list
            all_files.sort()

            args = msg.split(" ")
            if args[0] == "lock":
                i = int(args[1])
                lock_file(all_files[i])
            elif args[0] == "unlock":
                i = int(args[1])
                unlock_file(all_files[i])

            for each in locked_files:
                lock_i = all_files.index(each)
                all_files[lock_i] = all_files[lock_i] + " locked"

            # Return the sorted file list to the client in string format
            conn.send(str(all_files).encode(FORMAT))

    conn.close()


def handle_sync(dir1, dir2):
    while True:
        ignore = []
        for each in locked_files:
            ignore.append("^"+each.split(' :: ')[0][1:]+"$")
        # sync
        sync(dir1, dir2, 'sync', exclude=tuple(ignore), verbose=True)
        sync(dir2, dir1, 'sync', exclude=tuple(ignore), verbose=True)
        sleep(5)


def start_a():
    server.listen()
    print(f"[Listening] ServerA listening on {SERVER}:{PORT}")
    while True:
        #  wait for new connection to the server and store connection and ip address
        conn, address = server.accept()
        #  create a thread and pass the connection to the handle_client along with the args
        thread = threading.Thread(target=handle_client, args=(conn, address))
        # start the thread
        thread.start()


print("starting server A")
threading.Thread(target=handle_sync, args=(dir_name_a, dir_name_b)).start()
start_a()

