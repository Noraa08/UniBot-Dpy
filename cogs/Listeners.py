from urllib.request import urlopen
from discord.ext import commands
from datetime import datetime
from termcolor import colored
from typing import Literal
from main import util, db, langs_cache
from util import Locales
import discord

#langs = langs.Langs()
    
class Listeners(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(
            "Logged in as",
            colored(self.bot.user.name.replace("✨", ""), "blue", attrs=["blink"]),
        )
        # ---> UTIL VARS <---
        util.uptime = datetime.now()
        util.color = 0x202126
        util.footer = "© Uni"
        util.footer_icon = "https://media.discordapp.net/attachments/1041171337978335332/1057178574047686657/Picsart_22-12-27_03-10-01-878.jpg"
        Locales.fetch_langs(self.bot)
        print(langs_cache)
        await self.bot.tree.sync()
    
    @commands.Cog.listener()
    async def on_disconnect(self):
        if not self.bot.ws or self.bot.is_ws_ratelimited():
            request.urlopen(
                f"https://cd594a2f-0e9f-48f1-b3eb-e7f6e8665adf.id.repl.co/{os.environ['REPL_ID']}"
            )
            os.kill(1, 1)
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.MemberNotFound):
            return await util.throw_error(ctx, "user_not_found")
        elif isinstance(error, commands.UserNotFound):
            return await util.throw_error(ctx, "user_not_found", errors=True)
        elif isinstance(error, commands.MissingRequiredArgument):
            ctx.arg = error.param.name
            return await util.throw_error(ctx, "arg_not_found", error=True)
        elif isinstance(error, commands.NotOwner):
            return await util.throw_error(ctx, "not_owner", errors=True)
        elif isinstance(error, commands.MissingPermissions):
            return await util.throw_error(
                ctx,
                es="..",
                en=f"**{ctx.author.name}**, you **don't** have permissions enough to use this command",
                pt="..",
                fr="..",
                bold=False,
            )
        raise error
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        prefix = db.get(f"{message.guild.id}.prefix", "Guilds") or "?"
        if not message.content.startswith(prefix) or message.author.bot:
            return
        else:
            name = message.content[len(prefix) :].strip().split(" ")[0]
            cmds = db.get(f"{message.guild.id}.commands", "Guilds") or []
            found = next((item for item in cmds if item["name"] == name.lower()), None)
            if not found:
                return
            await message.channel.send(found["content"])
    
    
async def setup(bot):
    await bot.add_cog(Listeners(bot))
