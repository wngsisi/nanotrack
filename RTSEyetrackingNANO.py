import threading
import cv2
import ObjectDetectionModuleNANO as odm
import SerialModuleNANO as sm
import numpy as np
import base64
import  sys, os
import time
sys.path.append(os.getcwd())
sys.path.append(os.getcwd()+'/../')
imgstring = 0
frameWidth = 640
frameHeight = 480
filp = 2
rePose = 1
global conter
conter=100
perrorLR, perrorUD = 0, 0
faceCascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
serr = sm.initConnection('192.168.1.69', 7018)

class RTSCapture(cv2.VideoCapture):
    _cur_frame = None
    _reading = False
    schemes = ["rtsp://", "rtmp://"]
    @staticmethod
    def create(url, *schemes):
        rtscap = RTSCapture(url)
        rtscap.frame_receiver = threading.Thread(target=rtscap.recv_frame, daemon=True)
        rtscap.schemes.extend(schemes)
        if isinstance(url, str) and url.startswith(tuple(rtscap.schemes)):
            rtscap._reading = True
        elif isinstance(url, int):
            pass
        return rtscap
    def isStarted(self):
        ok = self.isOpened()
        if ok and self._reading:
            ok = self.frame_receiver.is_alive()
        return ok
    def recv_frame(self):
        while self._reading and self.isOpened():
            ok, frame = self.read()
            if not ok: break
            self._cur_frame = frame
        self._reading = False
    def read2(self):
        frame = self._cur_frame
        self._cur_frame = None
        return frame is not None, frame
    def start_read(self):
        self.frame_receiver.start()
        self.read_latest_frame = self.read2 if self._reading else self.read
    def stop_read(self):
        self._reading = False
        if self.frame_receiver.is_alive(): self.frame_receiver.join()
def findCenter(imgObjects, objects):
    cx, cy = -1, -1
    if len(objects) != 0:
        x, y, w, h = objects[0]
        cx = x + w//2
        cy = y + h//2
        cv2.circle(imgObjects, (cx, cy), 1, (0, 255, 0), cv2.FILLED)
        ih, iw, ic = imgObjects.shape
        cv2.line(imgObjects, (iw//2, cy), (cx, cy), (0, 255, 0), 1)
        cv2.line(imgObjects, (cx, ih//2), (cx, cy), (0, 255, 0), 1)
    return cx, cy, imgObjects

datas = [0, 1]
datae = [0]
def trackObject(cx, cy, w, h):
    global perrorLR, perrorUD
    kLR = [0.3, 0.3]
    kUD = [0.5, 0.5]
    if cx!=-1:
        errorLR = w//2 - cx
        posX1 = kLR[0] * errorLR + kLR[1] * (errorLR-perrorLR)
        posX = np.interp(posX1, [-w//2, w//2], [20, 160])
        perrorLR = errorLR
        errorUD = h//2 - cy
        posY1 = kUD[0] * errorUD + kUD[1] * (errorUD-perrorUD)
        posY = np.interp(posY1, [-w//2, w//2], [20, 160])
        perrorUD = errorUD
        data = [posX, posY]
        sm.sendData(serr, data)
print("System initialised")
if __name__ == '__main__':
    rtscap = RTSCapture.create('rtsp://admin:123456@192.168.1.102:554/h264/ch1/sub/av_stream')     # sys.argv[1]
    rtscap.start_read()
    fps = 0.0
    while rtscap.isStarted():
        ok, frame = rtscap.read_latest_frame()
        if not ok:
            continue

        frame = cv2.resize(frame, (0, 0), None, 0.5, 0.5)
        imgObjects, objects = odm.findObjects(frame, faceCascade, 1.08, 10)
        if len(objects) != 1:
            if 100 >= conter > 80:
                conter = conter - 1
            elif 80 >= conter > 0:
                conter = conter - 1
                d = bytes.fromhex('FF 01 00 00 00 00 01')
                serr.send(d)
            elif conter == 0:
                conter = 0
                if rePose != 0:
                    d = bytes.fromhex('FF 01 00 00 00 00 01')
                    serr.send(d)
                else:
                    pass
            else:
                pass
            print(conter)
        else:
            conter = 100
            pass

        cx, cy, imgObjects = findCenter(imgObjects, objects)
        h, w, c = imgObjects.shape

        cv2.line(imgObjects, (w // 2, 0), (w // 2, h), (255, 0, 255), 1)  
        cv2.line(imgObjects, (0, h // 2), (w, h // 2), (255, 0, 255), 1)
        trackObject(cx, cy, w, h)
        img = cv2.resize(imgObjects, (0, 0), None, 3, 3)
        imgstring = base64.b64encode(img)
        print(type(imgstring))
        #cv2.imshow("cam", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    print("no video stop.")
    print("sleeping 20 ")
    time.sleep(20)
    rtscap.stop_read()
    rtscap.release()


