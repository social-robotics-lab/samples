# 起動順序
- Sota: `java -jar RobotController.jar`
- MyPC: `python look.py`
- Sota: `./ffmpeg -f v4l2 -s 320x240 -thread_queue_size 8192 -i /dev/video0 -c:v libx264 -preset ultrafast -tune zerolatency -f h264 udp://192.168.11.4:5000?pkt_size=1024`
- MyPC: `python asr.py`
- Sota: `./ffmpeg -channels 1 -f alsa -thread_queue_size 8192 -i hw:2 -preset ultrafast -tune zerolatency -ac 1 -c:a pcm_s16le -ar 16000 -f s16le udp://192.168.11.4:5001?pkt_size=1024`