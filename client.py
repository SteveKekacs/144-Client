"""
This file contains functionality for communicating
with Rasperry Pi Server from remote Server on WIFI network.
"""
import socket
from pynput.keyboard import Key, Listener

# set port to connect to
PORT = 1198

# set Rasperry Pi IP
RP_IP = '10.251.45.1'

def run_client():
    print("Creating socket...")
    sock = socket.socket()
    print("Socket created...")

    print("Connecting to Rasperry Pi Server at %s:%d.." % (RP_IP, PORT))
    sock.connect((RP_IP, PORT))
    print("Connected to %s:%d..." % (RP_IP, PORT))

    # setup keyboard input
    keyboard = Listener()

    def process_key(key, release = False):
        try:
            cmd = ('.' + str(key).split('.')[1]).encode('utf-8')
            return cmd
        except:
            print("Invalid command...")
            return None

    def on_press(key):
        """ On key press process cmd and send if valid """
        cmd = process_key(key)
        if cmd:
            print("Sending %s...", str(cmd))
            sock.send(cmd)

    # continue to take user input till interrupt
    # on key input, send over socket
    with Listener(on_press=on_press, on_release=None) as listener:
        listener.join()


if __name__ == '__main__':
    run_client()

