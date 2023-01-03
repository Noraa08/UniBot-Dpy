from urllib.request import urlopen
import re, discord, requests, ast, configparser, aiohttp 
from discord.ext import commands
from typing import Literal
from random import choice
from time import sleep

class Util:
    def __init__(self, bot: commands.Bot, db) -> None:
        self.bot = bot
        self.db = db

    # ---> THROW_ERROR
    async def throw_error(self, ctx: commands.Context, property: str, options: dict = { "defer": False, "bold": True, "emoji": True }):
        try:
            text = self.locale(ctx, property, type="Errors")
            emojis = choice(
                [
                    "<:c_F:1035381195493621821>",
                    "<:c_afraid:1035381279186759690>",
                    "<:c_angry:1035381295490015243>",
                    "<:c_bored:1035381312170770502>",
                    "<:c_coffee:1035381228347609150>",
                    "<:c_cry:1035381211629105232>",
                    "<:c_no_more:1035381262199824424>",
                ]
            )
            m = await ctx.send(
                f"_ _ <:eg_wrong:1029412572899836055> {f'**{text}**' if options['bold'] else text} {emojis}" if options["emoji"] else text
            )
            if options["defer"]:
                sleep(7)
                m.delete()
        except:
            pass

    # ---> THROW_SUCCESS
    async def throw_fine(
        self,
        context: commands.Context,
        es: str,
        en: str,
        pt: str,
        fr: str,
        defer: bool = False,
        bold: bool = True,
        view=None,
        emoji: bool = True,
    ):
        try:
            text = self.lang(context, es, en, pt, fr)
            emojis = choice(
                [
                    "<:c_PumpkinHeart:1035380868644089966>",
                    "<:c_lof:1035380885375164518>",
                    "<:c_pat_:1035380935492915230>",
                    "<:c_ok:1035380901959446568>",
                    "<:c_sunglasses:1035380918422085692>",
                ]
            )
            m = await context.send(
                f"_ _ <:eg_right:1029412506743091280> {f'**{text}**' if bold else text} {emojis}"
                if emoji
                else text,
                view=view,
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
    def locale(self, ctx: commands.Context, property: str, cog: str = None, cmd: str = None, type: Literal[None, "Interactions", "Errors"] = None):        
        config = configparser.ConfigParser()
        lang = self.db.get(f"{ctx.guild.id if ctx else id}.language") or "en-EN"
        if type:
            config.read(f"./locales/Other/{type}.properties") 
        else:
            config.read(f'./locales/{cog or str(ctx.cog).split(".")[2].split(" ")[0]}/{cmd or ctx.command.name}.properties')
        try:
            txt = config.get(lang, property).replace("\\n", "\n")
            reg = re.findall("@{.+}", str(txt))
            for x in reg:
                txt = txt.replace(x, eval(x.strip("@{}")))
            return txt
        except:
            return "Error :/"

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
            url="https://api.sightengine.com/1.0/check.json",
            params={
                'url': image,
                'models': 'properties',
                'api_user': '74650740',
                'api_secret': 'fGYAQiiphAWG4ijXCbf3'
            }
        )
        return int(res["colors"]["dominant"]["hex"].strip("#"), 16)
