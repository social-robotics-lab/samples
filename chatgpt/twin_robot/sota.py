from robottools import RobotTools
import openai
import time
from queue import Queue
from threading import Thread

rt1 = RobotTools('192.168.11.12', 22222)
rt2 = RobotTools('192.168.11.20', 22222)

nod_motion = [
    dict(Msec=250, ServoMap=dict(HEAD_P=-15,)),
    dict(Msec=250, ServoMap=dict(HEAD_P=10, )),
    dict(Msec=250, ServoMap=dict(HEAD_P=-15, ))
]

# OpenAI APIキーをセットアップ
openai.api_key = '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'
model_engine = 'gpt-3.5-turbo-0613'

params = [
    {'role': 'system', 'content': 'あなたはユーザーの雑談相手です。'},
    {'role': 'system', 'content': '返事は短めに二文までにしてください。'}
]

d = rt1.say_text('起動しました。')
time.sleep(d)
d = rt2.say_text('起動しました。')
time.sleep(d)


def chat(label:str, recv_q:Queue, send_q:Queue, rt:RobotTools):
    while True:
        text = recv_q.get()
        rt.play_motion(motion=nod_motion)
        # ユーザーの入力を送信し、返答を取得
        params.append({'role': 'user', 'content': text})
        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=params,
            stream=True
        )

        collected_messages = []
        temporal_messages = []
        for chunk in response:
            chunk_message = chunk['choices'][0]['delta']
            if "content" in chunk_message:
                temporal_messages.append(chunk_message.get("content"))
                if '、' in chunk_message.get('content') or \
                   '。' in chunk_message.get('content') or \
                   '！' in chunk_message.get('content') or \
                   '？' in chunk_message.get('content'):
                    message = ''.join(temporal_messages)
                    params.append({'role': 'assistant', 'content': message})
                    print(f'ROBOT-{label}: {message}')
                    # ロボットに返答を発話させる
                    d = rt.say_text(message)
                    m = rt.make_beat_motion(d, speed=1.5)
                    rt.play_motion(m)
                    time.sleep(d)
                    temporal_messages.clear()
                    collected_messages.append(message)
        time.sleep(1)
        send_q.put(''.join(collected_messages))

q_1to2 = Queue()
q_2to1 = Queue()
robot1_th = Thread(target=chat, args=('1', q_2to1, q_1to2, rt1), daemon=True)
robot2_th = Thread(target=chat, args=('2', q_1to2, q_2to1, rt2), daemon=True)

robot1_th.start()
robot2_th.start()

q_1to2.put("こんにちは")

# 1000秒たったら終了
time.sleep(1000)