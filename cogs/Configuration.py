import discord, datetime, contextlib, io, re
from traceback import format_exception
from discord.ext import commands
from util import Locales

class Configuration(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_group(name="prefix", case_insensitive=True)
    async def prefix(self, ctx: commands.Context, opt=None, val=None):
        """Get prefixes of the guild"""
        prefixes = await self.bot.db.get(ctx.guild.id, "prefixes", "guilds")
        if prefixes:
            _ = []
            for n, x in enumerate(prefixes):
                _.append(f"{n+1}. {x}")
            embed = self.bot.util.Embed(ctx, 
                fields=[
                    { "name": "Prefixes:", "value": f'```{chr(10).join(_)}```' },
                    { "name": "Default:", "value": "```1. uni \n2. @Uni ✨#4378```" }
                ]
            )
            return await ctx.send(embed=embed)
        else: 
            return await ctx.send("No hay prefijos disponibles en el servidor, considera añadir uno usando `uni prefix add <NEW_PREFIX>`")

    @prefix.command(name="add")
    async def p_add(self, ctx: commands.Context, *, prefix: str):
        """Add a prefix to the bot"""
        prefixes = await self.bot.db.get(ctx.guild.id, "prefixes", "guilds")
        
        if prefixes.find(lambda x: x == prefix):
            return await Locales.send(ctx, "Configuration", "prefix_add", "prefix_exists", like="error", prefix=prefix)
        if len(prefix) >= 4:
            return await Locales.send(ctx, "Configuration", "prefix_add", "length_limit", like="error", prefix=prefix)
            
        prefixes.append(prefix)
        print (1, prefixes)
        await self.bot.db.set(ctx.guild.id, "prefixes", prefixes, "guilds")

        await Locales.send(ctx, "Configuration", "prefix_add", "fine_message", prefix=prefix)

    @prefix.command(name="remove", aliases=["delete", "del"])
    async def p_remove(self, ctx: commands.Context, *, prefix: str):
        """Remove a prefix to the bot"""
        _prefix = list((await self.bot.pool.fetchrow("SELECT prefixes from guilds where id=$1", ctx.guild.id))["prefixes"])
        if not prefix in _prefix:
            return await ctx.send("no existe bb")
        _prefix.remove(prefix)
        await self.bot.pool.execute("UPDATE guilds SET prefixes = $1 WHERE id=$2", _prefix, ctx.guild.id)
        await ctx.send(f"{_prefix}")
        #await util.throw_fine(ctx, "fine_message", view=view)
    

    """
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
    """

async def setup(bot: commands.Bot):
    await bot.add_cog(
        Configuration(bot)
    )
