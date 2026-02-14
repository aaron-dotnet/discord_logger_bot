import config   # bot token
import discord
from datetime import datetime
from dataclasses import dataclass
from discord import app_commands
from discord.ext import commands
import re

# Nuevo bot para hacer un log de usuarios.

# Message Content Intent (discord dev. portal)
intents : discord.Intents = discord.Intents.default()
intents.message_content = True

bot : commands.Bot = commands.Bot(command_prefix='/', intents=intents)
tree : app_commands.CommandTree = bot.tree

@dataclass
class DiscordUser:
    user_id: str
    user_Name: str
    display_names: list[str]
    avatar_url: str
    account_created: datetime
    joined_server: datetime
    roles: list[str]

# log de mensajes recibidos
@bot.event
async def on_message(message: discord.Message):
    if message.author == bot.user:
        return
    print(f'{message.author}: {message.content}')
    GetUserInfo(message.author)
    GetStuff(message.content)
    await bot.process_commands(message)


def GetUserInfo(member: discord.Member = None):
    # ToDo: testing, guardar en bd y refactorizar.

    embed = discord.Embed(title="User Info", color=discord.Color.blue())
    embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
    
    user_name: str = str(member)
    user_id: str = member.id
    display_name: str = member.display_name
    avatar_url: str = member.avatar.url if member.avatar else None
    account_created: datetime = member.created_at
    joined_server: datetime = member.joined_at
    roles: list[str]  = [role.name for role in member.roles if role.name != "@everyone"]
    
    discord_user = DiscordUser(user_name,user_id, display_name, avatar_url, account_created,joined_server,roles)
    print("done")
    print(discord_user.roles)

# rescatamos cositas interesantes:
def GetStuff(content: str):
    url_pattern = r"(?:(?:https?|ftp|file)://|www\.|ftp\.)(?:\([-A-Z0-9+&@#/%=~_|$?!:,.]*\)|[-A-Z0-9+&@#/%=~_|$?!:,.])*(?:\([-A-Z0-9+&@#/%=~_|$?!:,.]*\)|[A-Z0-9+&@#/%=~_|$])"
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    
    urls = GetAllMatches(url_pattern, content)
    emails = GetAllMatches(email_pattern, content)
    print(urls)
    print(emails)

# funcion general para expandir los futuros patterns
def GetAllMatches(regex_pattern:str ,content: str) -> list[str] | None:
    all_matches: list[str] = re.findall(regex_pattern, content)
    if all_matches != None:
        return all_matches
    
    return None


# para mantener el canal limpio
@tree.command(name="purge", description="Borra los ultimos 100 mensajes recientes")
async def purge(ctx: commands.Context):
    try:
        deleted = await ctx.channel.purge(limit=100)
        await ctx.send(f'Borrados {len(deleted)} mensajes.', delete_after=5)
    except Exception as e:
        await ctx.send(f'No se pudieron borrar los mensajes: {e}')


@bot.event
async def on_ready():
    print(f'----- BOT ONLINE: {bot.user} -----')
    try:
        # Sincroniza los comandos de slash con Discord
        synced: list[app_commands.AppCommand] = await tree.sync()
        print(f'[{len(synced)}] Comandos sincronizados.')
    except Exception as e:
        print(f'Error al sincronizar comandos: {e}')


# Inicia el bot
bot.run(config.TOKEN)