import discord
from discord.ext import commands
import random
import os
import asyncio
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()
TOKEN = os.getenv('discordToken')

# Configurar intents y bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!mafia ", intents=intents)

# Variables de juego
partida_activa = False
jugadores = []
max_jugadores = 0
roles = ["Mafioso", "Ciudadano", "Doctor", "Detective"]
rol_jugadores = {}  

# Variables de fase del juego
fase_actual = "día"  
votos_mafia = {}  

@bot.event
async def on_ready():
    print(f'✅ Bot conectado como {bot.user}')

@bot.command()
async def crear(ctx, numero_jugadores: int):
    global partida_activa, jugadores, max_jugadores

    if partida_activa:
        await ctx.send("Ya hay una partida en curso. Usa `!mafia reiniciar` para empezar de nuevo.")
        return
    
    if numero_jugadores < 2:
        await ctx.send("Necesitas al menos 2 jugadores para iniciar una partida.")
        return

    partida_activa = True
    max_jugadores = numero_jugadores
    jugadores.append(ctx.author)

    await ctx.send(f"¡Partida creada por {ctx.author.mention}! Se necesitan {max_jugadores} jugadores. Usa `!mafia unirme` para participar.")

@bot.command()
async def unirme(ctx):
    global jugadores

    if not partida_activa:
        await ctx.send("No hay una partida activa. Usa `!mafia crear <número>` para iniciar una.")
        return

    if ctx.author in jugadores:
        await ctx.send(f"{ctx.author.mention}, ya estás en la partida.")
        return

    jugadores.append(ctx.author)
    await ctx.send(f"{ctx.author.mention} se ha unido a la partida. ({len(jugadores)}/{max_jugadores})")

    if len(jugadores) == max_jugadores:
        await asignar_roles(ctx)

async def asignar_roles(ctx):
    global partida_activa, jugadores, rol_jugadores

    random.shuffle(jugadores)
    roles_asignados = ["Mafioso"] + random.choices(roles[1:], k=len(jugadores) - 1)
    random.shuffle(roles_asignados)

    for i, jugador in enumerate(jugadores):
        rol_jugadores[jugador] = roles_asignados[i]
        try:
            await jugador.send(f"Tu rol en la partida es: **{roles_asignados[i]}**")
        except discord.Forbidden:
            await ctx.send(f"No pude enviar mensaje privado a {jugador.mention}. Revisa tus ajustes de privacidad.")
    
    # Crear canal privado solo para mafiosos y el bot
    guild = ctx.guild
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        bot.user: discord.PermissionOverwrite(view_channel=True, send_messages=True)
    }
    mafiosos = [jugador for jugador, rol in rol_jugadores.items() if rol == "Mafioso"]
    for mafioso in mafiosos:
        overwrites[mafioso] = discord.PermissionOverwrite(view_channel=True, send_messages=True)

    await guild.create_text_channel("mafia-noche", overwrites=overwrites)
    await ctx.send("¡Todos los roles han sido asignados en privado! La partida comienza.")

@bot.command()
async def reiniciar(ctx):
    global partida_activa, jugadores, max_jugadores, fase_actual, votos_mafia, rol_jugadores

    partida_activa = False
    jugadores = []
    max_jugadores = 0
    fase_actual = "día"
    votos_mafia.clear()
    rol_jugadores.clear()
    await ctx.send("Se reinicio la partida.")

@bot.command()
async def noche(ctx):
    global fase_actual, votos_mafia

    if fase_actual == "noche":
        await ctx.send("🌙 Ya estamos en la fase de noche.")
        return

    fase_actual = "noche"
    votos_mafia.clear()
    await ctx.send("🌙 La noche ha caído. Mafiosos, elijan a quién eliminar con `!matar <jugador>` en su canal privado.")

@bot.command()
async def matar(ctx, victima: str):
    global votos_mafia, fase_actual

    if fase_actual != "noche":
        await ctx.send("❌ No puedes matar a nadie durante el día.")
        return

    if ctx.author not in votos_mafia:
        votos_mafia[ctx.author] = victima
        await ctx.send(f"☠️ Has votado por eliminar a {victima}.")
    else:
        await ctx.send("❌ Ya has votado. Espera a la mañana.")

@bot.command()
async def amanecer(ctx):
    global fase_actual, votos_mafia

    if fase_actual != "noche":
        await ctx.send("🌞 Ya es de día.")
        return

    fase_actual = "día"

    if not votos_mafia:
        await ctx.send("🌞 Amaneció, pero nadie fue eliminado esta noche.")
        return

    victima_final = max(set(votos_mafia.values()), key=list(votos_mafia.values()).count)
    votos_mafia.clear()

    await ctx.send(f"🌞 Amaneció... y encontramos el cuerpo de **{victima_final}**. ¡Los ciudadanos están aterrorizados!")


# Iniciar el bot
bot.run(TOKEN)