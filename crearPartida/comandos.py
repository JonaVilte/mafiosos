from discord.ext import commands
from crearPartida.roles import asignar_roles, reiniciar_partida
from dotenv import load_dotenv
import os
import discord

# Cargar variables de entorno
load_dotenv()
TOKEN = os.getenv('discordToken')

# Configurar intents
intents = discord.Intents.default()
intents.message_content = True

# Crear el bot
bot = commands.Bot(command_prefix="!mafia ", intents=intents)


# Variables globales de la partida
partida_activa = False
jugadores = []
max_jugadores = 0


@bot.command()
async def crear(ctx, numero_jugadores: int):
    """Crea una nueva partida."""
    global partida_activa, jugadores, max_jugadores

    if partida_activa:
        await ctx.send("⚠️ Ya hay una partida en curso. Usa `!mafia reiniciar` para empezar de nuevo.")
        return

    if numero_jugadores < 2:
        await ctx.send("❌ Necesitas al menos 2 jugadores para iniciar una partida.")
        return

    partida_activa = True
    max_jugadores = numero_jugadores
    jugadores.append(ctx.author)

    await ctx.send(f"🎲 ¡Nueva partida creada por {ctx.author.mention}! Se necesitan {max_jugadores} jugadores. Usa `!mafia unirme` para participar.")

@bot.command()
async def unirme(ctx):
    """Permite a los jugadores unirse a la partida."""
    global jugadores

    if not partida_activa:
        await ctx.send("❌ No hay una partida activa. Usa `!mafia crear <número>` para iniciar una.")
        return

    if ctx.author in jugadores:
        await ctx.send(f"{ctx.author.mention}, ya estás en la partida.")
        return

    jugadores.append(ctx.author)
    await ctx.send(f"✅ {ctx.author.mention} se ha unido a la partida. ({len(jugadores)}/{max_jugadores})")

    if len(jugadores) == max_jugadores:
        await asignar_roles(ctx)

@bot.command()
async def reiniciar(ctx):
    """Reinicia la partida."""
    reiniciar_partida()
    await ctx.send("🔄 La partida ha sido reiniciada. Usa `!mafia crear <número>` para empezar una nueva.")
