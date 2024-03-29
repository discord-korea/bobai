import json
import logging
import traceback

import discord
import revar
from discord.ext import commands

import config
from utils.database import *

"""
data/voice_channel.json example

{'channel_id': {'owner': user_id, 'members': [user_id, user_id, ...]}}

"""


class voice_generator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(config.setting.log.name)
        with open("data/voice_channel.json", encoding="UTF8") as f:
            self.crvoice_data = json.load(f)
        self.cool_users = []

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
                            del self.crvoice_data[str(before.channel.id)]
                            await self.bot.get_channel(before.channel.id).delete(
                                reason=f"🚀 | 모든 유저가 채널을 퇴장하여 {name} 채널이 삭제되었어요."
                            )
                            self.logger.info(f"🚀 | 모든 유저가 채널을 퇴장하여 {name} 채널이 삭제되었어요.")
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
                            if user.id in self.cool_users:
                                try:
                                    await user.send(
                                        f"안녕하세요, {user.mention}!\n\n>>> {after.channel.mention} 생성기의 쿨타임이 적용되어 있어요.\n잠시 후 다시 입장해주세요."
                                    )
                                except:
                                    pass
                                return
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
                                        bitrate=voice_channel.bitrate,
                                        rtc_region=voice_channel.rtc_region,
                                        video_quality_mode=voice_channel.video_quality_mode,
                                    )
                                else:
                                    new_channel = await voice_channel.guild.create_voice_channel(
                                        name=voice_name,
                                        overwrites=voice_channel.overwrites,
                                        bitrate=voice_channel.bitrate,
                                        rtc_region=voice_channel.rtc_region,
                                        video_quality_mode=voice_channel.video_quality_mode,
                                    )
                                await new_channel.set_permissions(
                                    self.bot.user,
                                    manage_channels=True,
                                    manage_permissions=True,
                                    connect=True,
                                    view_channel=True,
                                )
                                await new_channel.set_permissions(
                                    user,
                                    connect=True,
                                    speak=True,
                                )
                                await user.move_to(
                                    new_channel, reason=f"🚀 | {user}님이 방 생성을 요청하셨어요."
                                )
                                self.logger.info(
                                    f"🚀 | {voice_name}({voice_channel.id}) 생성이 완료되었어요."
                                )
                                self.crvoice_data[str(new_channel.id)] = {
                                    "owner": user.id,
                                    "members": [user.id],
                                }
                                self.cool_users.append(user.id)
                                await asyncio.sleep(10)
                                self.cool_users.remove(user.id)
                            except discord.Forbidden:
                                try:
                                    await user.send(
                                        f"안녕하세요, {user.mention}!\n\n>>> 권한이 부족하여 ``음챗 생성기``를 사용할 수 없어요.\n해당 서버의 관리자에게 문의해주세요."
                                    )
                                except:
                                    pass
                            except Exception as error:
                                self.logger.error(
                                    f"🚀 | {user}님의 방 생성 중, 오류가 발생했어요. (길드 : {after.channel.guild.id} | 오류 : {error})"
                                )
                                tb = traceback.format_exception(
                                    type(error), error, error.__traceback__
                                )
                                err = [line.rstrip() for line in tb]
                                errstr = "\n".join(err)
                                code = await ERROR_DB.add(
                                    after.channel.guild.id,
                                    after.channel.id,
                                    user.id,
                                    "음챗 생성 기능",
                                    errstr,
                                )

                                try:
                                    view = discord.ui.View()
                                    view.add_item(
                                        discord.ui.Button(
                                            label="서포트 서버 (삼해트의 공방)",
                                            emoji="<:discord_blurple:858642003327057930>",
                                            style=discord.ButtonStyle.link,
                                            url="https://discord.gg/TD9BvMxhP6",
                                        )
                                    )
                                    await user.send(
                                        f"안녕하세요, {user.mention}!\n\n>>> {user}님의 방 생성 중, 오류가 발생했어요.\n삼해트의 공방 ``#문의`` 채널에서 문의해주세요!\n- 오류 코드 : ``{code['id']}``",
                                        view=view,
                                    )
                                except:
                                    pass

            json.dump(
                self.crvoice_data, open("data/voice_channel.json", "w", encoding="UTF8")
            )


def setup(bot):
    bot.add_cog(voice_generator(bot))
