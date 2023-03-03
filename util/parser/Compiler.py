import pydash as _
import re

"""Thanks to @Pavez7274 & @Mid for the help!"""

async def last(t: str, f: str, r: str):
    p = t.split(f)
    last = p.pop()
    return f.join(p) + r + last

class Compiler:
    def __init__(self, code: str):
        self.code = code
        self.functions = []
        self.regex = None
        self.result = ""
        self.matched = None

    def set_funcs(self, fns):
        self.functions = fns
        self.regex = f"({'|'.join(self.functions)})".replace(".", "\\.")
        return self
    
    async def set_code(self, code: str):
        self.code = code
        return code
    
    async def magic(self):
        if self.matched or self.result:
            self.clear()
        if not self.code or not self.regex:
            return None
        fns, code = {}, self.code
        arr = re.findall(self.regex, code, flags=re.IGNORECASE)[::-1]
        if not arr:
            return None
        for index, fn in enumerate(arr):
            splitted = "".join(code.split(fn)[-1:])
            myid = f"FUNC#{index}"
            if splitted.startswith("["):
                inside, n = "", 0
                for char in splitted[1:]:
                    if char == "]" and n <= 0:
                        break
                    if char == "[":
                        inside += char
                        n += 1
                    elif char == "]" and n > 0:
                        inside += char
                        n -= 1
                    else:
                        inside += char
                total =  f"{fn}[{inside}]"
                fns[myid] = { "name": fn, "inside": inside, "total": total, "id": myid, "fields": list(map(lambda f: {"value": f.strip(), "overs": [] }, inside.split(";"))) }
                # replaceLast
                code = await last(code, total, myid)
            else:
                fns[myid] = { "name": fn, "inside": None, "total": fn, "id": myid, "fields": [] }
                #replaceLast
                code = await last(code, fn, myid)
        cloned, array = fns.copy(), list(fns.values())
        for fn in array:
            if not fn["inside"] or not len(fn["fields"]):
                continue
            if _.some(array, lambda F: _.some(F["fields"], lambda f: _.some(f["overs"], lambda o: o["id"] == fn["id"]))):
                _.unset(fns, fn["id"])
                continue
            for index, field in enumerate(fn["fields"]):
                possible_funcs = re.findall("FUNC#\d+", field["value"], flags=re.IGNORECASE)
                for possible_over in possible_funcs:
                    if _.get(cloned, possible_over):
                        fns[fn["id"]]["fields"][index]["overs"].append(cloned[possible_over])
                        _.unset(fns, possible_over)
        self.result = code
        self.matched = fns
        return fns
    
    def clear(self):
        self.result = ""
        self.matched = None
