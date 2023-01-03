from discord import Interaction, User, Message, ui
from discord.ext import commands

class UserMenu(ui.View):
    def __init__(self, ctx: commands.Context):
        super().__init__(timeout=160.0)
        self.ctx = ctx

    async def do_something(self, interaction: Interaction, user: User, message: Message):
        embed = discord.Embed(title="Editado!")
        await interaction.response.defer()
        await message.edit(embed=embed)

    async def interaction_check(self, interaction: Interaction):
        if self.ctx.author.id != interaction.user.id:
            await self.ctx.send("This interaction is not for u")
            return False
        else:
            return True

    
    @ui.select(cls=ui.UserSelect, placeholder="..")
    async def select(self, interaction: Interaction, select: ui.UserSelect):
        user = select.values[-1]
        msg = interaction.message
        await self.do_something(interaction, user, msg)
        return UserMenu(self.ctx)

    async def on_timeout(self):
        for items in self.children:
            items.disabled = True
        await self.message.edit(view=self)