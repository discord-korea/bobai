import config
import discord
from discord.ext import commands

bot = commands.AutoShardedBot(
    command_prefix=(config.bot.prefix if not config.test_mode else config.tbot.prefix),
    intents=discord.Intents.all(),
    owner_ids=config.setting.dev_ids,
    help_command=None,
)

bot.run(config.bot.token if not config.test_mode else config.tbot.token)
