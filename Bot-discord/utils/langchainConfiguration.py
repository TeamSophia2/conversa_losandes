from langchain import OpenAI, SQLDatabase
import openai
from langchain_experimental.sql import SQLDatabaseChain
import os
TOKEN_OPENAI = os.environ.get('GPT_TOKEN')
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
 Always answer in spanish. Don't put limits on the sql query unless the question sets a limit. Use the following format:

Question: Question here
SQLQuery: SQL Query to run
SQLResult: Result of the SQLQuery
Answer: Final answer here

{question}
"""

# Set up the database chain
dbChain = SQLDatabaseChain(llm=llm, database=db, verbose=True)
