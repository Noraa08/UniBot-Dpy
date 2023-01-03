import discord, datetime, contextlib, io, re, textwrap, traceback
from traceback import format_exception
from discord.ext import commands
from main import db, util
from util import ext
import subprocess
from contextlib import redirect_stdout
from typing import TYPE_CHECKING, Any, Awaitable, Callable, Union, Optional
from discord.ext.commands import Context

class Dev(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self._last_result: Optional[Any] = None
        self.sessions: set[int] = set()

    async def run_process(self, command: str) -> list:
        try:
            process = await asyncio.create_subprocess_shell(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            result = await process.communicate()
        except NotImplementedError:
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            result = await self.bot.loop.run_in_executor(None, process.communicate)

        return [output.decode() for output in result]

    def cleanup_code(self, content: str) -> str:
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        return content.strip('` \n')

    async def cog_check(self, ctx: Context) -> bool:
        return await self.bot.is_owner(ctx.author)

    def get_syntax_error(self, e: SyntaxError) -> str:
        if e.text is None:
            return f'```py\n{e.__class__.__name__}: {e}\n```'
        return f'```py\n{e.text}{"^":>{e.offset}}\n{e.__class__.__name__}: {e}```'

    @commands.command(hidden=True, name='eval2')
    async def _eval2(self, ctx: Context, *, body: str):
        """Evaluates a code"""

        env = {
            'bot': self.bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
            '_': self._last_result,
        }

        env.update(globals())

        body = self.cleanup_code(body)
        stdout = io.StringIO()

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        try:
            exec(to_compile, env)
        except Exception as e:
            return await ctx.send(f'```py\n{e.__class__.__name__}: {e}```')

        func = env['func']
        print(func)

        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            out = stdout.getvalue()
            await ctx.send(f'```py\n{out}{traceback.format_exc()}\n```')
        else:
            out = stdout.getvalue()
            try:
                await ctx.message.add_reaction('\u2705')
            except:
                pass

            if ret is None:
                if out:
                    self._last_result = stdout.getvalue()
                    await ctx.send(f'```py\n{out}```')
            else:
                embed = discord.Embed(
                    title="<:eg_right:1029412506743091280> Successful Evaluation.",
                    description=f'```py\n{out if out else "[ No output ]" }```',
                    color=0x202126,
                    timestamp=datetime.datetime.now(),
                )
                embed.add_field(name="Input", value=f"\n```{util.set_lines(body)}```")
        
                self._last_result = ret
                await ctx.send(embed=embed)

        
    @commands.command(name="eval", aliases=["ev", "e"])
    @commands.is_owner()
    async def _eval(self, ctx: commands.Context, *, text=None):
        if not text:
            return await util.throw_error(
                ctx,
                es="¡Necesita proporcionar un código para evaluar!",
                en="You need to provide a code to evaluate!",
                pt="..",
                fr="..",
            )

        def clean_code(code: str):
            if code.startswith("\`\`\`") and code.endswith("\`\`\`"):
                return "\n".join(code.split("\n")[1:])[:-3]
            return code

        code = clean_code(text)
        if "--p" in code or "--print" in code:
            code = f'print({re.sub("--p(rint)?", "", code, flags=re.IGNORECASE)})'
        local_variables = {
            "discord": discord,
            "commands": commands,
            "bot": commands.Bot,
            "ctx": ctx,
            "db": db,
            "util": util,
        }
        stdout = io.StringIO()
        try:
            with contextlib.redirect_stdout(stdout):
                exec(code, local_variables)
        except Exception as err:
            return await ctx.send(
                f'```py\n{"".join(format_exception(err, err, err.__traceback__))}```',
            )
        out = util.set_lines(stdout.getvalue())
        intup = util.set_lines(text)
        embed = discord.Embed(
            title="<:eg_right:1029412506743091280> Successful Evaluation.",
            description=f'```py\n{out if stdout.getvalue() else "[ No output ]" }```',
            color=0x202126,
            timestamp=datetime.datetime.now(),
        )
        embed.add_field(name="Input", value=f"\n```{intup}```")
        await ctx.send(embed=embed)

    @commands.command(name="load")
    @commands.is_owner()
    async def _load(self, ctx: commands.Context, extension=None):
        if not os.path.exists(f"./cogs/{extension}.py"):
            return await util.throw_error(ctx, text="That cog doesn't exist!")
        await ctx.bot.load_extension(f"cogs.{extension}")
        await util.throw_fine(
            ctx, text=f"**cogs.{extension}** successfully loaded!", bold=False
        )

    @commands.command(name="reload", aliases=["update"])
    @commands.is_owner()
    async def _reload(self, ctx: commands.Context, extension=None):
        if not os.path.exists(f"./cogs/{extension}.py"):
            return await util.throw_error(ctx, text="That cog doesn't exist!")
        old = ctx.bot.commands
        await ctx.bot.reload_extension(f"cogs.{extension}")
        view = (
            discord.ui.View()
            .add_item(
                discord.ui.Button(
                    style=discord.ButtonStyle.blurple,
                    label=f"Commands",
                    custom_id="general",
                    disabled=True,
                )
            )
            .add_item(
                discord.ui.Button(
                    style=discord.ButtonStyle.red,
                    label=f"Before: {len(old)}",
                    custom_id="before",
                    disabled=True,
                )
            )
            .add_item(
                discord.ui.Button(
                    style=discord.ButtonStyle.green,
                    label=f"After: {len(ctx.bot.commands)}",
                    custom_id="after",
                    disabled=True,
                )
            )
        )
        await util.throw_fine(
            ctx,
            text=f"**cogs.{extension}** successfully reloaded!",
            view=view,
            bold=False,
            defer=False,
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Dev(bot))
