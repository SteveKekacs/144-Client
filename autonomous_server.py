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
COMMAND_PORT=8995

MSG_SZ = 230563


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
    PACKET_SZ = MSG_SZ

    # for UDP change socket type and pckt size
    if protocol == 'UDP':
        socket_type = socket.SOCK_DGRAM
        PACKET_SZ = 57642

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
        frame_data = []
        # ceive data till message size met
        if protocol == 'TCP':
            while len(data) < MSG_SZ:
                data += conn.recv(PACKET_SZ)

            # get frame data
            frame_data = data[:MSG_SZ]

            # remove received frame data
            data = data[MSG_SZ:]
        else:
            frame_data = b''
            num_packet = 0
            while len(frame_data) < MSG_SZ:
                packet_data, addr = sock.recvfrom(PACKET_SZ)
                if packet_data[:5] == b'BEGIN':
                    frame_data = packet_data[5:]
                else:
                    frame_data += packet_data
                print(packet_data[:5], len(frame_data))

            print("done", len(frame_data), MSG_SZ)

        # convert to cv2 frame
        frame = pickle.loads(frame_data)

        # send stop command if stopsign detected
        if ss_classifier.detect_stopsign(frame):
            command_sock.send('stop'.encode('utf-8'))
            break

        # show frame
        cv2.imshow('frame',frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # close sockets
    sock.close()
    command_sock.close()


if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] in ['tcp', 'udp', 'rdp']:
        protocol = sys.argv[1].upper()
        receive_video(protocol)
    else:
        print("Error: Invalid argument")

