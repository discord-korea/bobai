import datetime
import logging

import discord
from discord.commands import slash_command
from discord.ext import commands

import config
from utils.embed import Embed


class core(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(config.setting.log.name)

    @commands.slash_command(
        name="정보",
        description="'뽀빠이' 봇의 정보를 확인해보세요!",
    )
    async def info(self, ctx):
        await ctx.defer()

        embed = Embed.default(
            title=f"{self.bot.user.name} 정보",
            timestamp=datetime.datetime.now(),
        )
        embed.add_field(
            name="출시일",
            value=f"<t:{str(self.bot.user.created_at.timestamp()).split('.')[0]}> (<t:{str(self.bot.user.created_at.timestamp()).split('.')[0]}:R>)",
        )
        embed.add_field(
            name="핑 (지연 시간)",
            value=f"``{round(self.bot.latency * 1000)}ms``",
            inline=False,
        )
        embed.add_field(name="서버 수", value=f"``{format(len(self.bot.guilds), ',')}개``")
        embed.add_field(name="개발 팀", value=f"``삼해트의 공방``")
        embed.set_thumbnail(url=self.bot.user.display_avatar)
        embed.set_footer(text=self.bot.user, icon_url=self.bot.user.display_avatar)

        view = discord.ui.View()
        view.add_item(
            discord.ui.Button(
                label="서포트 서버",
                emoji="<:discord_blurple:858642003327057930>",
                style=discord.ButtonStyle.link,
                url="https://discord.gg/TD9BvMxhP6",
            )
        )
        view.add_item(
            discord.ui.Button(
                label="오픈소스",
                emoji="<:github:855596917358592020>",
                style=discord.ButtonStyle.link,
                url="https://github.com/discord-korea/bobai",
            )
        )
        await ctx.respond(embed=embed, view=view)


def setup(bot):
    bot.add_cog(core(bot))
