from urllib.request import urlopen
import re, discord, requests, ast, configparser, aiohttp, builtins, pydash as _, json
from discord.ext import commands
from typing import Literal, List
from random import choice
from time import sleep
from fishhook import hook, orig

@hook(list)
def find(self, fn):
    for element in self:
        if fn(element):
            return element
    return None

class Util:
    def __init__(self, bot: commands.Bot, db) -> None:
        self.bot = bot
        self.db = db
    
    # ---> THROW_ERROR
    async def throw_error(
        self,
        ctx: commands.Context,
        property: str,
        error: bool = False,
        defer: bool = False,
        bold: bool = True,
        view=None,
        emoji: bool = True,
        type: str = None
    ):
        try:
            emojis = choice(self.bot.config["ERROR_EMOJIS"])
            text = (self.locale(ctx, property, type="Errors" if error else None) if property else text).replace("$(emoji)", emojis)
            res = f"{f'**{text}**' if bold else text} {(emojis if emojis else '') if not emojis in text else ''}"
            m = await ctx.send(
                f"_ _ <:eg_wrong:1029412572899836055> {res}")
            if defer:
                sleep(7)
                m.delete()
        except Exception as e:
            print(e)
    
    # ---> THROW_SUCCESS
    async def throw_fine(
        self,
        context: commands.Context,
        property: str,
        defer: bool = False,
        bold: bool = True,
        view=None,
        emoji: bool = True,
        send: bool = False
    ):
        try:
            text = self.locale(context, property) if property else text 
            emojis = choice(self.bot.config["FINE_EMOJIS"])
            res = f"{f'**{text}**' if bold else text} {emojis}" if emoji else f'**{text}**' if bold else text
            msg = f"_ _ <:eg_right:1029412506743091280> {res}"
            if send:
                return msg
            else:
                m = await context.send(
                    msg,
                    view=view
                )
                if defer:
                    sleep(7)
                    m.delete()
        except:
            pass
    
    # ---> SET_LINES
    def set_lines(self, x: str):
        i = 1
        lines = []
        for line in x.strip().split("\n"):
            lines.append(f"{str(i).zfill(3)} | {line}")
            i = i + 1
        return "\n".join(lines)
    
    
    # ---> LANG	
    async def locale(self, ctx: commands.Context, property: str, cog: str = None, cmd: str = None, type: Literal[None, "Interactions", "Errors"] = None):        
        """
        config = configparser.ConfigParser()
        lang = self.db.get(f"{ctx.guild.id if ctx else id}.language", "Guilds") or "en-EN"
        if type:
            config.read(f"./locales/Other/{type}.properties") 
        else:
            config.read(f'./locales/{cog or str(ctx.cog).split(".")[2].split(" ")[0]}/{cmd or ctx.command.name}.properties')
        try:
            txt = config.get(lang, property).replace("\\n", "\n")
            reg = re.findall("@{[^}]+}", str(txt))
            for x in reg:
                txt = txt.replace(x, str(eval(x.strip("@{}"))))#, { "ctx": ctx }))
            return txt
        except Exception as x:
            print(x)
            return "Error :/"
        """
        
    # ---> REQUEST
    async def request(self, *, url: str, params: dict = {}, extract: Literal["json", "read", "text"] = "json", as_dict=False):
        try:
            async with aiohttp.ClientSession() as session:
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
    
    def find(self, pred, iterable):
        for element in iterable:
            if pred(element):
                return element
        return None
