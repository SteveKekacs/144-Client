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

HOST=''
PORT=8089

def receive_video():
    print("Creating socket...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Socket created...")

    print("Binding to port %d..." % PORT)
    sock.bind((HOST,PORT))
    sock.listen(10)
    print("Socket is listening...")

    conn, (_, addr) = sock.accept()
    print("Established connection with %s..." % addr)

    # variable to hold data sent from Pi
    data = b''

    # size of struct L
    payload_size = struct.calcsize("L")

    # continue to receive video till interrupt
    while True:
        # receive data till payload size reached
        while len(data) < payload_size:
            data += conn.recv(4096)

        # get payload size from data
        packed_msg_size = data[:payload_size]

        # remove received data
        data = data[payload_size:]

        # get message size
        msg_size = struct.unpack("L", packed_msg_size)[0]

        # ceive data till message size met
        while len(data) < msg_size:
            data += conn.recv(4096)

        # get frame data
        frame_data = data[:msg_size]

        # remove received frame data
        data = data[msg_size:]

        # convert to cv2 frame
        frame=pickle.loads(frame_data)

        # show frame
        cv2.imshow('frame',frame)

        # TODO: Process objects, if found send stop command back to Pi

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

if __name__ == '__main__':
    receive_video()

