import os
import random
import discord
from discord.ext import commands
from utils.tools import Tools

TOKEN = os.environ.get('DISCORD_TOKEN')

class BOT(discord.Client):
    async def on_ready(self):
        print(f'Conectado como {self.user}')

    async def addDocument(self, message):
        # Verifica si se adjuntó un archivo al mensaje
        if len(message.attachments) > 0:
            file = message.attachments[0]
            # Guarda el archivo en el sistema
            with open('documento.csv', 'wb') as f:
                await file.save(f)

            # Lee y valida el archivo CSV
            tools = Tools()
            df = tools.readCSV('documento.csv')
            if df is not None:
                await message.channel.send('El archivo CSV ha sido validado correctamente.')
                print(df)
                # Envía el documento como un archivo CSV al canal
                #conectarse a la base de datos y agregar
            else:
                await message.channel.send('El archivo CSV no cumple con las columnas requeridas.')
        else:
            await message.channel.send('No se ha adjuntado ningún archivo al mensaje.')

intents = discord.Intents.default()
bot = BOT(intents=intents)

@bot.event
async def on_ready():
    print(f'Conectado como {bot.user}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith('!add'):
        print("hola")
        await bot.addDocument(message)
        print("chao")

# Inicia el bot
bot.run(TOKEN)
