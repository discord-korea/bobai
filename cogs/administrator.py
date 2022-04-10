import asyncio
import datetime
import logging

import discord
from discord.commands import slash_command
from discord.ext import bridge, commands

import config
from utils.database import *
from utils.embed import Embed


class administrator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(config.setting.log.name)

    @bridge.bridge_command(
        name="활성화",
        description="[🔒 '서버 관리자' 전용] 뽀빠이 서비스를 이 서버에서 활성화해요.",
    )
    @commands.has_permissions(administrator=True)
    @commands.max_concurrency(1, commands.BucketType.guild)
    @commands.guild_only()
    async def server_enable(self, ctx):
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

        async def check_for_msg(inter):
            if (inter.user.id == ctx.author.id and inter.message.id == msg.id) is False:
                await inter.followup.send(
                    f"{inter.user.mention}, 이 버튼은 명령어를 사용하신 유저만 누를 수 있어요.",
                    ephemeral=True,
                )
                return

        def check(inter):
            if (inter.user.id == ctx.author.id and inter.message.id == msg.id) is False:
                asyncio.create_task(check_for_msg(inter))
                return False
            else:
                return True

        try:
            interaction_check = await self.bot.wait_for(
                "interaction", check=check, timeout=60.0
            )
        except asyncio.TimeoutError:
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

        if interaction_check.custom_id == "cancel":
            embed = Embed.cancel(
                timestamp=datetime.datetime.now(),
                description="``취소`` 버튼을 누르셔서 활성화를 취소하였어요.",
            )
            Embed.user_footer(embed, ctx.author)
            return await msg.edit(embed=embed, view=None)

        elif interaction_check.custom_id == "confirm":
            await GUILD_DB.guild_add(ctx.guild.id)
            embed = Embed.default(
                timestamp=datetime.datetime.now(),
                title="<:check:962331111302774824> 서버 활성화 완료",
                description=f"``{ctx.guild.name}`` 서버에서 ``{self.bot.user.name}`` 서비스가 활성화되었어요.\n\n>>> ⚠ 이용약관 및 개인정보처리방침에 동의하시지 않는 경우, ``/비활성화`` 명령어로 서비스 사용을 중단할 수 있어요.\n**🚧 비활성화를 진행하면, ``{ctx.guild.name}`` 서버에서 봇을 사용할 수 없게 돼요.**",
            )
            Embed.user_footer(embed, ctx.author)
            return await msg.edit(embed=embed, view=None)


def setup(bot):
    bot.add_cog(administrator(bot))
