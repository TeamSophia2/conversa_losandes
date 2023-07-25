import os
import requests
from utils.tools import Tools


class Scraper:

    async def downloadDocument(self, title, url):
        if url:
            # Descargar el PDF desde el enlace proporcionado
            response = requests.get(url)
            if response.status_code == 200:
                # Guardar el PDF en el sistema local con el título como nombre de archivo
                pdf_file = f"{title}.pdf"
                with open(pdf_file, "wb") as file:
                    file.write(response.content)

                # Crear una instancia de la clase Tools
                tools = Tools()

                # Utilizar el método readPdf para obtener el texto del PDF
                tools.readPdf(pdf_file, title)

                os.remove(pdf_file)

            else:
                print(
                    f"La URL '{url}' no es válida. No se puede descargar el PDF.")

        else:
            print("El campo 'url' está vacío o contiene un valor inválido.")
