import pyaudio
import numpy as np

CHUNK = 1024  # 音声データのチャンクサイズ
FORMAT = pyaudio.paInt16  # 音声データのフォーマット
CHANNELS = 1  # モノラル
RATE = 44100  # サンプリングレート (Hz)
THRESHOLD = 500  # 終了判定の閾値（適宜調整）

p = pyaudio.PyAudio()
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

print("音声発話を開始してください...")

while True:
    data = stream.read(CHUNK)
    # 音声データをnumpy配列に変換
    audio_data = np.frombuffer(data, dtype=np.int16)

    # 音声のエネルギーを計算
    energy = np.sum(np.abs(audio_data)) / len(audio_data)

    if energy > THRESHOLD:
        print("発話中")
        started = True
    elif energy <= THRESHOLD:
        print("沈黙")

stream.stop_stream()
stream.close()
p.terminate()

