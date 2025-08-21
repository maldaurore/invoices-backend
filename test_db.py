from chromadb import PersistentClient
from src.utils.paths import STORE_DIR

print("Iniciando el cliente de ChromaDB...")
client = PersistentClient(path=STORE_DIR)
print("Obteniendo la colección 'productos'...")
collection = client.get_collection(name="productos")
print("Obteniendo la colección 'clientes'...")
clientes_collection = client.get_collection(name="clientes")


def embed(text):
    
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer('all-MiniLM-L6-v2')
    return model.encode(text).tolist()

query_producto = "laptop inspiron 15"
print("Realizando la consulta de productos...")
result = collection.query(
    query_embeddings=[embed(query_producto)],
    n_results=1
)

print(result['metadatas'][0][0])

query_cliente = "cliente juan pérez"
print("Realizando la consulta de clientes...")
result_cliente = clientes_collection.query(
    query_embeddings=[embed(query_cliente)],
    n_results=1
)

print(result_cliente['documents'][0][0])
print(result_cliente['metadatas'][0][0])
