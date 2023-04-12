import streamlit as st
import openai
import fitz  # PyMuPDF
import io
import requests
from typing import List
import os
import textwrap

# Configura tu clave de API de OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

def leer_pdf(archivo_pdf) -> str:
    lector_pdf = fitz.open(stream=archivo_pdf, filetype="pdf")
    texto = ""
    for num_pagina in range(lector_pdf.page_count):
        pagina = lector_pdf.load_page(num_pagina)
        texto += pagina.get_text("text")
    return texto

def dividir_texto_en_fragmentos(texto: str, palabras_por_fragmento: int) -> List[str]:
    palabras = texto.split()
    fragmentos = textwrap.wrap(" ".join(palabras), width=palabras_por_fragmento)
    return fragmentos

def resumir_texto(texto: str, palabras_maximas: int) -> str:
    tokens_maximos = palabras_maximas * 1.5  # Estimación para considerar espacios y puntuación
    respuesta = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"Resumen del siguiente texto en aproximadamente {palabras_maximas} palabras:\n\n{texto}\n",
        max_tokens=int(tokens_maximos),
        n=1,
        stop=None,
        temperature=0.7,
    )
    resumen = respuesta.choices[0].text.strip()
    return resumen

st.title("Resumidor de archivos PDF con IA")
archivo_subido = st.file_uploader("Sube un archivo PDF para resumir", type=["pdf"])
palabras_maximas = st.number_input("Introduce la cantidad de palabras en las que deseas que se resuma el texto", min_value=1, value=100)

if archivo_subido:
    with st.spinner("Resumiendo el archivo PDF..."):
        archivo_pdf = io.BytesIO(archivo_subido.read())
        texto = leer_pdf(archivo_pdf)

        # Divide el texto en fragmentos
        palabras_por_fragmento = 500
        fragmentos = dividir_texto_en_fragmentos(texto, palabras_por_fragmento)

        # Resumir cada fragmento y combinar los resultados
        resumen = ""
        for fragmento in fragmentos:
            resumen_fragmento = resumir_texto(fragmento, palabras_maximas)
            resumen += resumen_fragmento + "\n\n"

    st.write("Resumen del archivo PDF:")
    st.write(resumen)
