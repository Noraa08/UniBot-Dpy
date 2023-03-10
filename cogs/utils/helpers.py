import discord, datetime
from discord.ext import commands
from util import Views, Locales

class Helpers():
    def __init__(self, bot: commands.Bot):
        self.bot = bot   
        self.util = bot.util

    async def avatar(self, ctx: commands.Context, user: discord.Member = None):
        user = user if user else ctx.author
        embed = discord.Embed(
            #color=await self.bot.util.image_color(user.display_avatar.url) or self.bot.config.Colors.DARK.value, 
            title=await Locales.get(ctx, "Util", "avatar", "embed_title"),
            url=user.display_avatar.url, 
            timestamp=datetime.datetime.now()
        )
        embed.set_author(name=f"{user}", icon_url=user.display_avatar.url, url=f"https://discord.com/users/{user.id}")
        embed.set_image(url=user.display_avatar)
        embed.set_footer(text=f"{self.bot.config.footer}", icon_url=self.bot.config.footer_icon)
        
        view = Views.UserMenu(ctx)
        view.children[0].placeholder = await Locales.get(ctx, "Util", "avatar", "menu_placeholder")
        async def run(i: discord.Interaction, user: discord.User, message: discord.Message):
            #embed.color = await self.util.image_color(user.display_avatar.url)
            embed.set_author(name=f"{user}", icon_url=user.display_avatar.url)
            embed.set_image(url=user.display_avatar)
            embed.url = user.display_avatar.url
            view.children[1].url = user.display_avatar.url
            await i.response.edit_message(embed=embed, view=view)
        view.do_something = run
        view.add_item(discord.ui.Button(label=await Locales.get(ctx, "Util", "avatar", 'button_link'), url=user.display_avatar.url))
        view.message = await ctx.send(embed=embed, view=view)

    async def user_info(self, ctx: commands.Context, user: discord.Member = None):
        ctx.author = user 
        embed = self.util.Embed(
            ctx,
            title=await Locales.get(ctx, "Information", "embed_title", "user_info"),
            color=await self.util.image_color(user.display_avatar.url)
        )
        embed.set_thumbnail(url=user.display_avatar)
        embed.description = await Locales.get(ctx,
            "Information", "embed_description", "user_info",
            nick=user.nick, id=user.id, name=user.name, color=user.color
        )
        field1 = await Locales.get(ctx, "Information", "field_created", "user_info")
        embed.add_field(name=field1, value=f"_ _ <t:{round(user.created_at.timestamp())}>")
        field2 = await Locales.get(ctx, "Information", "field_joined", "user_info")
        embed.add_field(name=field2, value=f"_ _ <t:{round(user.joined_at.timestamp())}>")
        field3 = await Locales.get(ctx, "Information", "field_roles", "user_info")
        embed.add_field(name=field3, value= ", ".join([r.mention for r in user.roles][::-1][:-1]))
        return embed