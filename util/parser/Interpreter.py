import discord, re, string
from discord.ext import commands
from abc import ABC, abstractmethod
from util.functions import Functions
from util.compiler import Compiler
from util.container import Data
import typing

"""Thanks to @Pavez7274 & @Mid for the help!"""

def find(pred, iterable):
    for element in iterable:
        if pred(element):
            return element
    return None
    
class Interpreter:
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.compiler = Compiler("")
        self.functions = []
        self.load()
        self.compiler.set_funcs(list(map(lambda x: x.__name__.replace("_", "."), self.functions)))

    def fields(self, data, index: int = 0, unescape: bool = True):
        arr =  list(map(
            lambda a: a["value"]["unescape"].strip() if not unescape else a["value"].strip(),
            data["func"]["fields"]
        )) or []
        return [x for x in arr if x != '']

    async def resolve_fields(self, data, start = 0, end: int = None):
        for i in range(start, len(data["func"]["fields"])):
            if i == end:
                break
            data["func"] = await self.resolve_field(data, i)
        return data["func"]

    async def resolve_field(self, data, index: int):
        #print(8, data)
        if data["func"]["fields"][index]:
            for over in data["func"]["fields"][index]["overs"]:
                finded = find(lambda f: f["data"]["name"] == over["name"], self.functions)
                if finded:
                    over["resolve_fields"] = self.resolve_fields
                    over["resolve_field"] = self.resolve_field
                    new_data = { "data": data, "func": over, "code": data["func"]["fields"][index]["value"] }
                    reject = await finded(new_data)
                    if reject["code"] and data["func"]["inside"] and data["func"]["fields"]:
                        data["func"]["fields"][index]["value"] = reject["code"]
                        data["func"]["inside"] = ";".join(map(lambda field: field["value"], data["func"]["fields"]))
                        data["func"]["total"] = f'{data.func["name"]}[{data["func"]["inside"]}]'
        return data["func"]

    async def parse(self, text: str, ctx):
        if text:
            await self.compiler.set_code(text)
            await self.compiler.magic()
            data = {
                "ctx": ctx,
                "code": self.compiler.result or text,
                "fields": self.fields,
                "func": {},
                "embeds": discord.Embed()
            }
            
            entries = list(self.compiler.matched.copy().items()) if self.compiler.matched else None
            #print(entries[::-1])
            if entries:
                entries = entries[::-1]
                for fn in list(self.compiler.matched.copy().items()):
                    #print(1000, fn)
                    data = await self.run_function(fn[1], data) or data
            return data
            #if self.compiler.matched:
            #    for _, fn in self.compiler.matched.items():
            #       if data["break"]:
            #           break
            #       data = await self.run_function(fn, data) or data 
            #       print(1, data)
            #print("A", data["code"], text)
            #txt = re.sub(r"@FUNC#\d+", "", text, flags=re.A).strip()
            #data["ctn"].data["content"] = data["code"] if data["code"] else None
            #if data["code"]:
            #    data["ctn"].data["content"] = data["code"]
            #else:
            #    data["ctn"].data["content"] = None

            #return await data["ctn"].send(ctx)

    async def run_function(self, fn, d):
        try:
            finded = find(lambda f: f.__name__.replace("_", ".") == fn["name"], self.functions)
            if finded:
                fn["resolve_fields"] = self.resolve_fields
                fn["resolve_field"] = self.resolve_field
                d["func"] = fn
                reject = await finded(d)
                if reject["code"]:
                    d["code"] = reject["code"] or ""
            return d
        except Exception as e:
            print (e)

    def add_func(self, func): 
        self.functions.append(func)
        self.compiler.set_funcs(list(map(lambda x: x.__name__.replace("_", "."), self.functions)))
        #self.functions.sort(key=lambda a, b: len(b["data"]["name"]) - len(a["data"]["name"]))

    def load(self):
        for r in Functions():
            if r:
                self.add_func(r)

    async def test(self, text: str, ctx: commands.Context):
        self.functions = Functions(ctx)
        _ = Compiler(text)
        _.set_funcs(["@author.id", "@title"])
        _ = await _.magic()
        for y, x in _.items():
            embed = None
            text = text.replace(x["name"], str(funcs[x["name"].strip("@[]")]) if x["name"] in funcs else "")
            if x["inside"]:
                embed = discord.Embed(title=x["inside"])
            print(embed)
            #text = text.replace(x, str(funcs[_]) if _ in funcs else x)
        await ctx.send(content=text, embed=embed)
