import pandas as pd
import PyPDF2
from utils.databaseConnector import databaseConnector
import asyncio
from discord import Embed

class Tools:
    def readCSV(self, filename):
        # Lee el archivo CSV utilizando pandas
        try:
            df = pd.read_csv(filename)
        except pd.errors.ParserError:
            return None

        # Valida las columnas requeridas
        required_columns = ["LT", "AUTORES/AS", "TÍTULO", "AÑO",
                            "REVISTA", "DOI", "CATEGORÍA", "REGIÓN", "COMUNAS", "Enlace"]

        if set(required_columns).issubset(df.columns):
            return df
        else:
            return None

    async def readPdf(self,pdfFile, title, failedDownloads):
        # Lee el archivo PDF
        # Utilizar PyPDF2 para extraer el texto del PDF
        try:
            pdfText = ""
            with open(pdfFile, "rb") as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)
                for pageNum in range(num_pages):
                    page = pdf_reader.pages[pageNum]
                    pdfText += page.extract_text()


            
            if pdfText is not None:
                # Inserción del documento en la base de datos
                dbConnector = databaseConnector()
                dbConnector.connect()
                dbConnector.insertDocumentData(title, pdfText)
                dbConnector.close()
                print(f"Documento '{title}' insertado en la base de datos.")
            else:
                print(f"No se pudo leer el contenido del PDF '{title}'.")

        except Exception as e:
            print(f"Error en la lectura del PDF '{pdfFile}': {e}")
            failedDownloads.append(title)
