import discord, datetime
from discord.ext import commands
from util import views

class Helpers():
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def Avatar(self, ctx: commands.Context, user: discord.Member = None):
        user = user if user else ctx.author
        embed = discord.Embed(colour=await self.bot.util.image_color(user.display_avatar.url), title=self.bot.util.locale(ctx, "embed_title", cog="Util", cmd="avatar"), url=user.display_avatar.url, timestamp=datetime.datetime.now(),)
        embed.set_author(name=f"{user}", icon_url=user.display_avatar.url, url=f"https://discord.com/users/{user.id}")
        embed.set_image(url=user.display_avatar)
        embed.set_footer(text=f"{self.bot.util.footer}", icon_url=self.bot.util.footer_icon)
        ctx.config = self.bot.config
        ctx.util = self.bot.util   
        view = views.UserMenu(ctx)
        view.children[0].placeholder = self.bot.util.locale(ctx, "user_select_menu", type="Interactions")
        async def run(i: discord.Interaction, user: discord.User, message: discord.Message):
            embed.color = await self.bot.util.image_color(user.display_avatar.url)
            embed.set_author(name=f"{user}", icon_url=user.display_avatar.url)
            embed.set_image(url=user.display_avatar)
            embed.url = user.display_avatar.url
            view.children[1].url = user.display_avatar.url
            await i.response.edit_message(embed=embed, view=view)
        view.do_something = run
        view.add_item(discord.ui.Button(label=self.bot.util.locale(ctx, 'link_web_button', type="Interactions"), url=user.display_avatar.url))
        view.message = await ctx.send(embed=embed, view=view)
