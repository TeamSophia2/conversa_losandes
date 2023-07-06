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
        self.tools = Tools()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Conectado como {self.bot.user}')
    
    @commands.command(name='addDocument')
    async def addDocument(self, ctx):
        message = ctx.message
        # Verifica si se adjuntó un archivo al mensaje
        if len(message.attachments) > 0:
            file = message.attachments[0]
            
            # Guardar el archivo adjunto en el directorio temporal
            with tempfile.NamedTemporaryFile(delete=False) as f:
                temp_filepath = f.name
                await file.save(f)

            # Lee y valida el archivo CSV
            df = self.tools.readCSV(temp_filepath)
            if df is not None:
                await ctx.send('El archivo CSV ha sido validado correctamente.')
                #print(df)
                # Envía el documento como un archivo CSV al canal

            # Eliminar el archivo temporal
            os.remove(temp_filepath)
        else:
            await ctx.send('No se ha adjuntado ningún archivo al mensaje.')


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Conectado como {bot.user}')
    bot.add_cog(BOT(bot))

# Inicia el bot
bot.run(TOKEN)
