import cv2
import threading


class openCvCamera:
    def __init__(self, source):
        self.video_capture = cv2.VideoCapture(source)
        self.video_capture.set(3, 1280)
        self.video_capture.set(4, 720)
        self.lock = threading.Lock()
        self.image = None

    def getImage(self):
        if self.image is not None:
            return cv2.resize(self.image, (300, 400))

    def get_image_hd(self):
        return self.image

    def update(self):
        self.lock.acquire()
        ret, image = self.video_capture.read()

        if ret is not False:
            self.image = image

        self.lock.release()
