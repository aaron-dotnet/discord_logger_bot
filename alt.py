import discord
from discord import app_commands
from discord.ext import commands

import config  # bot token

"""
BOT ALTERNATIVO,
SOLO PARA COMPATIBILIDAD
NO ELIMINAR
"""


# Message Content Intent (discord dev. portal)
intents: discord.Intents = discord.Intents.default()
intents.message_content = True

bot: commands.Bot = commands.Bot(command_prefix="/", intents=intents)
tree: app_commands.CommandTree = bot.tree


def cow_say(msg: str) -> str:
    BASE: int = 300  # reservado para los caracteres necesarios del formato
    LARGO: int = len(msg)

    if LARGO + BASE > 2000:
        return "Limite de caracteres excedido. Muuu... :cow:"

    guiones: str = ""
    MAX_GUIONES: int = 80

    if LARGO <= MAX_GUIONES:
        guiones = "-" * len(msg)
    else:
        guiones = "-" * MAX_GUIONES

    cow: str = f"""
  {guiones}
< {msg} >
  {guiones}
     \\   ^__^
      \\  (oo)\\_______
         (__)\\       )\\/\\
             ||----w |
             ||     ||"""

    return f"```{cow}```"


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


@tree.command(name="cowsay", description="Responde con un mensaje usando el cow_say")
@app_commands.describe(mensaje="El mensaje que quieres mostrar")
async def cowsay_slash(interaction: discord.Interaction, mensaje: str):
    """
    Envía un mensaje formateado con cow_say.
    """
    try:
        cow_saying: str = cow_say(mensaje)
        await interaction.response.send_message(f"{cow_saying}")
    except Exception as e:
        await interaction.response.send_message(
            f"Ocurrio un error: {e}", ephemeral=True
        )


@tree.command(name="userinfo", description="Muestra información del usuario mencionado")
@app_commands.describe(member="El usuario del que quieres ver información (opcional)")
async def userinfo_slash(
    interaction: discord.Interaction,
    member: discord.Member = None,  # type:ignore
):
    # todo: ~~sacar conexiones del usuario~~
    # note: no es posible usando bots :(
    """
    Muestra información del usuario mencionado en formato embed.
    """
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


@tree.command(
    name="guay", description="Muestra el nivel de guay del usuario mencionado"
)
@app_commands.describe(member="El usuario del que quieres su nivel de guay")
async def guay_slash(interaction: discord.Interaction, member: discord.Member = None):  # type:ignore
    """
    Muestra el nivel de guay del usuario mencionado.
    """
    from random import randint

    MINIMO: int = 0
    MAXIMO: int = 100

    guay_nivel: int = randint(MINIMO, MAXIMO)
    target_member: discord.Member = member or interaction.user

    bar_length: int = 10  # Cada 10% es un bloque
    filled_length: int = int(bar_length * guay_nivel / MAXIMO)
    bar: str = "🤟🏻" * filled_length + "-" * (bar_length - filled_length)

    color_value: discord.Color
    icono: str = ""
    if guay_nivel <= 30:
        color_value = discord.Color.red()
        icono = "😔"
    elif guay_nivel <= 50:
        color_value = discord.Color.orange()
        icono = "😐"
    elif guay_nivel <= 70:
        color_value = discord.Color.yellow()
        icono = "🙂"
    else:
        color_value = discord.Color.green()
        icono = "😎"

    embed = discord.Embed(title=f"Guay Level     {icono}", color=color_value)
    embed.add_field(name="User", value=target_member.mention, inline=True)
    embed.add_field(name="Guay Level", value=f"{guay_nivel}%", inline=True)
    embed.add_field(name="Progress", value=bar, inline=False)
    embed.set_thumbnail(url=target_member.avatar.url if target_member.avatar else None)

    await interaction.response.send_message(embed=embed)


@bot.command()
async def purge(ctx: commands.Context):
    """
    Borra los ultimos 100 mensajes.
    """
    try:
        deleted = await ctx.channel.purge()  # type:ignore
        await ctx.send(f"Borrados {len(deleted)} mensajes.", delete_after=5)
    except Exception as e:
        await ctx.send(f"No se pudieron borrar los mensajes: {e}")


# @bot.command()
async def dmx(ctx: commands.Context, *, message_content: str):
    """
    Envia un mensaje directo con cow_say al usuario con ID especificado.
    """
    user_id: int = 1234
    try:
        user = await bot.fetch_user(user_id)
        message_content = cow_say(message_content)
        await user.send(f"{message_content}")
        print(f"DM enviado a {user.name}.")
    except Exception as e:
        await ctx.send(f"No se pudo enviar el mensaje: {e}")


# Inicia el bot
bot.run(config.TOKEN2)
