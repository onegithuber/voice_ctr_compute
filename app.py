#!/usr/bin/python
# -*- coding:utf-8 -*-
import base64
import json
import os
import wave

import pyaudio
import requests

API_KEY = 'rxQg9TaD0z9f3PQvlqFSoGBP'
SECRET_KEY = '2bab22d10e0814e1f6fc6f4163db8276'
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 8000
FRAMES_PER_BUFFER = 1024
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "./.out.wav"


class Token(object):
    def __init__(self):
        super(Token, self).__init__()

    def read_token(self):
        try:
            token_file = open(".token", 'r')
        except Exception, e:
            self.update_token()
            token_file = open(".token", 'r')
        token = token_file.readlines()
        if len(token) == 0:
            self.update_token()
            return
        token_file.close()
        return token

    def update_token(self):
        token_file = open("./.token", "w")
        token_file.write(self.get_token())
        token_file.close()

    def get_token(self):
        s = requests.session()
        url = 'https://openapi.baidu.com/oauth/2.0/token?grant_type=client_credentials&client_id=' + API_KEY +\
              '&client_secret=' + SECRET_KEY
        r = s.post(url)
        return json.loads(r.text).get('access_token')


TOKEN = Token().read_token()[0]


def record():
    pa = pyaudio.PyAudio()
    stream = pa.open(format=FORMAT,
                     channels=CHANNELS,
                     rate=RATE,
                     input=True,
                     frames_per_buffer=FRAMES_PER_BUFFER)

    frames = []
    for i in range(0, int(RATE / FRAMES_PER_BUFFER * RECORD_SECONDS)):
        data = stream.read(FRAMES_PER_BUFFER)  # 读声卡数据
        frames.append(data)
    stream.stop_stream()
    stream.close()
    pa.terminate()

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(pa.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()


def get_mac_address():
    import uuid
    node = uuid.getnode()
    mac = uuid.UUID(int=node).hex[-12:]
    return mac


def upload():
    vf = open(WAVE_OUTPUT_FILENAME, 'rb')
    voice = vf.read()
    length = len(voice)
    speech = base64.b64encode(voice)
    vf.close()

    data = {
        "format": "wav",
        "rate": 8000,
        "channel": 1,
        "token": TOKEN,
        "cuid": get_mac_address(),
        "len": length,
        "speech": speech
    }
    requrl = "http://vop.baidu.com/server_api"
    header = {"Content-Type": "application/json"}

    s = requests.session()

    # header 和 data 参数位置烦了，通过restful api测出来的
    r = s.post(requrl, header, data)

    result = json.loads(r.text)
    if result.get("err_msg") == "success.":
        return result.get("result")[0]
    elif "authentication failed." == result.get("err_msg"):
        Token().update_token()
        return "ERROR:", result.get("err_msg")
    elif result.get("err_msg") == "recognition error.":
        return result.get("err_msg")
    else:
        Token().update_token()
        return "ERROR:", result.get("err_msg")


def exec_cmd(cmd=''):
    # print cmd
    if u"开浏览器" in cmd or u"看网页" in cmd:
        os.system('open /Applications/Safari.app')
        exit()
    elif u"做什么" in cmd:
        os.system('open /Applications/Todoist.app/')
        exit()
    elif u"系统设置" in cmd:
        os.system('open /Applications/System\ Preferences.app/')
        exit()
    elif u"聊天" in cmd:
        os.system('open /Applications/QQ.app/')
        exit()
    elif u"代码" in cmd:
        os.system('open /Applications/Sublime\ Text.app/')
        exit()
    elif u"音乐" in cmd:
        os.system('open /Applications/diumoo.app')
        exit()

    elif u"说句话" == cmd:
        os.system('say "有什么可以帮你的吗？"')
    else:
        os.system('say "我没有听清楚，请再说一次"')


if __name__ == '__main__':
    os.system('say "有什么可以帮你的吗？"')
    while True:
        record()
        exec_cmd(upload())
