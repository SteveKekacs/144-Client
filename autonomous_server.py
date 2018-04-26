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
VIDEO_PORT=8088
COMMAND_PORT=8989

# size of packets to receive
PACKET_SZ = 130748 * 2


def detect_stop_sign(frame):
    # temp
    ret = random.randint(0, 50) == 10
    if ret:
        print("STOP!")
    return ret


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
    print("Connected sending socket to %s:%d..\n\n." % (SENDING_HOST_IP, COMMAND_PORT))

    # initialize stop sign detection
    print("Initializing stopsign detection classifier...")
    ss_classifier = StopSignClassifier()
    print("Stop Sign detection ready...")

    # variable to hold data sent from Pi
    data = b''

    # size of struct L
    payload_size = struct.calcsize("<L")

    # start car
    command_sock.send('start'.encode('utf-8'))

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

        # TODO: Process objects, if found send stop command back to Pi
        if ss_classifier.detect_stopsign(frame):
            print("Send stop command")
            # command_sock.send('stop'.encode('utf-8'))
            print("DONE")
            # break

        # show frame
        cv2.imshow('frame',frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # close sockets


if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] in ['tcp', 'udp', 'rdp']:
        protocol = sys.argv[1].upper()
        receive_video(protocol)
    else:
        print("Error: Invalid argument")

