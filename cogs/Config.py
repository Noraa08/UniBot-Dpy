import discord, datetime, contextlib, io, re
from traceback import format_exception
from discord.ext import commands
from main import db, util


class Config(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_group(name="set", aliases=["config"])
    async def _set(self, ctx: commands.Context, opt=None, val=None):
        await ctx.send("...")

    @_set.command(name="prefix")
    async def prefix(self, ctx: commands.Context, prefix: str):
        _prefix = db.get(f"{ctx.guild.id}.prefix", "Guilds") or "?"
        if len(prefix) > 5:
            return await util.throw_error(ctx, "prefix_length")
        if prefix == _prefix:
            return await util.throw_error(ctx, "same_prefix")
        db.set(f"{ctx.guild.id}.prefix", prefix, "Guilds")
        view = discord.ui.View().add_item(
                item=discord.ui.Button(
                    style=discord.ButtonStyle.green,
                    label=f"{util.locale(ctx, 'new')}: {prefix}",
                    disabled=True,
                )
        ).add_item(
                item=discord.ui.Button(
                    style=discord.ButtonStyle.red,
                    label=f"{util.locale(ctx, 'old')}: {_prefix}",
                    disabled=True,
                )
        )
        await util.throw_fine(ctx, "fine_message", view=view)
        
    @_set.command(name="lang", aliases=["language"])
    async def lang(self, ctx: commands.Context, lang: str):
        _lang = db.get(f"{ctx.guild.id}.language", "Guilds") or "en-EN"
        r = lang.lower().split("-")[0]
        if not r in ["es", "en", "pt", "br", "fr"]:
            ctx.langs = " • es-ES\n • en-EN\n • br-PT\n • fr-FR"
            return await util.throw_error(ctx, "invalid_lang")
        if f"{r}-{r.upper()}" == _lang:
            return await util.throw_error(ctx, "same_lang")
        db.set(f"{ctx.guild.id}.language", f"{r}-{r.upper()}", "Guilds")
        view = discord.ui.View().add_item(
                item=discord.ui.Button(
                    style=discord.ButtonStyle.green,
                    label=f"{util.locale(ctx, 'new')}: {r}-{r.upper()}",
                    disabled=True,
                )
            ).add_item(
                item=discord.ui.Button(
                    style=discord.ButtonStyle.red,
                    label=f"{util.locale(ctx, 'old')}: {_lang}",
                    disabled=True,
                )
            )
        await util.throw_fine(ctx, "fine_message", view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(Config(bot))
