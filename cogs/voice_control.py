import asyncio
import datetime
import logging
import json

import discord
from discord.commands import Option, SlashCommandGroup, permissions, slash_command
from discord.ext import commands

import config
from utils.database import *
from utils.embed import Embed
from utils.tool import CheckTool


class voice_control(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(config.setting.log.name)

    # ==========================================================

    """
    명령어를 사용한 유저가 음성 채널에 입장했는지 확인하는 코드입니다.
    """

    async def channel_check(self):
        if self.guild:
            if self.author.voice:
                return True
            else:
                embed = Embed.warn(
                    timestamp=datetime.datetime.now(),
                    description="먼저 음성 채널에 접속해주세요.",
                )
                Embed.user_footer(embed, self.author)
                await self.respond(embed=embed, ephemeral=True)
                return False
        else:
            embed = Embed.warn(
                timestamp=datetime.datetime.now(), description="서버에서만 사용 가능한 명령어에요."
            )
            Embed.user_footer(embed, self.author)
            await self.respond(embed=embed, ephemeral=True)
            return False

    # ==========================================================

    voice_control = SlashCommandGroup("음챗", "음성 채널 관리 기능이에요.")

    user_perm = voice_control.create_subgroup("유저", "음챗의 유저 권한 관리 기능이에요.")

    @voice_control.command(
        name="잠금",
        description="'음챗 생성기'를 통해 생성된 채널을 잠금해요.",
        checks=[channel_check],
    )
    async def voice_lock(self, ctx):
        await ctx.defer(ephemeral=True)

        with open("data/voice_channel.json", encoding="UTF8") as f:
            crvoice_data = json.load(f)

        if not str(ctx.author.voice.channel.id) in crvoice_data.copy().keys():
            return await ctx.respond(
                f"❌ | 이 채널({ctx.author.voice.channel.mention})은 ``음챗 생성기``를 통해 생성된 채널이 아니에요."
            )

        overwrite = ctx.author.voice.channel.overwrites_for(ctx.guild.default_role)
        await ctx.author.voice.channel.set_permissions(
            ctx.bot.user, manage_channels=True, manage_permissions=True, connect=True
        )
        if overwrite.connect:
            lock_enabled = True
            for perm in ctx.author.voice.channel.overwrites:
                if perm.id == self.bot.user.id:
                    pass
                else:
                    await ctx.author.voice.channel.set_permissions(perm, connect=False)
        else:
            lock_enabled = False
            for perm in ctx.author.voice.channel.overwrites:
                if perm.id == self.bot.user.id:
                    pass
                else:
                    await ctx.author.voice.channel.set_permissions(
                        perm, connect=True, speak=True
                    )
        await ctx.respond(
            f"✅ | ``음챗 생성기``를 통해 생성된 채널의 잠금이 ``{'활성화' if lock_enabled else '비활성화'}``되었어요."
        )

    @user_perm.command(
        name="추가",
        description="[🔒 음챗 잠금 필요] '음챗 생성기'를 통해 생성된 채널에 유저의 입장 권한을 추가해요.",
        checks=[channel_check],
    )
    async def user_perm_add_user(
        self,
        ctx,
        user: Option(discord.User, "추가할 유저를 입력해주세요.", required=True, name="유저"),
    ):
        await ctx.defer(ephemeral=True)

        overwrite = ctx.author.voice.channel.overwrites_for(ctx.guild.default_role)
        if overwrite.connect:
            return await ctx.respond("❌ | 잠금 처리되지 않은 채널입니다.")

        await ctx.author.voice.channel.set_permissions(user, connect=True, speak=True)
        await ctx.respond(f"✅ | {user}님을 {ctx.author.voice.channel.mention}에 추가하셨습니다!")

    @user_perm.command(
        name="제거",
        description="[🔒 음챗 잠금 필요] '음챗 생성기'를 통해 생성된 채널에 유저의 입장 권한을 제거해요.",
        checks=[channel_check],
    )
    async def user_perm_remove_user(
        self,
        ctx,
        user: Option(discord.User, "제거할 유저를 입력해주세요.", required=True, name="유저"),
    ):
        await ctx.defer(ephemeral=True)

        overwrite = ctx.author.voice.channel.overwrites_for(ctx.guild.default_role)
        if overwrite.connect:
            return await ctx.respond("❌ | 잠금 처리되지 않은 채널입니다.")

        overwriteForUser = ctx.author.voice.channel.overwrites_for(user)
        if not overwriteForUser.connect:
            return await ctx.respond("❌ | 해당 유저에게 권한이 부여되지 않았습니다.")

        await ctx.author.voice.channel.set_permissions(user, overwrite=None)
        await ctx.respond(f"✅ | {user}님을 {ctx.author.voice.channel.mention}에서 제거하셨습니다!")


def setup(bot):
    bot.add_cog(voice_control(bot))
