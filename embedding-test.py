from openai import OpenAI
from dotenv import load_dotenv
import asyncio

load_dotenv()

openai = OpenAI()

def embed(text):

    embedding = openai.embeddings.create(
        input=text, 
        model="text-embedding-3-small", 
        encoding_format="float"
    )
    print(embedding.data[0].embedding)

if __name__ == "__main__":
    embed("Hola, ¿cómo estás?")