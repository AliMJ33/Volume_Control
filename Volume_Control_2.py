import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

detector = HandDetector(maxHands=1, detectionCon=0.8)
video = cv2.VideoCapture(0)
video.set(3, 1280)
video.set(4, 720)

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

volRange = volume.GetVolumeRange()

minVol = volRange[0]
maxVol = volRange[1]

volumeBar = 400
vol = 0
volPer = 0
minlength, maxlength, length = 0, 0, 0
while True:
    _, img = video.read()
    hand = detector.findHands(img, draw=True)
    if hand:
        lmlist = hand[0]
        if len(lmlist) == 1:
            fingerup = detector.fingersUp(lmlist[0])
            cv2.circle(img, (lmlist[0]["lmList"][8][0], lmlist[0]["lmList"][8][1]), 5, (0, 255, 255), -1)
            cv2.circle(img, (lmlist[0]["lmList"][4][0], lmlist[0]["lmList"][4][1]), 5, (0, 255, 255), -1)
            cv2.line(img, (lmlist[0]["lmList"][8][0], lmlist[0]["lmList"][8][1]),
                          (lmlist[0]["lmList"][4][0], lmlist[0]["lmList"][4][1]), (0, 0, 0), 2)
            if lmlist[0]["type"] == "Left":
                cv2.putText(img, "Extend or reduce the dist of index finger and thumb.",
                            (100, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)
                cv2.putText(img, "Adjust min by bringing up your pinkie finger. Adjust max by holding all fingers up.",
                            (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)

                if fingerup==[1,1,0,0,1] or fingerup==[0,1,0,0,1] or fingerup==[0,0,0,0,1] or fingerup==[1,0,0,0,1]:
                    minlength, _, _ = detector.findDistance((lmlist[0]["lmList"][8][0], lmlist[0]["lmList"][8][1]),
                                                        (lmlist[0]["lmList"][4][0], lmlist[0]["lmList"][4][1]))
                if fingerup == [1, 1, 1, 1, 1]:
                    maxlength, _, _ = detector.findDistance((lmlist[0]["lmList"][8][0], lmlist[0]["lmList"][8][1]),
                                                            (lmlist[0]["lmList"][4][0], lmlist[0]["lmList"][4][1]))

            print("minimum: ", minlength, "\nmaximum: ", maxlength)
            if lmlist[0]["type"] == "Right":
                if fingerup != [1, 1, 0, 0, 1]:
                    length, _, _ = detector.findDistance((lmlist[0]["lmList"][8][0], lmlist[0]["lmList"][8][1]),
                                                         (lmlist[0]["lmList"][4][0], lmlist[0]["lmList"][4][1]))
                vol = np.interp(length, [minlength, maxlength], [0, 1])
                volumeBar = np.interp(length, [minlength, maxlength], [400, 150])
                volPer = np.interp(length, [minlength, maxlength], [0, 100])
                volume.SetMasterVolumeLevelScalar(vol, None)

        cv2.putText(img, f"{round(volPer, 2)}%", (250, 250), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 150, 255), 2)
        cv2.rectangle(img, (50, 150), (85, 400), (0, 255, 0), 3)
        cv2.rectangle(img, (50, int(volumeBar)), (85, 400), (0, 255, 0), cv2.FILLED)

    cv2.imshow("Camera Feedback", img)
    if cv2.waitKey(1) == 27:
        break

video.release()
cv2.destroyAllWindows()
