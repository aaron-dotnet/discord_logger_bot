import logging

import discord
from discord import app_commands
from discord.ext import commands

import config
import controller
from bot import events
from bot.commands import setup_commands

# Loggin
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger: logging.Logger = logging.getLogger(__name__)

intents: discord.Intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Discord intents
bot: commands.Bot = commands.Bot(command_prefix="/", intents=intents)
tree: app_commands.CommandTree = bot.tree


def init_db():
    controller.connect_db()
    controller.create_tables()


@bot.event
async def on_message(message: discord.Message):
    if message.author == bot.user:
        return

    events.on_message(message)
    await bot.process_commands(message)


@bot.event
async def on_member_join(member: discord.Member):
    events.on_member_join(member)


@bot.event
async def on_ready():
    init_db()
    setup_commands(tree, bot)

    print(f"----- BOT ONLINE: {bot.user} -----")
    print(f"Connected to {len(bot.guilds)} servers:")
    for guild in bot.guilds:
        print(f"- {guild.name} (ID: {guild.id})")

    try:
        synced: list[app_commands.AppCommand] = await tree.sync()
        print(f"[{len(synced)}] Comandos sincronizados.")
    except Exception as e:
        print(f"Error al sincronizar comandos: {e}")


bot.run(config.TOKEN)
