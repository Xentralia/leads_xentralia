# # # # # # # # # # # # # # # # # # # # # # # # # #
#              Generador de leads                 #
# V.3.0.0 //08 05 2025//                          #
# V.3.0.1 //12 05 2025//                          #
# V.3.1.1 //16 05 2025//                          #  
# V.3.1.5 //21 05 2025//                          #
# V.3.1.7 //23 05 2025//                          #
# V.3.2.7 //          //                          #
# V.3.3.8 //13 06 2025//                          #
# V.3.5.9 //16 06 2025//                          #
# V.3.5.10 //20 06 2025//                         #
# V.3.12.16 //02 07 2025//                        #
# V.3.14.16 //10 07 2025//                        #
# V.3.16.17 //16 07 2025//                        #
# Desplegado con streamlit y render               #
# Agente impulsado con OpenAI                     #
# Desarrollador: Sergio Emiliano López Bautista   #
# # # # # # # # # # # # # # # # # # # # # # # # # #


# ------------------------- Requerimentos y librerías -------------------------------
import io
import os
import csv
import time
import codecs
import requests
import streamlit as st
import pandas as pd
import re
from bs4 import BeautifulSoup
from dotenv import load_dotenv, find_dotenv
from openai import OpenAI
from utils.prompts import construir_prompt #Esto toma el archivo de prompts.py
from serpapi import GoogleSearch

# --------------------------- Seteadores ----------------------------------------------
st.set_page_config(page_title = "X Leadflow V.3.16.18",
                   page_icon = "📝",
                   layout="wide")

dotenv_path = find_dotenv()
load_dotenv(dotenv_path, override=True)
client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))
explorador = os.getenv("SERPAPI_API_KEY")

st.title("📝 Herramienta especializada en prospección de ventas a empresas, no a consumidores.")

# ------------------------------ Estructuras -----------------------------------------
class Cliente:
    def __init__(self, industria, postores, producto, zona, prioridad):
        self.industria = industria
        self.postores = postores
        self.producto = producto
        self.zona = zona
        self.prioridad = prioridad

# --------------------------- Funciones -----------------------------------------------
def instrucciones():
    with codecs.open("data/instrucciones2.txt", "r", encoding="utf-8") as f:
        fi = f.read()
    file = fi.split('\n')
    for linea in file:
        st.markdown(linea)

def agente(cliente):
    datos = vars(cliente)
    try:
        agente = client.responses.create(
            model = "gpt-4.1",
            input = construir_prompt("data/promptD5.txt", datos)
        )
        return agente.output_text
    except Exception as e:
        st.error(f"Error al generar una respuesta: {str(e)}")
        return None

def buscador(query, paginas=10):
    organicos=[]
    try:
        for i in range(paginas):
            params = {
                "engine": "google",
                "q": query,
                "start": i*10,
                "hl": "es",
                "google_domain": "google.com.mx",
                "api_key": explorador
            }
            search = GoogleSearch(params)
            results = search.get_dict()
            organicos += results.get("organic_results", [])
            time.sleep(1)
        return organicos
    
    except Exception as e:
        st.error(f"No se pudo completar la busqueda: {str(e)}")
        return None

