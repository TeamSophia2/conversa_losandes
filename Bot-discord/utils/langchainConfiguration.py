from langchain import OpenAI, SQLDatabase
import openai
from langchain_experimental.sql import SQLDatabaseChain
import os

TOKEN_OPENAI = os.environ.get('OPENAI_API_KEY')
openai.api_key = TOKEN_OPENAI



# Set up database
db = SQLDatabase.from_uri(
    f"mysql+pymysql://andes:andes@localhost/andes",
)
llm = OpenAI(openai_api_key=TOKEN_OPENAI, temperature=0)

# Create db chain
QUERY = """
Given an input question, first create a syntactically correct sql query to execute, then look at the query results and return the answer.
 Consider that the Document_Author table exists, which is the one that relates the documents to their respective author.
 Consider that the Document_Commune table exists, which is the one that relates the documents to their respective communes.
 Consider that the Document_Category table exists, which is the one that relates the documents to their respective category.
 Consider that the Document_Organization table exists, which is the one that relates the documents to their respective organization.
 Considerar that categoria is the value categoryName in the table Category.
 Consider that Laboratorio or laboratorio tematico is the value principalCategoryId in the table Category 
 Make sure you understand that when I mention "categoria," I'm referring to the categoryName value in the Category table
 Also, understand that "Laboratorio" or "laboratorio tematico" refers to the principalCategoryId value in the Category table.
 Always answer in spanish. Don't put limits on the sql query unless the question sets a limit. Use the following format:

Question: Question here
SQLQuery: SQL Query to run
SQLResult: Result of the SQLQuery
Answer: Final answer here

{question}
"""

# Set up the database chain
dbChain = SQLDatabaseChain(llm=llm, database=db, verbose=True)
