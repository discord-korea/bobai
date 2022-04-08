import json
import logging

import discord
import revar
from discord.ext import commands

import config
from utils.database import *


class create_voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(config.setting.log.name)
        with open("data/voice_channel.json", encoding="UTF8") as f:
            self.crvoice_data = json.load(f)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel != after.channel:
            if before.channel:
                if await VOICE_GENERATOR_DB.channel_search(
                    before.channel.guild.id, before.channel.id
                ):
                    return
                try:
                    key_data = self.crvoice_data[str(before.channel.id)]
                except KeyError:
                    key_data = None
                if key_data:
                    voice_channel = self.bot.get_channel(int(before.channel.id))
                    members = voice_channel.members
                    users = []
                    for user in members:
                        users.append(user)
                    if len(users) == 0:
                        name = f"{before.channel.name}({before.channel.id})"
                        try:
                            await self.bot.get_channel(before.channel.id).delete(
                                reason=f"🚀 | 모든 유저가 채널을 퇴장하여 {name} 채널이 삭제되었어요."
                            )
                            self.logger.info(f"🚀 | 모든 유저가 채널을 퇴장하여 {name} 채널이 삭제되었어요.")
                            del self.crvoice_data[str(before.channel.id)]
                        except Exception as error:
                            self.logger.error(
                                f"🚀 | {name} 채널 삭제 중, 오류가 발생했어요. (길드 : {before.channel.guild.id} | 오류 : {error})"
                            )

            if after.channel:
                if await VOICE_GENERATOR_DB.channel_search(
                    after.channel.guild.id, after.channel.id
                ):
                    voice_channel = self.bot.get_channel(int(after.channel.id))
                    members = voice_channel.members
                    users = []
                    for user in members:
                        if user.bot == False:
                            try:
                                voice_name = (
                                    await VOICE_GENERATOR_DB.channel_search(
                                        after.channel.guild.id, after.channel.id
                                    )
                                )["name"]
                                voice_name = revar.replace(
                                    voice_name,
                                    {
                                        "{{유저이름}}": str(user.name),
                                        "{{유저태그}}": f"{str(user.name)}#{str(user.discriminator)}",
                                    },
                                )
                                if voice_channel.category:
                                    new_channel = await voice_channel.category.create_voice_channel(
                                        name=voice_name,
                                        overwrites=voice_channel.overwrites,
                                    )
                                else:
                                    new_channel = (
                                        await voice_channel.guild.create_voice_channel(
                                            name=voice_name,
                                            overwrites=voice_channel.overwrites,
                                        )
                                    )
                                await user.move_to(
                                    new_channel, reason=f"🚀 | {user}님이 방 생성을 요청하셨어요."
                                )
                                self.logger.info(
                                    f"🚀 | {voice_name}({voice_channel.id}) 생성이 완료되었어요."
                                )
                                self.crvoice_data[str(new_channel.id)] = user.id
                            except Exception as error:
                                self.logger.error(
                                    f"🚀 | {user}님의 방 생성 중, 오류가 발생했어요. (길드 : {after.channel.guild.id} | 오류 : {error})"
                                )

            json.dump(
                self.crvoice_data, open("data/voice_channel.json", "w", encoding="UTF8")
            )


def setup(bot):
    bot.add_cog(create_voice(bot))
