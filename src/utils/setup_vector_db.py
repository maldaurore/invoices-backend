from chromadb import PersistentClient
from src.utils.paths import STORE_DIR
import os
import logging
from openai import OpenAI

logger = logging.getLogger(__name__)

openai = OpenAI()

productos = [
    {
        "id": "1",
        "nombre": "Laptop Dell Inspiron 15",
        "precio": 14500.00
    },
    {
        "id": "2",
        "nombre": "Smartphone Samsung Galaxy A54",
        "precio": 7800.00
    },
    {
        "id": "3",
        "nombre": "Monitor LG UltraWide 29",
        "precio": 5500.00
    },
    {
        "id": "4",
        "nombre": "Teclado Mecánico Logitech G Pro",
        "precio": 1200.00
    },
    {
        "id": "5",
        "nombre": "Mouse Inalámbrico Logitech M720",
        "precio": 800.00
    }
]

clientes = [
    {
        "nombre": "Juan Pérez",
        "direccion": "Calle Falsa 123, Ciudad Ficticia",
        "rfc": "JUAP800101XYZ"
    },
    {
        "nombre": "María López",
        "direccion": "Avenida Siempre Viva 742, Ciudad Ficticia",
        "rfc": "MALP800101XYZ"
    },
    {
        "nombre": "Carlos García",
        "direccion": "Boulevard de los Sueños Rotos 456, Ciudad Ficticia",
        "rfc": "CAG800101XYZ"
    },
    {
        "nombre": "Ana Torres",
        "direccion": "Plaza del Sol 789, Ciudad Ficticia",
        "rfc": "ANT800101XYZ"
    },
    {
        "nombre": "Luis Martínez",
        "direccion": "Calle del Río 321, Ciudad Ficticia",
        "rfc": "LUMA800101XYZ"
    }
]

def setup_db():

    logger.info("--- SETUP DE LA BASE DE DATOS VECTORIAL ---")

    logger.info("Creando directorio store...")
    if os.path.exists(STORE_DIR):
        logger.info("El directorio ya existe, se asume que la base de datos ya está configurada.")
        return
    
    os.makedirs(STORE_DIR, exist_ok=True)

    logger.info("Iniciando el cliente de ChromaDB...")
    client = PersistentClient(path=STORE_DIR)

    logger.info("Creando la colección 'productos'...")
    collection = client.create_collection(name="productos")

    logger.info("Creando la colección 'clientes'...")
    clientes_collection = client.create_collection(name="clientes")

    def embed(text):

        embedding = openai.embeddings.create(
            input=text, 
            model="text-embedding-3-small", 
            encoding_format="float"
        )
        return(embedding.data[0].embedding)

    logger.info("Agregando productos a la colección...")
    for producto in productos:
        logger.info(f"Agregando producto: {producto['nombre']}")
        try:
            
            collection.add(
                ids=[producto["id"]],
                documents=[producto["nombre"]],
                embeddings=[embed(producto["nombre"])],
                metadatas=[{
                    "precio": producto["precio"],
                    "nombre": producto["nombre"]
                }]
            )
        except Exception as e:
            logger.error(f"Error al agregar el producto {producto['nombre']}: {e}")

    logger.info("Agregando clientes a la colección...")
    for cliente in clientes:
        logger.info(f"Agregando cliente: {cliente['nombre']}")
        try:
            
            clientes_collection.add(
                ids=[cliente["rfc"]],
                documents=[cliente["nombre"]],
                embeddings=[embed(cliente["nombre"])],
                metadatas=[{
                    "direccion": cliente["direccion"],
                    "rfc": cliente["rfc"]
                }]
            )
        except Exception as e:
            logger.error(f"Error al agregar el cliente {cliente['nombre']}: {e}")

    logger.info("--- BASE DE DATOS VECTORIAL CONFIGURADA ---")