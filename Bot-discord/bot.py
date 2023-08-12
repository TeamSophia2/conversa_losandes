import os
from utils.databaseConnector import databaseConnector
from utils.scraper import Scraper
import asyncio
import discord
from discord.ext import commands
from utils.tools import Tools
import pandas as pd
from elasticsearch import Elasticsearch
import openai
import spacy

TOKEN = os.environ.get('DISCORD_TOKEN')
nlp = spacy.load("es_core_news_sm")

class BOT(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.es = Elasticsearch(["http://localhost:9200"])

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Conectado como {self.bot.user}')

    @commands.command(name='addManualDocument')
    async def addManualDocument(self, ctx, *, data_str: str):
        # Parsea los datos ingresados manualmente
        inputData = data_str.split(',')
        if len(inputData) != 10:  # Ajusta este valor según el número de columnas en tu CSV
            await ctx.send("El formato no es válido. Asegúrate de proporcionar todos los datos requeridos.")
            return

        # Obtener los datos ingresados manualmente
        lt, authors, title, año, revista, doi, categoria, region, comunas, url = map(
            str.strip, inputData)

        # Realiza el procesamiento de los datos y agrega el documento a la base de datos
        db_connector = databaseConnector()
        db_connector.connect()

        # Creamos un DataFrame a partir de los datos ingresados manualmente
        data = {
            "LT": [lt],
            "AUTORES/AS": [authors],
            "TÍTULO": [title],
            "AÑO": [año],
            "REVISTA": [revista],
            "DOI": [doi],
            "CATEGORÍA": [categoria],
            "REGIÓN": [region],
            "COMUNAS": [comunas],
            "Enlace": [url if url.lower() != 'no' else None],
        }
        df = pd.DataFrame(data)
        # Realizar el mismo proceso que en el comando !addDocument para guardar el documento en la base de datos
        db_connector.insertDocuments(df)
        db_connector.close()

        scraper = Scraper()
        tasks = []
        for _, row in df.iterrows():
            title = row['TÍTULO']
            url = row['Enlace']
            if pd.notna(url) and url.strip().lower() != 'nan':
                task = asyncio.create_task(
                    scraper.downloadDocument(title, url))
                tasks.append(task)
            else:
                print(
                    f"El documento '{title}' no tiene una URL válida. Se omitirá la descarga.")

        # Esperar a que todas las tareas de descarga terminen
        await asyncio.gather(*tasks)

        await ctx.send('Documento agregado.')

    @commands.command(name='addDocument')
    async def addDocument(self, ctx):
        message = ctx.message
        # Verifica si se adjuntó un archivo al mensaje
        if len(message.attachments) > 0:
            file = message.attachments[0]

            fileData = await file.read()

            # Lee y valida el archivo CSV
            tools = Tools()
            df = tools.readCsv(fileData)
            if df is not None:
                await ctx.send('El archivo CSV cumple con las columnas requeridas')
                # print(df)
                db_connector = databaseConnector()

                # conectarse a la base de datos y agregar

                db_connector.connect()
                db_connector.insertDocuments(df)

                db_connector.close()

                await ctx.send('Información del archivo CSV guardado en la base de datos')

                await ctx.send('Descargando documentos..')
                scraper = Scraper()

                # inicia las descargas y el guardado en la base de datos en segundo plano
                tasks = []
                for _, row in df.iterrows():
                    title = row['TÍTULO']
                    url = row['Enlace']
                    if pd.notna(url) and url.strip().lower() != 'nan':
                        task = asyncio.create_task(
                            scraper.downloadDocument(title, url))
                        tasks.append(task)
                    else:
                        print(
                            f"El documento '{title}' no tiene una URL válida. Se omitirá la descarga.")

                # Esperar a que todas las tareas de descarga terminen (opcional, puede que no sea necesario)
                await asyncio.gather(*tasks)

                await ctx.send('Documentos descargados.')

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
                df = tools.readCsv(pdf_data)

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

    # busca en el titulo y en abstract alguna palabra clave

    @commands.command(name='search')
    async def buscar(self, ctx, *, palabra_clave):
        # Realiza una consulta a Elasticsearch para buscar documentos que contengan la palabra clave en el título o abstract
        query = {
            "query": {
                "multi_match": {
                    "query": palabra_clave,
                    "fields": ["title", "abstract"]
                }
            }
        }

        # Realiza la búsqueda en Elasticsearch
        response = self.es.search(index="documentos", body=query)

        # Procesa los resultados y envía los mensajes en Discord
        if "hits" in response and "hits" in response["hits"]:
            hits = response["hits"]["hits"]
            for i, hit in enumerate(hits, start=1):
                source = hit["_source"]
                title = source.get("title", "Sin título")
                abstract = source.get("abstract", "Sin resumen")
                await ctx.send(f"Resultado {i}:\nTítulo: {title}\nResumen: {abstract}\n")
        else:
            await ctx.send("No se encontraron resultados para la palabra clave proporcionada.")

    # busca en principalCategory

    @commands.command(name='searchTematicLine')
    async def buscar_por_principal_categoria(self, ctx, principal_categoria):
        # Realiza la búsqueda en Elasticsearch por la principal categoría especificada
        search_body = {
            "query": {
                "match": {
                    "principalCategory": principal_categoria
                }
            }
        }

        response = self.es.search(index="documentos", body=search_body)

        # Procesa y muestra los resultados
        if "hits" in response and "hits" in response["hits"]:
            hits = response["hits"]["hits"]
            if len(hits) > 0:
                # Construye y envía el mensaje con los resultados
                result_message = "Resultados para la linea temática **{}**:\n".format(
                    principal_categoria)
                for hit in hits:
                    doc = hit["_source"]
                    result_message += "- **Título**: {}\n".format(doc["title"])
                    result_message += "  **URL**: {}\n".format(doc["url"])
                    result_message += "\n"

                await ctx.send(result_message)
            else:
                await ctx.send("No se encontraron resultados para la linea temática**{}**.".format(principal_categoria))
        else:
            await ctx.send("Ocurrió un error al buscar la linea temática **{}**.".format(principal_categoria))

    
    @commands.command(name='question')
    async def question(self,ctx, *, question):
        # Analiza sintácticamente la pregunta utilizando spaCy en español, se crea un objeto doc que representa el analisis sintactico
        # y linguistico del texto proporcionado en la pregunta.
        doc = nlp(question)

        # Extrae sustantivos y adjetivos como conceptos clave, incluyendo los que están después de un artículo
        nouns_adjectives_and_proper_nouns = []
        i = 0
        
        while i < len(doc):
            token = doc[i]
            if token.pos_ == "DET" and i + 1 < len(doc) and doc[i+1].pos_ == "NOUN":
                j = i + 2
                
                nouns_adjectives_and_proper_nouns.append(f"{token.text} {doc[i+1:j].text}")  # Agrega el artículo y el sustantivo con lo que sigue
                i = j  # Salta al índice después de lo que sigue
            elif token.pos_ == "NOUN" or token.pos_ == "ADJ" or token.ent_type_ == "PROPN":
                nouns_adjectives_and_proper_nouns.append(token.text)  # Agrega el sustantivo, adjetivo o nombre propio
                i += 1  # Avanza al siguiente token
            else:
                i += 1

                
        extracted_question = ', '.join(nouns_adjectives_and_proper_nouns)

        #await ctx.send(f"Sustantivos y conceptos clave: {extracted_question}")
        print(extracted_question)
            
        """query = {
            "query": {
                "multi_match": {
                    "query": keywords,
                    "fields": ["abstract"]
                }
            }
        }
        # Consulta la base de datos 
        response = self.es.search(index="documentos", body=query)

    
            
        #responder la pregunta utilizando OpenAI
        response = openai.Completion.create(
            engine="davinci",
            prompt=question,
            max_tokens=50
        )
        await ctx.send(response.choices[0].text.strip())"""
    

    @commands.command(name='commands')
    async def commands(self, ctx):
        help_message = (
            "**Comandos disponibles:**\n"
            "`!addManualDocument`: Agrega un documento manualmente. Uso: `!addManualDocument datos_del_documento`.\n"
            "`!addDocument`: Agrega documentos desde un archivo CSV adjunto. Uso: `!addDocument`.\n"
            "`!search palabra_clave`: Busca documentos por palabra clave en el título o abstract. Uso: `!search palabra_clave`.\n"
            "`!searchTematicLine tematica`: Busca documentos por linea temática. Uso: `!searchTematicLine tematica`."
        )
        await ctx.send(help_message)


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
    print(f'Conectado como {bot.user}')
    await bot.add_cog(BOT(bot))

# Inicia el bot
bot.run(TOKEN)