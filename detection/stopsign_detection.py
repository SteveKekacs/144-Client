import time

import cv2
import imutils
import numpy as np

class StopSignClassifier:
    def __init__(self, *args, **kwargs):
        self.load_classifier()

    def load_classifier(self):
        self.classifier = cv2.CascadeClassifier("/Users/stevenkekacs/144-Client/detection/stopsign_classifier.xml")

    def detect_stopsign(self, img):
        """
        Determines whether the input image contains a stop sign using the trained Haar classifier.
        If <example> is set, also draws a rectangle around the detected sign and displays the image.
        """
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Detect any stop signs in the image using the classifier at various scales.
        stop_signs = self.classifier.detectMultiScale(gray, 1.02, 10)

        # Draw a rectangle around each detected sign and display it.
        for (x,y,w,h) in stop_signs:
            cv2.rectangle(img, (x,y), (x+w , y+h), (255, 0, 0), 2)

        if len(stop_signs) > 0:
            stopsign_area = stop_signs[0][2] * stop_signs[0][3]
            print(stopsign_area)
            return True

        return False


