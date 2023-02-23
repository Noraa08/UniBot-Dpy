import discord, re, string, typing
from discord.ext import commands

class Data:
    def __init__(self, ctx: commands.Context):
        self.code = None
        self.embeds = []
        self.ctx = ctx
        self.func = {}
        
        self.reply_type = "send"

    def add_embed(self):
        self.embeds.append(discord.Embed())
