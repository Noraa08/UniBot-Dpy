from __future__ import annotations

from pprint import pp
from discord.ext import commands
from cogs.utils.config import Config
from termcolor import colored, cprint
from collections import Counter, defaultdict
from util import Middleware
from typing import Any, AsyncIterator, Callable, Coroutine, Iterable, Optional, Union
import discord, logging, config, aiohttp, os, re
""" ----------> IMPORTS <---------- """

os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True" 
os.environ["JISHAKU_HIDE"] = "True"

description = """Uni > World"""

log = logging.getLogger(__name__)

fallback = os.urandom(32).hex()
async def _prefix(_bot: commands.Bot, message: discord.Message):
    p = await _bot.pool.fetchrow(
        """
            SELECT prefixes
            FROM guilds
            WHERE id=$1
        """,
        message.guild.id,
    )

    if p is None:
        await _bot.pool.execute(
            """
                INSERT INTO guilds (id, prefixes, language)
                VALUES ($1, $2, $3)
            """,
            message.guild.id, [config.prefix], "en"
        )
        p = { "prefixes": [config.prefix] }

    _ = commands.when_mentioned_or("uni")(_bot, message)
    _.extend(p["prefixes"])
    comp = re.compile(f"^({'|'.join(map(re.escape, _))}).*", flags=re.I)
    match = comp.match(message.content)
    if match is not None:
        return match.group(1)
    return fallback


class UniBot(commands.AutoShardedBot):
    def __init__(self):
        allowed_mentions = discord.AllowedMentions(roles=False, everyone=False, users=True)
        intents = discord.Intents(
            guilds=True,
            members=True,
            bans=True,
            emojis=True,
            voice_states=True,
            messages=True,
            reactions=True,
            message_content=True,
        )
        super().__init__(
            command_prefix=_prefix,
            description=description,
            pm_help=None,
            help_attrs=dict(hidden=True),
            chunk_guilds_at_startup=False,
            heartbeat_timeout=150.0,
            allowed_mentions=allowed_mentions,
            intents=intents,
            enable_debug_events=True,
            strip_after_prefix=True,
            case_insensitive=True
        )

        self.util = Middleware.Util(self)
        self.session = None
        self.config = config
        self.resumes: defaultdict[int, list[datetime.datetime]] = defaultdict(list)
        self.identifies: defaultdict[int, list[datetime.datetime]] = defaultdict(list)
        self.spam_control = commands.CooldownMapping.from_cooldown(10, 12.0, commands.BucketType.user)
        self._auto_spam_count = Counter()
        
    async def setup_hook(self) -> None:
        self.session = aiohttp.ClientSession()
        self.prefixes: Config[list[str]] = Config('prefixes.json')
        self.blacklist: Config[bool] = Config('blacklist.json')

        self.bot_app_info = await self.application_info()
        self.owner_id = self.bot_app_info.owner.id

        print("\n")
        for file in os.listdir("./cogs"):
            if file.endswith(".py"):
                await self.load_extension(f"cogs.{file[:-3]}")
                print(
                    colored("Loaded extension:", "green"), colored(f"'{file[:-3]}'", "grey")
                )
        print("\n")
        await self.load_extension('jishaku')

    async def set_prefixes(self, guild: discord.abc.Snowflake, prefixes: list[str]) -> None:
        if len(prefixes) == 0:
            await self.prefixes.put(guild.id, [])
        elif len(prefixes) > 10:
            raise RuntimeError('Cannot have more than 10 custom prefixes.')
        else:
            await self.prefixes.put(guild.id, sorted(set(prefixes), reverse=True))

    async def add_to_blacklist(self, object_id: int):
        await self.blacklist.put(object_id, True)

    async def remove_from_blacklist(self, object_id: int):
        try:
            await self.blacklist.remove(object_id)
        except KeyError:
            pass

    async def on_ready(self):
        if not hasattr(self, 'uptime'):
            self.uptime = discord.utils.utcnow()
        log.info('Ready: %s (ID: %s)', self.user, self.user.id)

    async def on_shard_resumed(self, shard_id: int):
        log.info('Shard ID %s has resumed...', shard_id)
        self.resumes[shard_id].append(discord.utils.utcnow())

    @discord.utils.cached_property
    def stats_webhook(self) -> discord.Webhook:
        wh_id, wh_token = self.config.stat_webhook
        hook = discord.Webhook.partial(id=wh_id, token=wh_token, session=self.session)
        return hook

    async def log_spammer(self, ctx: Context, message: discord.Message, retry_after: float, *, autoblock: bool = False):
        guild_name = getattr(ctx.guild, 'name', 'No Guild (DMs)')
        guild_id = getattr(ctx.guild, 'id', None)
        fmt = 'User %s (ID %s) in guild %r (ID %s) spamming, retry_after: %.2fs'
        log.warning(fmt, message.author, message.author.id, guild_name, guild_id, retry_after)
        if not autoblock:
            return

        wh = self.stats_webhook
        embed = discord.Embed(title='Auto-blocked Member', colour=0xDDA453)
        embed.add_field(name='Member', value=f'{message.author} (ID: {message.author.id})', inline=False)
        embed.add_field(name='Guild Info', value=f'{guild_name} (ID: {guild_id})', inline=False)
        embed.add_field(name='Channel Info', value=f'{message.channel} (ID: {message.channel.id}', inline=False)
        embed.timestamp = discord.utils.utcnow()
        return await wh.send(embed=embed)

    async def get_context(self, origin: Union[discord.Interaction, discord.Message], /, *, cls=commands.Context) -> commands.Context:
        return await super().get_context(origin, cls=cls)

    async def process_commands(self, message: discord.Message):
        ctx = await self.get_context(message)

        if ctx.command is None:
            return
        if ctx.author.id in self.blacklist:
            return
        if ctx.guild is not None and ctx.guild.id in self.blacklist:
            return
            
        bucket = self.spam_control.get_bucket(message)
        current = message.created_at.timestamp()
        retry_after = bucket and bucket.update_rate_limit(current)
        author_id = message.author.id
        if retry_after and author_id != self.owner_id:
            self._auto_spam_count[author_id] += 1
            if self._auto_spam_count[author_id] >= 5:
                await self.add_to_blacklist(author_id)
                del self._auto_spam_count[author_id]
                await self.log_spammer(ctx, message, retry_after, autoblock=True)
            else:
                await self.log_spammer(ctx, message, retry_after)
            return
        else:
            self._auto_spam_count.pop(author_id, None)

        await self.invoke(ctx)

    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return
        await self.process_commands(message)

    async def on_guild_join(self, guild: discord.Guild) -> None:
        if guild.id in self.blacklist:
            await guild.leave()

    async def close(self) -> None:
        await super().close()
        #await self.session.close()

    async def start(self) -> None:
        await super().start(config.token, reconnect=True)
