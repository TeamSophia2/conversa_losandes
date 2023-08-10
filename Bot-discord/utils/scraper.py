import os
import requests
from utils.tools import Tools
import asyncio
import os

from utils.tools import Tools
from utils.databaseConnector import databaseConnector

class Scraper:
    def __init__(self):
        self.tools = Tools()

        self.download_and_save_queue = asyncio.Queue()

        # Iniciar el procesamiento de la cola en segundo plano
        asyncio.create_task(self.process_download_and_save_queue())

    async def downloadDocument(self, title, url):
        print(url)
        if url:
            try:
                # Utilizar asyncio.to_thread para hacer la llamada síncrona a requests.get en un subproceso
                response = await asyncio.to_thread(requests.get, url)
                if response.status_code == 200:
                    pdf_file = f"../../fernando/{title}.pdf"
                    with open(pdf_file, "wb") as file:
                        file.write(response.content)
                    # Agregar la tarea de descarga y guardado en la base de datos a la cola
                    await self.download_and_save_queue.put((pdf_file, title))

                else:
                    print(f"La URL '{url}' no es válida. No se puede descargar el PDF.")
            except Exception as e:
                print(f"Error al descargar el PDF desde '{url}': {e}")
        else:
            print("El campo 'url' está vacío o contiene un valor inválido.")



    async def process_download_and_save_queue(self):
        while True:
            # Esperar a que haya una tarea en la cola
            task = await self.download_and_save_queue.get()
            if task is None:
                # Si la tarea es None, significa que se ha terminado y se debe salir del bucle
                break

            pdf_file, title = task
            # Usar asyncio.to_thread para leer el contenido del PDF en un subproceso
            await asyncio.to_thread(self.tools.readPdf, pdf_file, title)

            # Eliminar el archivo PDF después de leer el contenido
            os.remove(pdf_file)