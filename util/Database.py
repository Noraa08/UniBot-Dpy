from discord.ext import commands

class Database():
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.pool = bot.pool

    async def get(self, id: int, key: str, table: str):
        try:
            query = await self.pool.fetchrow(
                """
                SELECT {0} from {1} where id={2}
                """.format(key, table, id)
            )
            if query:
                return query[key]
        except Exception as x:
            print(x)
            return None

    async def set(self, id: int, key: str, value, table: str):
        try:
            await self.pool.execute(
                """
                UPDATE {0} SET {1} = $1 WHERE id=$2
                """.format(table, key), value, id
            )
        except Exception as x:
            print(x)
            return None
        
