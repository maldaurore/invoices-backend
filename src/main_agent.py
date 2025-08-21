from agents import Agent
from src.tools import generar_factura_pdf, getClientAndPrices
from datetime import date
from pydantic import BaseModel

fecha_hoy = date.today().strftime("%d-%m-%Y")
INSTRUCTIONS = """
Eres un agente que genera facturas en PDF.
Tu tarea es generar una factura en PDF.

Los datos del receptor, así como los conceptos de la factura, serán proporcionados por el usuario.
Utiliza la herramienta `getClientAndPrices` para obtener los datos del cliente y los precios de los productos
Utiliza la herramienta `generar_factura_pdf` para crear la factura en PDF. 
El nombre del archivo deberá tener el siguiente formato: factura-nombre-cliente-fecha.pdf.
Usa guiones bajos en lugar de espacios para el nombre del archivo.
La fecha de hoy es: {}.
Asegúrate de incluir todos los detalles necesarios, como receptor, conceptos y totales.
No te preocupes por el emisor, ya que es un dato fijo y no se requiere que lo proporciones.
""".format(fecha_hoy)

class Response(BaseModel):
    texto: str
    archivo_generado: bool
    nombre_archivo: str | None

mainAgent = Agent(
    name="Generador de Facturas PDF",
    instructions=INSTRUCTIONS,
    model="gpt-4o-mini",
    tools=[generar_factura_pdf, getClientAndPrices],
    output_type=Response
)