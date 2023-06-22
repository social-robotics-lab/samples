import argparse
import time
import cv2
import mediapipe as mp
from collections import deque
from threading import Thread, Lock
from google.protobuf.json_format import MessageToDict


def read(cap:cv2.VideoCapture, stack:deque, lock:Lock):
    """ 画像を読み込み、スタックに追加する """
    while cap.isOpened():
        success, frame = cap.read()
        if success:
            with lock:
                stack.append(frame)


def main(args):
    lock = Lock()
    stack = deque()
    cap = cv2.VideoCapture(args.src)

    # Starting a thread for reading images
    Thread(target=read, args=(cap, stack, lock), daemon=True).start()
    time.sleep(1)

    # Recognition by MediaPipe
    mp_face_detection = mp.solutions.face_detection
    mp_drawing = mp.solutions.drawing_utils
    fps = 0
    skip_frames = 0
    try:
        with mp_face_detection.FaceDetection(
            model_selection=0, min_detection_confidence=0.5) as face_detection:
            while cap.isOpened():
                # スタックの一番上のデータを取得、その他を廃棄
                with lock:
                    if len(stack) == 0: continue
                    frame = stack.pop()
                    skip_frames = len(stack)
                    stack.clear()
                t_start = time.time()
                # 認識
                if frame is None: break
                # To improve performance, optionally mark the frame as not writeable to
                # pass by reference.
                frame.flags.writeable = False
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = face_detection.process(frame)
                # Draw the face detection annotations on the frame.
                frame.flags.writeable = True
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                if results.detections:
                    for detection in results.detections:
                        mp_drawing.draw_detection(frame, detection)

                # 認識結果を映像に反映
                cv2.putText(frame, text=f'FPS: {fps}', org=(3,15), fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                            fontScale=0.6, color=(255, 0, 0), thickness=2)
                cv2.imshow("frame", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    raise KeyboardInterrupt
                # 認識結果を自然数値化
                detection_dicts = [MessageToDict(d) for d in results.detections]
                # FPS計算
                t_end = time.time()
                proc_time = t_end - t_start
                fps = round(1.0 / proc_time, 2)
                skip_frames = int(30 * proc_time)
                print(f'Processing time = {proc_time}, fps = {fps}, Skip frames = {skip_frames}')

                # 認識結果を表示
                data = dict(timestamp=t_start, results=detection_dicts)
                print(data)

    except KeyboardInterrupt:
        pass

    if cap is not None: cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    parse = argparse.ArgumentParser()
    parse.add_argument('--src', default='udp://127.0.0.1:5000', type=str)
    args = parse.parse_args()
    main(args)
