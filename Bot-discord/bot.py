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
    
    
    @commands.command(name='addPdf')
    async def addDocument(self, ctx):
        message = ctx.message
        # Verifica si se adjuntó un archivo al mensaje
        if len(message.attachments) > 0:
            # Lee el archivo PDF desde el sistema de archivos en modo binario ('rb')
            with open('ruta_del_archivo.pdf', 'rb') as pdf_file:
                pdf_data = pdf_file.read()

            # Llama a la función readPdf con los datos del archivo PDF
            tools = Tools()
            df = tools.readPdf(pdf_data)
            
            # Verifica si se ha obtenido el DataFrame con el texto y el lenguaje
            if df is not None:
                print(df)
            else:
                print("Ha ocurrido un error al procesar el archivo PDF.")
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
