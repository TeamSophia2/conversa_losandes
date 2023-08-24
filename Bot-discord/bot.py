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
import tiktoken
from llama_index import LLMPredictor, ServiceContext, SimpleDirectoryReader,Document, VectorStoreIndex, StorageContext, load_index_from_storage
from utils.langchainConfiguration import dbChain, QUERY
from langchain.chat_models import ChatOpenAI
import re

TOKEN = os.environ.get('DISCORD_TOKEN')
TOKEN_OPENAI = os.environ.get('OPENAI_API_KEY')
openai.api_key = TOKEN_OPENAI


#nlp = spacy.load("es_core_news_sm")

class BOT(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.es = Elasticsearch(["http://localhost:9200"])
        self.titulo = None

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
        dbConnector = databaseConnector()
        dbConnector.connect()

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
        dbConnector.insertDocuments(df)
        dbConnector.close()

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
                dbConnector = databaseConnector()

                # conectarse a la base de datos y agregar

                dbConnector.connect()
                dbConnector.insertDocuments(df)

                dbConnector.close()

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

    """
    @commands.command(name='search')
    async def search(self, ctx, *, palabraClave):
        # Realiza una consulta a Elasticsearch para buscar documentos que contengan la palabra clave en el título o abstract
        query = {
            "query": {
                "multi_match": {
                    "query": palabraClave,
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
        """
    ###Metodo que toma argumentos y hace consulta a elasticsearch para obtener documentos
    ###relacionados a los argumentos
    @commands.command(name='search')
    async def search(self, ctx, *, command):
        params = command.split(",")
        searchParams = {}

        for param in params:
            key, value = param.strip().split(":")
            searchParams[key] = value

        print("Parámetros de búsqueda:")
        for key, value in searchParams.items():
            print(f"{key}: {value}")

        # Realizar la búsqueda en Elasticsearch
        searchBody = {
            "query": {
                "bool": {
                    "must": [],
                    "filter": []
                }
            },
            "sort": [{"_score": {"order": "desc"}}],
            "size":5
        }
        ###si se pasa como argumento, no es obligacion
        if searchParams.get("region"):
            searchBody["query"]["bool"]["must"].append({"match": {"region": searchParams["region"]}})
        if searchParams.get("categoria"):
            searchBody["query"]["bool"]["must"].append({"match": {"category": searchParams["categoria"]}})
        if searchParams.get("comuna"):
            searchBody["query"]["bool"]["must"].append({"match": {"commune": searchParams["comuna"]}})
        if searchParams.get("laboratorio"):
            searchBody["query"]["bool"]["must"].append({"match": {"labTematico": searchParams["laboratorio"]}})
        if searchParams.get("keywords"):
            keywords = searchParams["keywords"].split(";")
            keywordQueries = [{"match": {"content": keyword}} for keyword in keywords]
            searchBody["query"]["bool"]["must"].extend(keywordQueries)
        """
        if search_params.get("fecha_inicio") or search_params.get("fecha_fin"):
            date_range = {}
            if search_params.get("fecha_inicio"):
                date_range["gte"] = search_params["fecha_inicio"]
            if search_params.get("fecha_fin"):
                date_range["lte"] = search_params["fecha_fin"]
            search_body["query"]["bool"]["filter"].append({"range": {"publicationYear": date_range}})
        """
        response = self.es.search(index="nuevo_indice", body=searchBody)

        # Obtener los resultados y formatearlos
        results = response["hits"]["hits"]
        formattedResults = "\n".join([f"{i+1}. **{hit['_source']['title']}** (Score: {hit['_score']:.2f}) [{hit['_source']['link']}]" for i, hit in enumerate(results)])

        # Enviar los resultados como mensaje a Discord
        if formattedResults:
            responseMessage = f"Los 5 documentos más importantes:\n{formattedResults}"
            await ctx.send(responseMessage)
        else:
            await ctx.send("No se encontraron documentos.")
 


    # busca en principalCategory

    @commands.command(name='searchTematicLine')
    async def searchTematicLine(self, ctx, principalCategoria):
        # Realiza la búsqueda en Elasticsearch por la principal categoría especificada
        searchBody = {
            "query": {
                "match": {
                    "principalCategory": principalCategoria
                }
            }
        }

        response = self.es.search(index="documentos", body=searchBody)

        # Procesa y muestra los resultados
        if "hits" in response and "hits" in response["hits"]:
            hits = response["hits"]["hits"]
            if len(hits) > 0:
                # Construye y envía el mensaje con los resultados
                resultMessage = "Resultados para la linea temática **{}**:\n".format(
                    principalCategoria)
                for hit in hits:
                    doc = hit["_source"]
                    resultMessage += "- **Título**: {}\n".format(doc["title"])
                    resultMessage += "  **URL**: {}\n".format(doc["url"])
                    resultMessage += "\n"

                await ctx.send(resultMessage)
            else:
                await ctx.send("No se encontraron resultados para la linea temática**{}**.".format(principalCategoria))
        else:
            await ctx.send("Ocurrió un error al buscar la linea temática **{}**.".format(principalCategoria))

    
    @commands.command(name='question')
    async def question(self,ctx, *, input_text):
        if self.titulo is None:
            # Si no hay un título registrado, se le pide al usuario que proporcione el título
            _, self.titulo = input_text.split(".", 1)
        else:
            # Si ya hay un título registrado, el usuario proporciona la pregunta
            question, _ = input_text.split(".", 1)     
        # Construir la consulta de Elasticsearch
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"match": {"title": self.titulo}}
                    ]
                }
            }
        }
        #Consulta la base de datos 
        response = self.es.search(index="test_index", body=query)

        
        #Procesar los resultados y enviar mensajes en Discord
        if "hits" in response and "hits" in response["hits"]:
            hits = response["hits"]["hits"]
            content_list = []
            #await ctx.send("A continuación los documentos mas relevantes:")
            if hits:
                hit = hits[0]
                source = hit["_source"]
                content= source.get("content", "Sin contenido")
                content_list.append(content)
                score = hit["_score"]
                #await ctx.send(f"Resultado {i}:\nContenido: {content}\nScore: {score}\n")
            #print(abstracts_with_high_score)        
        else:
            await ctx.send("No se encontraron resultados para los conceptos clave proporcionados.")
            #print("No se encontraron resultados para los conceptos clave proporcionados.")


        directory = "../../alvaro"  # Reemplaza con la ruta al directorio que deseas verificar
        file_name = "index_store.json"
        file_path = os.path.join(directory, file_name)

        


        if os.path.exists(file_path):
            print("YA EXISTE INDEX")

            # Rebuild storage context
            storage_context = StorageContext.from_defaults(persist_dir=directory)

            # Load index from the storage context
            new_index = load_index_from_storage(storage_context)

            query_engine = new_index.as_query_engine()

            await ctx.send(question)
            response = query_engine.query(question)
            await ctx.send(response)
            #print(response) 

        else:
            print("NO EXISTE INDEX")
            #Transforma la lista a documento
            content_doc = [Document(text=t) for t in content_list]

            llm_predictor = LLMPredictor(llm=ChatOpenAI(model_name="gpt-3.5-turbo"))
            service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor)

            #Vectoriza
            index = VectorStoreIndex.from_documents(content_doc,service_context=service_context)
         
            # Persist index to disk
            index.storage_context.persist(persist_dir=directory)
            
            query_engine = index.as_query_engine()

            await ctx.send(question)
            response = query_engine.query(question)
            await ctx.send(response) 
            #print(response)
            
    

    @commands.command(name='query')
    async def query(self,ctx, *, question):
        question_prompt = QUERY.format(question=question)
        response = dbChain.run(question_prompt)
        await ctx.send(response)


    @commands.command(name='commands')
    async def commands(self, ctx):
        help_message = (
            "**Comandos disponibles:**\n"
            "`!addManualDocument`: Agrega un documento manualmente. Uso: `!addManualDocument datos_del_documento`.\n"
            "`!addDocument`: Agrega documentos desde un archivo CSV adjunto. Uso: `!addDocument`.\n"
            "`!search palabra_clave`: Busca documentos por palabra clave en el título o abstract. Uso: `!search palabra_clave`.\n"
            "`!searchTematicLine tematica`: Busca documentos por linea temática. Uso: `!searchTematicLine tematica`.\n"
            "`!question pregunta titulo`: Realiza una pregunta al contenido del documento del titulo. Uso: `!question pregunta. titulo`."
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