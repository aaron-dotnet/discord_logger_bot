import re
from dataclasses import dataclass
from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands

import config  # bot token
import controller

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

    print(f"{message.author}: {message.content}")

    user: DiscordUser = get_user_info(message.author)
    save_content_to_db(user, message)

    get_stuff(message.content, message.id)
    await bot.process_commands(message)


def get_user_info(member: discord.User | discord.Member) -> DiscordUser:
    user_name: str = str(member)
    user_id: int = member.id
    display_name: str = member.display_name
    avatar_url: str = member.avatar.url if member.avatar else ""
    account_created: datetime = member.created_at
    joined_server: datetime = member.joined_at  # type: ignore
    roles: list[str] = [role.name for role in member.roles if role.name != "@everyone"]  # type: ignore

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
    # guardamos el usuario (INSERT OR IGNORE maneja duplicados)
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
def get_stuff(content: str, message_id: int):
    url_pattern: str = r"(?:(?:https?|ftp|file)://|www\.|ftp\.)(?:\([-A-Z0-9+&@#/%=~_|$?!:,.]*\)|[-A-Z0-9+&@#/%=~_|$?!:,.])*(?:\([-A-Z0-9+&@#/%=~_|$?!:,.]*\)|[A-Z0-9+&@#/%=~_|$])"
    email_pattern: str = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    phone_number_pattern: str = r"(?:(?:\+\d{1,3}[-.\ ]?)?(?:\d{1,4}[-.\ ]?)?(?:\(?\d{3}\)?[-.\ ]?\d{3}[-.\ ]?\d{4})|(?:\+\d{1,3}[-.\ ]?)?(?:\d{2}[-\ ]\d{2}[-\ ]\d{2}[-\ ]\d{2}[-\ ]\d{2}))"
    ip_pattern: str = r"\b(?:\d{1,3}\.){3}\d{1,3}\b|(?:[0-9a-fA-F]{1,4}:){2,7}[0-9a-fA-F]{1,4}|::(?:[0-9a-fA-F]{1,4}:){0,6}[0-9a-fA-F]{1,4}|[0-9a-fA-F]{1,4}::(?:[0-9a-fA-F]{1,4}:){0,5}[0-9a-fA-F]{1,4}"
    discord_invite_pattern: str = r"discord(?:app)?\.com\/invite\/[a-zA-Z0-9]+|discord\.gg\/[a-zA-Z0-9]+"
    mention_pattern: str = r"<@!?\d+>"
    # add more patterns here:

    urls = get_all_matches(url_pattern, content)
    emails = get_all_matches(email_pattern, content)
    phones = get_phone_numbers(phone_number_pattern, content)
    ips = get_all_matches(ip_pattern, content)
    discord_invites = get_all_matches(discord_invite_pattern, content)
    mentions = get_all_matches(mention_pattern, content)

    for url in urls or []:
        controller.insert_filtered_content(message_id, "url", url)

    for email in emails or []:
        controller.insert_filtered_content(message_id, "email", email)

    for phone in phones or []:
        controller.insert_filtered_content(message_id, "phone", phone)

    for ip in ips or []:
        controller.insert_filtered_content(message_id, "ip", ip)

    for invite in discord_invites or []:
        controller.insert_filtered_content(message_id, "discord_invite", invite)

    for mention in mentions or []:
        controller.insert_filtered_content(message_id, "mention", mention)

    # print consola solo si hay resultados
    if urls or emails or phones or ips or discord_invites or mentions:
        print(f" >> [{message_id}] Content detected:")
        if urls:
            print(f"  URLs: {urls}")
        if emails:
            print(f"  Emails: {emails}")
        if phones:
            print(f"  Phones: {phones}")
        if ips:
            print(f"  IPs: {ips}")
        if discord_invites:
            print(f"  Discord Invites: {discord_invites}")
        if mentions:
            print(f"  Mentions: {mentions}")


# funcion general para expandir los futuros patterns
def get_all_matches(regex_pattern: str, content: str) -> list[str] | None:
    all_matches: list[str] = re.findall(regex_pattern, content)
    if all_matches:
        return all_matches

    return None


# alternativa (test)
def get_phone_numbers(regex_pattern: str, content: str) -> list[str] | None:
    matches = [m.group(0) for m in re.finditer(regex_pattern, content)]
    return matches or None


# para mantener el canal limpio
@tree.command(name="purge", description="Borra los ultimos 100 mensajes recientes")  # type: ignore
async def purge(ctx: commands.Context):
    try:
        deleted = await ctx.channel.purge(limit=100)  # type: ignore
        await ctx.send(f"Borrados {len(deleted)} mensajes.", delete_after=5)
    except Exception as e:
        await ctx.send(f"No se pudieron borrar los mensajes: {e}")


# evento para detectar nuevos usuarios que se unen al servidor
@bot.event
async def on_member_join(member: discord.Member):
    print(f" # Nuevo usuario se ha unido: {member} (ID: {member.id})")
    # pass


@bot.event
async def on_ready():
    init_db()
    print(f"----- BOT ONLINE: {bot.user} -----")
    print(f"Connected to {len(bot.guilds)} servers:")
    for guild in bot.guilds:
        print(f"- {guild.name} (ID: {guild.id})")
    try:
        # Sincroniza los comandos de slash con Discord
        synced: list[app_commands.AppCommand] = await tree.sync()
        print(f"[{len(synced)}] Comandos sincronizados.")
    except Exception as e:
        print(f"Error al sincronizar comandos: {e}")


# Inicia el bot
bot.run(config.TOKEN)
