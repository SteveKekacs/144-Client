"""
Receives opencv frames from Rasperry Pi Sender
to process for object detection.
"""
import sys
import cv2
import pickle
import numpy as np
import struct
import socket

HOST_IP=''
PORT=8089

# size of packets to receive
PACKET_SZ = 130748 * 2


def receive_video(protocol):
    # create socket
    # get socket type based on protocol
    socket_type = socket.SOCK_STREAM
    if protocol == 'UDP':
        socket_type = socket.SOCK_DGRAM

    print("Creating %s socket..." % protocol)
    sock = socket.socket(socket.AF_INET, socket_type)
    print("%s Socket created..." % protocol)

    # bind to host
    print("Binding to port %d..." % PORT)
    sock.bind((HOST_IP, PORT))

    # if TCP listen and accept connection
    conn = None
    if protocol == 'TCP':
        sock.listen(10)
        print("Socket is listening...")

        conn, (_, addr) = sock.accept()
        print("Established connection with %s..." % addr)


    # variable to hold data sent from Pi
    data = b''

    # size of struct L
    payload_size = struct.calcsize("<L")
    print(payload_size)

    # continue to receive video till interrupt
    while True:
        # receive data till payload size reached
        while len(data) < payload_size:
            data += conn.recv(PACKET_SZ)

        # get payload size from data
        packed_msg_size = data[:payload_size]

        # remove received data
        data = data[payload_size:]

        # get message size
        msg_size = struct.unpack("<L", packed_msg_size)[0]

        # ceive data till message size met
        while len(data) < msg_size:
            if protocol == 'TCP':
                data += conn.recv(PACKET_SZ)
            else:
                packet_data, addr = sock.recvfrom(PACKET_SZ)
                data += packed_data

        # get frame data
        frame_data = data[:msg_size]

        # remove received frame data
        data = data[msg_size:]

        # convert to cv2 frame
        frame = pickle.loads(frame_data)

        # show frame
        cv2.imshow('frame',frame)

        # TODO: Process objects, if found send stop command back to Pi
        # if stop_sign_detected(frame):
        #     send_command('stop')

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

if __name__ == '__main__':
    protcol = 'TCP'
    if sys.argv and sys.argv[0] in ['tcp', 'udp', 'rdp']:
        protocol = sys.argv[0].upper()
    else:
        print("Error: Invalid argument")
        return 

    receive_video(protocol)

