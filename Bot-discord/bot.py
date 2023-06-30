import os
import random
import discord
from discord.ext import commands

TOKEN = os.environ.get('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)
bot = commands.Bot(command_prefix='!')

@bot.command(name='roll', help='Simula el lanzamiento de un dado. Usa !roll numdados numlados')
async def roll(ctx, number_of_dice: int, number_of_sides: int): #importante el Converter :int
    dice = [
        str(random.choice(range(1, number_of_sides + 1)))
        for _ in range(number_of_dice)
    ]
    await ctx.send(', '.join(dice))

bot.run(TOKEN)
