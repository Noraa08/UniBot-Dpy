from discord.ext import commands
import sys, pydash as _, re, validators

async def author_name(d):
    await d["func"]["resolve_fields"](d)
    d["code"] = d["code"].replace(f'@{d["func"]["id"]}', d["ctx"].author.name)
    return {
        "code": None
    }

async def author_id(d):
    await d["func"]["resolve_fields"](d)
    return {
        "code": d["code"].replace(f'@{d["func"]["id"]}', str(d["ctx"].author.id))
    }

async def title(d):
    await d["func"]["resolve_fields"](d)
    f = d["fields"](d)
    setattr(d["embeds"], "title", f[0] if len(f) > 0 else "None")
    setattr(d["embeds"], "url", (f[1] if validators.url(f[1]) else None) if len(f) > 1 else None)
    d["code"] = d["code"].strip(f'@{d["func"]["id"]}')
    return { "code": None }

async def color(d):
    await d["func"]["resolve_fields"](d)
    f = d["fields"](d)
    if len(f) > 0:
        f = f[0].strip().strip("#")
        r=int(f, 16) if not re.search(r"[^A-F0-9]", f) else None
    else:
        r=None
    setattr(d["embeds"], "color", r)
    d["code"] = d["code"].strip(f'@{d["func"]["id"]}')
    return { "code": None }
    
def Functions():
    funcs = []
    for key, value in sys.modules[__name__].__dict__.items():
        if callable(value):
            funcs.append(value)
    print(funcs)
    return funcs #[author_id, title]
    """
    res = {
            # --> AUTHOR
        "author.id": ctx.author.id,
        "author.name": ctx.author.name,
        "author.tag": ctx.author,
        "author.discriminator": ctx.author.discriminator,
        "author.mention": ctx.author.mention,
        "author.avatar": ctx.author.display_avatar.url,
            # --> GUILD
        "guild.name": ctx.guild,
        "guild.id": ctx.guild.id,
        "guild.icon": ctx.guild.icon.url,
        "guild.members": ctx.guild.members,
        "guild.boosts": ctx.guild.premium_subscription_count
    }
    return res
    """ 


def load_doc(codec: str):
    if codec is None:
        return None
    allowed = ['name=', 'use=', 'explan=']
    d = {}
    for thing in allowed:
        if thing in codec:
            v = codec.split(thing)[1].split('\n')[0]
            try:
                v = json.loads(v)
            except:
                pass
            _.set_(d, thing.replace('=', ''), v)
    return d