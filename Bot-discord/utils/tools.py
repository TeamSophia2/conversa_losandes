import pandas as pd
from io import StringIO
import PyPDF4
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
    def readPdf(self,filename):
        # Abrir el archivo PDF en modo binario con PyPDF4
        with open(filename, "rb") as file:
            # Crear un lector de PDF
            reader = PyPDF4.PdfReader(file)
            
            # Inicializar listas para almacenar el texto y el idioma
            text_list = []
            lang_list = []
            
            # Leer cada página del PDF
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text = page.extract_text()
                
                # Si el texto no está vacío, agregarlo a la lista y detectar el idioma
                if text.strip():
                    # Decodificar el texto usando utf-8
                    text = text.decode('utf-8', errors='ignore')
                    text_list.append(text)
                    lang = detect(text)
                    lang_list.append(lang)
        
        # Crear el DataFrame con las listas
        df = pd.DataFrame({"text": text_list, "lang": lang_list})
        return df



        
    
