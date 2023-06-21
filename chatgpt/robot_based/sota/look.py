from commu.robottools_commu import RobotTools
import cv2
import time
import mediapipe as mp
mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils

rt = RobotTools('192.168.36.70', 22222)

def look(x:int, y:int, width=320, height=240):
    """ x, y を見る """
    curr_servo_map = rt.read_axes()
    # 画面中央から指定位置までのYawとPitchの角度を計算
    dx = x - width / 2
    dy = y - height / 2
    dyaw = round(dx * 48 / width) * (-1) # dx : width(pixel) = dyaw : 48deg
    dpitch = round(dy * 36 / height) # dy : height(pixel) = dpitch : 36deg
    # 頭部の関節の回転角を計算
    servo_map = {}
    ## head yaw
    if   curr_servo_map['HEAD_Y'] + dyaw > 85:
        servo_map.update(HEAD_Y=85)
    elif curr_servo_map['HEAD_Y'] + dyaw < -85:
        servo_map.update(HEAD_Y=-85)
    else:
        servo_map.update(HEAD_Y=curr_servo_map['HEAD_Y'] + dyaw)
    ## head pitch
    if   curr_servo_map['HEAD_P'] + dpitch > 5:
        servo_map.update(HEAD_P=5)
    elif curr_servo_map['HEAD_P'] + dpitch < -27:
        servo_map.update(HEAD_P=-27)
    else:
        servo_map.update(HEAD_P=curr_servo_map['HEAD_P'] + dpitch)
    # ポーズの実行
    pose = dict(Msec=500, ServoMap=servo_map)
    rt.play_pose(pose)


cap = cv2.VideoCapture('udp://127.0.0.1:5000')

with mp_face_detection.FaceDetection(
    model_selection=0, min_detection_confidence=0.5) as face_detection:
    timestamp = time.time()
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            # If loading a video, use 'break' instead of 'continue'.
            continue

        # To improve performance, optionally mark the image as not writeable to
        # pass by reference.
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = face_detection.process(image)

        # Draw the face detection annotations on the image.
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        # 鼻の位置の取得
        nose_tip = None
        if results.detections:
            for detection in results.detections:
                mp_drawing.draw_detection(image, detection)
                nose_tip = mp_face_detection.get_key_point(
                    detection, mp_face_detection.FaceKeyPoint.NOSE_TIP)
                # print(f'x={nose_tip.x}, y={nose_tip.y}')
                

        if nose_tip:
            if time.time() - timestamp > 0.5:
                # mediapipeの出力する値は0~1に正規化されているため、画像サイズに合わせて値を変換
                # x: width  [1, 0]
                # y: height [0, 1]
                # look((nose_tip.x - 1) * 320, nose_tip.y * 240)
                look((nose_tip.x) * 320, nose_tip.y * 240)
                timestamp = time.time()

        # Flip the image horizontally for a selfie-view display.
        cv2.imshow('MediaPipe Face Detection', cv2.flip(image, 1))
        if cv2.waitKey(5) & 0xFF == 27:
            break


cap.release()

cv2.destroyAllWindows()
   