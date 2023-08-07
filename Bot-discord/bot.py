import os

from utils.databaseConnector import databaseConnector
from utils.scraper import Scraper
import asyncio
import discord
from discord.ext import commands
from utils.tools import Tools
import pandas as pd

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
                await ctx.send('El archivo CSV cumple con las columnas requeridas')
                # print(df)
                db_connector = databaseConnector()

                # conectarse a la base de datos y agregar

                db_connector.connect()
                db_connector.insertDocuments(df)

                db_connector.close()

                scraper = Scraper()

                # inicia las descargas y el guardado en la base de datos en segundo plano
                tasks = []
                for _, row in df.iterrows():
                    title = row['TÍTULO']
                    url = row['Enlace']
                    if pd.notna(url) and url.strip().lower() != 'nan':
                        # Pasa el semáforo a la tarea para limitar las descargas simultáneas
                        task = asyncio.create_task(
                            scraper.downloadDocument(title, url))
                        tasks.append(task)
                    else:
                        print(
                            f"El documento '{title}' no tiene una URL válida. Se omitirá la descarga.")

                # Esperar a que todas las tareas de descarga terminen (opcional, puede que no sea necesario)
                await asyncio.gather(*tasks)

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
                    # Convierte el DataFrame a un formato legible (por ejemplo, a formato tabular)
                    df_str = df.to_string(index=False)

                    # Divide el contenido del DataFrame en partes más pequeñas
                    MAX_MESSAGE_LENGTH = 1500
                    messages = [df_str[i:i + MAX_MESSAGE_LENGTH]
                                for i in range(0, len(df_str), MAX_MESSAGE_LENGTH)]

                    # Envía cada parte del mensaje en Discord
                    for i, message in enumerate(messages, start=1):
                        await ctx.send(f'Parte {i}/{len(messages)}:\n```{message}```')
                else:
                    await ctx.send('Ha ocurrido un error al procesar el archivo PDF.')

            else:
                await ctx.send('El archivo adjunto no es un PDF válido.')
        else:
            await ctx.send('No se ha adjuntado ningún archivo al mensaje.')

    @commands.command(name='ping')
    async def ping(self, ctx):
        await ctx.send('Pong!')


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
    print(f'Conectado como {bot.user}')
    await bot.add_cog(BOT(bot))

# Inicia el bot
bot.run(TOKEN)
