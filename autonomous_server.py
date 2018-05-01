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
import random
import time
from detection.stopsign_detection import StopSignClassifier

HOST_IP=''
SENDING_HOST_IP='10.251.45.1'
VIDEO_PORT=8018
COMMAND_PORT=8019

MSG_SZ = 230400


def receive_video(protocol):
    # create socket
    # get socket type based on protocol
    socket_type = socket.SOCK_STREAM
    PACKET_SZ = MSG_SZ

    # for UDP change socket type and pckt size
    if protocol == 'UDP':
        socket_type = socket.SOCK_DGRAM
        PACKET_SZ = 11521

    print("Creating %s socket..." % protocol)
    sock = socket.socket(socket.AF_INET, socket_type)
    print("%s Socket created..." % protocol)

    # bind to host
    print("Binding to port %d..." % VIDEO_PORT)
    sock.bind((HOST_IP, VIDEO_PORT))

    # if TCP listen and accept connection
    conn = None
    if protocol == 'TCP':
        sock.listen(10)
        print("Socket is listening...")

        conn, (_, addr) = sock.accept()
        print("Established connection with %s..." % addr)

    # sleep then establish command socket
    time.sleep(3)
    print("\n\nCreating socket for sending car commands...")
    command_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Socket for sending car commands created...")

    print("Connecting sending socket to %s:%d..." % (SENDING_HOST_IP, COMMAND_PORT))
    while True:
        # try to connect to socket, if not ready sleep and try again
        try:
            command_sock.connect((SENDING_HOST_IP, COMMAND_PORT))
            break
        except:
            time.sleep(1)
    print("Connected sending socket to %s:%d...\n\n" % (SENDING_HOST_IP, COMMAND_PORT))

    # initialize stop sign detection
    print("Initializing stopsign detection classifier...")
    ss_classifier = StopSignClassifier()
    print("Stop Sign detection ready...\n\n")

    # variable to hold data sent from Pi
    data = b''

    # keep track of number of frames to know when to start car
    num_frame = 0

    # continue to receive video till interrupt
    while True:
        # receive data till message size met
        if protocol == 'TCP':
            while len(data) < MSG_SZ:
                data += conn.recv(PACKET_SZ)

            # get frame data
            frame_data = data[:MSG_SZ]

            # remove received frame data
            data = data[MSG_SZ:]
        else:
            frame_data = b''
            while len(frame_data) < MSG_SZ:
                packet_data, addr = sock.recvfrom(PACKET_SZ)
                if packet_data[:20] == (b'!' * 20):
                    frame_data = packet_data[20:]
                else:
                    frame_data += packet_data

        # convert to cv2 frame
        try:
            frame = np.fromstring(frame_data, dtype=np.uint8)
            frame = frame.reshape(240, 320, 3)
        except:
            continue 

        # increase frame count
        num_frame += 1

        # show frame
        cv2.imshow('frame',frame)

        # send stop command if stopsign detected
        if num_frame > 10 and ss_classifier.detect_stopsign(frame):
            print("Stopping car...")
            command_sock.send('stop'.encode('utf-8'))
            break

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        print("GOT ONE:", num_frame)
        if num_frame == 10:
            print("Starting car...")
            # start car
            command_sock.send('start'.encode('utf-8'))

    # close sockets
    sock.close()
    command_sock.close()


if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] in ['tcp', 'udp', 'rdp']:
        protocol = sys.argv[1].upper()
        receive_video(protocol)
    else:
        print("Error: Invalid argument")

