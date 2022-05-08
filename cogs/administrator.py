import asyncio
import datetime
import logging

import discord
from discord.commands import slash_command, SlashCommandGroup
from discord.ext import commands

import config
from utils.database import *
from utils.embed import Embed
from utils.tool import CheckTool


class administrator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(config.setting.log.name)

    # ==========================================================

    """
    서버 활성화 여부를 확인하는 코드입니다.
    """
    async def is_server_enabled(self):
        if not await GUILD_DB.guild_search(self.guild.id):
            embed = Embed.cancel(
                timestamp=datetime.datetime.now(),
                description="데이터베이스에 서버가 등록되어 있지 않아요.\n\n> 🌈 ``/활성화`` 명령어로 서버를 활성화하실 수 있어요. ",
            )
            Embed.user_footer(embed, self.author)
            await self.respond(embed=embed)
            return False
        else:
            return True


    # ==========================================================

    @commands.slash_command(
        name="활성화",
        description="[🔒 '서버 관리자' 전용] 뽀빠이 서비스를 이 서버에서 활성화해요.",
    )
    @commands.has_permissions(administrator=True)
    @commands.max_concurrency(1, commands.BucketType.guild)
    @commands.guild_only()
    async def server_enabled(self, ctx):
        await ctx.defer()

        if await GUILD_DB.guild_search(ctx.guild.id):
            embed = Embed.cancel(
                timestamp=datetime.datetime.now(),
                description="이미 데이터베이스에 서버가 등록되어 있어요.",
            )
            Embed.user_footer(embed, ctx.author)
            return await ctx.respond(embed=embed)

        check_embed = Embed.default(
            timestamp=datetime.datetime.now(),
            title="🔓 시스템 활성화",
            description=f"``{ctx.guild.name}`` 서버에서 ``{self.bot.user.name}`` 서비스를 활성화할까요?\n\n> **⚠ 활성화를 진행할 시, __서비스 이용약관 및 개인정보 처리방침에 동의__한 것으로 간주해요.**",
        )
        check_embed.add_field(
            name="문서",
            value=f">>> ~~<:documents:855596917131051018> 서비스 이용약관\n<:documents:855596917131051018> 개인정보 처리방침~~",
        )
        Embed.user_footer(check_embed, ctx.author)

        view = discord.ui.View()
        view.add_item(
            discord.ui.Button(
                label="확인",
                emoji="<:check:962331111302774824>",
                style=discord.ButtonStyle.green,
                custom_id="confirm",
            )
        )
        view.add_item(
            discord.ui.Button(
                label="취소",
                emoji="<:cancel:962331128604291072>",
                style=discord.ButtonStyle.red,
                custom_id="cancel",
            )
        )
        msg = await ctx.respond(embed=check_embed, view=view)

        result = await CheckTool.button_check(ctx, msg)

        if result is None:
            embed = Embed.cancel(
                timestamp=datetime.datetime.now(),
                description="제한시간이 초과되어 취소되었어요.",
            )
            Embed.user_footer(embed, ctx.author)
            try:
                return await msg.edit(
                    content=None,
                    embed=embed,
                    view=None,
                )
            except:
                return

        if result.custom_id == "cancel":
            embed = Embed.cancel(
                timestamp=datetime.datetime.now(),
                description="``취소`` 버튼을 누르셔서 활성화를 취소하였어요.",
            )
            Embed.user_footer(embed, ctx.author)
            return await msg.edit(embed=embed, view=None)

        elif result.custom_id == "confirm":
            await GUILD_DB.guild_add(ctx.guild.id)
            embed = Embed.default(
                timestamp=datetime.datetime.now(),
                title="<:check:962331111302774824> 서버 활성화 완료",
                description=f"``{ctx.guild.name}`` 서버에서 ``{self.bot.user.name}`` 서비스가 활성화되었어요.\n\n>>> ⚠ 이용약관 및 개인정보처리방침에 동의하시지 않는 경우, ``/비활성화`` 명령어로 서비스 사용을 중단할 수 있어요.\n**🚧 비활성화를 진행할 시, ``{ctx.guild.name}`` 서버에서 봇을 사용할 수 없게 돼요.**",
            )
            Embed.user_footer(embed, ctx.author)
            return await msg.edit(embed=embed, view=None)

    @commands.slash_command(
        name="비활성화",
        description="[🔒 '서버 관리자' 전용] 뽀빠이 서비스를 이 서버에서 비활성화해요.",
        checks=[is_server_enabled],
    )
    @commands.has_permissions(administrator=True)
    @commands.max_concurrency(1, commands.BucketType.guild)
    @commands.guild_only()
    async def server_disabled(self, ctx):
        await ctx.defer()

        check_embed = Embed.default(
            timestamp=datetime.datetime.now(),
            title="🔓 시스템 비활성화",
            description=f"``{ctx.guild.name}`` 서버에서 ``{self.bot.user.name}`` 서비스를 비활성화할까요?\n\n> **⚠ 비활성화를 진행할 시, ``{ctx.guild.name}`` 서버에 설정된 모든 데이터는 삭제되고, 봇을 사용할 수 없게 돼요.**",
        )
        Embed.user_footer(check_embed, ctx.author)

        view = discord.ui.View()
        view.add_item(
            discord.ui.Button(
                label="확인",
                emoji="<:check:962331111302774824>",
                style=discord.ButtonStyle.green,
                custom_id="confirm",
            )
        )
        view.add_item(
            discord.ui.Button(
                label="취소",
                emoji="<:cancel:962331128604291072>",
                style=discord.ButtonStyle.red,
                custom_id="cancel",
            )
        )
        msg = await ctx.respond(embed=check_embed, view=view)

        result = await CheckTool.button_check(ctx, msg)

        if result is None:
            embed = Embed.cancel(
                timestamp=datetime.datetime.now(),
                description="제한시간이 초과되어 취소되었어요.",
            )
            Embed.user_footer(embed, ctx.author)
            try:
                return await msg.edit(
                    content=None,
                    embed=embed,
                    view=None,
                )
            except:
                return

        if result.custom_id == "cancel":
            embed = Embed.cancel(
                timestamp=datetime.datetime.now(),
                description="``취소`` 버튼을 누르셔서 비활성화를 취소하였어요.",
            )
            Embed.user_footer(embed, ctx.author)
            return await msg.edit(embed=embed, view=None)

        elif result.custom_id == "confirm":
            await GUILD_DB.guild_remove(ctx.guild.id)
            embed = Embed.default(
                timestamp=datetime.datetime.now(),
                title="<:check:962331111302774824> 서버 비활성화 완료",
                description=f"``{ctx.guild.name}`` 서버에서 ``{self.bot.user.name}`` 서비스가 비활성화되었어요.\n\n>>> 👋 ``{ctx.guild.name}`` 서버에서 서비스를 사용해 주셔서 감사했어요. 마음이 바뀌신다면 ``/활성화`` 명령어를 사용하셔서 다시 사용해주실 수 있어요.",
            )
            Embed.user_footer(embed, ctx.author)
            return await msg.edit(embed=embed, view=None)

    # ==========================================================

    voice_create = SlashCommandGroup("생성기", "음성 채널 생성기 기능이에요.")

    @voice_create.command(name="리스트", description="[🔒 '서버 관리자' 전용] 서버에서 활성화된 '음챗 생성기' 목록을 확인해요.", checks=[is_server_enabled])
    @commands.has_permissions(manage_guild=True)
    @commands.max_concurrency(1, commands.BucketType.guild)
    @commands.guild_only()
    async def voice_create_list(self, ctx):
        data = (await GUILD_DB.guild_search(ctx.guild.id))["generator_channel"]
        embed = Embed.default(title=f"📃 {ctx.guild.name} 음성 생성기 목록", description=f"현재 총 ``{len(data)}개``의 음성 생성기가 등록되어 있어요.")
        Embed.user_footer(embed, ctx.author)
        for voice in data:
            voice_channel = self.bot.get_channel(int(voice))
            if voice_channel:
                embed.add_field(name=voice_channel.name, value=f">>> 생성 채널 : {voice_channel.mention}\n생성될 채널 이름 : ``{data[voice]['name']}``", inline=False)
            else:
                embed.add_field(name="조회 불가", value=f"해당 채널은 조회할 수 없어요. 삭제 후 재등록이 필요해요.", inline=False)

        await ctx.respond(embed=embed)


    #user_perm = voice_control.create_subgroup("유저", "음챗의 유저 권한 관리 기능이에요.")

def setup(bot):
    bot.add_cog(administrator(bot))
