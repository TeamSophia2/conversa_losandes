import pandas as pd
from io import StringIO, BytesIO
from langdetect import detect
import PyPDF2
from utils.databaseConnector import databaseConnector


class Tools: 

    # Metodo que lee un archivo csv, y valida que las columnas son las requeridas
    # si cumple lo anterior devuelve un df, en caso contrario None
    def readCsv(self, file_data):
        # Convierte los datos del archivo en un objeto StringIO
        csv_data = file_data.decode('utf-8')
        csv_file = StringIO(csv_data)

        # Lee el archivo CSV utilizando pandas
        try:
            df = pd.read_csv(csv_file)
        except pd.errors.ParserError:
            return None

        # Valida las columnas requeridas
        required_columns = ["LT", "AUTORES/AS", "TÍTULO", "AÑO",
                            "REVISTA", "DOI", "CATEGORÍA", "REGIÓN", "COMUNAS", "Enlace"]

        if set(required_columns).issubset(df.columns):
            return df
        else:
            return None

    # funcion para leer el pdf descagado y guardarlo en la base de datos
    def readPdf(self,pdfFile, title):
            # Lee el archivo PDF
            # Utilizar PyPDF2 para extraer el texto del PDF
            try:
                pdfText = ""
                with open(pdfFile, "rb") as file:
                    pdfReader = PyPDF2.PdfReader(file)
                    numPages = len(pdfReader.pages)
                    for pageNum in range(numPages):
                        page = pdfReader.pages[pageNum]
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