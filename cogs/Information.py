import discord, datetime, contextlib, io, re
from traceback import format_exception
from discord.ext import commands
from util import Views, Locales
from cogs.utils.helpers import Helpers

class Information(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.config = bot.config
        self.util = bot.util
        
    @commands.hybrid_group(name="user")
    async def user(self, ctx: commands.Context, user: discord.Member = None) -> None:
       async with ctx.typing():
            user = user or ctx.author
            embed = await Helpers(self.bot).user_info(ctx, user)
            async def run(i: discord.Interaction, user: discord.User, message: discord.Message):
                embed = await Helpers(self.bot).user_info(ctx, user)
                await i.response.edit_message(embed=embed)
            view = Views.UserMenu(ctx)
            view.children[0].placeholder = await Locales.get(ctx, "Other", "user_select_menu", "views")
            view.do_something = run
            view.message = await ctx.send(embed=embed, view=view)
        

    @user.command(name="info", aliases=["whois", "information"])
    async def info(self, ctx: commands.Context, user: discord.Member = None) -> None:
        async with ctx.typing():
            user = user or ctx.author
            embed = await Helpers(self.bot).user_info(ctx, user)
            async def run(i: discord.Interaction, user: discord.User, message: discord.Message):
                embed = await Helpers(self.bot).user_info(ctx, user)
                await i.response.edit_message(embed=embed)
            view = Views.UserMenu(ctx)
            view.children[0].placeholder = await Locales.get(ctx, "Other", "user_select_menu", "views")
            view.do_something = run
            view.message = await ctx.send(embed=embed, view=view)
        
    @user.command(name="avatar", aliases=["av", "pfp"])
    async def avatar(self, ctx: commands.Context, user: discord.User = None) -> None:
        await Helpers(self.bot).avatar(ctx, user)

    # @user.command(name="perms", aliases=["permissions"])
    # async def perms(self, ctx)

async def setup(bot: commands.Bot):
    await bot.add_cog(
        Information(bot)
    )
