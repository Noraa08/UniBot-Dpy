import discord, datetime, contextlib, io, re
from traceback import format_exception
from discord.ext import commands
from main import db, util, cmds
from util import ext, views
from deep_translator import GoogleTranslator
from langdetect import detect, DetectorFactory
DetectorFactory.seed = 0

class Util(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

	# ----> AVATAR <----
    @commands.command(name="avatar", aliases=["av", "pfp"])
    async def avatar(self, ctx: commands.Context, user: discord.Member = None):
        await cmds.Avatar(ctx, user)

    @commands.hybrid_command(name="translate", aliases=["tr"])
    async def translate(self, ctx: commands.Context, target: str = "en", *, text: str = None):
        async with ctx.typing():
            _ = ctx.message
            t = GoogleTranslator(source='auto', target=target)
            if _.reference:
                res = t.translate(_.reference.resolved.content)
                lang = detect(_.reference.resolved.content)
            else:
                res = t.translate(text)
                lang = detect(text)
            await ctx.send(f"_ _    **{lang}** to **{target.upper()}**\n{res}")

async def setup(bot: commands.Bot):
    await bot.add_cog(Util(bot))
