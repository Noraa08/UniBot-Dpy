import discord, datetime, contextlib, io, re
from traceback import format_exception
from discord.ext import commands
from main import db, util, cmds
from util import ext, views


class Util(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

	# ----> AVATAR <----
    @commands.command(name="avatar", aliases=["av", "pfp"])
    async def avatar(self, ctx: commands.Context, user: discord.Member = None):
        await cmds.Avatar(ctx, user)

async def setup(bot: commands.Bot):
    await bot.add_cog(Util(bot))
