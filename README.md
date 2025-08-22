
# Invoice Generator Backend

Este proyecto es el backend para una web de generación de facturas mediante un agente de IA. Utiliza el OpenAI Agents SDK y function_tools para crear facturas en PDF y acceder a los datos de clientes y productos. El backend expone una API que interactúa con un frontend tipo chat, permitiendo la generación y descarga de facturas de manera sencilla y automatizada.

## Arquitectura

- **Frontend:** Interfaz de chat donde el usuario puede enviar mensajes de texto o voz. Los mensajes de voz se transcriben a texto antes de enviarse al agente.
- **Backend (este proyecto):** API en Flask que recibe los mensajes, los procesa con un agente IA (OpenAI Agents SDK), accede a la base de datos vectorial de clientes/productos, genera la factura en PDF y responde con un enlace de descarga.

## Características
- Generación automática de facturas en PDF usando IA.
- Transcripción de mensajes de voz a texto.
- Acceso inteligente a datos de clientes y productos mediante base de datos vectorial (ChromaDB).
- API REST con endpoints para chat, transcripción y descarga de facturas.
- Integración con OpenAI Agents SDK y function_tools.
- Manejo de logs y errores.
- Soporte para vistas asíncronas (async) en Flask.

## Requisitos
- Python 3.12+
- uv (gestor de dependencias)
- Flask (con extra async)
- OpenAI SDK
- chromadb
- python-dotenv
- fpdf
- qrcode

## Instalación
1. Clona el repositorio:
   ```bash
   git clone https://github.com/maldaurore/invoices-backend.git
   cd invoices-backend
   ```
2. Instala las dependencias:
   ```bash
   uv pip install -r requirements.txt
   ```
3. Crea un archivo `.env` y agrega tu clave de OpenAI:
   ```env
   OPENAI_API_KEY=tu_clave_aqui
   TRANSCRIBE_MODEL=whisper-1
   ```

## Uso
1. Inicia el servidor:
   ```bash
   uv run app.py
   ```
2. Endpoints principales:
   - `/send-message` (POST): Recibe mensajes del chat y genera facturas.
   - `/transcribe` (POST): Transcribe archivos de audio a texto.
   - `/download/<filename>` (GET): Descarga el PDF generado.
   - `/health` (GET): Verifica el estado de la API y la clave de OpenAI.

## Estructura del proyecto
```
app.py
requirements.txt
pyproject.toml
src/
  main_agent.py
  tools.py
  utils/
    paths.py
    setup_vector_db.py
output/
store/
```

## Pruebas
Ejecuta los tests con:
```bash
uv run test_db.py
```

## Notas
- Asegúrate de tener configurada tu clave de OpenAI en el archivo `.env`.
- Los archivos PDF generados se guardan en la carpeta `output/`.
- Los datos de productos y clientes se almacenan en una base de datos vectorial (ChromaDB).

## Licencia
MIT
