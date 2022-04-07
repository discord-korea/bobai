import asyncio
import logging

import aiohttp
import discord
from discord.ext import commands

import config


class listener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(config.setting.log.name)

    @commands.Cog.listener()
    async def on_shard_connect(self, shard_id):
        self.logger.info(f"📥 | {self.bot.user}의 {shard_id+1}번째 샤드가 연결되었습니다.")

    @commands.Cog.listener()
    async def on_shard_disconnect(self, shard_id):
        self.logger.info(f"📥 | {self.bot.user}의 {shard_id+1}번째 샤드가 연결 해제되었습니다.")

    @commands.Cog.listener()
    async def on_shard_resumed(self, shard_id):
        self.logger.info(f"🔁 | {self.bot.user}의 {shard_id+1}번째 샤드가 재시작되었습니다.")

    @commands.Cog.listener()
    async def on_shard_ready(self, shard_id):
        self.logger.info(f"🚥 | {self.bot.user}의 {shard_id+1}번째 샤드가 준비되었습니다.")

        if config.test_mode == False and config.setting.webhook_url != "":
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    config.setting.webhook_url,
                    data={
                        "avatar_url": str(self.bot.user.display_avatar),
                        "username": self.bot.user.name,
                        "content": f"[{self.bot.user.mention}] 🚥 {shard_id+1}번째 샤드가 준비되었습니다.",
                    },
                ) as r:
                    return

    @commands.Cog.listener()
    async def on_ready(self):
        self.logger.info(f"🚥 | {self.bot.user}이(가) 준비되었습니다.")


def setup(bot):
    bot.add_cog(listener(bot))
