import random
import discord

# Variables de juego
partida_activa = False
jugadores = []
max_jugadores = 0

# Roles disponibles
roles = ["Mafioso", "Ciudadano", "Doctor", "Detective"]

async def asignar_roles(ctx):
    """Asigna roles aleatoriamente y los envía por mensaje privado."""
    global jugadores

    if len(jugadores) < 2:
        await ctx.send("❌ No hay suficientes jugadores para iniciar la partida.")
        return

    random.shuffle(jugadores)
    roles_asignados = random.choices(roles, k=len(jugadores))

    for i, jugador in enumerate(jugadores):
        try:
            await jugador.send(f"🔍 Tu rol en la partida es: **{roles_asignados[i]}**")
        except discord.Forbidden:
            await ctx.send(f"⚠️ No pude enviar mensaje privado a {jugador.mention}. Revisa tus ajustes de privacidad.")

    await ctx.send("🎭 ¡Todos los roles han sido asignados en privado! La partida comienza.")

def reiniciar_partida():
    """Reinicia los datos de la partida."""
    global partida_activa, jugadores, max_jugadores
    partida_activa = False
    jugadores = []
    max_jugadores = 0
