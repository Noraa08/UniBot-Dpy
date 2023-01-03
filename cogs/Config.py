import discord, datetime, contextlib, io, re
from traceback import format_exception
from discord.ext import commands
from main import db, util


class Config(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command(name="set", aliases=["config"])
    async def _set(self, ctx: commands.Context, opt=None, val=None):
        prefix, lang = (
            db.get(f"{ctx.guild.id}.prefix", "Guilds") or "?",
            db.get(f"{ctx.guild.id}.lang", "Guilds") or "es",
        )
        # --> PREFIX OPT
        if opt == "prefix":
            if not val:
                return await util.throw_error(
                    ctx,
                    es="¡Necesitas proporcionar un prefijo para establecer!",
                    en="You need to provide a prefix to set!",
                    pt="Você precisa fornecer um prefixo para definir!",
                    fr="Vous devez fournir un préfixe à définir !",
                )
            if len(val) > 5:
                return await util.throw_error(
                    ctx,
                    es="¡No puedes establecer un prefix con mas de 5 carácteres!",
                    en="You cannot set a prefix with more than 5 characters!",
                    pt="Você não pode definir um prefixo com mais de 5 caracteres!",
                    fr="Vous ne pouvez pas définir un préfixe avec plus de 5 caractères !",
                )
            if val == prefix:
                return await util.throw_error(
                    ctx,
                    es="¡No puedes establecer el mismo prefijo!",
                    en="You can't set the same prefix!",
                    pt="Você não pode definir o mesmo prefixo!",
                    fr="Vous ne pouvez pas définir le même préfixe !",
                )
            view = (
                discord.ui.View()
                .add_item(
                    item=discord.ui.Button(
                        style=discord.ButtonStyle.green,
                        label=f"{util.lang(ctx, 'Ahora:', 'New:', 'Novo:', 'Nouveau:')} {r}-{r.upper()}",
                        disabled=True,
                    )
                )
                .add_item(
                    item=discord.ui.Button(
                        style=discord.ButtonStyle.red,
                        label=f"{util.lang(ctx, 'Antes:', 'Old:', 'Antigo:', 'Ancien:')} {lang}-{lang.upper()}",
                        disabled=True,
                    )
                )
            )
            db.set(f"{ctx.guild.id}.prefix", val)
            await util.throw_fine(
                ctx,
                es=f"Prefix actualizado con éxito!",
                en="Prefix updated successfully!",
                pt=f"Prefixo atualizado com sucesso!",
                fr=f"Préfixe mis à jour avec succès!",
                view=view,
            )
        # --> LANG OPT
        elif opt == "lang" or opt == "language":
            if not val:
                return await util.throw_error(
                    ctx,
                    "**¡Necesitas proporcionar un idioma para establecer!**\nIdiomas Validos: ```es-ES, en-EN, pt-BR, fr-FR```",
                    "**You need to provide a lang to set!**\nValid Languages: ```es-ES, en-EN, pt-BR, fr-FR```",
                    "Você precisa fornecer um prefixo para definir!**\nIdiomas válidos: ```es-ES, en-EN, pt-BR, fr-FR```",
                    "Vous devez fournir un préfixe à définir !**\nLangues valides: ```es-ES, en-EN, pt-BR, fr-FR```",
                    bold=False,
                )
            r = val.lower().split("-")[0]
            if not r in ["es", "en", "pt", "br", "fr"]:
                return await util.throw_error(
                    ctx,
                    "**¡Necesitas proporcionar un idioma valido!**\nIdiomas Validos: ```es-ES, en-EN, pt-BR, fr-FR```",
                    "**You need to provide a valid lang!**\nValid Languages: ```es-ES, en-EN, pt-BR, fr-FR```",
                    "Você precisa fornecer um idioma válido!**\nIdiomas válidos: ```es-ES, en-EN, pt-BR, fr-FR```",
                    "Vous devez fournir une langue valide !**\nLangues valides: ```es-ES, en-EN, pt-BR, fr-FR```",
                    bold=False,
                )
            if r == lang:
                return await util.throw_error(
                    ctx,
                    "¡No puedes establecer el mismo idioma!",
                    "You can't set the same lang!",
                    "Você não pode definir o mesmo idioma!",
                    "Vous ne pouvez pas définir le même lengue !",
                )
            db.set(f"{ctx.guild.id}.lang", r)
            view = (
                discord.ui.View()
                .add_item(
                    item=discord.ui.Button(
                        style=discord.ButtonStyle.green,
                        label=f"{util.lang(ctx, 'Ahora:', 'New:', 'Novo:', 'Nouveau:')} {r}-{r.upper()}",
                        disabled=True,
                    )
                )
                .add_item(
                    item=discord.ui.Button(
                        style=discord.ButtonStyle.red,
                        label=f"{util.lang(ctx, 'Antes:', 'Old:', 'Antigo:', 'Ancien:')} {lang}-{lang.upper()}",
                        disabled=True,
                    )
                )
            )
            await util.throw_fine(
                ctx,
                f"Idioma actualizado con éxito!",
                "Language updated successfully!",
                f"Idioma atualizado com sucesso!",
                f"Langue mis à jour avec succès!",
                view=view,
            )
        # --> MENU OPT
        else:
            i = 1
            res = []
            cmds = ["prefix", "[lang/language]"]
            for x in sub:
                res.append(f"{i} - {prefix}set {x} <value>")
                i = i + 1
            sub = "\n".join(res)
            embed = discord.Embed(
                title="Set Module",
                description=f"_ _ {util.lang(ctx, 'Establece configuraciones del bot, como el prefijo, el idioma y etc...', 'Set bot settings, such as prefix, language and etc...', 'Defina as configurações do bot, como prefixo, idioma e etc...', 'Définissez les paramètres du bot, tels que le préfixe, la langue, etc.')}",
                color=0x303136,
            )
            embed.set_thumbnail(
                url="https://cdn.discordapp.com/emojis/960724387382845451.png?v=1"
            )
            embed.set_author(
                name=f"{ctx.author.name}", icon_url=ctx.author.display_avatar.url
            )
            embed.add_field(
                name=util.lang(
                    ctx,
                    "Sub-comandos:",
                    "Sub-commands:",
                    "Subcomandos:",
                    "Sous-commandes:",
                ),
                value=f"```{sub}```",
            )
            embed.set_footer(text=f"{util.footer}", icon_url=f"{util.logo}")
            await ctx.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Config(bot))
