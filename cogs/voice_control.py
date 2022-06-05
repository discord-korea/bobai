import asyncio
import datetime
import json
import logging

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
                failEmbed = Embed.warn(
                    timestamp=datetime.datetime.now(),
                    description="먼저 음성 채널에 접속해주세요.",
                )
                Embed.user_footer(failEmbed, self.author)
                await self.respond(embed=failEmbed, ephemeral=True)
                return False
        else:
            failEmbed = Embed.warn(
                timestamp=datetime.datetime.now(), description="서버에서만 사용 가능한 명령어에요."
            )
            Embed.user_footer(failEmbed, self.author)
            await self.respond(embed=failEmbed, ephemeral=True)
            return False

    """
    명령어를 사용한 유저의 음성 채널이 '음챗 생성기'를 통해 만들어졌는지 확인하는 코드입니다.
    """

    async def voice_check(self):
        with open("data/voice_channel.json", encoding="UTF8") as f:
            crvoice_data = json.load(f)

        if not str(self.author.voice.channel.id) in crvoice_data.keys():
            failEmbed = embed = Embed.cancel(
                description=f"이 채널({self.author.voice.channel.mention})은 ``음챗 생성기``를 통해 생성된 채널이 아니에요.",
                timestamp=datetime.datetime.now(),
            )
            Embed.user_footer(failEmbed, self.author)
            await self.respond(
                embed=failEmbed,
                ephemeral=True,
            )
            return False
        elif (
            not crvoice_data[str(self.author.voice.channel.id)]["owner"]
            == self.author.id
        ):
            failEmbed = embed = Embed.cancel(
                description=f"이 명령어를 사용할 권한이 없어요.\n🚧 이 채널({self.author.voice.channel.mention})은 <@{crvoice_data[str(self.author.voice.channel.id)]['owner']}>님이 생성한 채널이에요.",
                timestamp=datetime.datetime.now(),
            )
            Embed.user_footer(failEmbed, self.author)
            await self.respond(
                embed=failEmbed,
                ephemeral=True,
            )
            return False
        else:
            return True

    """
    명령어를 사용한 유저의 음성 채널이 잠금되었는지 확인하는 코드입니다.
    """

    async def lock_check(self):
        overwrite = self.author.voice.channel.overwrites_for(self.guild.default_role)
        if overwrite.connect == True or overwrite.connect == None:
            failEmbed = Embed.cancel(
                description=f"이 채널({self.author.voice.channel.mention})은 잠금 처리되지 않은 채널이에요.\n\n🔒 ``/음챗 잠금`` 명령어를 사용하여 잠금을 진행해주세요.",
                timestamp=datetime.datetime.now(),
            )
            Embed.user_footer(failEmbed, self.author)
            await self.respond(
                embed=failEmbed,
                ephemeral=True,
            )
            return False
        else:
            return True

    # ==========================================================

    voice_control = SlashCommandGroup("음챗", "음성 채널 관리 기능이에요.")

    user_perm = voice_control.create_subgroup("유저", "음챗의 유저 권한 관리 기능이에요.")

    @voice_control.command(
        name="잠금",
        description="'음챗 생성기'를 통해 생성된 채널을 잠금해요.",
        checks=[channel_check, voice_check],
    )
    async def voice_lock(self, ctx):
        await ctx.defer(ephemeral=True)
        await ctx.author.voice.channel.set_permissions(
            ctx.bot.user, manage_channels=True, manage_permissions=True, connect=True
        )
        overwrite = ctx.author.voice.channel.overwrites_for(ctx.guild.default_role)
        
        with open("data/voice_channel.json", encoding="UTF8") as f:
            crvoice_data = json.load(f)

        if overwrite.connect or overwrite.connect is None:
            lock_enabled = True
            for perm in ctx.author.voice.channel.overwrites:
                if perm.id == self.bot.user.id or perm.id == ctx.author.id:
                    pass
                else:
                    await ctx.author.voice.channel.set_permissions(perm, connect=False)
                    crvoice_data[str(ctx.author.voice.channel.id)]["members"].append(user.id)

        else:
            lock_enabled = False
            for perm in ctx.author.voice.channel.overwrites:
                if perm.id == self.bot.user.id or perm.id == ctx.author.id:
                    pass
                else:
                    await ctx.author.voice.channel.set_permissions(
                        perm, connect=True, speak=True
                    )
            crvoice_data[str(ctx.author.voice.channel.id)]["members"] = [ctx.author.id]

        json.dump(
            crvoice_data, open("data/voice_channel.json", "w", encoding="UTF8")
        )

        successEmbed = Embed.default(
            title="✅ 설정 완료",
            description=f"``음챗 생성기``를 통해 생성된 채널의 잠금이 ``{'활성화' if lock_enabled else '비활성화'}``되었어요.",
            timestamp=datetime.datetime.now(),
        )
        Embed.user_footer(successEmbed, ctx.author)
        await ctx.respond(embed=successEmbed)

    @user_perm.command(
        name="추가",
        description="[🔒 음챗 잠금 필요] '음챗 생성기'를 통해 생성된 채널에 유저의 입장 권한을 추가해요.",
        checks=[channel_check, voice_check, lock_check],
    )
    async def user_perm_add_user(
        self,
        ctx,
        user: Option(discord.User, "추가할 유저를 입력해주세요.", required=True, name="유저"),
    ):
        await ctx.defer(ephemeral=True)
        if user == self.bot.user or user == ctx.author:
            failEmbed = Embed.cancel(
                description=f"{self.bot.user.mention} 또는 자기 자신은 제거할 수 없어요.",
                timestamp=datetime.datetime.now(),
            )
            Embed.user_footer(failEmbed, ctx.author)
            return await ctx.respond(embed=failEmbed)

        with open("data/voice_channel.json", encoding="UTF8") as f:
            crvoice_data = json.load(f)

        overwriteForUser = ctx.author.voice.channel.overwrites_for(user)
        if overwriteForUser.connect:
            failEmbed = Embed.cancel(
                description=f"해당 유저({user.mention})는 이미 이 채널에 접근할 수 있는 권한이 있어요.",
                timestamp=datetime.datetime.now(),
            )
            Embed.user_footer(failEmbed, ctx.author)
            return await ctx.respond(embed=failEmbed)
        await ctx.author.voice.channel.set_permissions(user, connect=True, speak=True)
        successEmbed = Embed.default(
            title="✅ 설정 완료",
            description=f"{user}님을 {ctx.author.voice.channel.mention}에 추가했어요!\n\n📥 이제 해당 채널에 접근하실 수 있어요.",
            timestamp=datetime.datetime.now(),
        )
        Embed.user_footer(successEmbed, ctx.author)

        crvoice_data[str(ctx.author.voice.channel.id)]["members"].append(user.id)

        json.dump(
            crvoice_data, open("data/voice_channel.json", "w", encoding="UTF8")
        )

        await ctx.respond(embed=successEmbed)

    @user_perm.command(
        name="제거",
        description="[🔒 음챗 잠금 필요] '음챗 생성기'를 통해 생성된 채널에 유저의 입장 권한을 제거해요.",
        checks=[channel_check, voice_check, lock_check],
    )
    async def user_perm_remove_user(
        self,
        ctx,
        user: Option(discord.User, "제거할 유저를 입력해주세요.", required=True, name="유저"),
    ):
        await ctx.defer(ephemeral=True)
        if user == self.bot.user or user == ctx.author:
            failEmbed = Embed.cancel(
                description=f"{self.bot.user.mention} 또는 자기 자신은 제거할 수 없어요.",
                timestamp=datetime.datetime.now(),
            )
            Embed.user_footer(failEmbed, ctx.author)
            return await ctx.respond(embed=failEmbed)

        with open("data/voice_channel.json", encoding="UTF8") as f:
            crvoice_data = json.load(f)

        overwriteForUser = ctx.author.voice.channel.overwrites_for(user)
        if not overwriteForUser.connect:
            failEmbed = Embed.cancel(
                description=f"해당 유저({user.mention})는 이 채널에 접근할 수 있는 권한이 없어요.",
                timestamp=datetime.datetime.now(),
            )
            Embed.user_footer(failEmbed, ctx.author)
            return await ctx.respond(embed=failEmbed)
        await ctx.author.voice.channel.set_permissions(user, overwrite=None)
        successEmbed = Embed.default(
            title="✅ 설정 완료",
            description=f"{user}님을 {ctx.author.voice.channel.mention}에서 제거했어요!\n\n📤 이제 해당 채널에 접근할 수 없어요.",
            timestamp=datetime.datetime.now(),
        )
        Embed.user_footer(successEmbed, ctx.author)

        crvoice_data[str(ctx.author.voice.channel.id)]["members"].remove(user.id)

        json.dump(
            crvoice_data, open("data/voice_channel.json", "w", encoding="UTF8")
        )

        await ctx.respond(embed=successEmbed)


def setup(bot):
    bot.add_cog(voice_control(bot))
