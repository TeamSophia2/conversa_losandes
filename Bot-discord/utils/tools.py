import pandas as pd
from io import StringIO, BytesIO
import pdfplumber
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

    """Toma un archivo y devuelve un dataframe solamente con dos atributos(Columnas): 
    texto completo del pdf(text) y el idioma(lang)"""
    """
    def readPdf(self, pdf_data):
        # Convierte los datos del archivo en un objeto StringIO
        #pdf = pdf_data.decode('utf-8')
        pdf_stream = BytesIO(pdf_data)

        # Lee el archivo PDF utilizando PyPDF2
        try:
            pdf_reader = PdfReader(pdf_stream)
        except Exception as e:
            print("Error al leer el archivo PDF:", e)
            return None

        # Procesar el PDF y extraer el texto y el lenguaje
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()

        lang = detect(text)

        # Crea un DataFrame con el texto y el lenguaje
        df = pd.DataFrame({'text': [text], 'lang': [lang]})

        return df
    """

    # funcion para leer el pdf descagado y guardarlo en la base de datos
    def readPdf(self, pdfFile, title):
        # Lee el archivo PDF
        # Utilizar PyPDF2 para extraer el texto del PDF
        pdfText = ""
        with open(pdfFile, "rb") as file:
            pdf_reader = PyPDF2.PdfReader(pdfFile)
            num_pages = len(pdf_reader.pages)
            for pageNum in range(num_pages):
                page = pdf_reader.pages[pageNum]
                pdfText += page.extract_text()

        dbConnector = databaseConnector()

        # conectarse a la base de datos y agregar

        dbConnector.connect()
        # Llamar al método insertDocumentData de la clase DatabaseConnector para guardar la información en la base de datos
        dbConnector.insertDocumentData(title, pdfText)
        dbConnector.close()
