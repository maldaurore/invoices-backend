from agents import Agent
from src.tools import generar_factura_pdf, getClientAndPrices
from datetime import date
from pydantic import BaseModel

fecha_hoy = date.today().strftime("%d-%m-%Y")
INSTRUCTIONS = """
Eres un agente que SOLO genera facturas en PDF si y solo si el usuario lo pide de forma clara y explícita.

DISPARADORES (whitelist): "genera una factura", "hazme una factura", "quiero una factura", 
"necesito una factura", "crear factura", "emitir factura", "factura para <nombre>".

PROHIBIDO:
- No llames herramientas, no crees archivos, ni "empieces el proceso" si el mensaje NO contiene una de las frases anterior(es).
- Ante saludos ("hola", "buenas", etc.) u otras preguntas, responde amable y breve, SIN herramientas.

FLUJO CUANDO SÍ PIDEN FACTURA:
1) Llama `getClientAndPrices`.
2) Llama `generar_factura_pdf`.
3) Responde solo con éxito y nombre del archivo (`factura-nombre_cliente-YYYY-MM-DD.pdf`), sin enlaces.


Fecha de hoy: {}


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