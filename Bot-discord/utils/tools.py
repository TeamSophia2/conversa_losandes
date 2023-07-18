import pandas as pd
from io import StringIO
import PyPDF4
from langdetect import detect
import fitz


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
    def readPdf(self, file_data, encoding='utf-8'):
        text_list = []
        pdf_file = StringIO(file_data.decode('utf-8'))
        pdf_document = fitz.open(stream=pdf_file, filetype="pdf")

        for page_number in range(pdf_document.page_count):
            page = pdf_document.load_page(page_number)
            text_list.append(page.get_text(encoding=encoding))

        pdf_document.close()

        # Detectar el lenguaje del texto en el PDF
        lang_list = [detect(text) for text in text_list]

        # Crear el DataFrame con las columnas "text" y "lang"
        df = pd.DataFrame({
            'text': text_list,
            'lang': lang_list
        })

        return df


        
    
