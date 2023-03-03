import discord, datetime, contextlib, io, re, random, json
from traceback import format_exception
from discord.ext import commands
from util import Middleware, Views
from difflib import get_close_matches
from typing_extensions import Annotated
    
class TagPaginator(Views.BaseButtonPaginator): 
    async def format_page(self, entries, ctx: discord.Interaction):
        embed = discord.Embed(title='All Tags', color=0x303136)
        rows = []
        for i, x in enumerate(entries):
            rows.append(f'`# {str(i+1).zfill(2)}` ::  **[{x["name"]}](https://discord.gg/users/{x["owner_id"]})** `(ID: {x["id"]})`')
        embed.description = f"{chr(10).join(rows)}"
        embed.set_footer(icon_url=util.footer_icon, text=util.footer + ' • Page {0.current_page}/{0.total_pages}'.format(self))
        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/1061867240586236005.png?v=1")
        embed.set_author(name=f"{ctx.user}", icon_url=ctx.user.display_avatar.url, url=f"https://discord.com/users/{ctx.user.id}")
        
        return embed
    
def get_tags(ctx):
    res = db.get(f"{ctx.guild.id}.tags")
    return res
    
def add_tags(ctx, body):
    tags = get_tags(ctx)
    if tags:
        tags.append(body)
        print(tags)
        db.set(f"{ctx.guild.id}.tags", tags)
    else:
        db.set(f"{ctx.guild.id}.tags", [body])
    
def tag_matches(query, ctx):
    row = []
    tags = get_tags(ctx)
    if not tags:
        return None
    for x in tags:
        row.append(x["name"])
    res = get_close_matches(query, row)
    return res 
    
def find_tags(query, ctx: commands.Context):
    tags = get_tags(ctx)
    if not tags:
        return None
    return util.find(lambda x: x.get("name") == query or x.get("content") == query, tags)
    
async def view_tag(ctx: commands.Context, name):
    match, tag = (tag_matches(name, ctx), find_tags(name, ctx))
    if not tag:
        if match:
            ctx.matches = chr(10).join(match)
            return await util.throw_error(ctx, "tag_not_found2")  
        else:
            return await util.throw_error(ctx, "tag_not_found")
    await _.parse(tag["content"], ctx)#, mention_author=False)
    
async def edit_tag(ctx: commands.Context, name, n_content):
    tag = find_tags(name, ctx)
    tags = get_tags(ctx)
    if tag:
        res = { "name": name, "content": n_content, "id": tag["id"], "pos": tag["pos"], "owner_id": tag["owner_id"] }
    else:
        await util.throw_error(ctx, "tag_not_found")
        
    if tags:
        tags[tag["pos"]] = res
        db.set(f"{ctx.guild.id}.tags", tags)
    else:
        db.set(f"{ctx.guild.id}.tags", [res])


async def delete_tag(ctx: commands.Context, name):
    tag = find_tags(name, ctx)
    tags = get_tags(ctx)
    tags = tags.remove(tag)
    db.set(f"{ctx.guild.id}.tags", tags)
        
class TagName(commands.clean_content):
	def __init__(self, *, lower: bool = False):
		self.lower: bool = lower
		super().__init__()
	
	async def convert(self, ctx: commands.Context, argument: str) -> str:
		converted = await super().convert(ctx, argument)
		lower = converted.lower().strip()
	
		if not lower:
			raise commands.BadArgument('Missing tag name.')
	
		if len(lower) > 100:
			raise commands.BadArgument('Tag name is a maximum of 100 characters.')
	
		first_word, _, _ = lower.partition(' ')
	
		# get tag command.
		root: commands.GroupMixin = ctx.bot.get_command('tag')  # type: ignore
		if first_word in root.all_commands:
			raise commands.BadArgument('This tag name starts with a reserved word.')
	
		return converted.strip() if not self.lower else lower
		
class Tags(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
    
    # ----> TAG <----
    @commands.hybrid_group(name="tag", aliases=["t"])
    async def tag(self, ctx: commands.Context, *, name: Annotated[str, TagName(lower=True)]):
        await view_tag(ctx, name)
        
    @tag.command(name="view")
    async def view(self, ctx: commands.Context, *, name):
        ctx.command.name = "tag"
        await view_tag(ctx, name)
    
    @view.autocomplete("name")
    async def autocomplete_callback(self, interaction: discord.Interaction, current: str):
        tags = get_tags(interaction)
        row = []
        for x in tags:
            print(x["name"])
            # row.append(x["name"])
        return [
            discord.app_commands.Choice(name=name["name"], value=name["name"])
            for name in tags if current.lower() in name["name"].lower()
        ]
    
    @tag.command(name="add")
    async def add(self, ctx: commands.Context, name: Annotated[str, TagName], *, content: Annotated[str, commands.clean_content]):
        if len(name) < 2 or len(content) < 2:
            ctx.arg = "name" if len(name) < 2 else "content"
            ctx.len = 2
            return await util.throw_error(ctx, "length_limit")
        if find_tags(name, ctx):
            ctx.name = name
            return await util.throw_error(ctx, "tag_exists")

        id = list(range(1, 500))
        random.shuffle(id)

        tags = get_tags(ctx)
        dict = { "name": name, "content": content, "id": id.pop(), "pos": len(tags) if tags else 0, "owner_id": ctx.author.id }
        add_tags(ctx, dict)
        ctx.name = name
        await util.throw_fine(ctx, "add_message")
        
    @tag.command(name="edit")
    async def edit(self, ctx: commands.Context, name: Annotated[str, TagName], *, new_content: Annotated[str, commands.clean_content] = None):
        await edit_tag(ctx, name, new_content)
        ctx.name = name
        await util.throw_fine(ctx, "edit_message")

    @tag.command(name="delete", aliases=["remove", "del"])
    async def delete(self, ctx: commands.Context, name: Annotated[str, TagName]):
        tag, tags = (find_tags(name, ctx), get_tags(ctx))
        if not tag:
            await util.throw_error(ctx, "tag_not_found")
        else:
            view = Views.Confirmation(ctx)
            ctx.name = name
            view.message = await ctx.send(f'_ _ {util.locale(ctx, "confirm_message")}', view=view)
            await view.wait()
            if view.value is None:
                for x in view.children:
                    x.disabled = True
            elif view.value:
                for x in view.children:
                    x.disabled = True
                msg = await util.throw_fine(ctx, "confirm_accept", send=True)
                await delete_tag(ctx, name)
                await view.last_interaction.response.edit_message(content=msg, view=view)
            else:
                for x in view.children:
                    x.disabled = True
                msg = await util.throw_fine(ctx, "confirm_deny", send=True)
                await view.last_interaction.response.edit_message(content=msg, view=view)
                
    @tag.command(name="all")
    async def all(self, ctx: commands.Context):
        tags = get_tags(ctx)
        if tags:
            await TagPaginator.start(ctx, entries=tags, per_page=15)
        else:
            await util.throw_error(ctx, "no_tags")

    @tag.command(name="raw")
    async def raw(self, ctx: commands.Context, name: Annotated[str, TagName]):
        match, tag = (tag_matches(name, ctx), find_tags(name, ctx))
        if tag:
            f = io.BytesIO(json.dumps(tag).encode())
            f.seek(0)
            await ctx.send(file=discord.File(fp=f, filename=f"{tag['name']}_raw.json"))
        else:
            if match:
                ctx.matches = chr(10).join(match)
                return await util.throw_error(ctx, "tag_not_found2")  
            else:
                return await util.throw_error(ctx, "tag_not_found")
    
async def setup(bot: commands.Bot):
	await bot.add_cog(Tags(bot))
