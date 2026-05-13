import PyPDF2
from docx import Document

from google import genai
from google.genai.types import Content
from django.conf import settings

# Crear cliente Gemini con tu API key
client = genai.Client(api_key=settings.GEMINI_API_KEY)


def extraer_texto(archivo):
    extension = archivo.name.split(".")[-1].lower()

    if extension == "pdf":
        return leer_pdf(archivo)

    elif extension == "docx":
        return leer_docx(archivo)

    else:
        return ""
    

def leer_pdf(archivo):
    texto = ""
    reader = PyPDF2.PdfReader(archivo)
    for page in reader.pages:
        texto += page.extract_text() + "\n"
    return texto


def leer_docx(archivo):
    texto = ""
    doc = Document(archivo)
    for p in doc.paragraphs:
        texto += p.text + "\n"
    return texto


def generar_sinopsis(texto):
    if not texto.strip():
        return "No se pudo generar sinopsis. El archivo está vacío."

    prompt = (
        "Elabora una sinopsis breve, objetiva y de estilo académico sobre el siguiente contenido. "
        "Limítate a 3–5 líneas y destaca únicamente el propósito, metodología y conclusión general del texto:\n\n"
        f"{texto}"
    )

    # Llamada correcta al modelo Gemini más rápido que tienes
    response = client.models.generate_content(
        model="models/gemini-2.5-flash",
        contents=Content(parts=[{"text": prompt}])
    )

    return response.text.strip()
