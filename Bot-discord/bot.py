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
from llama_index import LLMPredictor, ServiceContext, SimpleDirectoryReader,Document, VectorStoreIndex, StorageContext, load_index_from_storage
from llama_index.node_parser import SimpleNodeParser
from llama_index.storage.storage_context import StorageContext
from utils.langchainConfiguration import dbChain, QUERY
from langchain.chat_models import ChatOpenAI
import re
from discord import Embed
from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.chains.question_answering import load_qa_chain
from langchain.chains import RetrievalQA
import chromadb
from chromadb.utils import embedding_functions
from langchain.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter, TokenTextSplitter
#from langchain.schema import Document
from langchain.chains import VectorDBQA, RetrievalQA
from llama_index.vector_stores import ChromaVectorStore
from chromadb.config import Settings
import pinecone
from llama_index.vector_stores import PineconeVectorStore, WeaviateVectorStore
import logging
import sys
import weaviate
import PyPDF2
import mysql.connector
from langchain.prompts import PromptTemplate
import io
import gc
from memory_profiler import profile
import matplotlib.pyplot as plt
from discord import File
import subprocess


TOKEN = os.environ.get('DISCORD_TOKEN')
TOKEN_OPENAI = os.environ.get('OPENAI_API_KEY')

PINECONE_API_KEY = "5db87f39-0d3c-46cd-b782-7452ac788fa3"
PINECONE_ENVIRONMENT = "gcp-starter"


env_vars = {TOKEN,TOKEN_OPENAI}
openai.api_key = TOKEN_OPENAI
#nlp = spacy.load("es_core_news_sm")

