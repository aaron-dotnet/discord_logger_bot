import discord
from discord import app_commands
from discord.ext import commands

import config  # bot token

"""
BOT ALTERNATIVO,
SOLO PARA REFERENCIAS
"""


# Message Content Intent (discord dev. portal)
intents: discord.Intents = discord.Intents.default()
intents.message_content = True

bot: commands.Bot = commands.Bot(command_prefix="/", intents=intents)
tree: app_commands.CommandTree = bot.tree


@bot.event
async def on_ready():
    print(f"----- BOT ONLINE: {bot.user} -----")
    print(f"Connected to {len(bot.guilds)} servers:")
    for guild in bot.guilds:
        print(f"- {guild.name} (ID: {guild.id})")
    try:
        # Sincroniza los comandos de slash con Discord
        synced = await tree.sync()
        print(f"Sincronizados {len(synced)} comandos de slash.")
    except Exception as e:
        print(f"Error al sincronizar comandos: {e}")


# log de mensajes recibidos
@bot.event
async def on_message(message: discord.Message):
    if message.author == bot.user:
        return
    print(f"{message.author}: {message.content}")
    await bot.process_commands(message)


# ==================== SLASH COMMANDS ====================


@tree.command(name="userinfo", description="Ger discord user information")
@app_commands.describe(member="Select an user (Optional)")
async def userinfo_slash(interaction: discord.Interaction, member: discord.Member):
    target_member: discord.Member = member or interaction.user
    roles = [role.name for role in target_member.roles if role.name != "@everyone"]

    embed = discord.Embed(title="User Info", color=discord.Color.blue())
    embed.set_thumbnail(url=target_member.avatar.url if target_member.avatar else None)
    embed.add_field(name="Username", value=str(target_member), inline=True)
    embed.add_field(name="User ID", value=target_member.id, inline=True)

    embed.add_field(name="User Activity", value=target_member.activity, inline=False)
    embed.add_field(
        name="User Display Name", value=target_member.display_name, inline=False
    )

    embed.add_field(
        name="Account Created",
        value=target_member.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        inline=False,
    )
    embed.add_field(
        name="Joined Server",
        value=target_member.joined_at.strftime("%Y-%m-%d %H:%M:%S"),  # type: ignore
        inline=False,
    )
    embed.add_field(
        name="Roles", value=", ".join(roles) if roles else "No Roles", inline=False
    )

    await interaction.response.send_message(embed=embed)


@bot.command()
async def send_DM(ctx: commands.Context, *, message_content: str):
    """
    Envia un mensaje directo con cow_say al usuario con ID especificado.
    """
    user_id: int = 1234
    try:
        user: discord.User = await bot.fetch_user(user_id)
        message_content = "hello world"

        await user.send(message_content)
        print(f"DM enviado a {user.name}.")
    except Exception as e:
        await ctx.send(f"No se pudo enviar el mensaje: {e}")


# Inicia el bot
bot.run(config.TOKEN_OLD)
