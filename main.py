from util import ext, web, midb, helpers
from discord.ext import commands, tasks
from termcolor import colored, cprint 
import discord, dotenv, asyncio, os 

dotenv.load_dotenv()

db = midb.Database(path="./util/database", tables=["Guilds", "Main"])

bot = commands.Bot(
    command_prefix=(
        lambda client, message: db.get(f"{message.guild.id}.prefix", "Guilds") or "?"
    ),
    owner_ids=[db.get("devs.id", "Main")],
    strip_after_prefix=True,
    case_insensitive=True,
    intents=discord.Intents.all(),
)

util = ext.Util(bot, db)
bot.util = util
cmds = helpers.Helpers(bot)


async def main(bot: commands.Bot):
    print("\n")
    for file in os.listdir("./cogs"):
        if file.endswith(".py"):
            await bot.load_extension(f"cogs.{file[:-3]}")
            print(
                colored("Loaded extension:", "green"), colored(f"'{file[:-3]}'", "grey")
            )
    print("\n")
    async with bot:
        await bot.start(os.getenv("DISCORD_TOKEN"))

if __name__ == "__main__":
    asyncio.run(main(bot))
    web.keep_alive()