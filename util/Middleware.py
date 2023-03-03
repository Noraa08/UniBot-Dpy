from urllib.request import urlopen
from discord.ext import commands
from typing import Literal, List
from random import choice
from time import sleep
from fishhook import hook, orig
from logging.handlers import RotatingFileHandler
import re, discord, requests, ast, configparser, aiohttp, builtins, pydash as _, json, logging, contextlib, datetime


@hook(list)
def find(self, fn):
    """FIND HOOK"""
    for element in self:
        if fn(element):
            return element
    return None

class Util:
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    def Embed(self, ctx: commands.Context, **kwargs):
        if not "color" in kwargs:
            kwargs["color"] = 0x303136
        if not "footer" in kwargs:
            kwargs["footer"] = { "text": self.bot.config.footer, "icon_url": self.bot.config.footer_icon }
        if not "author" in kwargs:
            kwargs["author"] = { "name": str(ctx.author), "icon_url": ctx.author.display_avatar.url }
        kwargs["timestamp"] = datetime.datetime.now().astimezone(tz=datetime.timezone.utc).isoformat()
        embed = discord.Embed().from_dict(kwargs)
        return embed
        
    def set_lines(self, x: str):
        """Set formatted lines to a string"""
        i = 1
        lines = []
        for line in x.strip().split("\n"):
            lines.append(f"{str(i).zfill(3)} | {line}")
            i += 1
        return "\n".join(lines)
    
    # ---> REQUEST
    async def request(self, *, url: str, params: dict = {}, extract: Literal["json", "read", "text"] = "json", as_dict=False):
        try:
            async with self.bot.session as session:
                async with session.get(url=url, params=params) as res:
                    if res.status != 200 and res.status != 201:
                        return 10
                    if extract.lower() == "json":
                        return (
                            Response(await res.json(), res.status, res.content_type)
                            if as_dict
                            else await res.json()
                        )
                    elif extract.lower() == "read":
                        return (
                            Response(await res.read(), res.status, res.content_type)
                            if as_dict
                            else await res.read()
                        )
                    elif extract.lower() == "text":
                        return (
                            Response(await res.text(), res.status, res.content_type)
                            if as_dict
                            else await res.text()
                        )
        except:
            pass
    
    async def image_color(self, image):
        res = await self.request(
            url=f"https://api.munlai.fun/json/dominant?image={image}",
        )
        return int(res["data"]["dominant"]["hex"].strip("#"), 16)


class RemoveNoise(logging.Filter):
    def __init__(self):
        super().__init__(name='discord.state')

    def filter(self, record: logging.LogRecord) -> bool:
        if record.levelname == 'WARNING' and 'referencing an unknown' in record.msg:
            return False
        return True

@contextlib.contextmanager
def setup_logging():
    log = logging.getLogger()

    try:
        discord.utils.setup_logging()
        # __enter__
        max_bytes = 32 * 1024 * 1024  # 32 MiB
        logging.getLogger('discord').setLevel(logging.INFO)
        logging.getLogger('discord.http').setLevel(logging.WARNING)
        logging.getLogger('discord.state').addFilter(RemoveNoise())

        log.setLevel(logging.INFO)
        handler = RotatingFileHandler(filename='uni.log', encoding='utf-8', mode='w', maxBytes=max_bytes, backupCount=5)
        dt_fmt = '%Y-%m-%d %H:%M:%S'
        fmt = logging.Formatter('[{asctime}] [{levelname:<7}] {name}: {message}', dt_fmt, style='{')
        handler.setFormatter(fmt)
        log.addHandler(handler)

        yield
    finally:
        # __exit__
        handlers = log.handlers[:]
        for hdlr in handlers:
            hdlr.close()
            log.removeHandler(hdlr)
            