class BOT(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.es = Elasticsearch(["http://localhost:9200"])
        self.titulo = None

        self.index = pinecone.Index("llama-index-intro")
        self.vector_store = PineconeVectorStore(pinecone_index=self.index)
        self.loaded_index = VectorStoreIndex.from_vector_store(vector_store=self.vector_store)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Conectado como {self.bot.user}')

    @commands.command(name='addManualDocument')
    async def addManualDocument(self, ctx, *, data_str: str):
        # Parsea los datos ingresados manualmente
        inputData = data_str.split(',')
        print("inputData:", inputData)
        if len(inputData) != 10:  # Ajusta este valor según el número de columnas en tu CSV
            await ctx.send("El formato no es válido. Asegúrate de proporcionar todos los datos requeridos.")
            return

        # Obtener los datos ingresados manualmente
        lt, authors, title, año, revista, doi, categoria, region, comunas, url = map(str.strip, inputData)

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
        print(df)
        # Realizar el mismo proceso que en el comando !addDocument para guardar el documento en la base de datos
        await db_connector.insertsDocuments(df)
        db_connector.close()

        failedDownloads = []
        scraper = Scraper()
        tasks = []
        for _, row in df.iterrows():
            title = row['TÍTULO']
            url = row['Enlace']

            if pd.notna(url) and url.strip().lower() != 'nan':
                
            # Conectar a la base de datos y verificar si el título ya existe
                db_connector = databaseConnector()
                db_connector.connect()
                cursor = db_connector.connection.cursor()

                cursor.execute("SELECT content FROM Document WHERE title = %s", (title,))
                existing_content = cursor.fetchone()
                #print(existing_content)
                if existing_content == (None,):
                    #db_connector.insertsDocuments(df)  # Conectar y agregar documentos a la base de datos
                    #db_connector.close()  # Cierra la conexión a la base de datos
                    # Ejecutar las operaciones de descarga y lectura en un subproceso usando run_in_executor
                    try:
                        print("Antes de la llamada")
                        await asyncio.create_task(scraper.downloadDocument(title, url, failedDownloads))
                        print("Después de la llamada")
                    except Exception as e:
                        print(f"Error durante la ejecución de downloadDocument: {e}")
                        failedDownloads.append(title)
                    
                else:
                    # El documento ya existe en la base de datos, y 'existing_content' contiene el contenido previamente guardado.
                    db_connector.close()  # Cierra la conexión a la base de datos
                    print(f"El documento '{title}' ya existe en la base de datos. No es necesario descargarlo nuevamente.")
            else:
                failedDownloads.append(title)
                print(f"El documento '{title}' no tiene una URL válida. Se omitirá la descarga.")

        # Esperar a que todas las tareas de descarga terminen
        

        if failedDownloads:
            await ctx.send('El documento no pudo ser guardado')
            
        else:     
            await ctx.send('Documento agregado a la base de datos')

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
                
                # Conectarse a la base de datos y agregar
                db_connector = databaseConnector()
                db_connector.connect()
                await db_connector.insertsDocuments(df)
                db_connector.close()

                await ctx.send('Información del archivo CSV guardado en la base de datos')

                await ctx.send('Descargando documentos y guardando información en segundo plano')
                # Crear una instancia de la clase Scraper

                scraper = Scraper()

                
                # Inicia las descargas y el guardado en la base de datos en segundo plano
                tasks = []
                failedDownloads = []
                for _, row in df.iterrows():
                    title = row['TÍTULO']
                    url = row['Enlace']

                    if pd.notna(url) and url.strip().lower() != 'nan':
                    # Conectar a la base de datos y verificar si el título ya existe
                        db_connector = databaseConnector()
                        db_connector.connect()
                        cursor = db_connector.connection.cursor()

                        cursor.execute("SELECT content FROM Document WHERE title = %s", (title,))
                        existing_content = cursor.fetchone()
                        #print(existing_content)
                        if existing_content == (None,):
                            #db_connector.insertsDocuments(df)  # Conectar y agregar documentos a la base de datos
                            #db_connector.close()  # Cierra la conexión a la base de datos
                            # Ejecutar las operaciones de descarga y lectura en un subproceso usando run_in_executor
                            try:
                                print("Antes de la llamada")
                                await asyncio.create_task(scraper.downloadDocument(title, url, failedDownloads))
                                print("Después de la llamada")
                            except Exception as e:
                                print(f"Error durante la ejecución de downloadDocument: {e}")
                                failedDownloads.append(title)
                            
                        else:
                            # El documento ya existe en la base de datos, y 'existing_content' contiene el contenido previamente guardado.
                            db_connector.close()  # Cierra la conexión a la base de datos
                            print(f"El documento '{title}' ya existe en la base de datos. No es necesario descargarlo nuevamente.")
                    else:
                        failedDownloads.append(title)
                        print(f"El documento '{title}' no tiene una URL válida. Se omitirá la descarga.")

                # Esperar a que todas las tareas finalicen
              
                 
                await ctx.send('Documentos descargados y agregados a la base de datos.')
                if failedDownloads:
                    await ctx.send(f'Estos documentos no pudieron ser agregados a la base de datos:')

                    resultsPerPage = 5
                    totalPages = (len(failedDownloads) + resultsPerPage - 1) // resultsPerPage

                    page = 1

                    while page <= totalPages:
                        start_index = (page - 1) * resultsPerPage
                        end_index = min(start_index + resultsPerPage, len(failedDownloads))
                        currentPageResults = failedDownloads[start_index:end_index]

                        formattedPageResults = "\n".join([f"{i + 1}. {result}\n" for i, result in enumerate(currentPageResults)])
                        embed = Embed(title=f"Página {page} de {totalPages}", description=formattedPageResults)

                        message = await ctx.send(embed=embed)

                        # Agregar las reacciones al mensaje
                        reactions = []
                        if totalPages > 1:
                            if page > 1:
                                reactions.append('⏪')  # Botón para ir a la primera página
                                reactions.append('⬅️')  # Botón para retroceder una página
                            if page < totalPages:
                                reactions.append('➡️')  # Botón para avanzar una página
                                reactions.append('⏩')  # Botón para ir a la última página

                        for reaction in reactions:
                            await message.add_reaction(reaction)

                        if totalPages > 1:
                            def check(reaction, user):
                                return user == ctx.author and reaction.message == message

                            try:
                                reaction, _ = await self.bot.wait_for('reaction_add', timeout=300.0, check=check)

                                if reaction.emoji == '⬅️' and page > 1:
                                    page -= 1
                                elif reaction.emoji == '➡️' and page < totalPages:
                                    page += 1
                                elif reaction.emoji == '⏪':
                                    page = 1  # Ir a la primera página
                                elif reaction.emoji == '⏩':
                                    page = totalPages  # Ir a la última página

                                await message.delete()
                            except asyncio.TimeoutError:
                                break
                        else:
                            break


            else:
                await ctx.send('El archivo CSV no cumple con las columnas requeridas. Vuelva a ejecutar el comando incluyendo un archivo valido')
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

    @commands.command(name='getTesis')
    async def getTesis(self, ctx):
        scraper = Scraper()
        await ctx.send('Iniciando obtención de tesis en segundo plano. Se notificará cuando termine.')

        file_path = await scraper.scrapeTesis()

        # Verificar si el archivo existe antes de enviarlo
        if file_path and os.path.exists(file_path):
            with open(file_path, 'rb') as file:
                csv_file = discord.File(file, filename='tesis_data_listo.csv')
                await ctx.send('Obtencion de tesis completado. Aquí está el archivo CSV:', file=csv_file)
        else:
            await ctx.send('Error al obtener el archivo de scraping de tesis.')

        os.remove(file_path)


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
            parts = param.strip().split(":", 1)
            if len(parts) == 2:
                key, value = parts
                validKeys = {"year", "category", "city", "region", "laboratory", "keywords"}
                if key.strip() in validKeys:
                    searchParams[key] = value.replace(":", "\:")
                else:
                # Enviar un mensaje al usuario indicando que la clave no es válida
                    await ctx.send(f"Error: La clave '{key.strip()}' no es válida. Por favor, verifica los parámetros.")
                    return
        print("Parámetros de búsqueda:")
       
        for key, value in searchParams.items():
            print(f"{key}: {value}")

        dbConnector = databaseConnector()
        dbConnector.connect()

        # Construir la consulta SQL
        query = "SELECT DISTINCT Document.title, Document.url"
        joins = []  # Aquí guardaremos las cláusulas INNER JOIN
        conditions = []
        order_by = []
        occurrences_conditions = []
        # Iterar sobre todos los parámetros proporcionados
        for key, value in searchParams.items():
            if key == "year":
                yearRange = value.split("-")
                if len(yearRange) == 2:
                    conditions.append(f"publicationYear BETWEEN {yearRange[0]} AND {yearRange[1]}")
                else:
                    conditions.append(f"publicationYear = {yearRange[0]}")

            elif key == "category":
                category = value.strip()
                conditions.append(f"Document_Category.categoryName = '{category}'")
                joins.append("INNER JOIN Document_Category ON Document.documentId = Document_Category.documentId")

            elif key == "city":
                city = value.strip()
                conditions.append(f"Commune.name = '{city}'")
                joins.append("INNER JOIN Document_Commune ON Document.documentId = Document_Commune.documentId")
                joins.append("INNER JOIN Commune ON Document_Commune.communeId = Commune.communeId")

            elif key == "region":
                region = value.strip()
                region_condition = f"TRIM(Commune.region) LIKE '%{region}%'"
                conditions.append(region_condition)
                joins.append("INNER JOIN Document_Commune ON Document.documentId = Document_Commune.documentId")
                joins.append("INNER JOIN Commune ON Document_Commune.communeId = Commune.communeId")

            elif key == "laboratory":
                laboratory = value.strip()
                laboratory = laboratory.replace(r"\:", ":")
                conditions.append(f"Category.principalCategoryId = '{laboratory}'")
                joins.append("INNER JOIN Document_Category ON Document.documentId = Document_Category.documentId")
                joins.append("INNER JOIN Category ON Document_Category.categoryName = Category.categoryName")

            elif key == "keywords":
                keywords = [kw.strip() for kw in value.split(";")]
                occurrences_count_expr = ", ".join([
                    f"CAST((CHAR_LENGTH(content) - CHAR_LENGTH(REPLACE(LOWER(content), '{kw}', ''))) / CHAR_LENGTH('{kw}') AS SIGNED) AS `{kw}_occurrences`"
                    for kw in keywords
                ])
                query += f", {occurrences_count_expr}"
                order_by.extend([f"`{kw}_occurrences` DESC" for kw in keywords])
                occurrences_conditions = [f"CAST((CHAR_LENGTH(content) - CHAR_LENGTH(REPLACE(LOWER(content), '{kw}', ''))) / CHAR_LENGTH('{kw}') > 0 AS SIGNED)" for kw in keywords]

        # Continuar con la construcción de la consulta
        query += " FROM Document"

        # Combinar las cláusulas INNER JOIN
        if joins:
            query += " " + " ".join(joins)

        # Combinar todas las condiciones
        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        # Filtrar por coincidencias positivas en palabras clave

        if occurrences_conditions:
            if conditions:
                query += " AND " + " AND ".join(occurrences_conditions)
            else:
                query += " WHERE " + " AND ".join(occurrences_conditions)

        # Ordenar los resultados por relevancia (cantidad de palabras clave coincidentes)
        if order_by:
            query += " ORDER BY " + ", ".join(order_by)

        print(query)

        if "keywords" in searchParams:
            await ctx.send("Buscando resultados... Los resultados estarán ordenados por coincidencia de palabras clave.")
            await ctx.send("Nota: Puedes realizar búsquedas de dcumentos utilizando keywords en español o inglés")
        results = dbConnector.executeQuery(query)

        if not results:
            await ctx.send("No se encontraron resultados.")
            return
       


        # Procesar los resultados
        total_results = len(results)
        resultsPerPage = 5
        totalPages = (total_results + resultsPerPage - 1) // resultsPerPage

        page = 1

        while page <= totalPages:
            start_index = (page - 1) * resultsPerPage
            end_index = min(start_index + resultsPerPage, total_results)
            currentPageResults = results[start_index:end_index]

            formattedPageResults = "\n".join([f"{i+1}. **{result[0]}**\n" for i, result in enumerate(currentPageResults)])
            embed = Embed(title=f"Página {page} de {totalPages}", description=formattedPageResults)

            message = await ctx.send(embed=embed)

            # Agregar las reacciones al mensaje
            reactions = []
            if totalPages > 1:
                if page > 1:
                    reactions.append('⏪')  # Botón para ir a la primera página
                    reactions.append('⬅️')  # Botón para retroceder una página
                if page < totalPages:
                    reactions.append('➡️')  # Botón para avanzar una página
                    reactions.append('⏩')  # Botón para ir a la última página

            for reaction in reactions:
                await message.add_reaction(reaction)

            if totalPages > 1:
                def check(reaction, user):
                    return user == ctx.author and reaction.message == message

                try:
                    reaction, _ = await self.bot.wait_for('reaction_add', timeout=300.0, check=check)

                    if reaction.emoji == '⬅️' and page > 1:
                        page -= 1
                    elif reaction.emoji == '➡️' and page < totalPages:
                        page += 1
                    elif reaction.emoji == '⏪':
                        page = 1  # Ir a la primera página
                    elif reaction.emoji == '⏩':
                        page = totalPages  # Ir a la última página

                    await message.delete()
                except asyncio.TimeoutError:
                    break
            else:
                break



 


    @commands.command(name='questionDocument')
    async def questionDocument(self,ctx, *, input_text): 
        #logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
        #logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))
        directory = "../../alvaro"   
        if "." in input_text:
            print("CON TITULO")
            split_text = input_text.split(".")
            # Archivos y directorios que deseas eliminar
            files_to_delete = ['docstore.json', 'graph_store.json', 'index_store.json', 'vector_store.json']
            # Construir y ejecutar el comando para eliminar los archivos
            for filename in files_to_delete:
                file_path = os.path.join(directory, filename)
                if os.path.exists(file_path):
                    os.system(f'sudo rm -R {file_path}')
            question = split_text[0]
            self.titulo = split_text[1].strip()  # Elimina espacios en blanco alrededor del título
            
        else:
            question = input_text
            print("SIN TITULO")
        print(self.titulo)

        file_name = "index_store.json"
        file_path = os.path.join(directory, file_name)


        dbConnector = databaseConnector()
        dbConnector.connect()
        query = f"SELECT content FROM Document WHERE title = '{self.titulo}';"
        content_list = [str(dbConnector.retrieve_content(query))]
        #print(content_list)

        if os.path.exists(file_path):
            print("YA EXISTE INDEX")

            # Rebuild storage context
            storage_context = StorageContext.from_defaults(persist_dir=directory)

            # Load index from the storage context
            new_index = load_index_from_storage(storage_context)

            query_engine = new_index.as_query_engine()

            
            response = query_engine.query(question)
            response_str = str(response)
            # Divide la respuesta en partes más pequeñas (2000 caracteres cada una)
            partes = [response_str[i:i+2000] for i in range(0, len(response_str), 2000)]

            # Envia cada parte como un mensaje separado
            for parte in partes:
                await ctx.send(parte)
            #await ctx.send(response)
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

            
            response = query_engine.query(question)
            response_str = str(response)
            # Divide la respuesta en partes más pequeñas (2000 caracteres cada una)
            partes = [response_str[i:i+2000] for i in range(0, len(response_str), 2000)]

            # Envia cada parte como un mensaje separado
            for parte in partes:
                await ctx.send(parte)
            #await ctx.send(response) 
            #print(response)
        dbConnector.close()


    '''@commands.command(name='vectorize')
    async def vectorize(self,ctx):
        batch_size = 10  # Número de documentos por lote
        dbConnector = databaseConnector()
        dbConnector.connect()
        query = "SELECT content FROM Document"
        results = dbConnector.retrieve_content(query)
        print(results[11])
        docs = []
        count=0
        for row in results:
            content = row
            if content is not None:
                docs.append(content)
                count += 1
            if count == 10:
                break
        
        
        
        # Procesar los documentos
        buffer = io.StringIO('\n'.join(docs))
        text_splitter = TokenTextSplitter(chunk_size=200, chunk_overlap=0)
        texts = text_splitter.split_text(buffer.read())
        buffer.close()

        persist_directory = 'db'
        embedding = OpenAIEmbeddings(openai_api_key=TOKEN_OPENAI)
        vectordb = Chroma.from_texts(texts, embedding=embedding, persist_directory=persist_directory)
        vectordb.persist()

        #Liberar memoria
        del docs
        del buffer
        del texts
        del vectordb
        gc.collect()


        dbConnector.close()
        #print(f"Vectorizados {count} documentos")
        await ctx.send(f"Se vectorizaron {count} documentos")'''

 
    @commands.command(name='analysis')
    async def analysis(self, ctx):
        dbConnector = databaseConnector()
        dbConnector.connect()

        queries = [
            ("Número total de documentos", "SELECT COUNT(*) as Total_Documents FROM Document WHERE content is not Null;"),
            ("Autores más prolíficos", "SELECT authorName, COUNT(documentId) as Num_Documentos FROM Document_Author JOIN Author ON Document_Author.authorId = Author.authorId GROUP BY Document_Author.authorId ORDER BY Num_Documentos DESC LIMIT 5;"),
            ("Distribución de documentos en los laboratorios temáticos", "SELECT C.principalCategoryId, COUNT(DC.documentId) as Num_Documentos FROM Category C LEFT JOIN Document_Category DC ON C.categoryName = DC.categoryName GROUP BY C.principalCategoryId ORDER BY Num_Documentos DESC LIMIT 3;"),
            ("Revistas que han publicado la mayor cantidad de documentos", "SELECT organizationName, COUNT(documentId) as Num_Documentos FROM Document_Organization JOIN Organization ON Document_Organization.organizationId = Organization.organizationId GROUP BY Document_Organization.organizationId ORDER BY Num_Documentos DESC LIMIT 3;"),
            ("Evolución de la producción de documentos a lo largo de los años", "SELECT CASE WHEN publicationYear BETWEEN 1980 AND 1990 THEN '1980-1990' WHEN publicationYear BETWEEN 1991 AND 2000 THEN '1991-2000' WHEN publicationYear BETWEEN 2001 AND 2010 THEN '2001-2010' WHEN publicationYear BETWEEN 2011 AND 2020 THEN '2011-2020' WHEN publicationYear >= 2021 THEN '2021-' ELSE 'Otros' END AS Rango, COUNT(*) AS Número_de_Documentos FROM Document GROUP BY Rango ORDER BY Rango;")
        ]

        total_pages = len(queries)
        page = 1

        while page <= total_pages:
            title, query = queries[page - 1]

            # Ejecutar la consulta
            results = dbConnector.executeQuery(query)

     
           # Construir el mensaje con los resultados
            message = f"{page}. **{title}**:\n\n"
            if "Número total de documentos" in title:
                message += f" - En la base de datos existen {results[0][0]} documentos.\n"
            elif "Autores más prolíficos" in title:
                for result in results:
                    message += f" - {result[0]} con {result[1]} documentos.\n"
            elif "Distribución de documentos en los laboratorios temáticos" in title:
                for result in results:
                    message += f" - {result[0]} con {result[1]} documentos.\n"
            elif "Revistas que han publicado la mayor cantidad de documentos" in title:
                for result in results:
                    message += f" - {result[0]} con {result[1]} documentos.\n"
            elif "Evolución de la producción de documentos a lo largo de los años" in title:
                for result in results:
                    message += f" - {result[0]}: {result[1]} documentos.\n"





            # Manejar gráficos (si es necesario)
            file = None
           
            plt.figure(figsize=(8, 8))
            if "laboratorios temáticos" in title.lower():
                print("categorias")
                categorias = [row[0] for row in results]
                print(categorias)
                num_documentos = [row[1] for row in results]
                print(num_documentos)
                plt.pie(num_documentos, labels=categorias, autopct='%1.1f%%', startangle=140)
                plt.title("Documentos por laboratorios temáticos")
                plt.savefig("/home/fernando/grafico_temporal.png")
                file = File("/home/fernando/grafico_temporal.png")

                # Adjuntar el gráfico al mensaje de Embed
                message += "\nVer el gráfico a continuación:"
                file = File("/home/fernando/grafico_temporal.png")

            if "producción de documentos" in title.lower():
                años = [row[0] for row in results]
                num_documentos = [row[1] for row in results]
                plt.bar(años, num_documentos)
                plt.xlabel("Rango de Años")
                plt.ylabel("Número de Documentos")
                plt.title("Evolución de la Producción de Documentos a lo largo de los Años")

                # Guardar el gráfico como imagen (opcional)
                plt.savefig("/home/fernando/grafico_temporal.png")
                file = File("/home/fernando/grafico_temporal.png")

                # Adjuntar el gráfico al mensaje de Embed
                message += "\nVer el gráfico a continuación:"
                file = File("/home/fernando/grafico_temporal.png")

            # Enviar resultados y gráficos como un único mensaje
            embed = Embed(title=f"Página {page} de {total_pages}", description=message)
            if file:
                embed.set_image(url="attachment://grafico_temporal.png")  # Adjuntar gráfico al mensaje
            sent_message = await ctx.send(embed=embed, file=file)
            if os.path.exists("/home/fernando/grafico_temporal.png"):
                os.remove("/home/fernando/grafico_temporal.png")
            # Agregar las reacciones al mensaje
            reactions = []
            if total_pages > 1:
                if page > 1:
                    reactions.append('⏪')  # Botón para ir a la primera página
                    reactions.append('⬅️')  # Botón para retroceder una página
                if page < total_pages:
                    reactions.append('➡️')  # Botón para avanzar una página
                    reactions.append('⏩')  # Botón para ir a la última página

            for reaction in reactions:
                await sent_message.add_reaction(reaction)

            def check(reaction, user):
                return user == ctx.author and reaction.message == sent_message

            try:
                reaction, _ = await self.bot.wait_for('reaction_add', timeout=300.0, check=check)

                if reaction.emoji == '⬅️' and page > 1:
                    page -= 1
                elif reaction.emoji == '➡️' and page < total_pages:
                    page += 1
                elif reaction.emoji == '⏪':
                    page = 1  # Ir a la primera página
                elif reaction.emoji == '⏩':
                    page = total_pages  # Ir a la última página

                await sent_message.delete()
            except asyncio.TimeoutError:
                break

    @commands.command(name='questionDB')
    async def questionDB(self,ctx,*, question): 
        # Load and process the text
        '''context = """Basándote solo en el contexto dado, informacion dada o en el artiuclo dado, 
        responde la pregunta, si no tienes el contexto debes mencionar que no tienes informacion 
        sobre el tema, ademas evita mencionar la frase "segun el contexto proporcionado", o 
        "basandome en el contexto dado" o "segun el articulo proporcionado" """  '''
        #question_with_context = context + question
        embedding = OpenAIEmbeddings(openai_api_key=TOKEN_OPENAI)
        persist_directory = 'db'

        # load the persisted database from disk, and use it as normal. 
        vectordb = Chroma(persist_directory=persist_directory, embedding_function=embedding) 
        qa = RetrievalQA.from_chain_type(llm=ChatOpenAI(temperature=0.4, openai_api_key=TOKEN_OPENAI,model_name="gpt-3.5-turbo", 
        max_tokens=512), chain_type="stuff", retriever=vectordb.as_retriever())
        result = qa({"query": question})
        #print(result["result"])
        await ctx.send(result["result"])

        #print(qa.run(question))
        #await ctx.send(qa.run(question)) 

        del embedding
        del vectordb
        del qa
        del result
        gc.collect()
   
    @commands.command(name='query')
    async def query(self,ctx, *, question):
        question_prompt = QUERY.format(question=question)
        response = dbChain.run(question_prompt)
        await ctx.send(response)

    
    pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENVIRONMENT)
    


    @commands.command(name='test')
    async def test(self,ctx, *, inputText):
        query_engine = self.loaded_index.as_query_engine()
        response = query_engine.query(inputText)
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