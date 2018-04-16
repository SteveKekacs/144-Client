"""
This file contains functionality for communicating
with Rasperry Pi Server from remote Server on WIFI network.
"""
import socket
from pynput.keyboard import Key, Listener

# set port to connect to
port = 1128

# set Rasperry Pi IP
RP_IP = '127.0.0.1'


def run_client():
    print("Creating socket...")
    sock = socket.socket()
    print("Socket created...")

    print("Connecting to Rasperry Pi Server...")
    sock.connect((RP_IP, port))
    print("Connected to %s:%d..." % (RP_IP, port))

    # setup keyboard input
    keyboard = Listener()

    # continue to take user input till interrupt
    # on key input, send over socket
    with Listener(on_press=sock.send, on_release=None) as listener:
        listener.join()


if __name__ == '__main__':
    run_client()

