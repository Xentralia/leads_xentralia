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
from bs4 import BeautifulSoup
from dotenv import load_dotenv, find_dotenv
from openai import OpenAI
from utils.prompts import construir_prompt #Esto toma el archivo de prompts.py
from serpapi import GoogleSearch


# --------------------------- Seteadores ----------------------------------------------
st.set_page_config(page_title = "X Leadflow V.3.5.10",
                   page_icon = "📝",
                   layout="wide")

dotenv_path = find_dotenv()
load_dotenv(dotenv_path, override=True)
client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))
explorador = os.getenv("SERPAPI_API_KEY")
#client = OpenAI(api_key = st.secrets["OPENAI_API_KEY"])
#comentario generico

st.title("📝 Generador de directorio de clientes potenciales")

# ------------------------------ Estructuras ----------------------------------------
class Cliente:
    def __init__(self, industria, postores, producto, zona):
        self.industria = industria
        self.postores = postores
        self.producto = producto
        self.zona = zona

# --------------------------- Funciones -----------------------------------------------
def agente(cliente):
    datos = vars(cliente) #Esta línea cambia la clase cliente a un diccionario
    try:
        agente = client.responses.create(
            model = "gpt-4.1",
            input = construir_prompt("data/promptD2.txt", datos)
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
                "start": i*10, #Esto usa más páginas en el buscador
                "hl": "es",
                "google_domain": "google.com.mx",
                "api_key": explorador
            }
            search = GoogleSearch(params)
            results = search.get_dict()
            organicos += results.get("organic_results", [])
            time.sleep(1) #Esto evita que se trabe, aunque no estoy seguro por qué
        return organicos
    
    except Exception as e:
        st.error(f"No se pudo completar la busqueda: {str(e)}")
        return None
    
def escritor(csv):
    try:
        escribano = client.responses.create(
            model="gpt-4.1",
            input=f"Toma los datos de {csv} y dame solamente un dataframe listo para poder usarlo"
        )

        st.write_stream(maquina_de_escribir(escribano.output_text))

    except Exception as e:
        st.error('No se logró desplegar la vista previa de la información')

def maquina_de_escribir(respuesta):
    for word in respuesta.split(" "):
        yield word + " "
        time.sleep(0.01)

def csv_maker(p4):
    print("xd")
    salida = io.StringIO()
    writer = csv.writer(salida)
    writer.writerow(["Rating", "Sitio web", "link", "sitelinks"])

    for campo in p4:
        writer.writerow([
            campo.get("position", ""),
            campo.get("link", ""),
            campo.get("displayed_link", ""),
            campo.get("sitelinks", ""),
        ])
    return salida.getvalue()
    
def instrucciones():
    with codecs.open("data/instrucciones.txt", "r", encoding="utf-8") as f:
        fi = f.read()
    file = fi.split('\n')
    for linea in file:
        st.markdown(linea)

def enriquecer(link):
    try:
        response = requests.get(link, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        texto = soup.get_text()[:3000]

        prompt = f"""
        Este es el contenido parcial de la página web de una empresa:

        {texto}

        Extrae, si es posible:
        - Nombre del negocio
        - Número de teléfono
        - Correo electrónico de contacto
        - Nombre de persona de contacto (si está disponible)

        Devuelve la información como:
        Nombre: ...
        Teléfono: ...
        Correo: ...
        Contacto: ...
        """

        completador = client.responses.create(
            model = "gpt-4.1",
            input = prompt
        )
        return completador.output_text
    
    except Exception as e:
        return f"Error: {e}"
    
def parsear(respuesta): #gpt a diccionario
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

st.sidebar.header("Ayudame proporcionandome esta información:")

#---------------------------------------------------------------------------
industria = st.sidebar.selectbox("Industria:", ["Manufactura", "Alimenticia", "Automotriz", "Textil", "Tecnológica", "Otra"])
if industria == "Otra":
    industria = st.sidebar.text_input("Especifique la industria:")
#---------------------------------------------------------------------------   
postores = st.sidebar.text_input("¿A quiénes les vendes?")
producto = st.sidebar.text_input("¿Qué vendes?")
zona = st.sidebar.text_input("¿En qué zona buscas clientes?")
#---------------------------------------------------------------------------

if st.sidebar.button("Buscar clientes"):
    if all([industria, postores, producto, zona]):
        with st.spinner("Buscando leads..."):
            cliente = Cliente(industria, postores, producto, zona)
            query = agente(cliente)
            if query:
                leads = buscador(query)
                #st.markdown(leads)
                df = tabla(leads)
                st.success("Clientes potenciales encontrados")
                st.dataframe(df)

                st.download_button(
                    label="Descargar CSV",
                    data=df.to_csv(index=False),
                    file_name="leads_enriquecidos.csv",
                    mime="text/csv"
                )
    else:
        st.warning("Por favor completa todos los campos.")
