import cv2


class StopSignClassifier:
    def __init__(self, *args, **kwargs):
        # on init load classifier
        self.load_classifier()

    def load_classifier(self):
        # loads classifier from pre-trained classifier file (must use absolute path)
        self.classifier = cv2.CascadeClassifier("/Users/stevenkekacs/144-Client/detection/stopsign_classifier.xml")

    def detect_stopsign(self, img):
        """
        Determines whether the input image contains a stop sign using the trained Haar classifier.
        """
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Detect any stop signs in the image using the classifier at various scales.
        stop_signs = self.classifier.detectMultiScale(gray, 1.02, 10)

        # if stop signs found, draw rectange, calc area and return True
        if stop_signs.any():
            # get position and dimensions
            x, y, w, h = stop_signs[0]

            # draw rectangle around stop sign
            cv2.rectangle(img, (x, y), (x+w , y+h), (255, 0, 0), 2)

            # calculate area of stop sign
            stopsign_area = w * h
            print("Stopsign found:", stopsign_area)

            # return True for stopsign found
            return True

        # no stop sign found so return False
        return False


