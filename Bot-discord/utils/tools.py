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

    @classmethod
    async def paginar_resultados(cls, ctx, results, results_per_page=5):
        total_results = len(results)
        total_pages = (total_results + results_per_page - 1) // results_per_page
        page = 1

        while page <= total_pages:
            start_index = (page - 1) * results_per_page
            end_index = min(start_index + results_per_page, total_results)
            current_page_results = results[start_index:end_index]

            formatted_page_results = "\n".join([f"{i+1}. **{result[0] if isinstance(result, tuple) else result}**\n" for i, result in enumerate(current_page_results)])
            embed = Embed(title=f"Página {page} de {total_pages}", description=formatted_page_results)

            message = await ctx.send(embed=embed)

            # Agregar las reacciones al mensaje
            reactions = []
            if total_pages > 1:
                if page > 1:
                    reactions.append('⏪')  # Botón para ir a la primera página
                    reactions.append('⬅️')  # Botón para retroceder una página
                if page < total_pages:
                    reactions.append('➡️')  # Botón para avanzar una página
                    reactions.append('⏩')  # Botón para ir a la última página

            for reaction in reactions:
                await message.add_reaction(reaction)

            if total_pages > 1:
                def check(reaction, user):
                    return user == ctx.author and reaction.message == message

                try:
                    reaction, _ = await cls.bot.wait_for('reaction_add', timeout=300.0, check=check)

                    if reaction.emoji == '⬅️' and page > 1:
                        page -= 1
                    elif reaction.emoji == '➡️' and page < total_pages:
                        page += 1
                    elif reaction.emoji == '⏪':
                        page = 1  # Ir a la primera página
                    elif reaction.emoji == '⏩':
                        page = total_pages  # Ir a la última página

                    await message.delete()
                except asyncio.TimeoutError:
                    break
            else:
                break
