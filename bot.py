import datetime
import logging
import os

import discord
import jishaku
from discord.ext import bridge

import config

bot = bridge.AutoShardedBot(
    command_prefix=(config.bot.prefix if not config.test_mode else config.tbot.prefix),
    intents=discord.Intents.all(),
    owner_ids=config.setting.dev_ids,
    help_command=None,
    allowed_mentions=discord.AllowedMentions(replied_user=False),
)

now = datetime.datetime.now()
logger = logging.getLogger(config.setting.log.name)
logger.setLevel("INFO")
stream = logging.StreamHandler()
handler = logging.FileHandler(
    filename=f"logs/{datetime.datetime.now().strftime('%Y%m%d%H%M')}.log",
    encoding="utf-8",
    mode="w",
)
formatter = logging.Formatter("[%(asctime)s] (%(levelname)s) %(message)s")
handler.setFormatter(formatter)
stream.setFormatter(formatter)
logger.addHandler(handler)
logger.addHandler(stream)

logger.info(
    f"📡 | 봇 익스텐션을 로드합니다. (모드 : {'정식 모드' if not config.test_mode else '테스트 모드'})"
)

cogs = sorted([i.replace(".py", "") for i in os.listdir("./cogs") if i.endswith(".py")])

bot.load_extension("jishaku")
logger.info(f"✅ | jishaku 로드 성공")

for i in cogs:
    try:
        bot.load_extension(f"cogs.{i}")
        logger.info(f"✅ | cogs.{i} 로드 성공")
    except Exception as error:
        logger.error(f"❎ | cogs.{i} 로드 실패 {error}")

bot.run(config.bot.token if not config.test_mode else config.tbot.token)
