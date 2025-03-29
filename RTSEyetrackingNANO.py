
import threading
import cv2
import SerialModuleNANO as sm
import numpy as np
import  sys, os
from ultralytics import YOLO
model = YOLO("yolo11n-pose.pt")

share_mem_file = os.path.join(os.environ['TEMP'], 'camera_frame.mmap')
sys.path.append(os.getcwd())
sys.path.append(os.getcwd()+'/../')

frameWidth = 640
frameHeight = 480
filp = 2
rePose = 1
global conter ,nose
nose=(0,0)
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

    if len(objects) != 0:
        cv2.circle(imgObjects, (cx, cy), 1, (0, 255, 0), cv2.FILLED)
        ih, iw, ic = imgObjects.shape
        cv2.line(imgObjects, (iw//2, cy), (cx, cy), (0, 255, 0), 1)
        cv2.line(imgObjects, (cx, ih//2), (cx, cy), (0, 255, 0), 1)
    return cx, cy, imgObjects

datas = [0, 1]
datae = [0]

def findnose(img,nose):
    imgObjects = img.copy()
    detected = True
    nose = [-1, -1]
    results = model.predict(imgObjects, device=0, classes=[0])
    for result in results:
        boxes = result.boxes

        if len(boxes)==0:
            detected = False
            nose = [-1, -1]
            return img, nose, detected
            break


        for i in range(len(boxes)):
            print(len(results))
            x, y, w, h = map(int, boxes.xywh[i].tolist())
            x = x - w // 2
            y = y - h // 2
            print(x, y, w, h)
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

        keypoint = result.keypoints
        for point in range(len(keypoint)):
            nose = keypoint.xy[point][0]
            x, y = map(int, nose)
            intnose=[x,y]
            if x != 0 or y != 0:
                cv2.circle(img, (x, y), 5, (0, 0, 255), -1)


    return  img,intnose,detected
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
if __name__ == '__main__':
    rtscap = RTSCapture.create('rtsp://admin:123456@192.168.1.102:554/h264/ch1/sub/av_stream')     # sys.argv[1]
    rtscap.start_read()
    fps = 0.0

    while rtscap.isStarted():
        ok, frame = rtscap.read_latest_frame()
        if not ok:
            continue
        frame = cv2.resize(frame, (480,640 ))
        imgObjects, nose, detected = findnose(frame, nose)
        #imgObjects, objects = odm.findObjects(frame, faceCascade, 1.08, 10)
        if not detected:
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

        #cx, cy, imgObjects = findCenter(imgObjects, objects)
        cx, cy = nose[0], nose[1]
        print(type(cx), type(nose))
        h, w, c = imgObjects.shape
        cv2.line(imgObjects, (w // 2, 0), (w // 2, h), (255, 0, 255), 1)  
        cv2.line(imgObjects, (0, h // 2), (w, h // 2), (255, 0, 255), 1)
        print(cx, cy, w, h
        )
        trackObject(cx, cy, w, h)
        img = cv2.resize(imgObjects, (640, 480))
        cv2.imshow("cam", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            d = bytes.fromhex( 'ff 01 00 00 00 00 01')
            sm.send(serr,d)
            break

    rtscap.stop_read()
    rtscap.release()
    cv2.destroyAllWindows()
