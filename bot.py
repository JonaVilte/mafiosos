from crearPartida.comandos import bot, TOKEN

@bot.event
async def on_ready():
    print(f'✅ Bot conectado como {bot.user}')


# Iniciar el bot
bot.run(TOKEN)
