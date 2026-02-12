import streamlit as st
import time
from groq import Groq
from gtts import gTTS
import base64
import io
import json
import re
import requests

# --- CONFIGURAÇÃO DA INTERFACE ---
st.set_page_config(page_title="SmartProf", layout="wide")

# URL da imagem do robô (Professor)
IMAGE_URL = "https://thumbs.dreamstime.com/b/professor-de-rob%C3%B4-moderno-na-faculdade-gradua%C3%A7%C3%A3o-que-mant%C3%A9m-o-conceito-intelig%C3%AAncia-artificial-para-laptops-online-robot-pac-218181889.jpg?w=576"

def get_base64_img(url):
    try:
        response = requests.get(url)
        return base64.b64encode(response.content).decode()
    except:
        return ""

img_data = get_base64_img(IMAGE_URL)

# --- CSS REFINADO (FOCO NA VISIBILIDADE DOS BOTÕES) ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');

    /* Fundo com o Robô */
    [data-testid="stAppViewContainer"] {{
        background-image: url("data:image/png;base64,{img_data}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}

    /* Esconder elementos nativos */
    [data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stSidebarNav"] {{
        display: none !important;
    }}

    /* CAMPO DE NOME: Altura máxima para evitar cortes */
    .stTextInput > div > div > input {{
        background-color: rgba(255, 255, 255, 0.95) !important;
        border: 4px solid #1A237E !important;
        border-radius: 20px !important;
        height: 120px !important; 
        font-size: 20px !important;
        text-align: center !important;
        color: #1A237E !important;
        font-weight: 600 !important;
    }}

    .stTextInput {{
        margin-top: 25vh !important;
        padding: 0 10% !important;
    }}

    /* CONTAINER PARA BOTÕES (Simulando Tabela) */
    .button-row {{
        display: flex !important;
        flex-direction: row !important;
        justify-content: center !important;
        gap: 15px !important;
        width: 100% !important;
        margin-top: 30px !important;
        padding-bottom: 100px; /* Garante que não suma no celular */
    }}

    /* Estilo dos Botões do Streamlit */
    .stButton > button {{
        width: 118px !important; /* Tamanho fixo para ambos */
        height: 50px !important;
        background-color: white !important;
        border: 3px solid #1A237E !important;
        border-radius: 15px !important;
        font-size: 16px !important;
        font-weight: 700 !important;
        color: #1A237E !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    }}

    .stButton > button:hover {{
        background-color: #1A237E !important;
        color: white !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- ESTADO ---
if 'ecra' not in st.session_state: st.session_state.ecra = 1
if 'nome' not in st.session_state: st.session_state.nome = ""

# --- ECRÃ 1: IDENTIFICAÇÃO ---
if st.session_state.ecra == 1:
    # Campo de Nome
    nome_input = st.text_input("", value=st.session_state.nome, placeholder="Escreve o teu nome aqui", label_visibility="collapsed")

    # Criando a "Tabela" com st.columns mas sem fixar no fundo (para não sumir)
    st.markdown('<div class="button-row">', unsafe_allow_html=True)
    c1, c2 = st.columns([1, 1])
    
    with c1:
        if st.button("↑ SUBMETER"):
            if nome_input:
                st.session_state.nome = nome_input
                st.session_state.ecra = 2
                st.rerun()

    with c2:
        if st.button("🗑 LIMPAR"):
            st.session_state.nome = ""
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- ECRÃ 2: INTERAÇÃO ---
elif st.session_state.ecra == 2:
    st.markdown('<style>[data-testid="stAppViewContainer"] { background-image: none !important; background-color: white; }</style>', unsafe_allow_html=True)
    st.title(f"Olá, {st.session_state.nome}!")
    if st.button("🏠 VOLTAR"):
        st.session_state.ecra = 1
        st.rerun()


