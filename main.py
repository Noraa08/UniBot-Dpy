from util import Middleware, Database, Web
from discord.ext import commands
import discord, asyncio, json, asyncpg, config, logging

from bot import UniBot
""" ^ ----> IMPORTS <---- ^ """

langs_cache = {}

async def create_pool() -> asyncpg.Pool:
    async def init(con):
        await con.set_type_codec(
            'jsonb',
            schema='pg_catalog',
            encoder=lambda x: json.dumps(x),
            decoder=lambda x: json.loads(x),
            format='text',
        )

    return await asyncpg.create_pool(
        **config.postgresql,
        init=init,
        command_timeout=60,
        max_size=20,
        min_size=20,
    )  # type: ignore

async def run_bot():
    log = logging.getLogger()
    try:
        pool = await create_pool()
    except Exception:
        log.exception('Could not set up PostgreSQL. Exiting.')
        return

    async with UniBot() as bot:
        bot.pool = pool
        bot.db = Database.Database(bot)
        await bot.start()


def main():
    """Launches the bot."""
    with Middleware.setup_logging():
        asyncio.run(run_bot())

if __name__ == '__main__':
    main()