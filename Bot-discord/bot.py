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
from llama_index import TreeIndex, SimpleDirectoryReader,Document


TOKEN = os.environ.get('DISCORD_TOKEN')
TOKEN_OPENAI = os.environ.get('GPT_TOKEN')
openai.api_key = TOKEN_OPENAI


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
        question, titulo = input_text.split("?")     
        # Construir la consulta de Elasticsearch
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"match": {"title": titulo}}
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
            for i, hit in enumerate(hits, start=1):
                source = hit["_source"]
                content = source.get("content", "Sin contenido")
                print(content)
                content_list.append(content)
                #abstract = source.get("abstract", "Sin contenido")
                score = hit["_score"]
                #await ctx.send(f"Resultado {i}:\nContenido: {content}\nScore: {score}\n")
            #print(abstracts_with_high_score)        
        else:
            await ctx.send("No se encontraron resultados para los conceptos clave proporcionados.")
            #print("No se encontraron resultados para los conceptos clave proporcionados.")

        #print(content_list)
        text_list = ["""Andean Geology www.andeangeology.clAndean Geology 44 (1): 1-16. January, 2017 doi: 
        10.5027/andgeoV44n1-a01 Ultramafic rocks in the North Patagonian Andes: 
        is their emplacement associated with the Neogene tectonics of the
        Liquiñe-Ofqui Fault Zone?
        Francisco Hervé1,2, Francisco Fuentes1, Mauricio Calderón1, Mark Fanning3, 
        Paulo Quezada1,6, Robert Pankhurst4, Carlos Rapela5
        1 Carrera de Geología, Universidad Andrés Bello, Sazié 2119, Santiago, Chile.
        fherve@unab.cl;  ffuentes@unab.cl; m.calderon@unab.cl
        2 Departamento de Geología, Universidad de Chile, Plaza Ercilla 803, Santiago, Chile.
        fherve@cec.uchile.cl
        3 Research School of Earth Sciences, The Australian National University, Canberra, ACT 0200, Australia.
        mark.fanning@anu.edu.au
        4 Visiting Research Associate, British Geological Survey, Keyworth, Nottingham NG12 5GG, United Kingdom.
        rjpankhurst@gmail.com
        5 Centro de Investigaciones Geológicas, Universidad Nacional de la Plata, Diagonal 113, No. 275, 1900 La Plata, Argentina.
        crapela@cig.museo.unlp.edu.ar
        6 Seremi de Minería Región de Aysén, Ministerio de Minería, Baquedano 336, Coyhaique, Chile.
        pquezada@minmineria.cl
        
        ABSTRACT. Serpentinites and fresh or partially serpentinized  harzburgite crop out in the western slope of the 
        North Patagonian Andes of continental Chiloé (41°44’-42°12’S). These rocks are spatially associated with low-grade 
        metamorphic rocks containing Cenozoic detrital zircons. The metamorphic rocks, together with Devonian metasediments, 
        have been mapped previously as Late Paleozoic-Triassic metamorfic complex, an age no longer tenable for at least part 
        of the complex. Transpressional tectonic emplacement of the ultrama fic body or bodies is thought to have been related 
        to activity on the Liquiñe-Ofqui Fault Zone, following a late Oligocene-Early Miocene extensional phase in the forearc region of the present Andes. This fault zone occurs immediately east of the outcrops of the ultramafic rocks and has been interpreted previously as generating a hemi- flower or flower structure .
        Keywords: Serpentinites, North Patagonian Andes, Liquiñe-Ofqui Fault Zone, Neogene tectonics.
        RESUMEN. Rocas ultramáficas en los Andes norpatagónicos: ¿está su emplazamiento asociado a la actividad 
        tectónica Neógena de la Zona de Falla Liquiñe-Ofqui? En la vertiente occidental de los Andes norpatagonicos de 
        Chiloé continental (41°44’-42°12’ S) afloran serpentinitas y harzburgitas frescas o parcialmente serpentinizadas. 
        Estas rocas están espacialmente asociadas con rocas metamórficas de bajo grado que contienen circones detríticos 
        Cenozoicos. Estas rocas metamórficas, junto a metasedimentos Devónicos, han sido mapeados previamente como del 
        Paleozoico superior-Triásico, una edad que no es sostenible para al menos una parte de ellos. El emplazamiento tectónico 
        transpresivo del o de los cuerpos ultramáficos, se supone relacionado a la actividad de la Zona de Fallas Liquiñe-Ofqui, después de una fase extensional del Oligoceno tardío-Mioceno temprano en la región de antearco de los Andes actuales.  
        La mencionada zona de fallas aparece inmediatamente al este de los afl oramientos de rocas ultramáficas, y ha sido 
        previamente interpretada como causante de una estructura de flor o hemi flor.  
        Palabras clave: Serpentinitas, Andes norpatagónicos, Zona de Falla Liquiñe Ofqui, Tectónica neógena.2
        Ultramafic  rocks  in the north Patagonian  andes: is their  emPlacement  associated  with the neogene  tectonics ...
        1. Introduction
        Ongoing research in the western foothills of the 
        North Patagonian Andes between latitudes 41° S and 
        43° S (Fig. 1) has included the study of previously 
        little-known ultramafic rock bodies that crop out 
        in the area. This portion of the Andean Main Range 
        is locally named Continental Chiloé, as it is at the same latitude as Chiloé island which forms part of the Coast Range to the west and from which it is separated by marine invasion of the Longitudinal 
        Depression. The existence of ultramafic rocks at Río Velásquez in northern Peninsula Huequi was 
        mentioned by Muñoz-Cristi (1931)1, who stated that 
        they cut across volcanic and sedimentary formations. 
        Subsequently they were referred to by Hervé et 
        al. (1978) and Pankhurst et al. (1992) but without 
        further information. Pérez (1999), Crignola (1999) 
        and later Caro (2006) gave more detailed accounts of the lithology, distribution and geochemistry of 
        the ultramafic rocks, in the latter case obtained 
        during gold prospecting activities in the area. The geological evolution here has been relatively less studied than other regions, mainly due to the lack 
        FIG. 1. Geological sketch map of the studied area, after Encinas et al. (2013), with the study area outlined by the rectangle. Outcrop 
        areas of supposed basement rocks are shaded. Acronyms refer to: BMMC  (Bahía Mansa metamorphic complex), CMC  (Chonos 
        metamorphic complex), MRMC (Main Range metamorphic complex) and EAMC (Eastern Andes metamorphic complex). The 
        main faults in the Liquiñe-Ofqui fault zone ( LOFZ ) are indicated, as well as the position of a point in the Nazca plate relative to the 
        continent through Cenozoic time (relative approach velocity shown in the the top left-hand graphic), after Cande and Leslie (1986).
        1 Muñoz-Cristi, J. 1931. Informe preliminar sobre los yacimientos platiníferos de Comau, Provincia de Chiloé. (Unpublished  
        report), Departamento de Minas y Petróleo, Santiago, Chile: 9 p. 3
        Hervé et al. / Andean Geology 44 (1): 1-16, 2017
        of continuous roads from the adjacent areas of the 
        mainland, so that access is mainly from the sea; 
        forest cover is also very dense. 
        Outcrops of ultramafic rocks are scarce in the 
        Chilean Andes. Heavily serpentinized ultramafic 
        bodies occur sparsely in the Western Series of the 
        paleo-accretionary wedge represented by the Coast 
        Range metamorphic complexes of south-central Chile 
        (Vergara, 1970; Ojeda, 1976; Alfaro, 1980; Hervé, 
        1988; Godoy and Kato, 1990; Crignola et al., 1997; 
        Duhart et al., 2001). They have been considered 
        as emplaced in a Late Paleozoic supra-subduction 
        zone environment (Barra et al., 1998; Höfer et al., 
        2001; González-Jiménez et al., 2014). Peridotites 
        form part of a banded layered mafic intrusion, 
        mainly composed of troctolites and gabbro, in the Pennsylvanian Coastal Batholith of Central Chile 
        (Hervé and del Campo, 1975; Hernández, 2006). 
        Another significant occurrence of ultramafic rocks 
        is in the Neogene Taitao ophiolite immediately south 
        of the Chile triple junction, considered to have been 
        emplaced by obduction related to collision of the Chile Ridge with the continental margin (Forsythe and Nelson, 1985; Anma et al ., 2006). Ultramafic 
        rock mantle xenoliths are known from Neogene 
        volcanic rocks in the Patagonian Andes and in 
        extra-Andean Patagonia (Schilling et al ., 2008), 
        giving an indication of the present composition of the mantle below Patagonia.
        We have studied ultramafic rocks at Peninsula 
        Huequi, at Pichicolo and at Caleta Puelche (Fig. 2). 
        These dispersed outcrops are considered here to be 
        part of the same geological unit, whose full extension 
        in the area is not known. The outcrop area in the 
        northern part of Peninsula Huequi was mapped as a 
        Paleozoic-Triassic metamorphic complex (Crignola, 
        1999), and the ultramafic rocks have been considered 
        to be in fault contact with Devonian intrusive rocks 
        at Pichicolo (Duhart, 2008).
        Neither the age nor the emplacement mode of 
        the Huequi-Pichicolo-Caleta Puelche ultramafic 
        unit is known. We present new information on 
        the petrology, age and geological relationships 
        of associated rock units. We present four U-Pb 
        detrital zircon age patterns and four igneous U-Pb zircon crystallization ages for rock units spatially 
        associated with the ultramafic rocks (in some places 
        in direct contact); these allow some constraints on 
        the possible emplacement ages of the latter. Two of 
        the detrital zircon samples are from rocks previously mapped as a part of the supposedly Late Paleozoic 
        Llancahue epi-metamorphic complex (Cembrano, 1990), one is from the Early Devonian (Fortey et 
        al., 1992) Buill slates and one from the Miocene 
        Ayacara Formation (Levi et al., 1966; Rojas, 2003; 
        Encinas et al., 2013).
        2. Regional geological setting
        The Continental Chiloé segment of the Andes 
        has a protracted evolution since at least Devonian times. At present, the area faces subduction of the 
        Nazca plate, with the Chile triple junction being 
        located 300 km to the southwest. A metamorphic 
        complex, which has been correlated (Cembrano, 
        1990; Pankhurst et al., 1992) with the late Paleozoic 
        accretionary complex of the coastal cordillera ( e.g., 
        Hervé, 1988) forms a major part of the outcrops. The Mesozoic geology is dominated by the North 
        Patagonian Batholith (Pankhurst et al ., 1992; 
        Sernageomin, 2003; Pankhurst et al., 1999), formed 
        as a result of subduction beneath the continental 
        margin. The area then experienced generalized 
        extension during the late Oligocene-early Miocene 
        (Encinas et al., 2015), which allowed the deposition 
        of deep water sediments due to marine incursions from both Pacific and Atlantic oceans (Encinas et 
        al., 2014). Extension was followed by shortening 
        when subduction became more orthogonal to the 
        margin during the late Miocene, the extensional 
        basins were inverted and the Liquiñe-Ofqui Fault 
        Zone (LOFZ), a major right lateral wrench fault 
        extending for more than 1,000 km in the North 
        Patagonian Andes, formed in a transpressional 
        regime (Hervé, 1976; Cembrano et al., 1996). The 
        modern chain of supra-subduction zone volcanoes outlasted the glacial period during which the study area was entirely covered by ice (Heusser, 1990). Intense uplift and erosion during the late Miocene 
        contractional episode (Adriasola et al., 2005) exposed 
        the plutonic rocks of the North Patagonian Batholith 
        along the trace of the LOFZ.
        3. Local geology
        The oldest well-dated rocks in the region are 
        the Buill slate boulders (Fig. 2), in which Levi 
        et al. (1966) and later Fortey et al. (1992) found 
        Devonian trilobites; such fossils are extremely scarce 
        in Chile. Mainly foliated low-grade metamorphic 4
        Ultramafic  rocks  in the north Patagonian  andes: is their  emPlacement  associated  with the neogene  tectonics ...
        FIG. 2. Detailed sketch map of the studied area (modified from Sernageomin, 2003 and Encinas et al., 2013) indicating sample locations 
        and the U-Pb zircon ages obtained in this study. The location of the geological cross-section illustrated in figure 6 is shown 
        (A-B). Liquiñe-Ofqui Fault Zone (LOFZ).5
        Hervé et al. / Andean Geology 44 (1): 1-16, 2017
        rocks which crop out in this area have been given 
        local names by different authors (Cembrano, 1990; 
        Sanhueza, 1996; Crignola, 1999; Pérez, 1999). 
        The metamorphic rock assemblages at Peninsula 
        Huequi and the surrounding fjords to the southwest 
        (Fiordo Reñihue) and east (Fiordo Comau) have 
        been encompassed within a single mid Paleozoic-
        Triassic metamorphic rock unit (MPT) defined by 
        Encinas et al. (2014). As well as the psammopelitic 
        component, this unit bears pillow basalts in different 
        stages of deformation and metamorphism. In the 
        area of Llancahue and Pelada islands (Fig. 2) 
        there are extensive outcrops of metamorphic rocks which Cembrano (1990) mapped as the Llancahue 
        epi-metamorphic complex, consisting of two zones 
        of well-foliated low-grade metasedimentary and 
        metavolcanic rocks; pillowed basalts cropping out on the west coast of Isla Llancahue in association 
        with low-grade metasediments were also incorporated 
        due to outcrop and structural continuity with more 
        foliated and metamorphosed rocks to the south and 
        east. Pankhurst et al. (1992) reported a whole-rock 
        Rb-Sr isochron of 292±2 Ma for the Huinay schists 
        on the shores of Fiordo Comau (Fig. 2), interpreted 
        as indicating “partial isotopic homogenization during 
        metamorphism”. The outcrop includes amphibolite-
        grade rocks. Correlation with the Llancahue epi-
        metamorphic complex is not well established but has been assumed, for example by Encinas et al. (2013). Outcrops along the coast ranges of south 
        central Chile, including Isla Chiloé west of the 
        studied area, represent a late Paleozoic accretionary 
        complex mainly formed at the active western margin 
        of Gondwana ( e.g., Hervé, 1988), and the supposedly 
        broadly coeval Llancahue epi-metamorphic complex 
        and equivalents were considered to belong to that 
        unit in most previous work in the area ( e.g., Duhart, 
        2008 or Encinas et al., 2013).
        Apart from some possibly Jurassic volcanic 
        rocks (Pérez, 1999), Mesozoic rocks are mainly 
        represented by plutons of the North Patagonian 
        Batholith, which extends in time through to late 
        Miocene (Cembrano, 1990; Sernageomin, 2003; 
        Pankhurst et al., 1999). 
        Cenozoic volcanic and sedimentary rocks are 
        represented by the marine Ayacara Formation (Levi 
        et al., 1966; Rojas, 2003). It comprises two members: 
        a lower one of coarse-grained sedimentary and 
        volcaniclastic rocks, and an upper one of alternating 
        siltstone and sandstone. Detrital zircons in the lower member have an early Miocene age peak accompanied 
        by minor Early Cretaceous, Jurassic and Devonian 
        peaks, in contrast with the very narrow early Miocene 
        age range shown by zircons in the upper member 
        (Encinas et al ., 2013). These authors concluded 
        that the Ayacara Formation was deposited during the early-middle Miocene in a deep marine forearc basin generated by extension, probably related to 
        subduction erosion of the continental margin. Later, 
        the basin was inverted, contemporaneously with the 
        establishment of a transpressional regime along the 
        LOFZ. Beck et al. (1993) and Rojas et al. (1994) used paleomagnetic studies to identify the rotation 
        of small blocks west of the LOFZ, involving the 
        Neogene rocks. The depositional environment of the 
        Ayacara Formation is similar to that of the Traiguen 
        Formation (Encinas et al., 2015), 200 km farther 
        south along the Andes. Somewhat differing scenarios 
        have been considered: an extensional basin related to the activity of the LOFZ (Hervé et al., 1995), a 
        tectonic basin formed by the action of an indentor 
        due to increase in oblique subduction velocity 
        (Lefort et al., 2006), or a deep intra-arc marine basin 
        related to the general extension which affected the 
        whole Andean orogen during late Oligocene-earliest 
        Miocene times (Encinas et al., 2015).
        4. Methodology
        Samples were collected from localities displaying 
        the typical outcrop characteristics of the different units, as detailed below. Petrological observations 
        in thin sections and X-ray Diffraction (XRD) studies 
        were made at the Laboratory for the Analysis of 
        Solids at Universidad Andrés Bello, Santiago. Zircons 
        were separated by standard methods of crushing, grinding, Wilfley table, magnetic and heavy liquid separation at Universidad de Chile, Santiago. 
        Zircon analyses were undertaken at the Research 
        School of Earth Sciences, The Australian National 
        University, Canberra. The grains were mounted 
        in epoxy, polished to about half-way through the 
        grains, and cathodoluminescence (CL) images were 
        obtained for every zircon to select appropriate areas 
        for analysis. U-Th-Pb analyses were carried out using 
        sensitive high-resolution ion microprobes (SHRIMP 
        II and SHRIMP RG) with procedures similar to 
        those described by Williams (1998; and references therein). When an igneous crystallization age was required, 15 to 20 grains were analysed from each 6
        Ultramafic  rocks  in the north Patagonian  andes: is their  emPlacement  associated  with the neogene  tectonics ...
        sample; and where possible, 60 or more grains when 
        identification of sedimentary provenance was the 
        purpose. Crystallization ages, where calculated, are 
        reported here with 95% confidence limits.
        5. Ultramafic rocks
        Some of the most extensive outcrops of ultramafic 
        rocks in the area are located in the northeastern 
        shore of Peninsula Huequi, northeast of Poyo                                       
        (Fig. 2). According to the geological map of the 
        study zone, compiled after Cembrano (1990) and 
        Sanhueza (1996), this area is underlain by the mid 
        Paleozoic-Triassic metamorphic rock unit (MPT), 
        sensu Encinas et al. (2013), which are bounded to 
        the east by Miocene plutonic rocks. Pérez (1999) indicates a patchy distribution of ultramafic rocks, 
        mainly in tectonic contact with sedimentary and 
        metavolcanic rocks. A discontinuous beach section 
        of ca. 1 km east of Poyo exposes ultramafic rocks, 
        terminated to the east by a cross-cutting tonalitic 
        dyke. Caro (2006) was able to follow the peridotite 
        outcrops for 1.5 km up Río Velásquez (Fig. 2) in 
        contact with schists of volcaniclastic protoliths. The 
        peridotites here correspond mainly to harzburgite with 
        coarse-grained protogranular texture composed by 
        olivine, orthopyroxene and spinel. In thin sections, 
        harzburgites have preferentially orientated olivine 
        crystals some with intracrystalline deformation. 
        Characteristic textures of serpentinite are observed as 
        mesh texture developed from olivine, dense network 
        of veins cutting olivines and orthopyroxenes, and as total replacement of the original rock.  
        Additional ultramafic rock outcrops, mainly 
        serpentinites, have been observed at Caleta Puelche, 
        where they are associated with foliated black phyllites 
        and intruded by dioritic/tonalitic dykes. The remnants 
        of harzburgites show a foliated texture characterized 
        by visible porphyroclasts of orthopyroxene and 
        olivine. At Pichicolo, a cataclastic Devonian tonalite 
        is in fault contact with serpentinite (Duhart, 2008), 
        considered to be pre-Triassic in age. Ultramafic 
        bodies correspond to green to black fine-grained rocks which are completely serpentinized. 
        Preliminary results of powder XRD analyses 
        have allowed to identify antigorite and lizardite 
        as the main serpentine polymorphs. Fine-grained 
        magnetite is also present in some samples. 
        Serpentine minerals have been altered to talc and                                                                           carbonates. The rocks in the western part of Isla Llancahue 
        are mapped by Encinas et al. (2013) as belonging 
        to the same MPT unit, a generalization from the 
        original definition of the Llancahue epi-metamorphic 
        complex (Cembrano, 1990). Outcrops of somewhat 
        foliated pillow basalts spatially associated with 
        alternating beds of foliated black shales and 
        sandstones are observed at Puerto Bonito (Fig. 3a). 
        Similar foliated pillow basalts and pillow breccias crop out at Fiordo Andrade, on the northern coast of Isla Llancahue. Towards the southern end of the island the unit contains higher-grade metamorphic 
        rocks (Cembrano, 1990), which were sampled at 
        Punta Quiaca (Fig. 3b). Fiordo Comau has outcrops 
        of foliated metamorphic rocks (Fig. 3c) intruded 
        by granites that in parts, such as Fiordo Cahuelmo 
        (Fig. 3d), constitute a stack of parallel sheets several 
        metres thick. These rocks, also ascribed to the 
        MPT, crop out extensively along the fjord shores; they constitute the Huinay schists of Pankhurst et al. (1992).
        6. Geochronology
        The results of the SHRIMP dating of rocks from 
        Chiloé continental is summarized in table 1, with 
        fuller analytical data in the Electronic files 1 to 8. 
        The localities of all dated samples are shown in 
        figure 2, with GPS readings in table 1.
        6.1. Sedimentary and metamorphic rocks
        Sample FO10150 is a biotite-hornblende gneiss 
        with folded quartz veins, from Rocas Blancas, a 
        locality near Huinay in Fiordo Comau considered 
        to be late Paleozoic (Pankhurst et al., 1992). Only 
        25 zircon grains could be hand picked from the 
        heavy mineral concentrate; 15 were analysed, 
        concentrating on euhedral grains with oscillatory 
        CL zoning interpreted as primary igneous zircon. 
        The results (not shown in the figures) have a very dispersed range in ages from ~15 Ma to ~2335 Ma, 
        with a small grouping of three grains at about 58 Ma.                           
        Although of doubtful significance, this latter group 
        may provide an estimate for the maximum depositional 
        age of the sedimentary protolith; further zircon would 
        need to be separated and analysed to investigate this 
        contention. Alternatively, the rock could be interpreted 
        as a Neogene orthogneiss derived from anatexis of Paleogene or younger sedimentary rocks.7
        Hervé et al. / Andean Geology 44 (1): 1-16, 2017
        FIG. 3. Photographs of outcrops from which the analysed samples were taken. A. Cleaved siltstones and sandstone bed (FO1415) at 
        Puerto Bonito, SW shore of Llancahue island, mapped as part of the late Paleozoic-Triassic basement by Cembrano (1990) and 
        Encinas et al. (2013). Stratification (S0) and main cleavage (S1) are indicated; B. Micashists at Punta Quiaca, southern end of 
        Isla Llancahue, mapped as higher-grade part of the Late Paleozoic-Triassic basement by Cembrano (1990). Main foliation Sp 
        (probably S1), showing boudinaged veins (inside the white ellipse); C. Lllancahue epi-metamorphic complex at Punta Quiaca 
        showing an interpreted tight fold (dashed lines) of quartzite bed with axial plane cleavage Sp (FO14158); D. Huinay schists: 
        alternating bands of amphibolite facies metamorphic rocks and granitic bodies (FO14153) at Fiordo Cahuelmó. 
        TABLE 1. SUMMARY OF U-Pb SHRIMP GEOCHRONOLOGICAL DETERMINATIONS ON ZIRCONS.  
        Sample Rock type LocalityGeographical 
        coordinatesCrystallization
        Age (Ma)MSWD (n)Main detrital ages (Ma)
        Youngest Other peaks
        FO10150 Bt-Hbl
        gneissRoca 
        Blanca42°20’49.9”S  
        72°26’59.2”W- - 58 (15)-2335
        FO14165 meta-
        sandstone Buill 42°25’12.6”S  
        72°42’7.0”W- - 405 469, 570, 631, 1100-
        1200, 1388, 2643
        FO14163 meta-
        sandstonePuerto 
        Bonito42°07’56.3”S  
        72°34’26.2”W36.2±0.5 1.3 (26) - 53, 115, 175, 350-400
        FO14158 quartzite Punta 
        Quiaca42°10’06.4”S  
        72°29’20.4”W52.5±0.5 1.7 (19) - - 
        FO14168 sandstone N of Buill 42°21’30.2”S  
        72°40’20.4”W21.7±0.2 1.4 (49) - - 
        FO14148 Bt-Hbl 
        tonaliteFiordo 
        Cahuelmo42°14’50.0”S  
        72°23’46.8”W 8.2±0.2 1.4 (17/18) - - 
        FO14153 leuco-granite Fiordo 
        Cahuelmo42°15’58.5”S  
        72°25’42.2”W23.0±0.2 0.6 (13) 32 - 
        FO1516 Bt-tonalite E of Polyo 42°11’59.3”S  
        72°36’07.7”W13.3±0.2 0.8 (15) - - 
        FO1524 Bt-Hbl
        tonalitePuelche 
        ramp41°44’39.0”S  
        72°39’25.1”W 9.3±0.3 0.9 (16) - - 
        (n): number of areas analysed;  Bt: biotite;  Hbl: hornblende.8
        Ultramafic  rocks  in the north Patagonian  andes: is their  emPlacement  associated  with the neogene  tectonics ...
        Sample FO14165 is a ~10 cm thick layer of 
        fine-grained metasandstone intercalated in silicified 
        black slates at Buill. The zircons are predominantly 
        subequant round to subround grains and a few euhedral 
        crystals with pyramidal terminations. The CL images 
        reveal a variety of internal concentric zoning, both 
        igneous and metamorphic in origin. The detrital age 
        pattern for 70 zircons analysed (Fig. 4) has well-
        represented groupings corresponding to Ordovician 
        (~450-480 Ma), late Proterozoic (~570-635 Ma), 
        Middle Proterozoic or Grenvillian peaks around 
        1050-1215 Ma, a subdued ~1,400 Ma clustering and 
        an older late Archean dispersed one (~2605-2645 Ma). 
        At the younger end, a single grain with a 206Pb/238U 
        date of ~14 Ma is considered to have lost radiogenic 
        Pb. The grouping at ~390-415 Ma is for analyses of 
        oscillatory zoned grains and this is interpreted as the 
        best constraint on a maximum possible sedimentation 
        age of around 405 Ma, consistent with the Early 
        Devonian paleontological age of the slate boulders 
        studied by Fortey et al. (1992).
        Two samples from the epi-metamorphic complex 
        at Isla Llancahue have surprisingly young maximum 
        possible sedimentation ages, for a unit considered regionally to be of Late Paleozoic to Triassic age. 
        FO14163 is a 1m thick cleaved metasandstone 
        layer with graded EW/45N bedding intercalated in 
        predominant black pelites with slump structures, 
        at Puerto Bonito, southwestern Isla Llancahue. 
        S1 cleavage is N55W/65N. The zircon population 
        contains abundant euhedral crystals with pyramidal 
        terminations and simple igneous CL zoning (oscillatory 
        or length-parallel for prismatic grains). From the 
        70 grains analysed (Fig. 4) the youngest 21 have 
        a weighted mean 206Pb/238U age of 36.2±0.5 Ma                   
        (MSWD=1.3). There are scattered Paleocene, Early 
        Cretaceous and Early Jurassic analyses, with a 
        significant clustering in the Devonian between ~350 
        and ~400 Ma. FO14158 is a pale coloured quartzite 
        in a folded packet of well-foliated micaschists and 
        metasandstones at Punta Quiaca, southern tip of 
        Isla Llancahue. The main foliation Sp crenulates a 
        previous foliation, and is parallel to the lithological 
        banding: asymmetric kinematic indicators testify 
        to simple shear deformation. The metasandstones are boudinaged, and intrafolial isoclinal folds are present (Sp N35W/ 90). The analysed sample has feldspar phenocrysts in a fine-grained matrix, and 
        was probably originally a tuff (metabasites are also 
        present in the studied section). A small number of elongate prismatic zircon grains were hand -picked 
        from the heavy mineral concentrate. They usually 
        have broken terminations and many have axial 
        cavities commonly seen in volcanic zircon. From 
        the 36 grains analysed (Fig. 4), three with Miocene-
        Pliocene U-Pb ages have high common Pb contents 
        and are considered to have lost radiogenic Pb. There 
        is a dominant clustering around 50-60 Ma, but with 
        an asymmetric probability density distribution. A 
        weighted mean for 19 analyses has some scatter with 
        a 206Pb/238U age of 52.5±0.5 Ma (MSWD=1.7), and 
        we interpret this sample as derived from a Paleocene 
        tuffaceous protolith.
        FO14168 is a fine-grained tuffaceous sandstone 
        from north of Buill belonging to the Ayacara 
        Formation. It has a homogeneous population of 
        euhedral zircon crystals, with pyramidal terminations 
        and prominent central cavities consistent with a 
        volcanic paragenesis; the internal CL structure 
        showing broad to weak zoning is also common 
        to volcanic zircon. Forty nine of the 52 grains 
        analysed (Fig. 4) have an early Miocene weighted 
        mean 206Pb/238U age of 21.7±0.2 Ma (MSWD=1.4), 
        in accordance with the age assigned to this unit by Encinas et al. (2013).
        6.2. Igneous rock crystallization ages 
        FO14148 is a coarse-grained foliated biotite-
        hornblende tonalite from the eastern end of Fiordo 
        Cahuelmo, with dark 3-15 cm inclusions elongated 
        in the N30W/90 trending tectonic foliation. The 
        zircons are generally ~200-400 µm long, elongate euhedral grains with bipyramidal terminations and simple igneous internal CL structures. A weighted mean 
        206Pb/238U age of 8.2±0.2 Ma (MSWD=1.4) 
        for 17 of 18 grains analysed (Fig. 5) is considered to record igneous crystallization age. 
        A fine-grained, isotropic leucogranite that forms 
        a 1m thick flat-lying sheet intruding schists of 
        the Comau metamorphic complex at the southern 
        entrance of Estero Cahuelmo (FO14153) has a 
        more complicated zircon population. Whereas the 
        majority of the grains are elongate euhedral crystals 
        with pyramidal terminations, the CL images reveal 
        the presence of older inherited components enclosed 
        within otherwise oscillatory-zoned zircon. The 
        inherited zircon ages (Fig. 5) range to ~1100 Ma with 
        a prominent, though hardly statistical cluster around 
        ~30-32 Ma. A weighted mean for 13 oscillatory 9
        Hervé et al. / Andean Geology 44 (1): 1-16, 2017
        FIG. 4. U-Pb plots for zircon data from the four metasedimentary samples analysed in this study. Tera-Wasserburg plots (right-hand 
        side) and age versus probability plots (left-hand side).10
        Ultramafic  rocks  in the north Patagonian  andes: is their  emPlacement  associated  with the neogene  tectonics ...
        FIG. 5. U-Pb plots for zircon data from the four igneous rock samples analysed in this study. Tera-Wasserburg plots (right-hand side) 
        and age versus probability plots (left-hand side).11
        Hervé et al. / Andean Geology 44 (1): 1-16, 2017
        zoned igneous areas of the 22 areas analysed has 
        a late Oligocene crystallization 206Pb/238U age of 
        23.0±0.2 Ma (MSWD=0.61). 
        FO1516 is a 5 m wide tabular body (N10E/70E) 
        of biotite tonalite in the Huequi peridotite east of 
        Poyo. It has a columnar structure, with columns 
        perpendicular to the margins. It is a phaneritic, 
        isotropic rock, with no inclusions. A system of 
        quartz veins parallel to the contact does not extend 
        into the surrounding ultramafic rock, suggesting 
        emplacement into brittle country rock, probably at 
        shallow depths. The zircons are dominantly elongate 
        prismatic grains or fragments, around 100 µm in 
        length with rare coarser subhedral grains. The CL 
        images show length-parallel zoning with some 
        grains having subdued sector and/or oscillatory 
        zoning. The 18 grains analysed (Fig. 5) have low to 
        moderate U (~35-390 ppm) with a few very high U 
        areas also present. A probability density plot shows 
        an assymmetric distribution of 206Pb/238U ages, with 
        a main peak around 13 Ma and a possible older 
        component also present. Fifteen analyses forming the 
        dominant grouping give a weighted mean 206Pb/238U 
        age of 13.3±0.2 Ma (MSWD+0.81), which we 
        interpret as the igneous crystallization age. 
        At Caleta Puelche, a tonalite (FO1524) intrudes 
        metamorphosed black shales that apparently overlie 
        a serpentinite body containing some fresh peridotite 
        portions. It is a phaneritic, isotropic rock, with 
        inclusions of the country rock. The abundant coarse-
        grained (~200-300 µm long) euhedral zircons are 
        remarkably clear and have bipyramidal terminations. 
        The CL images show simple igneous internal structure 
        and 16 of the 18 grains analysed give a weighted 
        mean 206Pb/238U age of 9.3±0.3 Ma (MSWD=0.86) 
        interpreted as the igneous crystallization age (Fig. 5). 
        7. Discussion
        No direct age determinations have been obtained on 
        the crystallization or emplacement of the harzburgite 
        or associated serpentinite. However, some of the 
        plutonic rocks observed to intrude the ultramafic 
        rocks and their overlying sedimentary rocks have 
        mid-to-late Miocene ages. The contact relationships 
        between the ultramafic rocks and the other geological 
        units are diverse. At Pichicolo, Duhart (2008) presents 
        evidences of a fault contact between a Devonian 
        pluton and serpentinite. At Puelche, the northernmost 
        outcrop of ultramafic rocks in the studied area, foliated serpentinite underlies foliated metasedimentary 
        rocks, of unknown age. At Huequi peninsula, Caro (2006) states that the partly serpentinized peridotite 
        is overlain by schists of volcanic protolith, which 
        underlie black slates and are spatially associated 
        with olivine and pyroxene ophitic gabbros, mafic 
        gneisses and schists that contain serpentine.
        The U-Pb ages of detrital zircons from the slates at 
        Buill previously mapped as part of the mid-Paleozoic 
        to Triassic MPT unit (Encinas et al., 2014), have 
        yielded an Early Devonian maximum possible 
        sedimentation age (405 Ma), concordant with the 
        paleontological age of lithologically similar Lower 
        Devonian fossil-bearing slate boulders assigned by 
        Fortey et al. (1992).
        The U-Pb SHRIMP zircon dating of low-grade 
        metamorphic rocks of the Llancahue epi-metamorphic 
        complex (Cembrano, 1990) has yielded surprising results. The maximum possible depositional ages 
        of these rocks appears to be Late Paleocene at Roca 
        Blanca, early Eocene at Punta Quiaca, and late 
        Eocene at Puerto Bonito. These results rule out the 
        previous correlation of these rocks with the Late 
        Paleozoic accretionary complex of the Coast Ranges 
        in Central Chile based on similar metamorphic 
        grade and lithology (Sernageomin, 2003; Duhart, 
        2008; Encinas et al., 2013). Pankhurst et al. (1992) 
        produced a whole rock Rb-Sr age of 292±2 Ma for the Huinay schists. This “age” was interpreted as metamorphic by the authors with great caution, as 
        several points plotted outside the errorchron and 
        were omitted from the calculation. Late Oligocene 
        and late Miocene plutons intruding the Huinay 
        schists dated here do not in any way imply that the 
        intruded rocks are Paleozoic, but neither do they 
        prove that they are younger.
        The obtained ages for rocks of the Llancahue epi-
        metamorphic complex at Punta Quiaca and Puerto 
        Bonito of Isla Llancahue, and for the Huinay schists 
        at Roca Blanca, have no counterpart in previously dated geological units in the area. They are older 
        than the late Oligocene-early Miocene Ayacara 
        Formation, which however has a volcanoclastic lower 
        member with an unknown base: the metasandstone 
        from Puerto Bonito has some resemblance to the 
        younger sample CAYA 4 of the lower member of the 
        Ayacara Formation (Encinas et al., 2013), in sharing 
        Cretaceous and Late Paleozoic detrital zircon age peaks, pointing to similar geological source areas. At Puerto Bonito, and at Fiordo Andrade, foliated 12
        Ultramafic  rocks  in the north Patagonian  andes: is their  emPlacement  associated  with the neogene  tectonics ...
        pillow lavas seemingly underlie the metasedimentary 
        rocks with a shared foliation, and thus are probably 
        also Cenozoic, but older than the Ayacara Formation. 
        Encinas et al . (2013) report an Eocene age for 
        volcanic rocks at Isla Mitahue in the outcrop area of 
        the Traiguén Formation, suggesting that deposition 
        of volcanic rocks in the area started before the late 
        Oligocene-early Miocene volcanic maximum.
        According to Encinas et al. (2013) deposition of 
        the Ayacara Formation is broadly contemporaneous 
        with plate reorganization in the Pacific Ocean, which 
        gave rise to the Nazca plate. The data presented here 
        suggest that extensional deposition basins in this area started to develop in Paleocene and Eocene 
        times: basaltic volcanism in this initial stage is 
        represented by the pillow basalts at Isla Llancahue 
        island. Paleomagnetic studies (Rojas et al., 1994) 
        showed that counter-clockwise block rotations took 
        place west of the LOFZ, in response to a buttressed 
        dextral movement of the continental margin. This 
        tectonic scenario allows the generation of extensional 
        basins in co-existence with compressional areas, and 
        the Ayacara Formation may have been deposited 
        in a deep basin in which this mechanism enhanced 
        the general early Miocene extension in the forearc.
        The structure of the area was interpreted as a 
        half-flower structure by Hervé (1994) and as a full 
        flower structure by Encinas et al. (2013) based on 
        the transpressional regime attending the LOFZ. The 
        associated reverse faults might have cut the thinned 
        continental crust of the extensional basins and thrust 
        a slice, or slices, of the underlying lithospheric 
        mantle now represented by the harzburgites and 
        derived serpentinitic rocks. The association of the 
        ultramafic rocks with gabbros and pillow basalts 
        suggests that bi-modal volcanism occurred in 
        these basins, as silicic volcaniclastic rocks are an 
        important component of the deposits of the Ayacara 
        Formation. However, the lack of a well-defined 
        dyke swarm in this area is notable, and contrasts 
        with what is seen in the contemporaneous Traiguén 
        Formation ~200 km to the south (Silva, 2003; 
        Encinas et al., 2014). 
        The association of ultramafic rocks, pillow 
        basalts and turbiditic sediments in a basin or basins 
        aligned parallel to a main lithospheric structure-
        the LOFZ-can be interpreted as representing an 
        ophiolitic suite (Pérez, 1999) developed in a suture 
        zone. The western block, mainly comprising the 
        Late Paleozoic accretionary prism, which might be identified as the Chiloé block of Forsythe (1982), started to rift from the South America continent in 
        the Paleocene, reaching maximum separation during 
        the late Oligocene-early Miocene and colliding back 
        with the continent starting in the mid Miocene. Thus 
        the Cenozoic evolution of this section of the North Patagonian Andes may have involved splitting off of an autochthonous terrane which soon collided back with the mother continent (Fig. 6).
        8. Conclusions
        A partially serpentinized harzburgite body crops 
        out in the western foothills of the Main Range 
        Andes in Continental Chiloé. Previous work was 
        taken to indicate that this hitherto little-known body 
        belongs to a presumed late Paleozoic volcanic and 
        sedimentary assemblage. SHRIMP U-Pb analyses 
        of detrital zircons from the Buill slates, which have 
        Devonian fossils, gave a maximum deposition age 
        of 405 Ma, consistent with that part of the unit 
        genuinely being Paleozoic. However, such data 
        for other rocks attributed to this unit give variable maximum possible sedimentation ages of 58 Ma, 
        53 Ma and 36 Ma, clearly indicating that they were 
        deposited during Cenozoic times. SHRIMP U-Pb 
        ages of magmatic zircon from four cross-cutting 
        intrusive rocks range from 24 Ma to 8 Ma, in general 
        agreement with this younger depositional age. A 
        corollary is that deformational metamorphism with 
        regional extension developed in the area during the 
        Cenozoic, lasting until after the late Oligocene-early 
        Miocene deposition of the Ayacara Formation. 
        The ultramafic rocks are interpreted as having 
        been tectonically emplaced during the Cenozoic, in 
        a tectonic regime associated with transpressional 
        tectonics in the Liquiñe-Ofqui Fault Zone. This 
        emplacement probably took place during or after mid-Miocene extension of the forearc crust, and 
        incorporated a thin sliver of supra-subduction 
        continental crust covering the up-thrust mantle rocks.
        Acknowledgements
        This study was supported by FONDECYT project 
        1130227. Captain C. Barrientos took us safely to the 
        coastal exposures from Hornopirén. Dr. V . Haussermann 
        of Huinay scientific station supported part of the initial 
        field work in the area. Dr. G. Galaz revised initial ver -
        sions of the manuscript and produced figures 1 and 2. Revision by Dr. P. Duhart improved the text. 13
        Hervé et al. / Andean Geology 44 (1): 1-16, 2017
        FIG. 6. A. Schematic NE-SW geological cross-section of the study area (see figure 2 for location), showing the structural relations 
        between the different lithostratigraphic units, plutonic complexes and the Liquiñe-Ofqui Fault Zone (LOFZ). The flower 
        structure is related to the transpressional regime attending the LOFZ since the late Miocene;  B. Paleogeographic reconstructions 
        for periods between 60-40 and 40-20 Ma, based on data and interpretations summarized in the text, indicating the generalized 
        transtensional depositional environment and magmatism. It is highlighted the emplacement of oceanic-type mafic crust in zones of maximum extension.14
        Ultramafic  rocks  in the north Patagonian  andes: is their  emPlacement  associated  with the neogene  tectonics ...
        References
        Adriasola, A.C.; Thomson, S.N.; Brix, M.R.; Hervé, F.; 
        Stockhert, B. 2005. Postmagmatic cooling and late 
        Cenozoic denudation of the North Patagonian Batho -
        lith in the Los Lagos region of Chile, 41°-42°15’S. 
        International Journal of Earth Sciences 95: 504. doi: 
        10.1007/s00531-005-0027-9.
        Alfaro, G. 1980. Antecedentes preliminares sobre la 
        composición y génesis de las cromitas de La Cabaña 
        (Cautín). Revista Geológica de Chile 11: 29-41. doi: 
        10.5027/andgeoV7n3-a02.
        Anma, R.; Armstrong, R.; Danhara, T.; Orihashi, Y .; 
        Iwano, H. 2006. Zircon sensitive high mass-resolution 
        ion micro- probe U-Pb and fission-track ages for 
        gabbros and sheeted dykes of the Taitao ophiolite, 
        Southern Chile, and their tectonic implications. Island 
        Arc 15: 130-142. 
        Barra, F.; Rabbia, O.; Alfaro, G.; Miller, H.; Höfer, 
        C.; Kraus, S. 1998. Serpentinitas y cromititas de 
        La Cabaña, Cordillera de la Costa, Chile central. 
        Revista Geológica de Chile 25: 29-44. doi: 10.5027/
        andgeoV25n1-a03.
        Beck, M.; Rojas, C.; Cembrano, J. 1993. On the nature 
        of buttressing in strike slip fault systems. Geology 
        21: 755-758.
        Cande, S.C.; Leslie, R.B. 1986. Late Cenozoic tectonics 
        of the southern Chile trench. Journal of Geophysical 
        Research 91B: 471-496.
        Caro, R. 2006. Estudio geológico de los placeres auríferos 
        de la Península de Huequi, Chiloé continental, 
        X Región, Chile. Memoria de Título de Geólogo 
        (Unpublished), Universidad de Chile, Departamento 
        de Geología: 89 p. 
        Cembrano, J. 1990. Las rocas plutónicas del borde 
        occidental del batolito norpatagónico y rocas 
        metamórficas asociadas, Chiloé continental. Memoria 
        de Título de Geólogo (Unpublished), Universidad de 
        Chile, Departamento de Geología, : 64 p. 
        Cembrano, J.; Hervé, F.; Lavenu, A. 1996. The Liquiñe-
        Ofqui Fault Zone: a long lived intra-arc fault system 
        in southern Chile. Tectonophysics 250: 55-66. 
        Crignola, P. 1999. Geología del Fiordo Reñihue y parte 
        occidental de la Peninsula Huequi, Chiloé Continental, 
        X Region, Chile. Memoria de Titulo de Geólogo 
        (Unpublished), Universidad de Concepción: 115 p.
        Crignola, P.; Duhart, P.; McDonough, M.; Muñoz, J. 
        1997. Antecedentes geoquímicos acerca del origen 
        de los esquistos máficos y cuerpos ultramáficos en la 
        Cordillera de la Costa, sector norte de la X Región, Chile. In Congreso Geológico Chileno, No. 8, Actas 
        2: 1254-1258. Antofagasta. 
        Duhart, P. 2008. Processos metalogeneticos em 
        ambientes de arco magmatico tipo andino, caso 
        de estudo: mineralizacoes da regiao dos Andes 
        Patagonicos setentrionais do Chile. Tesis de Doutorado 
        (Unpublished), Universidade de Sao Paulo, Instituto 
        de Geociencias: 215 p. Brasil.
        Duhart, P.; McDonough, M.; Muñoz, J.; Martin, M.; 
        Villeneuve, M. 2001. El Complejo Metamórfico Bahía 
        Mansa en la cordillera de la Costa del centro-sur de 
        Chile (39°30’-42°00’S): geocronología K-Ar, 40Ar/39Ar 
        y U-Pb e implicancias en la evolución del margen sur-occidental de Gondwana. Revista Geológica de 
        Chile 28: 179-208.
        Encinas, A.; Zambrano, P.A.; Finger, K.L.; Valencia, V .;                    
        Buatois, L.A.; Duhart, P. 2013. Implications of Deep-
        marine Miocene Deposits on the Evolution of the North 
        Patagonian Andes. Journal of Geology 121: 215-238.
        Encinas, A.; Pérez, F.; Nielsen, S.N.; Finger, K.L.; Valencia, 
        V .; Duhart, P. 2014. Geochronologic and paleontologic 
        evidence for a Pacific-Atlantic connection during 
        the late Oligocene-early Miocene in the Patagonian 
        Andes (43-44°S). Journal of South American Earth 
        Sciences 55: 1-18.
        Encinas, A.; Folguera, A.; Oliveros, V .; De Girolamo, 
        Del Mauro, L.; Tapia, F.; Riffo, R.; Hervé, F.; 
        Finger, K.L.; Valencia, V .A.; Gianni, G.; Álvarez, O.         
        2015. Late Oligocene-early Miocene submarine 
        volcanism and deep-marine sedimentation in an 
        extensional basin of southern Chile: implications on 
        the tectonic development of the North Patagonian 
        Andes. Geological Society of America Bulletin 128 
        (5-6): 807. doi: 10.1130/B31303.1.
        Forsythe, R.D. 1982. The late Paleozoic to early Mesozoic 
        evolution of southern South America: a plate tectonic 
        interpretation. Journal of the Geological Society 
        139: 671-682.
        Forsythe, R.D.; Nelson, E.P. 1985. Geological manifestation 
        of ridge collision: Evidence from the Golfo de Penas-
        Taitao Basin, Southern Chile. Tectonics 4 (5): 477-495.
        Fortey, R.; Pankhurst, R.J.; Hervé, F. 1992. Devonian 
        trilobites at Buill, Southern Chile. Revista Geológica 
        de Chile 19: 133-144.
        Godoy, E.; Kato, T. 1990. Late Paleozoic serpentinites 
        and mafic schists from the Coast Range accretionary 
        complex, central Chile: their relation to aeromagnetic 
        anomalies. Geologische Rundschau 79: 121-130. 
        González-Jiménez, J.M.; Barra, F.; Walker, R.J.; Reich, 
        M.; Gervilla, F. 2014. Geodynamic implications of 15
        Hervé et al. / Andean Geology 44 (1): 1-16, 2017
        ophiolitic chromitites in the La Cabaña ultramafic 
        bodies, Central Chile. International Geology Review 56 
        (12): 1466-1483. doi: 10.1080/00206814.2014.947334.
        Hervé, M. 1976. Estudio Geológico de la Falla Liquiñe-
        Reloncaví en el área de Liquiñe: antecedentes de un 
        movimiento transcurrente. In Congreso Geológico 
        Chileno, Actas 1: B39-B56. Santiago.
        Hervé, F. 1988. Late Paleozoic subduction and accretion 
        in southern Chile. Episodes 11: 183-188.
        Hervé, F. 1994. The Southern Andes between 39° and 44° 
        S Latitude: the geological signature of a transpressive 
        tectonic regime related to a magmatic arc. In Tectonics of 
        the Southern Central Andes (Reutter, K.J.; Scheuber, E.; 
        Wigger, P.J.; editors). Springer-Verlag: 243-248. Berlin.
        Hervé, F.; Del Campo, M. 1975. Estudio petrográfico 
        del gabro de Laguna Verde, Provincia de Valparaíso, 
        Chile. Revista Geológica de Chile 2: 22-33. doi: 
        10.5027/andgeoV2n1-a03.
        Hervé, F.; Araya, E.; Fuenzalida, J.L.; Solano, A. 1978. 
        Nuevos antecedentes sobre la geología de Chiloé 
        continental. In Congreso Geológico Argentino, No. 7, Actas 1: 629-638. Neuquén.
        Hervé, F.; Pankhurst, R.J.; Drake, R.; Beck, M. 1995. 
        Pillow metabasalts in a mid-Tertiary extensional 
        basin adjacent to the Liquiñe-Ofqui fault zone: the Isla Magdalena area, Aysén, Chile. Journal of South 
        American Earth Sciences 8: 33-46. 
        Hernández, L. 2006. Rocas máficas y ultramáficas 
        en Laguna Verde, Chile central. Memoria Título 
        de Geólogo (Unpublished), Universidad de Chile, 
        Departamento de Geología: 132 p. 
        Heusser, C.J. 1990. Chilotan piedmont glacier in the 
        southern Andes during the last glacial maximum. 
        Revista Geologica de Chile 17 (1): 3-18. doi: 10.5027/
        andgeoV17n1-a01.
        Höfer, C.; Kraus, S.; Miller, H.; Alfaro, G.; Barra, F. 
        2001. Chromite-bearing serpentinite bodies within an 
        arc-backarc metamorphic complex near La Cabaña, 
        south Chilean Coastal Cordillera. Journal of South 
        American Earth Sciences 14: 113-126. doi:10.1016/
        S0895-9811(01)00011-6.
        Lefort, J.P.; Aifa, T.; Hervé, F. 2006. Structural and AMS study 
        of a Miocene dyke swarm located above the Patagonian 
        subduction. In Dyke Swarms- Time Markers of Crustal 
        Evolution (Hanski, E; Mertanen, S.; Ramö, T.; Vuollo, J.;                                                                                           
        editors), Taylor and Francis Group: 225-241. London.
        Levi, B.; Aguilar, A.; Fuenzalida, R. 1966. Reconocimiento 
        geológico en las provincias de Llanquihue y Chiloé. Instituto de Investigaciones Geológicas, Boletin 19: 
        45 p. Santiago.Ojeda, J.M. 1976. Estudio petrológico y estructural del 
        basamento metamórfico y de la serpentinita de Morro 
        Bonifacio, provincia de Valdivia, Décima Región. 
        Memoria de Título (Unpublished), Universidad de Chile, Departamento de Geología: 94 p.
        Pankhurst, R.J.; Hervé, F.; Rojas, L.; Cembrano, J. 1992. 
        Magmatism and Tectonics in continental Chiloé, 
        Chile (42°-42° 30’). Tectonophysics 205: 283-294.
        Pankhurst, R.J.; Weaver, S.D.; Hervé, F.; Larrondo, P.; 1999. 
        Mesozoic-Cenozoic evolution of the North Patagonian 
        Batholith in Aysen, Southern Chile. Journal of the 
        Geological Society 156: 673-694. London.
        Pérez, Y . 1999. Geología de la region oriental de la 
        Peninsula Huequi y zonas costeras del Fiordo 
        Comau (42°00’-42°30’S), Chiloé Continental, 
        Provincia de Palena, X Región. Memoria de Título 
        de Geólogo (Unpublished), Universidad de Concep-                                                     
        ción: 172 p.
        Rojas, C. 2003. Estratigrafía, facies y paleomagnetismo de 
        la Formación Ayacara, Provincia de Palena. Memoria 
        Título de Geólogo (Unpublished), Universidad de 
        Chile, Departamento de Geología: 84 p.
        Rojas, C.; Beck, M.; Jr., Burmester, R.F.; Cembrano, J.; 
        Hervé, F. 1994. Paleomagnetism of the Mid Tertiary 
        Ayacara Formation, southern Chile: counterclockwise 
        rotation in a dextral shear zone. Journal of South 
        American Earth Sciences 7: 45-56.
        Sanhueza, A. 1996. El Complejo Acrecionario y la Zona 
        de Falla Liquiñe-Ofqui en los fiordos Reñihué y 
        Comau (42°-43°S), Chiloé Continental. Memoria de 
        Título de Geólogo y Grado de Magíster en Geología 
        (Unpublished), Universidad de Chile, Departamento 
        de Geología: 93 p.
        Schilling, M.; Carlson, R.W.; Vieira, R.; Dantas, C.; 
        Bertotto, G.W.; Koester, E. 2008. Re-Os isotope 
        constraints on subcontinental lithospheric mantle 
        evolution of southern South America Earth and 
        Planetary Science Letters 268: 89-101.
        SERNAGEOMIN  (Servicio Nacional de Geología y 
        Minería) 2003. Mapa Geológico de Chile, Versión 
        Digital: Sernageomin Publicación Geológica Digital 
        4, CD- ROM, version 1.0, scale 1:1.000.000. Chile.
        Silva, C. 2003. Ambiente geotectónico de erupción y 
        metamorfismo de metabasaltos almohadillados, 
        Andes Norpatagónico (42ºS-46ºS), Chile. Memoria de 
        Título de Geólogo y Grado de Magíster en Geología 
        (Unpublished), Universidad de Chile, Departamento 
        de Geología.
        Vergara, L. 1970. Prospección de yacimientos de cromo 
        y hierro en La Cabaña, Cautín. Memoria de Título 16
        Ultramafic  rocks  in the north Patagonian  andes: is their  emPlacement  associated  with the neogene  tectonics ...
        (Unpublished), Universidad de Chile, Departamento 
        de Geología: 96 p. 
        Williams, I.S. 1998. U-Th-Pb geochronology by ion 
        microprobe. In Applications of Microanalytical Techniques to Understanding Mineralizing Pro -
        cesses (McKibben, M.A.; Shanks III, W.C.; Ridley, 
        W.I.; editors). Reviews of Economic Geology 7:                                                                                           
        1-35.
        Manuscript received: March 16, 2016; revised/accepted: October 24, 2016; available onlin e: October  27, 2016."""]
        #crear documento manualmente
        content_doc = [Document(text=t) for t in text_list]


        print(content_doc)
       

        # Mensajes para la conversación con el modelo
        """prompt = f"{question} {content}"
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        answer = response.choices[0].message["content"]
        #await ctx.send(f"Respuesta por OpenAI: {answer}")
        print(f"Respuesta por OpenAI: {answer}")"""
        

        
    

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