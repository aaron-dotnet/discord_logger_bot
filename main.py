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
    
    user: DiscordUser = get_user_info(message.author)
    save_content_to_db(user, message)

    get_stuff(message.content)
    await bot.process_commands(message)


def get_user_info(member: discord.User | discord.Member) -> DiscordUser:
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
        roles,
    )

    return discord_user

# preparamos la base de datos
def init_db():
    controller.connect_db()
    controller.create_tables()

# guardamos el usuario en la db
def save_content_to_db(user: DiscordUser, message: discord.Message):
    # primero preguntamos si existe el usuario
    exists: bool = controller.user_exists(user.user_id)  # True/False, si no existe lo crea (todo: optimizar esto)
    if not exists:
        controller.insert_discord_user(
            user.user_id,
            user.user_name,
            user.display_names,
            user.avatar_url,
            user.account_created.isoformat(),
            user.joined_server.isoformat(),
            user.roles,
            )
    # guardamos el contenido del mensaje
    controller.insert_message(
        message.id,
        user.user_id,
        message.content,
        message.created_at.isoformat(),
    )


# rescatamos cositas interesantes:
def get_stuff(content: str):
    url_pattern: str = r"(?:(?:https?|ftp|file)://|www\.|ftp\.)(?:\([-A-Z0-9+&@#/%=~_|$?!:,.]*\)|[-A-Z0-9+&@#/%=~_|$?!:,.])*(?:\([-A-Z0-9+&@#/%=~_|$?!:,.]*\)|[A-Z0-9+&@#/%=~_|$])"
    email_pattern: str = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    phone_number_pattern: str = r"(?:(?:\+\d{1,3}[-.\ ]?)?(?:\d{1,4}[-.\ ]?)?(?:\(?\d{3}\)?[-.\ ]?\d{3}[-.\ ]?\d{4})|(?:\+\d{1,3}[-.\ ]?)?(?:\d{2}[-\ ]\d{2}[-\ ]\d{2}[-\ ]\d{2}[-\ ]\d{2}))"

    urls = GetAllMatches(url_pattern, content) 
    emails = GetAllMatches(email_pattern, content)
    phones = get_phone_numbers(phone_number_pattern, content)

    print(urls)
    print(emails)
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
    init_db()
    print(f"----- BOT ONLINE: {bot.user} -----")
    try:
        # Sincroniza los comandos de slash con Discord
        synced: list[app_commands.AppCommand] = await tree.sync()
        print(f"[{len(synced)}] Comandos sincronizados.")
    except Exception as e:
        print(f"Error al sincronizar comandos: {e}")


# Inicia el bot
bot.run(config.TOKEN)
