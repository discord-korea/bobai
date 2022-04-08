import asyncio

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
        return await client.guilds.find_one({"guild_id": guild_id})

    async def guild_add(guild_id: int):
        """
        서버 정보를 검색합니다.

        Parameters
        ----------
        guild_id: int
            - 추가할 길드의 아이디를 입력합니다.
        """
        return await client.guilds.insert_one({"_id": guild_id, "generator_channel": []})

class VOICE_GENERATOR_DB:
    """
    '음챗 생성기'를 위한 데이터베이스 유틸 목록입니다.
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

        result = await client.guilds.find_one({'_id': guild_id})
        if result:
            if channel_id in result['generator_channel']:
                return True
        return False

    async def channel_add(guild_id: int, channel_id: int):
        """
        데이터베이스에 저장된 생성 채널을 검색합니다.

        Parameters
        ----------
        guild_id: int
            - 추가할 채널이 있는 길드의 아이디를 입력합니다.
        channel_id: int
            - 추가할 채널의 아이디를 입력합니다.
        """

        find_data = (await client.guilds.find_one({'_id': guild_id}))['generator_channel']
        find_data += [channel_id]
        await client.guilds.update_one({'_id': guild_id}, {'$set': {'generator_channel': find_data}})
