import json
from fpdf import FPDF
import qrcode
from datetime import datetime
import uuid
import os
from agents import function_tool
from pydantic import BaseModel
from src.utils.paths import OUTPUT_DIR, PROJECT_ROOT, STORE_DIR
from chromadb import PersistentClient
import logging
import unicodedata
import re
from openai import OpenAI

logger = logging.getLogger(__name__)

UMBRAL_SIMILITUD = 0.5

client = PersistentClient(path=STORE_DIR)
productos_collection = client.get_collection(name="productos")
clientes_collection = client.get_collection(name="clientes")
openai = OpenAI()

class Emisor(BaseModel):
    nombre: str
    rfc: str
    direccion: str
    
class Receptor(BaseModel):
    nombre: str
    rfc: str
    direccion: str
    
class Concepto(BaseModel):
    descripcion: str
    cantidad: int
    precio_unitario: float
    
class Precio(BaseModel):
    descripcion: str
    precio: float

EMISOR = Emisor (
    nombre='Empresa Ficticia S.A. de C.V.',
    rfc='AAA010101AAA',
    direccion='Calle Falsa 123, CDMX',
) 

class FacturaPDF(FPDF):
    def header(self):
        # Logo
        logo_path = os.path.join(PROJECT_ROOT, "src", 'logo.jpg')
        self.image(logo_path, 10, 8, 33) 
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Factura CFDI 4.0 (Simulada)', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')   

def embed(text):

    embedding = openai.embeddings.create(
        input=text, 
        model="text-embedding-3-small", 
        encoding_format="float"
    )
    return(embedding.data[0].embedding)

def normalize_filename(filename):
    nfkd = unicodedata.normalize('NFKD', filename)
    only_ascii = nfkd.encode('ASCII', 'ignore').decode('ASCII')
    safe = re.sub(r'[^\w\.-]', '_', only_ascii)
    return safe

@function_tool
def generar_factura_pdf(receptor: Receptor, conceptos: list[Concepto], output_file: str = "factura.pdf"):
    """Genera una factura en PDF con los datos del receptor y los conceptos proporcionados."""

    logger.info("Generando factura PDF...")
    logger.info(f"Receptor: {receptor}")
    logger.info(f"Conceptos: {conceptos}")

    try:
        pdf = FacturaPDF()
        pdf.add_page()
        pdf.ln(20)
        pdf.set_font("Arial", size=10)

        # Folio
        folio = str(uuid.uuid4())
        fecha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Encabezado
        pdf.cell(0, 10, f'Folio Fiscal (UUID): {folio}', ln=True)
        pdf.cell(0, 10, f'Fecha de emisión: {fecha}', ln=True)
        pdf.ln(5)

        # Datos emisor y receptor
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(95, 10, 'EMISOR:', ln=0)
        pdf.cell(95, 10, 'RECEPTOR:', ln=1)
        pdf.set_font("Arial", size=10)
        pdf.cell(95, 10, f"Nombre: {EMISOR.nombre}", ln=0)
        pdf.cell(95, 10, f"Nombre: {receptor.nombre}", ln=1)

        pdf.cell(95, 10, f"RFC: {EMISOR.rfc}", ln=0)
        pdf.cell(95, 10, f"RFC: {receptor.rfc}", ln=1)

        pdf.cell(95, 10, f"Dirección: {EMISOR.direccion}", ln=0)
        pdf.cell(95, 10, f"Dirección: {receptor.direccion}", ln=1)

        pdf.ln(5)

        # Tabla de conceptos
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(80, 10, 'Descripción', 1)
        pdf.cell(30, 10, 'Cantidad', 1)
        pdf.cell(40, 10, 'Precio Unitario', 1)
        pdf.cell(40, 10, 'Importe', 1, ln=1)

        pdf.set_font("Arial", size=10)
        subtotal = 0
        for c in conceptos:
            importe = c.cantidad * c.precio_unitario
            subtotal += importe
            pdf.cell(80, 10, c.descripcion, 1)
            pdf.cell(30, 10, str(c.cantidad), 1)
            pdf.cell(40, 10, f"${c.precio_unitario:.2f}", 1)
            pdf.cell(40, 10, f"${importe:.2f}", 1, ln=1)

        iva = subtotal * 0.16
        total = subtotal + iva

        # Totales
        pdf.ln(5)
        pdf.cell(150, 10, 'Subtotal:', 0, 0, 'R')
        pdf.cell(40, 10, f"${subtotal:.2f}", 0, ln=1)
        pdf.cell(150, 10, 'IVA (16%):', 0, 0, 'R')
        pdf.cell(40, 10, f"${iva:.2f}", 0, ln=1)
        pdf.cell(150, 10, 'Total:', 0, 0, 'R')
        pdf.cell(40, 10, f"${total:.2f}", 0, ln=1)

        # QR simulado
        qr_data = f"UUID:{folio}\nRFC:{EMISOR.rfc}\nTotal:{total:.2f}"
        qr = qrcode.make(qr_data)
        qr_file = "temp_qr.png"
        qr.save(qr_file)
        pdf.image(qr_file, x=10, y=pdf.get_y()+10, w=40)
        os.remove(qr_file)

        # Leyenda
        pdf.set_y(pdf.get_y() + 50)
        pdf.set_font("Arial", 'I', 8)
        pdf.multi_cell(0, 10, "Este documento es una representación impresa de un CFDI simulado. No tiene validez fiscal.")

        normalized_filename = normalize_filename(output_file)
        logger.info(f"Nombre de archivo normalizado: {normalized_filename}")
        file_path = os.path.join(OUTPUT_DIR, normalized_filename)
        pdf.output(file_path)
        logger.info(f"Factura generada: {file_path}")
        return f"Factura generada: {file_path}"

    except Exception as e:
        logger.error(f"Error al generar la factura: {e}")
        return f"Error al generar la factura: {e}"

