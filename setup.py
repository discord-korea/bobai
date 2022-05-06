import json
import os

try:
    os.popen("mkdir logs")
    print("logs 폴더 생성 완료")
except Exception as error:
    print(error)

try:
    os.popen("mkdir data")
    print("data 폴더 생성 완료")
except Exception as error:
    print(error)

try:
    with open("data/voice_channel.json", "w") as f:
        f.write("{}")
    print("data/voice_channel.json 생성 완료")
except Exception as error:
    print(error)

try:
    with open("data/command_usages.json", "w") as f:
        f.write("{}")
    print("data/command_usages.json 생성 완료")
except Exception as error:
    print(error)
