import os
import random
import discord
from discord.ext import commands
from utils.tools import Tools
import tempfile

TOKEN = os.environ.get('DISCORD_TOKEN')

class BOT(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Conectado como {self.bot.user}')
    
    @commands.command(name='addDocument')
    async def addDocument(self, ctx):
        message = ctx.message
        # Verifica si se adjuntó un archivo al mensaje
        if len(message.attachments) > 0:
            file = message.attachments[0]
            # Guarda el archivo en el sistema
            # Guardar el archivo adjunto en el directorio temporal
            
            file_data = await file.read()
            # Lee y valida el archivo CSV
            tools = Tools()
            df = tools.readCSV(file_data)
            if df is not None:
                await ctx.send('El archivo CSV ha sido validado correctamente.')
                #print(df)
                # conectarse a la base de datos y agregar
            else:
                await ctx.send('El archivo CSV no cumple con las columnas requeridas.')
        else:
            await ctx.send('No se ha adjuntado ningún archivo al mensaje.')
    
    @commands.command(name='addPdf')  # Agregar el comando para agregar el PDF
    async def addPdf(self, ctx):
        message = ctx.message
        # Verifica si se adjuntó un archivo al mensaje
        if len(message.attachments) > 0:
            file = message.attachments[0]
            # Guarda el archivo en el sistema
            # Guardar el archivo adjunto en el directorio temporal
            
            file_data = await file.read()
            # Leer y procesar el archivo PDF
            tools = Tools()
            df = tools.readPdf(file_data)
            if df is not None:
                await ctx.send('El archivo PDF ha sido procesado correctamente.')
                print(df)
                # conectarse a la base de datos y agregar
            else:
                await ctx.send('No se pudo procesar el archivo PDF.')
        else:
            await ctx.send('No se ha adjuntado ningún archivo al mensaje.')


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Conectado como {bot.user}')
    await bot.add_cog(BOT(bot))

# Inicia el bot
bot.run(TOKEN)
