import os
import requests
from utils.tools import Tools
import asyncio
import re
import aiohttp
import subprocess

class Scraper:
    

    async def downloadDocument(self, title, url, failedDownloads):
        print("esto en downloadDocument")
        print(url)
        if url:
            if "drive.google.com" in url:
                # Si la URL es de Google Drive, descargar desde allí
                await self.downloadFromGoogleDrive(title, url, failedDownloads)
            else:
                try:
                    # Utilizar aiohttp para descargar de otras fuentes
                    async with aiohttp.ClientSession() as session:
                        async with session.get(url) as response:
                            if response.status == 200:
                                pdfFile = f"{title[:100]}.pdf"  # Acorta el título para el nombre de archivo
                                with open(pdfFile, "wb") as file:
                                    file.write(await response.read())
                                # Leer el contenido del PDF y agregar a la base de datos
                                tools=Tools()
                                await tools.readPdf(pdfFile, title,failedDownloads)
                                os.remove(pdfFile)
                            else:
                                print(f"La URL '{url}' no es válida. No se puede descargar el PDF.")
                                failedDownloads.append(title)
                except Exception as e:
                    print(f"Error al descargar el PDF desde '{url}': {e}")
                    failedDownloads.append(title)
                    
        else:
            print("El campo 'url' está vacío o contiene un valor inválido.")
            failedDownloads.append(title)

    async def downloadFromGoogleDrive(self, title, url, failedDownloads):
        # Extraer el ID del archivo de Google Drive de la URL
        match = re.search(r"/d/([^/]+)/", url)
        if match:
            file_id = match.group(1)
            direct_download_url = f"https://drive.google.com/uc?id={file_id}"

            # Acorta el título para el nombre de archivo
            pdfFile = f"{title[:100]}.pdf"

            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(direct_download_url) as response:
                        if response.status == 200:
                            with open(pdfFile, "wb") as file:
                                file.write(await response.read())
                            # Agregar la tarea de descarga y guardar el título completo en la base de datos a la cola
                            tools=Tools()
                            await tools.readPdf(pdfFile, title, failedDownloads)
                            os.remove(pdfFile)
                        else:
                            print(f"La URL de Google Drive '{url}' no es válida. No se puede descargar el PDF.")
                            failedDownloads.append(title)
                            
            except Exception as e:
                print(f"Error al descargar el PDF desde Google Drive: {e}")
                failedDownloads.append(title)

        else:
            print(f"La URL de Google Drive '{url}' no es válida. No se pudo extraer el ID del archivo.")
            failedDownloads.append(title)

    async def scrapeTesis(self):
        try:
            # Ejecutar el script como un subproceso
            proceso = subprocess.Popen(['python3', '/home/fernando/Documentos/conversar_los_andes_mia/conversar_los_andes/Bot-discord/hola/scrapingListaLista.py'])

            # Esperar hasta que el archivo exista
            file_path = '/home/fernando/Documentos/conversar_los_andes_mia/conversar_los_andes/Bot-discord/hola/tesis_data_listo.csv'
            while not os.path.exists(file_path):
                await asyncio.sleep(1)

            return file_path

        except Exception as e:
            print(f'Error al ejecutar el script: {e}')
            return None