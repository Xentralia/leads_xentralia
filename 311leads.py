###################################################
#              Generador de leads                 #
# V.3.0.0 //08 05 2025//                          #
# V.3.0.1 //12 05 2025//                          #
# V.3.1.1 //16 05 2025//                          #  
# V.3.1.5 //21 05 2025//                          #
# V.3.1.7 //23 05 2025//                          #
# V.3.2.7 //          //                          #
# Desplegado con streamlit                        #
# Agentes impulsados con OpenAI                   #
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


# ------------------- Estructura de Cliente para almacenar datos ---------------------
class Cliente:
    def __init__(self, industria, postores, producto, zona):
        self.industria = industria
        self.postores = postores
        self.producto = producto
        self.zona = zona

# --------------------------- Seteadores ----------------------------------------------
st.set_page_config(page_title="Generador de diccionario", layout="wide")

dotenv_path = find_dotenv()
load_dotenv(dotenv_path, override=True)
client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))
#client = OpenAI(api_key = st.secrets["OPENAI_API_KEY"])
#comentario generico

st.title("Generador de directorio de clientes potenciales")
iz, der = st.columns(2, border=True)

# --------------------------- Funciones -----------------------------------------------
def agente1(cliente):
    try:
        agente1 = client.responses.create(
        model = "gpt-4.1",
        input = f"Dame únicamente el prompt necesario para poder buscar información de clientes potenciales en {cliente.industria} que sean similares a {cliente.postores} y tengan como producto {cliente.producto} en {cliente.zona}."
        )
        return agente1.output_text
    
    except Exception as e:
        st.error(f"Error al generar una respuesta: {str(e)}")
        return None

def agente2(prompt):
    try:
        agente2 = client.responses.create(
        model= "gpt-4.1",
        input= prompt
        )
        return agente2.output_text

    except Exception as e:
        st.error(f"Prompt de busqueda inválido: {str(e)}")
        return None

def agente3(respuesta2):
    try:
        agente3 = client.responses.create(
        model= "gpt-4.1",
        input= f"Si la información de {respuesta2} no es suficientemente en cantidad o detalle, optimizala para encontrar leads, segmetarlos y entregame solamente el prompt neceario para generar leads basado en esa información"
        )
        return agente3.output_text

    except Exception as e:
        st.error(f"xdxdxd: {str(e)}")
        return None

def agente4(prompt2):
    try:
        agente4 = client.responses.create(
        model= "gpt-4.1",
        input = f"Dame solamente los leads, con un formato de directorio, donde me digas los correos o numeros de contacto de cada lead, además de una descrpción muy breve de quienes son, basado en {prompt2} y no hagas preguntas finales, ni sugerencias. Además dame datos completamente verídicos y nada genérico"
        )
        return agente4.output_text
    
    except Exception as e:
        st.error(f"Error al encontrar los clientes: {str(e)}")
        return None

def maquina_de_escribir(respuesta):
    for word in respuesta.split(" "):
        yield word + " "
        time.sleep(0.02)

def instrucciones():
    with codecs.open("instrucciones.txt", "r", encoding="utf-8") as f:
        fi = f.read()
    file = fi.split('\n')
    for linea in file:
        der.markdown(linea)


# -------------------------------- Interfaz (MAIN)-----------------------------------------
p4 = None
cliente = Cliente(None, None, None, None)

der.markdown("## ¡Bienvenido!")
instrucciones()

iz.header("Ayudame proporcionandome esta información:")

with st.spinner("Buscando clientes..."):

    iz.markdown("¿En qué industria estás?")
    ind = iz.radio(
        "Selecciona una opción",
        ["Manufactura", "Alimenticia", "Automotriz", "Textil", "Tecnológica", "Otra"],
        )
    if ind == "Otra":
        ind = iz.text_input("¿En qué industria estás?")
            
    with iz.form("form", border=False):
        
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
                cliente = Cliente(ind, pos, prod, zona)         #1
                p1 = agente1(cliente)                           #2
                p2 = agente2(p1)                                #
                p3 = agente3(p2)                                #
                p4 = agente4(p3)                                #
                der.success("Clientes potenciales encontrados") #3

                der.markdown("### Vista previa de la información")
                der.write_stream(maquina_de_escribir(p4))

            elif pos == None or prod == None or zona == None:
                der.warning("Por favor completa los campos requeridos")
                         
    if p4 != None:
        der.download_button(
            label = "Descargar información",
            data = str(p4),
            file_name = f"información_{cliente.industria}.txt",
            mime = "text/plain"
        )
