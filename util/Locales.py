import aiohttp, requests, re
from discord.ext import commands
from main import langs_cache, db

def get(ctx: commands.Context, cog: str, command: str, key: str):
    lang = db.get(f"{ctx.guild.id}.language", "Guilds") or "en"
    try:
        txt = langs_cache[cog][command][lang][key]#.replace("\\n", "\n")
        print (txt, lang)
        reg = re.findall("@{[^}]+}", str(txt))
        for x in reg:
            txt = txt.replace(x, str(eval(x.strip("@{}"))))#, { "ctx": ctx }))
        return txt or "???"
    except Exception as x:
        print(x)
        return "???"
    
def fetch_langs(bot: commands.Bot):
    for cog in bot.cogs.items():
        for cmd in cog[1].get_commands():
            url = f"https://github.com/Noraa08/Uni-Langs/raw/main/locales/{cog[0].upper()}/{str(cmd).lower()}.json"
            res = requests.get(url)
            if res:
                langs_cache[cog[0]] = {}
                langs_cache[cog[0]][str(cmd)] = res.json()
            else:
                pass