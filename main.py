import re
from dataclasses import dataclass
from datetime import datetime

import discord
import controller
from discord import app_commands
from discord.ext import commands

import config  # bot token

# Nuevo bot para hacer un log de usuarios.

# Message Content Intent (discord dev. portal)
intents: discord.Intents = discord.Intents.default()
intents.message_content = True

bot: commands.Bot = commands.Bot(command_prefix="/", intents=intents)
tree: app_commands.CommandTree = bot.tree


@dataclass
class DiscordUser:
    user_id: int
    user_name: str
    display_names: str  # list[str] (todo: guardar historial de alias)
    avatar_url: str
    account_created: datetime
    joined_server: datetime
    roles: list[str]


# log de mensajes recibidos
@bot.event
async def on_message(message: discord.Message):
    if message.author == bot.user:
        return
    # print(f'{message.author}: {message.content}')
    get_user_info(message.author)
    get_stuff(message.content)
    await bot.process_commands(message)


def get_user_info(member: discord.User | discord.Member):
    # ToDo: testing, guardar en bd y refactorizar.

    user_name: str = str(member)
    user_id: int = member.id
    display_name: str = member.display_name
    avatar_url: str = member.avatar.url if member.avatar else ""
    account_created: datetime = member.created_at
    joined_server: datetime = member.joined_at
    roles: list[str] = [role.name for role in member.roles if role.name != "@everyone"]

    discord_user = DiscordUser(
        user_id,
        user_name,
        display_name,
        avatar_url,
        account_created,
        joined_server,
        roles
    )
    # Guardar usuario
    controller.connect_db()
    controller.validate_table("users")
    controller.insert_discord_user(
        user_id=user_id,
        username=user_name,
        display_name=display_name,
        avatar_url=avatar_url,
        account_created=account_created,
        joined_server=joined_server,
        roles=roles
    )

    print(discord_user.roles)


# rescatamos cositas interesantes:
def get_stuff(content: str):
    # url_pattern: str = r"(?:(?:https?|ftp|file)://|www\.|ftp\.)(?:\([-A-Z0-9+&@#/%=~_|$?!:,.]*\)|[-A-Z0-9+&@#/%=~_|$?!:,.])*(?:\([-A-Z0-9+&@#/%=~_|$?!:,.]*\)|[A-Z0-9+&@#/%=~_|$])"
    # email_pattern: str = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    # mexican_rfc_pattern: str = r"/^([A-Z,Ñ,&]{3,4}([0-9]{2})(0[1-9]|1[0-2])(0[1-9]|1[0-9]|2[0-9]|3[0-1])[A-Z|\d]{3})$/"
    phone_number_pattern: str = r"(?:(?:\+\d{1,3}[-.\ ]?)?(?:\d{1,4}[-.\ ]?)?(?:\(?\d{3}\)?[-.\ ]?\d{3}[-.\ ]?\d{4})|(?:\+\d{1,3}[-.\ ]?)?(?:\d{2}[-\ ]\d{2}[-\ ]\d{2}[-\ ]\d{2}[-\ ]\d{2}))"

    # urls = GetAllMatches(url_pattern, content) 
    # emails = GetAllMatches(email_pattern, content)
    # rfcs = GetAllMatches()
    phones = get_phone_numbers(phone_number_pattern, content)

    # print(urls)
    # print(emails)
    # print(rfcs)
    print(phones)


# funcion general para expandir los futuros patterns
def GetAllMatches(regex_pattern: str, content: str) -> list[str] | None:
    all_matches: list[str] = re.findall(regex_pattern, content)
    if all_matches is not None:
        return all_matches

    return None


# alternativa (test)
def get_phone_numbers(regex_pattern: str, content: str) -> list[str] | None:
    matches = [m.group(0) for m in re.finditer(regex_pattern, content)]
    return matches or None


# para mantener el canal limpio
@tree.command(name="purge", description="Borra los ultimos 100 mensajes recientes")
async def purge(ctx: commands.Context):
    try:
        deleted = await ctx.channel.purge(limit=100)
        await ctx.send(f"Borrados {len(deleted)} mensajes.", delete_after=5)
    except Exception as e:
        await ctx.send(f"No se pudieron borrar los mensajes: {e}")


@bot.event
async def on_ready():
    print(f"----- BOT ONLINE: {bot.user} -----")
    try:
        # Sincroniza los comandos de slash con Discord
        synced: list[app_commands.AppCommand] = await tree.sync()
        print(f"[{len(synced)}] Comandos sincronizados.")
    except Exception as e:
        print(f"Error al sincronizar comandos: {e}")


# Inicia el bot
bot.run(config.TOKEN)
