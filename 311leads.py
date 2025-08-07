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
import asyncio
from agents import Agent, Runner
from dotenv import load_dotenv, find_dotenv
from openai import OpenAI
from utils.prompts import construir_prompt #Esto toma el archivo de prompts.py

# --------------------------- Seteadores ----------------------------------------------
st.set_page_config(page_title = "X Leadflow V.4.0.0",
                   page_icon = "📝",
                   layout="wide")

dotenv_path = find_dotenv()
load_dotenv(dotenv_path, override=True)
client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))
denue_token = os.getenv("DENUE_TOKEN")

st.title("📝 Herramienta especializada en prospección de ventas a empresas, no a consumidores.")

# ------------------------------ Estructuras -----------------------------------------
class Cliente:
    def __init__(self, industria, postores, producto, zona, tamanio):
        self.industria = industria        
        self.postores = postores
        self.producto = producto
        self.zona = zona
        self.tamanio = tamanio

#agente_buscador = Agent(name="buscador",
                        #instructions="Tu tarea es delegar a otros agentes ")

# --------------------------- Funciones -----------------------------------------------
def buscar_denue(palabra, lat, lon, radio, token):
    url = f"https://www.inegi.org.mx/app/api/denue/v1/consulta/buscar/{palabra}/{lat},{lon}/{radio}/{token}"
    response = requests.get(url)
    print(url)
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)
        return df
    else:
        print(f"Error {response.status_code}: No se pudo consultar la API")
        return None

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
            #tools=[{"type": "web_search_preview"}],
            input = "Qué hora es en este momento en CDMX, Tokio, Beijing, Diblín, Seúl, Madrid y Londres?"
        )
        return agente.output_text
    except Exception as e:
        st.error(f"Error al generar una respuesta: {str(e)}")
        return None

    except Exception as e:
        st.error(f"Algo alió mal. {str(e)}")
        return None
    
def parsear_leads(respuesta):
    bloques = respuesta.strip().split("---")
    leads = []

    for bloque in bloques:
        lead = {}
        for linea in bloque.strip().split("\n"):
            if ":" in linea:
                clave, valor = linea.split(":", 1)
                lead[clave.strip()] = valor.strip()
        if lead:
            leads.append(lead)
    return leads

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
#prioridad = st.sidebar.pills("¿Qué datos son relevantes para ti?", ["Correos", "Telefonos", "Redes sociales"], selection_mode="multi")

tamanio = st.sidebar.pills("Tamaño del cliente", ["Pequeño", "Mediano", "Grande"], selection_mode="multi")

acuerdo = st.sidebar.checkbox("Confirmo que comprendo y acepto que los prospectos son generados automáticamente " \
                      "por Inteligencia Artificial (IA) mediante análisis de fuentes públicas.  " \
                      "La información debe ser verificada antes de ser utilizada, XentraliA no garantiza precisión ni disponibilidad de datos. " \
                      "Me comprometo a cumplir con leyes aplicables de protección de datos.")


if acuerdo:
    if st.sidebar.button("🔍 Buscar Prospectos"):
        if all([industria, postores, producto, zona, tamanio]):

            with st.spinner("Recopilando información..."):
                cliente = Cliente(industria, postores, producto, zona, tamanio)

                p4 = agente(cliente)
                st.success("Clientes encontrados")
                st.markdown(p4)

                leads = parsear_leads(p4)
                df = pd.DataFrame(leads)
                csv_completo=df.to_csv(index=False)

                #asyncio.run(root_agent(cliente)) 

                iz, der = st.columns([1,1], gap="small")
                with iz:
                    st.download_button(
                        label = "Info completa",
                        data = str(p4),
                        file_name = f"información_{cliente.industria}.txt",
                        mime = "text/plain"
                    )
                with der:
                    st.download_button(
                        label="Sólo leads en CSV",
                        data= csv_completo,
                        file_name="leads_CSV.csv",
                        mime="text/csv"
                    )
        else:
            st.sidebar.warning("Por favor completa todos los campos.")
