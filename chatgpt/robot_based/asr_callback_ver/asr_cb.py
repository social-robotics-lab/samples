from commu.robottools_commu import RobotTools
import openai
import speech_recognition as sr
import time
import ffmpeg
import azure.cognitiveservices.speech as speechsdk

rt = RobotTools('192.168.11.41', 22222)

# OpenAI APIキーをセットアップ
openai.api_key = 'ここにAPIキーを入れる'

# OpenAIのGPTに接続
model_engine = 'gpt-3.5-turbo'

# 音声認識器を作成
r = sr.Recognizer()

# ChatGPTへのリクエストに含めるパラメータ
params = [
    {'role': 'system', 'content': 'あなたはユーザーの雑談相手です。ユーザーの発話には、短めに2文程度で返答するようにしてください。'}
]



# FFmpeg
process = (
    ffmpeg
    .input('udp://127.0.0.1:5001', format='s16le', acodec='pcm_s16le', ac=1, ar='16k')
    .output('-', format='s16le', acodec='pcm_s16le', ac=1, ar='16k')
    .run_async(pipe_stdout=True)
)

# Azure Speech SDK
speech_key = 'ここにAPIキーを入れる'
service_region = 'japanwest'
lang = 'ja-JP'

done = False

# ロボットの発話中に音声認識による発話生成をさせないために使う変数
time_robot_starts_speech = 0
speech_duration = 0

# Callback funcs
def recognizing_cb(evt):
    #print(f'Recognizing: {evt.result.text}')
    pass

def recognized_cb(evt):
    user_input = evt.result.text
    print('USER: ' + user_input)

    if user_input == '': return

    # ロボットが発話中は音声認識はするが発話生成はしない
    global time_robot_starts_speech, speech_duration
    if time.time() > time_robot_starts_speech + speech_duration:
        # ユーザーの入力を送信し、返答を取得
        params.append({'role': 'user', 'content': user_input})
        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=params
        )
        message = response.choices[0].message.content
        params.append({'role': 'assistant', 'content': message})
        print('ROBOT: ' + message)

        # ロボットに返答を発話させる
        speech_duration = rt.say_text(message)
        m = rt.make_beat_motion(speech_duration, speed=1.5)
        rt.play_motion(m)
        time_robot_starts_speech = time.time()

def session_started_cb(evt):
    print(f'Session started: {evt}')

def session_stopped_cb(evt):
    print(f'Session stopped: {evt}')
    global done
    done = True

def canceled_cb(evt):
    print(f'CLOSING on {evt}')
    global done
    done = True


# Config a speech recognizer
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
speech_config.speech_recognition_language=lang

stream = speechsdk.audio.PushAudioInputStream()
audio_config = speechsdk.audio.AudioConfig(stream=stream)

speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

# Connect callbacks to the events fired by the speech recognizer
speech_recognizer.recognizing.connect(recognizing_cb)
speech_recognizer.recognized.connect(recognized_cb)
speech_recognizer.session_started.connect(session_started_cb)
speech_recognizer.session_stopped.connect(session_stopped_cb)
speech_recognizer.canceled.connect(canceled_cb)

# Start continuous speech recognition
speech_recognizer.start_continuous_recognition()
try:
    while not done:

        in_bytes = process.stdout.read(1024)
        if not in_bytes:
            break

        stream.write(in_bytes)

except KeyboardInterrupt:
    pass

stream.close()
speech_recognizer.stop_continuous_recognition()
