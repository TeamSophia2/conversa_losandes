import pymysql
import pandas as pd


class databaseConnector:
    def __init__(self):
        self.host = 'localhost'
        self.user = 'andes'
        self.password = 'andes'
        self.database = 'andes'
        self.connection = None

    def connect(self):
        try:
            self.connection = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            print("Conexión a la base de datos exitosa.")
        except pymysql.Error as e:
            print(f"Error al conectar a la base de datos: {e}")

    def close(self):
        if self.connection:
            self.connection.close()
            print("Conexión a la base de datos cerrada.")

    def insertsDocuments(self, df):
        commune_region_data = pd.read_csv('match comunas regiones.csv')

        cursor = self.connection.cursor()
             # Recorre el DataFrame y procesa los documentos
        for w, row in df.iterrows():
            # Extrae los valores del DataFrame
            doi = row['DOI']
            url = row['Enlace'] if pd.notna(row['Enlace']) else None
            documentType = None
            publicationYear = row['AÑO']
            title = row['TÍTULO']
            content = None
            abstract = None
            category = row['CATEGORÍA']
            author = row['AUTORES/AS']

            # Verifica si el valor doi es NaN y reemplázalo con None
            if pd.notna(doi):
                doi = str(doi)
            else:
                doi = None

            # Inserta el registro en la tabla Documento sin proporcionar el valor de IDDocumento
            query = "INSERT INTO Document (doi, url, documentType, publicationYear, title, content, abstract) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            values = (
                doi,
                url,
                documentType,
                publicationYear,
                title,
                content,
                abstract
            )
            cursor.execute(query, values)
            self.connection.commit()

            # Obtén el documentId recién insertado
            documentId = cursor.lastrowid

            # ingresa datos a Document_Category

            category_list = category.split(';')
            for category in category_list:
                category = category.strip()
                # Verifica que la temática exista en la tabla Tematica
                cursor.execute(
                    "SELECT categoryName FROM Category WHERE categoryName = %s", (category,))
                result = cursor.fetchone()

                if result:

                    # Inserta la relación en Documento_Tematica
                    cursor.execute(
                        "INSERT INTO Document_Category (documentId, categoryName) VALUES (%s, %s)", (documentId, category))
                    self.connection.commit()
                else:
                    # Si la temática no existe, manejar el caso
                    print(w)

            authors = [author.strip() for author in author.split(';')]
            for author in authors:

                # Verifica si el autor ya existe en la tabla Author
                query = "SELECT authorId FROM Author WHERE authorName = %s"
                # Agrega strip() para eliminar espacios en blanco al inicio y final del nombre
                values = (author,)
                cursor.execute(query, values)
                result = cursor.fetchone()

                if result:
                    # Si el autor ya existe, no es necesario insertarlo nuevamente
                    # print(f"El autor '{author}' ya está registrado en la base de datos.")
                    author_id = result[0]
                else:
                    # Si el autor no existe, insertarlo en la tabla Author
                    query = "INSERT INTO Author (authorName) VALUES (%s)"
                    cursor.execute(query, values)
                    self.connection.commit()

                    cursor.execute(
                        "SELECT authorId FROM Author WHERE authorName = %s", (author,))
                    author_id = cursor.fetchone()[0]

                # Inserta la relación en Document_Author
                cursor.execute(
                    "INSERT INTO Document_Author (documentId, authorId) VALUES (%s, %s)", (documentId, author_id))
                self.connection.commit()

            # Tabla Commune

            comunas = [str(c).strip() for c in str(row['COMUNAS']).split(
                ',') if str(c).strip() and str(c).strip().lower() != 'nan']
            # Verificar si las comunas ya existen en la tabla Commune
            for comuna in comunas:
                cursor.execute(
                    "SELECT communeId FROM Commune WHERE name = %s ", (comuna, ))
                result = cursor.fetchone()

                if result:
                    communeId = result[0]
                    # Si la comuna ya existe, no es necesario agregarla nuevamente

                else:
                    # Buscar la región correspondiente en el DataFrame commune_region_df
                    region_match = commune_region_data[commune_region_data['Comuna'] == comuna]

                    # match
                    if not region_match.empty:
                        region = region_match['Región'].iloc[0]
                        latitude = region_match['Latitud (Decimal)'].iloc[0]
                        longitude = region_match['Longitud (decimal)'].iloc[0]

                        query = "INSERT INTO Commune (name, region, latitude, longitude) VALUES (%s, %s, %s, %s)"
                        values = (comuna, region, latitude, longitude)
                        cursor.execute(query, values)
                        self.connection.commit()

                        cursor.execute(
                            "SELECT communeId FROM Commune WHERE name = %s", (comuna,))
                        communeId = cursor.fetchone()[0]

                    # no match
                    else:
                        # Insertar la comuna en la tabla Commune con los campos region, latitude y longitude como NULL
                        # print(f"No se encontró la región para la comuna '{comuna}'. Se debe realizar el match manualmente.")
                        query = "INSERT INTO Commune (name, region, latitude, longitude) VALUES (%s, NULL, NULL, NULL)"
                        values = (comuna,)
                        cursor.execute(query, values)
                        self.connection.commit()
                        cursor.execute(
                            "SELECT communeId FROM Commune WHERE name = %s", (comuna,))
                        communeId = cursor.fetchone()[0]

                    # Inserta la relación en Document_Commune
                cursor.execute(
                    "INSERT INTO Document_Commune (documentId, communeId) VALUES (%s, %s)", (documentId, communeId))
