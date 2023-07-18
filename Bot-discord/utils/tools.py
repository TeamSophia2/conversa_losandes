import pandas as pd
from io import StringIO
import pdfplumber
from langdetect import detect


class Tools:
    def readCSV(self, file_data):
        # Convierte los datos del archivo en un objeto StringIO
        csv_data = file_data.decode('utf-8')
        csv_file = StringIO(csv_data)

        # Lee el archivo CSV utilizando pandas
        try:
            df = pd.read_csv(csv_file)
        except pd.errors.ParserError:
            return None

        # Valida las columnas requeridas
        required_columns = ["LT", "AUTORES/AS", "TÍTULO", "AÑO", "REVISTA", "DOI", "CATEGORÍA", "REGIÓN", "COMUNAS", "Enlace"]

        if set(required_columns).issubset(df.columns):
            return df
        else:
            return None


    """Toma un archivo y devuelve un dataframe solamente con dos atributos(Columnas): 
    texto completo del pdf(text) y el idioma(lang)"""
    def readPdf(self, pdf_data):
        # Convierte los datos del archivo en un objeto StringIO
        #pdf = pdf_data.decode('utf-8')
        pdf_stream = StringIO(pdf)

        # Lee el archivo PDF utilizando PyPDF2
        try:
            pdf_reader = PyPDF2.PdfFileReader(pdf_stream)
        except:
            return None

        # Procesar el PDF y extraer el texto y el lenguaje
        text = ""
        for page_num in range(pdf_reader.numPages):
            page = pdf_reader.getPage(page_num)
            text += page.extract_text()

        lang = detect(text)

        # Crea un DataFrame con el texto y el lenguaje
        df = pd.DataFrame({'text': [text], 'lang': [lang]})

        return df


        
    
