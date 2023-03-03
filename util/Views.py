from __future__ import annotations
from random import choice

from typing import (
    Generic, 
    List,
    TYPE_CHECKING,
    Type, 
    TypeVar
)

from discord import Interaction, User, Message, ui
from discord.ext import commands
import discord

T = TypeVar('T')

class UserMenu(ui.View):
    def __init__(self, ctx: commands.Context, config, util):
        super().__init__(timeout=160.0)
        self.ctx = ctx
        self.config = config
        self.util = util
    
    async def do_something(self, interaction: Interaction, user: User, message: Message):
        embed = discord.Embed(title="Editado!")
        await interaction.response.defer()
        await message.edit(embed=embed)
      
    async def interaction_check(self, interaction: Interaction):
        if self.ctx.author.id != interaction.user.id:
            emojis = choice(self.config["ERROR_EMOJIS"])
            text = (self.util.locale(self.ctx, "not_author", type="Interactions"))
            res = f"{text} {emojis}"
            await interaction.response.send_message(
                f"_ _ <:eg_wrong:1029412572899836055> {res}",
                ephemeral=True
            )
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


class BaseButtonPaginator(Generic[T], discord.ui.View):
    """
    The Base Button Paginator class. Will handle all page switching without
    you having to do anything.
    
    Attributes
    ----------
    entries: List[Any]
        A list of entries to get spread across pages.
    per_page: :class:`int`
        The number of entries that get passed onto one page.
    pages: List[List[Any]]
        A list of pages which contain all entries for that page.
    clamp_pages: :class:`bool`
        Whether or not to clamp the pages to the min and max. 
    """
    if TYPE_CHECKING:
        ctx: commands.Context[commands.Bot]
    
    def __init__(self, *, entries: List[T], per_page: int = 6, clamp_pages: bool = True) -> None:
        super().__init__(timeout=180)
        self.entries: List[T] = entries
        self.per_page: int = per_page
        self.clamp_pages: bool = clamp_pages
            
        self._current_page = 0
        self.pages = [entries[i: i+per_page] for i in range(0, len(entries), per_page)]
        
    @property
    def max_page(self) -> int:
        """:class:`int`: The max page count for this paginator."""
        return len(self.pages)
    
    @property
    def min_page(self) -> int:
        """:class:`int`: The min page count for this paginator."""
        return 1

    @property
    def current_page(self) -> int:
        """:class:`int`: The current page the user is on."""
        return self._current_page + 1
    
    @property
    def total_pages(self) -> int:
        """:class:`int`: Returns the total amount of pages."""
        return len(self.pages)
        
    async def format_page(self, entries: List[T], ctx: Interaction, /) -> discord.Embed:
        """|coro|
        
        Used to make the embed that the user sees.
        
        Parameters
        ----------
        entries: List[Any]
            A list of entries for the current page.
           
        Returns
        -------
        :class:`discord.Embed`
            The embed for this page.
        """
        raise NotImplementedError('Subclass did not overwrite format_page coro.')
    
    def _switch_page(self, count: int, /) -> List[T]:
        self._current_page += count
        
        if self.clamp_pages:
            if count < 0: # Going down
                if self._current_page < 0: 
                    self._current_page = self.max_page - 1
            elif count > 0: # Going up
                if self._current_page > self.max_page - 1: # - 1 for indexing
                    self._current_page = 0

        if self._current_page == 0:
            self.children[0].disabled = True
        if self._current_page == 1:
            self.children[0].disabled = False
        if self._current_page == self.max_page:
            self.children[1].disabled = True

        print(self._current_page)
        return self.pages[self._current_page]
    
    @discord.ui.button(emoji='<:pp_2:1040132248126631946>', style=discord.ButtonStyle.blurple)
    async def on_arrow_backward(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        entries = self._switch_page(-1)
        embed = await self.format_page(entries, interaction)
        return await interaction.response.edit_message(embed=embed)
        
    @discord.ui.button(emoji='<:pp_3:1040132791305777192>', style=discord.ButtonStyle.blurple)
    async def on_arrow_forward(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        entries = self._switch_page(1)
        embed = await self.format_page(entries, interaction)
        return await interaction.response.edit_message(embed=embed)
    
    @discord.ui.button(emoji='<:p_stopp:1061873348142977094>', style=discord.ButtonStyle.blurple)
    async def on_stop(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        for child in self.children:
            child.disabled = True # type: ignore
            
        self.stop()
        
        return await interaction.response.edit_message(view=self)

    @classmethod
    async def start(
        cls: Type[BaseButtonPaginator],
        context: commands.Context,
        *, 
        entries: List[T],
        per_page: int = 6,
        clamp_pages: bool = True
    ) -> BaseButtonPaginator[T]:
        """|coro|
        
        Used to start the paginator.
        
        Parameters
        ----------
        context: :class:`commands.Context`
            The context to send to. This could also be discord.abc.Messageable as `ctx.send` is the only method
            used.
        entries: List[T]
            A list of entries to pass onto the paginator.
        per_page: :class:`int`
            A number of how many entries you want per page.
            
        Returns
        -------
        :class:`BaseButtonPaginator`[T]
            The paginator that was started.
        """
        new = cls(entries=entries, per_page=per_page, clamp_pages=clamp_pages)
        new.ctx = context
        context.user = context.author
        if new.max_page == 1:
            for child in new.children:
                child.disabled = True # type: ignore

        embed = await new.format_page(new.pages[0], context)
        await context.send(embed=embed, view=new)
        return new


class Confirmation(discord.ui.View):
    def __init__(self, ctx):
        super().__init__()
        self.value = None
        self.last_interaction = None
        self.ctx = ctx

    async def do_something(self, ctx, interaction: Interaction, message: Message):
        embed = discord.Embed(title="Editado!")
        await interaction.response.defer()
        await message.edit(embed=embed)

    async def interaction_check(self, interaction: Interaction):
        if self.ctx.author.id != interaction.user.id:
            await interaction.response.send_message("This interaction is not for u")
            return False
        else:
            return True
            
    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = True
        self.last_interaction = interaction
        self.stop()
        
    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.grey)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = False
        self.last_interaction = interaction
        self.stop()
        