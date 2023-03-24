import glob
import os
import time
import socket
import threading

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


def get_files():
    # Directory path from which the files are to be retrieved
    dir_name = './directoryA/'
    # Get list of all files only in the given directory
    list_of_files = filter(os.path.isfile, glob.glob(dir_name + '*'))
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

            # Establish a connection to serverB and get the files from directoryB
            dir2_files = send("Get file List from serverB")
            # Convert the str to list
            dir2_files_list = dir2_files.strip('][').split(', ')

            # Combine the files of directoryA and directoryB
            all_files = dir1_files_list + dir2_files_list
            # Sort the file list
            all_files.sort()
            # Return the sorted file list to the client in string format
            conn.send(str(all_files).encode(FORMAT))

    conn.close()


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
start_a()

