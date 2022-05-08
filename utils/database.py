import asyncio
import datetime
import random
import string

import motor.motor_asyncio

import config

client = motor.motor_asyncio.AsyncIOMotorClient(config.setting.database.host_uri)[
    config.setting.database.collect_name
]
client.get_io_loop = asyncio.get_running_loop


class GUILD_DB:
    """
    서버 관련 데이터베이스 유틸 목록입니다.
    """

    async def guild_search(guild_id: int):
        """
        서버 정보를 검색합니다.

        Parameters
        ----------
        guild_id: int
            - 검색한 길드의 아이디를 입력합니다.
        """
        return await client.guilds.find_one({"_id": guild_id})

    async def guild_add(guild_id: int):
        """
        서버를 추가합니다.

        Parameters
        ----------
        guild_id: int
            - 추가할 길드의 아이디를 입력합니다.
        """
        return await client.guilds.insert_one(
            {"_id": guild_id, "generator_channel": {}}
        )

    async def guild_remove(guild_id: int):
        """
        서버를 제거합니다.

        Parameters
        ----------
        guild_id: int
            - 제거할 길드의 아이디를 입력합니다.
        """
        return await client.guilds.delete_one({"_id": guild_id})


class VOICE_GENERATOR_DB:
    """
    '음챗 생성기'를 위한 데이터베이스 유틸 목록입니다.

    구조
    ----------
    {'_id': guild_id, 'generator_channel': {channel_id: {'voice_name': channel_name}}}
    """

    async def channel_search(guild_id: int, channel_id: int):
        """
        데이터베이스에 저장된 생성 채널을 검색합니다.

        Parameters
        ----------
        guild_id: int
            - 조회할 채널이 있는 길드의 아이디를 입력합니다.
        channel_id: int
            - 조회할 채널의 아이디를 입력합니다.

        Return_Value
        ----------
        bool (True or False)
        """

        result = await client.guilds.find_one({"_id": guild_id})
        if result:
            if str(channel_id) in result["generator_channel"].keys():
                return result["generator_channel"][str(channel_id)]
        return None

    async def channel_add(
        guild_id: int, channel_id: int, channel_name: str = "{{유저이름}}님의 방"
    ):
        """
        데이터베이스에 저장된 생성 채널을 추가합니다.

        Parameters
        ----------
        guild_id: int
            - 추가할 채널이 있는 길드의 아이디를 입력합니다.
        channel_id: int
            - 추가할 채널의 아이디를 입력합니다.
        channel_name: str
            - 만들어질 채널의 이름을 입력합니다. 입력하지 않을 경우, '{{유저이름}}님의 방'으로 자동 설정됩니다.
        """

        find_data = (await client.guilds.find_one({"_id": guild_id}))[
            "generator_channel"
        ]
        find_data[str(channel_id)] = {"name": channel_name}
        await client.guilds.update_one(
            {"_id": guild_id}, {"$set": {"generator_channel": find_data}}
        )


class ERROR_DB:
    """
    오류 처리 관련 데이터베이스 유틸입니다.
    """

    async def search(code: str):
        """
        데이터베이스에 오류 로그를 검색합니다.

        Parameters
        ----------
        code: str
            - 오류 코드를 str로 입력합니다.
        """

        return await client.errors.find_one({"_id": code})

    async def add(guild_id: int, channel_id: int, user_id:int, command: str, error: str):
        """
        데이터베이스에 오류 로그를 추가합니다.

        Parameters
        ----------
        guild_id: int
            - 오류가 발생한 서버의 아이디를 입력합니다.
        channel_id: int
            - 오류가 발생한 채널의 아이디를 입력합니다.
        user_id: int
            - 오류를 발생시킨 유저의 아이디를 입력합니다.
        command: str
            - 오류가 발생한 명령어를 입력합니다.
        error: str
            - 오류 내용을 str형식으로 입력합니다.
        """

        while True:
            string_pool = string.ascii_letters + string.digits
            error_id = ""

            for sul in range(8):
                error_id += random.choice(string_pool)

            if (await ERROR_DB.search(error_id)) is None:
                break

        await client.errors.insert_one(
            {
                "_id": error_id,
                "info": {
                    "guild_id": guild_id,
                    "channel_id": channel_id,
                    "user_id": user_id,
                    "command": command,
                    "datetime": datetime.datetime.now(),
                },
                "error": error,
            }
        )

        return {"id": error_id}

    async def delete(code: str):
        """
        데이터베이스의 오류 로그를 삭제합니다.

        Parameters
        ----------
        code: str
            - 오류 코드를 str로 입력합니다.
        """

        return await client.errors.delete_one({"_id": code})
