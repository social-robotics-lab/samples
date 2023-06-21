from commu.robottools_commu import RobotTools
import openai
import time
import azure.cognitiveservices.speech as speechsdk

rt = RobotTools('192.168.11.58', 22222)
rt.play_pose(dict(Msec=250, ServoMap=dict(L_EYE_Y=-10, R_EYE_Y=10)))

nod_motion = [
    dict(Msec=250, ServoMap=dict(HEAD_P=-15,)),
    dict(Msec=250, ServoMap=dict(HEAD_P=10, )),
    dict(Msec=250, ServoMap=dict(HEAD_P=-15, ))
]
eye_blink = [
    dict(Msec=100, ServoMap=dict(EYELID=-45,)),
    dict(Msec=100, ServoMap=dict(EYELID=0, )),
]

speech_key, service_region = "ここにAPIキーを入れる", "japanwest"
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
speech_config.speech_recognition_language='ja-JP'


# OpenAI APIキーをセットアップ
openai.api_key = 'ここにAPIキーを入れる'
model_engine = 'gpt-3.5-turbo'

speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)
print("Say something...")

params = [
    {'role': 'system', 'content': 'あなたはユーザーの雑談相手です。'},
    {'role': 'system', 'content': '返事は短めに二文までにしてください。'}
]

while True:
    result = speech_recognizer.recognize_once()

    # Checks result.
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print('USER: ' + result.text)
        rt.play_motion(motion=nod_motion)

        # ユーザーの入力を送信し、返答を取得
        params.append({'role': 'user', 'content': result.text})
        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=params,
            stream=True
        )
        collected_messages = []
        for chunk in response:
            chunk_message = chunk['choices'][0]['delta']
            if "content" in chunk_message:
                collected_messages.append(chunk_message.get("content"))
                if '、' in chunk_message.get('content') or \
                   '。' in chunk_message.get('content') or \
                   '？' in chunk_message.get('content'):
                    message = ''.join(collected_messages)
                    params.append({'role': 'assistant', 'content': message})
                    print('ROBOT: ' + message)
                    # ロボットに返答を発話させる
                    d = rt.say_text(message)
                    m = rt.make_beat_motion(d, speed=1.5)
                    rt.play_motion(m)

                    # 発話中は音声認識を止める
                    time.sleep(d)                    
                    collected_messages.clear()

    elif result.reason == speechsdk.ResultReason.NoMatch:
        print("No speech could be recognized: {}".format(result.no_match_details))
        rt.play_motion(eye_blink)
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print("Speech Recognition canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))

    if result.text.startswith('終了'):
        break

    rt.play_motion(eye_blink)