def getClientData(nombreCliente: str) -> Receptor:
    logger.debug(f"Obteniendo datos del cliente '{nombreCliente}'")

    result = clientes_collection.query(
        query_embeddings=[embed(nombreCliente)],
        n_results=1
    )
    
    if result['distances'][0][0] >= UMBRAL_SIMILITUD:
        logger.error(f"No se encontró un cliente similar a '{nombreCliente}'")
        raise Exception("Cliente no encontrado")

    nombreClienteEncontrado = result['documents'][0][0]
    clienteInfo = result['metadatas'][0][0]

    logger.debug(f"Cliente encontrado en la base de datos vectorial: {nombreClienteEncontrado} con info {clienteInfo}")

    return Receptor(
        nombre=nombreClienteEncontrado,
        rfc=clienteInfo["rfc"],
        direccion=clienteInfo["direccion"]
    )

def getProductsPrices(conceptos: list[str]) -> list[Precio]:
    logger.debug(f"Obteniendo precios de conceptos: {conceptos}")

    result = productos_collection.query(
        query_embeddings=[embed(c) for c in conceptos],
        n_results=1
    )

    conceptosEncontrados = [
        {
            "descripcion": result['documents'][i][0],
            "precio": result['metadatas'][i][0]["precio"]
        }
        for i in range(len(result['documents']))
    ]
    
    if (len(conceptosEncontrados) < len(conceptos)):
        logger.error(f"No se encontraron todos los conceptos. Conceptos solicitados: {conceptos}, Conceptos encontrados: {conceptosEncontrados}")
        raise Exception("No se encontraron todos los conceptos solicitados")

    logger.debug(f"Conceptos encontrados en la base de datos vectorial: {conceptosEncontrados}")
    return conceptosEncontrados

@function_tool
def getClientAndPrices(nombreCliente: str, productos: list[str]) -> tuple[Receptor, list[Precio]]:
    """Obtiene los datos del cliente y los precios de los productos."""
    logger.debug("Obteniendo datos del cliente...")
    receptor = getClientData(nombreCliente)
    logger.debug("Obteniendo precios de productos...")
    precios = getProductsPrices(productos)
    
    return receptor, precios