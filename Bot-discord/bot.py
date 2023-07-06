import os
import random
import discord
from discord.ext import commands
from utils.tools import Tools

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
            with open('documento.csv', 'wb') as f:
                await file.save(f)

            # Lee y valida el archivo CSV
            tools = Tools()
            df = tools.readCSV('documento.csv')
            if df is not None:
                await ctx.send('El archivo CSV ha sido validado correctamente.')
                #print(df)
                # conectarse a la base de datos y agregar
                os.remove('documento.csv')
            else:
                await ctx.send('El archivo CSV no cumple con las columnas requeridas.')
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
