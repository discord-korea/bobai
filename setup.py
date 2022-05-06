import json
import os
import asyncio


async def setup():
    logs_result = os.popen("mkdir logs")

    data_result = os.popen("mkdir data")

    await asyncio.sleep(1)

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


asyncio.run(setup())
