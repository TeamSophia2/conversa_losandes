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
    async def addPdf(self, ctx):
        message = ctx.message
        # Verifica si se adjuntó un archivo al mensaje
        if len(message.attachments) > 0:
            file = message.attachments[0]
            # Verifica si el archivo es un PDF
            if file.filename.lower().endswith('.pdf'):
                # Obtiene los datos binarios del archivo PDF adjunto
                pdf_data = await file.read()

                # Lee y valida el archivo PDF
                tools = Tools()
                df = tools.readPdf(pdf_data)

                if df is not None:
                    await ctx.send('El archivo PDF ha sido procesado correctamente.')
                    # Convertir el DataFrame a una cadena y enviarlo en el mensaje
                    df_string = df.to_string(index=False)
                    await ctx.send(f"Contenido del DataFrame:\n```\n{df_string}\n```")
                    # Aquí puedes trabajar con el DataFrame 'df' que contiene el texto y el lenguaje.
                else:
                    await ctx.send('Ha ocurrido un error al procesar el archivo PDF.')

            else:
                await ctx.send('El archivo adjunto no es un PDF válido.')
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
