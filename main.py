from util import ext, web, midb, helpers, interpreter, compiler
from discord.ext import commands, tasks
from termcolor import colored, cprint 
import (
    discord, 
    dotenv, 
    asyncio, 
    os, 
    json, 
    asyncpg,
    config
)

dotenv.load_dotenv()

langs_cache = {}

# Load Config File
with open('Config.json', 'r') as stream:
    config = json.load(stream)#["Config"]
        
# Start MIDB
db = midb.Database(path="./util/database", tables=["Guilds", "Main"])


def prefix(client: commands.Bot, message: discord.Message):
    p = db.get(f"{message.guild.id}.prefix", "Guilds") or "?"
    return [p, "uni"]

# Start Client
bot = commands.Bot(
    command_prefix=prefix,
    owner_ids=[852970774067544165],
    strip_after_prefix=True,
    case_insensitive=True,
    intents=discord.Intents.all(),
)

# Start Utils
util = ext.Util(bot, db)

# Start Parser
_ = interpreter.Interpreter(bot)

# Set Bot Values
bot.db = db
bot.util = util

# Start Helper Commands
cmds = helpers.Helpers(bot)

async def create_pool() -> asyncpg.Pool:
    def _encode_jsonb(value):
        return json.dumps(value)
    def _decode_jsonb(value):
        return json.loads(value)

    async def init(con):
        await con.set_type_codec(
            'jsonb',
            schema='pg_catalog',
            encoder=_encode_jsonb,
            decoder=_decode_jsonb,
            format='text',
        )

    return await asyncpg.create_pool(
        config.postgresql,
        init=init,
        command_timeout=60,
        max_size=20,
        min_size=20,
    )  # type: ignore        
    
# Cog Loader
async def main(bot: commands.Bot):
    pool = await create_pool()
    print("\n")
    for file in os.listdir("./cogs"):
        if file.endswith(".py"):
            await bot.load_extension(f"cogs.{file[:-3]}")
            print(
                colored("Loaded extension:", "green"), colored(f"'{file[:-3]}'", "grey")
            )
    print("\n")
    await bot.load_extension('jishaku')
    try:
        async with bot:
            bot.pool = pool
            await bot.start(os.getenv("DISCORD_TOKEN"))
    except KeyboardInterrupt:
        await bot.logout()


if __name__ == "__main__":
    asyncio.run(main(bot))
    web.keep_alive()