def enriquecer(link):
    try:
        if any(host in link for host in ["mercadolibre", "amazon", "youtube", "facebook"]):
            return "Nombre: -\nTeléfono: -\nCorreo: -\nContacto: -"

        response = requests.get(link, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        texto = soup.get_text()[:3000]

        correos = re.findall(r"[\w\.-]+@[\w\.-]+\\.\w+", texto)
        telefonos = re.findall(r"\+?\d[\d\s\-]{7,}\d", texto)
        
        textoD = {
            "contenido": texto,
            "emails": correos,
            "telefonos": telefonos
        }

        completador = client.responses.create(
            model = "gpt-4.1",
            input = construir_prompt("data/promptD3.txt", textoD)
        )
        return completador.output_text

    except Exception as e:
        return f"Nombre: -\nTeléfono: -\nCorreo: -\nContacto: -"

def parsear(respuesta):
    datos = {"Nombre": "", "Teléfono": "", "Correo": "", "Contacto": ""}
    for linea in respuesta.split("\n"):
        if ":" in linea:
            clave, valor = linea.split(":", 1)
            if clave.strip() in datos:
                datos[clave.strip()] = valor.strip()
    return datos

def tabla(leads):
    tab = []
    progreso = st.progress(0)

    for i, r in enumerate(leads):
        link = r.get("link", "")
        rico = enriquecer(link)
        datos = parsear(rico)
        datos["Enlace"] = link
        tab.append(datos)
        progreso.progress((i + 1) / len(leads))

    return pd.DataFrame(tab)

# -------------------------------- Interfaz (MAIN)-----------------------------------------
st.markdown("## ¡Bienvenido!")
instrucciones()

st.sidebar.markdown("# Encontremos a tus clientes ideales")
st.sidebar.header("Completa estos datos clave:")

industria = st.sidebar.selectbox("Industria principal:", 
                                ["Agroindustria", "Alimentos", "Arquitectura", "Artes/Cultural", "Automotriz",
                                 "Bebidas", "Bienes Raíces",
                                 "Ciberseguridad", "Construcción", "Consultoría", "Contabilidad",
                                 "Diseño", "Dispositivos Médicos",
                                 "e-commerce", "e-learning", "Educación", "Energía", "Entretenimiento",
                                 "Farmacéutica", "Finanzas", "Fintech", "Fitness/Wellness",
                                 "Gobierno",
                                 "Hardware Tecnológico", "Hospitales/Clínicas", "Hotelería",
                                 "Industrial", "Inteligencia Artificial",
                                 "Legal", "Logística",
                                 "Manufactura", "Medios", "Moda",
                                 "Nutrición",
                                 "ONGs/Social", "Organismos Gubernamentales",
                                 "Plásticos", "Publicidad/Marketing",
                                 "Química",
                                 "Recursos Humanos", "Retail/Comercio",
                                 "Salud", "Seguros", "Software", "Suplementos",
                                 "Tecnología", "Telecomunicaciones", "Textil", "Transporte", "Turismo",
                                 "Videojuegos", "Otra"],
                                index=None,
                                placeholder="¿En qué sector operas?")
if industria == "Otra":
    industria = st.sidebar.text_input("Especifica:")

postores = st.sidebar.text_input("Clientes ideales:", 
                                 placeholder="¿Qué empresas o perfiles buscas?")
producto = st.sidebar.text_input("Tu producto/servicio", 
                                 placeholder="¿Qué ofreces específicamente?")
zona = st.sidebar.text_input("Zona de cobertura", 
                             placeholder="Estados, regiones, ciudades")
prioridad = st.sidebar.text_input("¿Qué datos son más relevantes para ti?", 
                                  placeholder="Correos, teléfonos, redes sociales")

acuerdo = st.sidebar.checkbox("Confirmo que comprendo y acepto que los prospectos son generados automáticamente " \
                      "por Inteligencia Artificial (IA) mediante análisis de fuentes públicas.  " \
                      "La información debe ser verificada antes de ser utilizada, XentraliA no garantiza precisión ni disponibilidad de datos. " \
                      "Me comprometo a cumplir con leyes aplicables de protección de datos.")


if acuerdo:
    if st.sidebar.button("🔍 Buscar Prospectos"):
        if all([industria, postores, producto, zona]):

            with st.spinner("Recopilando información..."):
                cliente = Cliente(industria, postores, producto, zona, prioridad)

                p4 = agente(cliente)
                st.success("Clientes encontrados")
                st.markdown(p4)

                st.download_button(
                    label = "Descargar txt",
                    data = str(p4),
                    file_name = f"información_{cliente.industria}.txt",
                    mime = "text/plain"
                )
        else:
            st.sidebar.warning("Por favor completa todos los campos.")
