import os
import requests
from utils.tools import Tools
import asyncio
import re
import aiohttp

class Scraper:
    

    async def downloadDocument(self, title, url):
        print("esto en downloadDocument")
        print(url)
        if url:
            if "drive.google.com" in url:
                # Si la URL es de Google Drive, descargar desde allí
                await self.downloadFromGoogleDrive(title, url)
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
                                await tools.readPdf(pdfFile, title)
                                os.remove(pdfFile)
                            else:
                                print(f"La URL '{url}' no es válida. No se puede descargar el PDF.")
                                #self.failedDownloads.append(title)
                except Exception as e:
                    print(f"Error al descargar el PDF desde '{url}': {e}")
                    
        else:
            print("El campo 'url' está vacío o contiene un valor inválido.")


    async def downloadFromGoogleDrive(self, title, url):
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
                            await tools.readPdf(pdfFile, title)
                            os.remove(pdfFile)
                        else:
                            print(f"La URL de Google Drive '{url}' no es válida. No se puede descargar el PDF.")
                            #self.failedDownloads.append(title, self.failedDownloads)
                            
            except Exception as e:
                print(f"Error al descargar el PDF desde Google Drive: {e}")
                #self.failedDownloads.append(title)

        else:
            print(f"La URL de Google Drive '{url}' no es válida. No se pudo extraer el ID del archivo.")
