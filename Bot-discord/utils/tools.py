import pandas as pd

class Tools:
    def readCSV(self, filename):
        # Lee el archivo CSV utilizando pandas
        try:
            df = pd.read_csv(filename)
        except pd.errors.ParserError:
            return None

        # Valida las columnas requeridas
        required_columns = ["LT", "AUTORES/AS", "TÍTULO", "AÑO", "REVISTA", "DOI", "CATEGORÍA", "REGIÓN", "COMUNAS", "Enlace"]

        if set(required_columns).issubset(df.columns):
            return df
        else:
            return None

    def readPdf(self, filename):
        # Lee el archivo PDF 
        return 0
