import aiohttp, requests, re
from discord.ext import commands
from main import langs_cache
from random import choice 

async def get(
    ctx: commands.Context,
    key: str,
    *,
    cog: str = None, 
    command: str = None, 
    **kwargs):
    lang = langs_cache[str(ctx.guild.id)]["lang"] or "es"
    try:
        txt = langs_cache[cog][command][lang][key]
        for x, y in kwargs.items():
           txt = txt.replace(f"@{x}", y)
           return txt or key
    except Exception as x:
        print(x)
        return key
    
async def fetch_langs(bot: commands.Bot):
    for cog_name, cog in bot.cogs.items():
        for cmd in cog.__cog_commands__:
            cmd_name = str(cmd.qualified_name).replace(' ', '_').lower()
            url = f"https://github.com/Noraa08/UniBot-Dpy/raw/locales/locales/{cog_name}/{cmd_name}.json"
            res = requests.get(url)
            if res:
                langs_cache[cog_name] = {}
                langs_cache[cog_name][cmd_name] = res.json()
            else:
                pass
    for guild in bot.guilds:
        lang = await bot.db.get(guild.id, "language", "guilds")
        langs_cache[str(guild.id)] = {} 
        langs_cache[str(guild.id)]["lang"] = lang

async def send(
        ctx: commands.Context,
        cog: str,
        command: str,
        key: str,
        like: str = "Fine",
        defer: bool = False,
        bold: bool = True,
        view=None,
        emoji: bool = True,
        **kwargs
    ):
    try:
        emojis = choice(ctx.bot.config.fine_emojis if like.lower() == "fine" else ctx.bot.config.error_emojis)
        text = (await get(ctx, cog, command, key, **kwargs)).replace("@emoji", emojis)
        res = f"{f'**{text}**' if bold else text} {(emojis if emojis else '') if not emojis in text else ''}"
        like = "<:eg_right:1029412506743091280>" if like.lower() == "fine" else "<:eg_wrong:1029412572899836055>"
        m = await ctx.send(
            f"_ _ {like} {res}"
        )
        if defer:
            sleep(7)
            m.delete()
    except Exception as e:
        print(e)


async def send_error(
        ctx: commands.Context,
        cog: str,
        command: str,
        key: str,
        defer: bool = False,
        bold: bool = True,
        view=None,
        emoji: bool = True,
        **kwargs
    ):
    try:
        emojis = choice(ctx.bot.config.fine_emojis)
        text = (await get(ctx, cog, command, key, **kwargs)).replace("@emoji", emojis)
        res = f"{f'**{text}**' if bold else text} {(emojis if emojis else '') if not emojis in text else ''}"
        m = await ctx.send(
            f"_ _ <:eg_right:1029412506743091280> {res}")
        if defer:
            sleep(7)
            m.delete()
    except Exception as e:
        print(e)
    