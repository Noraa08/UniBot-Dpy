import discord, datetime, contextlib, io, re
from traceback import format_exception
from discord.ext import commands
from main import db, util
from util import ext, views
from cogs.Util import Util

class Info(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_group(name="user")
    async def user(self, ctx: commands.Context, user: discord.Member = None) -> None:
       await self.info(ctx, user)

    @user.command(name="info", aliases=["whois", "information"])
    async def info(self, ctx: commands.Context, user: discord.Member = None) -> None:
        if not user:
            user = ctx.author
        guild = self.bot.get_guild(ctx.guild.id)
        embed = discord.Embed(
            title=util.locale(ctx, "embed_title", cmd="info"),
            color=await util.image_color(user.display_avatar.url)
        )
        embed.set_footer(text=f"{util.footer}", icon_url=util.footer_icon)
        embed.set_author(name=f"{user}", icon_url=user.display_avatar.url, url=f"https://discord.com/users/{user.id}")
        desc = util.locale(ctx, "embed_description", cmd="info")
        desc = desc.replace("{user_nick}", f"{util.locale(ctx, 'nickname', cmd='info')} {user.nick}" if user.nick else "").replace("{user_name}", f"{user}").replace("{user_id}", f"`{user.id}`").replace("{user_color}", f"`{str(user.color).replace('#0000000', '#95a5a6')}`")
        embed.description = desc
        embed.set_thumbnail(url=user.display_avatar)
        embed.add_field(
            name=util.locale(ctx, "embed_field_created", cmd="info"),
            value=f"_ _ <t:{round(user.created_at.timestamp())}>"
        )
        if guild.get_member(user.id):
            embed.add_field(
                name=util.locale(ctx, "embed_field_joined", cmd="info"),
                value=f"_ _ <t:{round(user.joined_at.timestamp())}>"
            )
        embed.add_field(
            name=util.locale(ctx, "embed_field_roles", cmd="info"),
            value= ", ".join(reversed([r.mention for r in user.roles]))
        )
        async def run(i: discord.Interaction, user: discord.User, message: discord.Message):
            embed.color = await util.image_color(user.display_avatar.url)
            embed.set_author(name=f"{user}", icon_url=user.display_avatar.url, url=f"https://discord.com/users/{user.id}")
            desc = util.locale(ctx, "embed_description", cmd="info")
            desc = desc.replace("{user_nick}", f"{util.locale(ctx, 'nickname', cmd='info')} {user.nick}" if user.nick else "").replace("{user_name}", f"{user}").replace("{user_id}", f"`{user.id}`").replace("{user_color}", f"`{str(user.color).replace('#0000000', '#95a5a6')}`")
            embed.description = desc
            embed.set_thumbnail(url=user.display_avatar)
            embed.fields[0].value = f"_ _ <t:{round(user.created_at.timestamp())}>"
            embed.fields[1].value = f"_ _ <t:{round(user.joined_at.timestamp())}>"
            embed.fields[2].value = ", ".join(reversed([r.mention for r in user.roles]))
            await i.response.edit_message(embed=embed)
        view = views.UserMenu(ctx)
        view.children[0].placeholder = util.locale(ctx, "user_select_menu", type="Interactions")
        view.do_something = run
        view.message = await ctx.send(embed=embed, view=view)
        
    @user.command(name="avatar", aliases=["av", "pfp"])
    async def avatar(self, ctx: commands.Context, user: discord.User = None) -> None:
        await Util.avatar(self, ctx, user)

    # @user.command(name="perms", aliases=["permissions"])
    # async def perms(self, ctx)

async def setup(bot: commands.Bot):
    await bot.add_cog(Info(bot))
