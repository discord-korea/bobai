import asyncio
import datetime
import json
import logging

import aiohttp
import discord
from discord.ext import commands

import config
from utils.embed import Embed
from utils.tool import ErrorTool


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
        with open("data/voice_channel.json", encoding="UTF8") as f:
            self.crvoice_data = json.load(f)

        for ch in self.crvoice_data.copy().keys():
            voice_channel = self.bot.get_channel(int(ch))
            if voice_channel:
                members = voice_channel.members
                users = []
                for user in members:
                    users.append(user)
                if len(users) == 0:
                    name = f"{voice_channel.name}({voice_channel.id})"
                    try:
                        await self.bot.get_channel(voice_channel.id).delete(
                            reason=f"🚀 | 모든 유저가 채널을 퇴장하여 {name} 채널이 삭제되었어요."
                        )
                        self.logger.info(f"🚀 | 모든 유저가 채널을 퇴장하여 {name} 채널이 삭제되었어요.")
                        del self.crvoice_data[str(voice_channel.id)]
                    except Exception as error:
                        self.logger.error(
                            f"🚀 | {name} 채널 삭제 중, 오류가 발생했어요. (길드 : {voice_channel.guild.id} | 오류 : {error})"
                        )
            else:
                self.logger.info(f"🚀 | 모든 유저가 채널을 퇴장하여 채널 이름 조회 불가({ch}) 채널이 삭제되었어요.")
                del self.crvoice_data[str(ch)]

        json.dump(
            self.crvoice_data, open("data/voice_channel.json", "w", encoding="UTF8")
        )

    @commands.Cog.listener()
    async def on_application_command(self, ctx):
        self.logger.info(f"💻 {ctx.author}({ctx.author.id}) - '/{ctx.command}' 명령어 사용")

    @commands.Cog.listener()
    async def on_application_command_error(self, ctx, error):
        try:
            error = error.original
        except:
            pass

        print(error)

        if isinstance(error, commands.CommandNotFound):
            return

        elif isinstance(error, commands.MissingPermissions):
            mps = ", ".join(ErrorTool.check_perm(perm=error.missing_permissions))
            embed = Embed.warn(
                timestamp=datetime.datetime.now(), description="사용자의 권한이 부족해요."
            )
            embed.add_field(name="필요 권한", value=f"```{mps}```")
            Embed.user_footer(embed, ctx.author)

        elif isinstance(error, commands.NoPrivateMessage):
            embed = Embed.warn(
                timestamp=datetime.datetime.now(), description="서버에서만 사용 가능한 명령어에요."
            )
            Embed.user_footer(embed, ctx.author)

        elif isinstance(error, commands.MaxConcurrencyReached):
            embed = Embed.warn(
                timestamp=datetime.datetime.now(), description="처리 대기중인 명령어가 있어요."
            )
            Embed.user_footer(embed, ctx.author)

        elif isinstance(error, commands.DisabledCommand):
            embed = Embed.warn(
                timestamp=datetime.datetime.now(), description="비활성화된 명령어에요."
            )
            Embed.user_footer(embed, ctx.author)

        elif isinstance(error, commands.CommandOnCooldown):
            cooldown = int(error.retry_after)
            hours = cooldown // 3600
            minutes = (cooldown % 3600) // 60
            seconds = cooldown % 60
            time = []
            if not hours == 0:
                time.append(f"{hours}시간")
            if not minutes == 0:
                time.append(f"{minutes}분")
            if not seconds == 0:
                time.append(f"{seconds:02}초")
            embed = Embed.warn(
                timestamp=datetime.datetime.now(),
                description=f"이 명령어는 ``{' '.join(time)}`` 뒤에 사용하실 수 있어요.",
            )
            Embed.user_footer(embed, ctx.author)

        else:
            embed = Embed.error(
                timestamp=datetime.datetime.now(), description="오류 코드는 ``ㅁㄴㅇㄹ``입니다."
            )

        try:
            await ctx.respond(embed=embed, ephemeral=True)
        except:
            await ctx.reply(embed=embed, mention_author=False)


def setup(bot):
    bot.add_cog(listener(bot))
