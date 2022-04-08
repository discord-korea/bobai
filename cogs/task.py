import datetime
import logging
import os
from itertools import cycle

import aiohttp
import discord
import revar
from discord.ext import commands, tasks

import config


class task(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(config.setting.log.name)

        self.presences = cycle(config.setting.presences)
        self.activity_change.start()
        if config.test_mode == False:
            self.update_stats.start()

    def cog_unload(self):
        self.activity_change.stop()
        try:
            self.update_stats.stop()
        except:
            pass

    @tasks.loop(seconds=10)
    async def activity_change(self):
        await self.bot.wait_until_ready()
        for shard in self.bot.shards.values():
            nowp = next(self.presences)
            act_check = {
                "playing": discord.ActivityType.playing,
                "watching": discord.ActivityType.watching,
                "listening": discord.ActivityType.listening,
            }
            activity_type = act_check[nowp["type"]]
            name = revar.replace(
                nowp["name"],
                {
                    "{{서버}}": str(len(self.bot.guilds)),
                    "{{유저}}": str(len(self.bot.users)),
                    "{{샤드}}": str(shard.id + 1),
                },
            )
            await self.bot.change_presence(
                activity=discord.Activity(
                    name=f"/정보 | {name}",
                    type=activity_type,
                ),
                shard_id=shard.id,
            )

    @tasks.loop(hours=3)
    async def update_stats(self):
        await self.bot.wait_until_ready()
        async with aiohttp.ClientSession() as session:
            if not config.setting.koreanbots_token == "":
                async with session.post(
                    f"https://koreanbots.dev/api/v2/bots/{self.bot.user.id}/stats",
                    data={
                        "servers": len(self.bot.guilds),
                        "shards": len(self.bot.shards),
                    },
                    headers={"Authorization": config.setting.koreanbots_token},
                ) as res:
                    if res.status != 200:
                        self.logger.error(
                            f"❌ 한디리 서버수 업데이트 실패 ({(await res.json())['message']})"
                        )
                    else:
                        self.logger.info(
                            f"✅ 한디리 서버수 업데이트 성공 ({(await res.json())['message']})"
                        )

            if not config.setting.topgg_token == "":
                async with session.post(
                    f"https://top.gg/api/bots/{self.bot.user.id}/stats",
                    data={
                        "server_count": len(self.bot.guilds),
                        "shard_count": len(self.bot.shards),
                    },
                    headers={"Authorization": config.setting.topgg_token},
                ) as res:
                    if res.status != 200:
                        self.logger.error(
                            f"❌ TOP.GG 서버수 업데이트 실패 ({(await res.json())['error']})"
                        )
                    else:
                        self.logger.info(f"✅ TOP.GG 서버수 업데이트 성공")

            if not config.setting.archiver_token == "":
                async with session.post(
                    f"https://api.archiver.me/bots/{self.bot.user.id}/server",
                    json={
                        "servers": int(len(self.bot.guilds)),
                    },
                    headers={
                        "Authorization": f"Bearer {config.setting.archiver_token}"
                    },
                ) as res:
                    if res.status != 200:
                        self.logger.error(
                            f"❌ Archiver 서버수 업데이트 실패 ({(await res.json())['message']})"
                        )
                    else:
                        self.logger.info(
                            f"✅ Archiver 서버수 업데이트 성공 ({(await res.json())['message']})"
                        )

            if not config.setting.universe_token == "":
                async with session.post(
                    f"https://universelist.kr/api/bots/{self.bot.user.id}/stat",
                    data={
                        "servers": int(len(self.bot.guilds)),
                        "users": int(len(self.bot.users)),
                    },
                    headers={"Authorization": config.setting.archiver_token},
                ) as res:
                    if res.status != 200:
                        self.logger.error(
                            f"❌ Universelist 서버수 업데이트 실패 ({(await res.json())['message']})"
                        )
                    else:
                        self.logger.info(
                            f"✅ Universelist 서버수 업데이트 성공 ({(await res.json())['message']})"
                        )


def setup(bot):
    bot.add_cog(task(bot))
