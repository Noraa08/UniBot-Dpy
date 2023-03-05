from urllib.request import urlopen
from discord.ext import commands
from datetime import datetime
from termcolor import colored
from typing import Literal
from util import Locales
import discord
    
class Listeners(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        await Locales.fetch_langs(self.bot)
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
            return await util.throw_error(ctx, "Others", "errors", "user_not_found")
        elif isinstance(error, commands.UserNotFound):
            return await util.throw_error(ctx, "Others", "errors", "user_not_found", errors=True)
        elif isinstance(error, commands.MissingRequiredArgument):
            return await util.throw_error(ctx, "Others", "errors", "arg_not_found", arg=error.param.name)
        elif isinstance(error, commands.NotOwner):
            return await util.throw_error(ctx, "Others", "errors", "not_owner")
        elif isinstance(error, commands.MissingPermissions):
            return await util.throw_error(ctx, "Others", "errors", "missing_perms", bold=False, name=ctx.author.name)
        raise error
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """
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
        """
    
async def setup(bot):
    await bot.add_cog(Listeners(bot))
