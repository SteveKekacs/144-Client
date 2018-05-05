# 144-Client
This is the code that runs on an external server, in our case a MacBook Air running macOS High Sierra, that performs object recognition (for stop signs) on video that is transmitted from the Raspberry Pi which has a camera module attached. 

There are three important files:
1. `autonomous_receiver.py`: Takes in one paramater that specifies which protocol to use (either UDP or TCP), sets up the appropriate sockets and receives video frames from the Raspberry Pi for processing. After an initial 10 frames are received, a `start` command is sent to the Pi to signal the car to start driving, then each following frame is passed through our Stop Sign object detector and once a match has been found sends a `stop` command back to the Pi to signal to the car that a stop sign has been found.
2. `detection/stopsign_detection.py`: Defines a simple `StopSignClassifier` class that loads a pre-trained haar stop sign classifier file (`detection/stopsign_classifier.xml`), and contains a function that given an opencv frame, attempts to detect a stop sign and returns `True` if found else `False`.
3. `detection/stopsign_classifier.xml`: Pre-trained haar classifier for stop signs.

There is also one irrelevant file (for fun) `client.py`, that allows you to manually drive the mobile RC car from an external server.
