import pandas as pd
from io import StringIO
import fitz
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
    def readPdf(self, filename):
        # Abrir el archivo PDF en modo binario con PyMuPDF
        pdf_document = fitz.open(filename)

        # Inicializar listas para almacenar el texto y el idioma
        text_list = []
        lang_list = []

        # Leer cada página del PDF
        for page_num in range(pdf_document.page_count):
            page = pdf_document.load_page(page_num)
            text = page.get_text("text", flags=fitz.TEXT_INHIBIT_SPACES)

            # Si el texto no está vacío, agregarlo a la lista y detectar el idioma
            if text.strip():
                text_list.append(text)
                lang = detect(text)
                lang_list.append(lang)

        # Cerrar el documento PDF
        pdf_document.close()

        # Crear el DataFrame con las listas
        df = pd.DataFrame({"text": text_list, "lang": lang_list})
        return df



        
    
