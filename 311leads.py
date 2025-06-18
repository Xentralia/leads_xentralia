###################################################
#              Generador de leads                 #
# V.3.0.0 //08 05 2025//                          #
# V.3.0.1 //12 05 2025//                          #
# V.3.1.1 //16 05 2025//                          #  
# V.3.1.5 //21 05 2025//                          #
# V.3.1.7 //23 05 2025//                          #
# V.3.2.7 //          //                          #
# V.3.3.8 //13 06 2025//                          #
# V.3.5.9 //16 06 2025//                          #
# Desplegado con streamlit y render               #
# Agente impulsado con OpenAI                     #
# Desarrollador: Sergio Emiliano López Bautista   #
###################################################


# ------------------------- Requerimentos y librerías -------------------------------
import io
import os
import time
import codecs
import streamlit as st
from dotenv import load_dotenv, find_dotenv
from openai import OpenAI
from utils.prompts import construir_prompt #Esto toma el archivo de prompts.py


# ------------------- Estructura de Cliente para almacenar datos ---------------------
class Cliente:
    def __init__(self, industria, postores, producto, zona):
        self.industria = industria
        self.postores = postores
        self.producto = producto
        self.zona = zona

# --------------------------- Seteadores ----------------------------------------------
st.set_page_config(page_title = "Generador de diccionario",
                   page_icon = "📝",
                   layout="wide")

dotenv_path = find_dotenv()
load_dotenv(dotenv_path, override=True)
client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))
#client = OpenAI(api_key = st.secrets["OPENAI_API_KEY"])
#comentario generico

st.title("📝 Generador de directorio de clientes potenciales")

# --------------------------- Funciones -----------------------------------------------
def agente(cliente):
    datos = vars(cliente) #Esta línea cambia la clase cliente a un diccionario
    try:
        agente = client.responses.create(
            model = "gpt-4.1",
            input = construir_prompt("data/promptD1.txt", datos)
        )
        return agente.output_text
    
    except Exception as e:
        st.error(f"Error al generar una respuesta: {str(e)}")
        return None

def maquina_de_escribir(respuesta):
    for word in respuesta.split(" "):
        yield word + " "
        time.sleep(0.02)

def instrucciones():
    with codecs.open("data/instrucciones.txt", "r", encoding="utf-8") as f:
        fi = f.read()
    file = fi.split('\n')
    for linea in file:
        st.markdown(linea)

# -------------------------------- Interfaz (MAIN)-----------------------------------------
p4 = None
cliente = Cliente(None, None, None, None)

st.markdown("## ¡Bienvenido!")
instrucciones()

with st.sidebar:
    st.header("Ayudame proporcionandome esta información:")

    st.markdown("¿En qué industria estás?")
    ind = st.radio(
        "Selecciona una opción",
        ["Manufactura", "Alimenticia", "Automotriz", "Textil", "Tecnológica", "Otra"],
        )
    if ind == "Otra":
        ind = st.text_input("¿En qué industria estás?")

    with st.form("form", border=False):
        #--------------------------------------------------------------
        pos = st.text_input("¿A quiénes les vendes?",
                            placeholder="Ej: Seguidores de instagram, Mayoristas, Samunsung")
        prod = st.text_input("¿Qué vendes?",
                             placeholder="Ej: Pan, reguladores, etiquetas, diseños")
        zona = st.text_input("¿En qué zona buscas clientes?", 
                            placeholder="Ej: CDMX, Valle de México, Peninsula de Yucatan")
        #--------------------------------------------------------------
        usuario = st.form_submit_button("Aceptar")


if usuario:
    if ind or pos or prod or zona:
        with st.spinner("Buscando clientes..."):
            cliente = Cliente(ind, pos, prod, zona)         #1
            p4 = agente(cliente)                            #2
            st.success("Clientes potenciales encontrados")  #3

            st.markdown("### Vista previa de la información")
            st.write_stream(maquina_de_escribir(p4))

    elif pos == None or prod == None or zona == None:
        st.warning("Por favor completa los campos requeridos")
                         
    if p4 != None:
        st.download_button(
            label = "Descargar información",
            data = str(p4),
            file_name = f"información_{cliente.industria}.txt",
            mime = "text/plain"
        )

