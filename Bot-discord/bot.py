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
            
            # Lee y valida el archivo CSV
            tools = Tools()
            df = await tools.readCSV(file)
            if df is not None:
                await ctx.send('El archivo CSV ha sido validado correctamente.')
                #print(df)
                # 
                # conectarse a la base de datos y agregar
                #...
            else:
                await ctx.send('El archivo CSV no cumple con las columnas requeridas.')
        else:
            await ctx.send('No se ha adjuntado ningún archivo al mensaje.')


intents = discord.Intents.default()
intents.messages = True  # Habilitar el permiso intents.MessageContent

bot = commands.Bot(command_prefix='!', intents=intents)

# Agregar el cog al bot
bot.add_cog(BOT(bot))

# Inicia el bot
bot.run(TOKEN)
