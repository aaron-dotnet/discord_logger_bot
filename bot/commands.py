from discord.ext import commands


def setup_commands(tree, bot):
    @tree.command(name="purge", description="Borra los ultimos 100 mensajes recientes")
    async def purge(ctx: commands.Context):
        try:
            deleted = await ctx.channel.purge(limit=100)  # type:ignore
            await ctx.send(f"Borrados {len(deleted)} mensajes.", delete_after=5)
        except Exception as e:
            await ctx.send(f"No se pudieron borrar los mensajes: {e}")
