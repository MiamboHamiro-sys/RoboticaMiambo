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

IMAGE_URL = "https://thumbs.dreamstime.com/b/professor-de-rob%C3%B4-moderno-na-faculdade-gradua%C3%A7%C3%A3o-que-mant%C3%A9m-o-conceito-intelig%C3%AAncia-artificial-para-laptops-online-robot-pac-218181889.jpg?w=576"

def get_base64_img(url):
    try:
        response = requests.get(url)
        return base64.b64encode(response.content).decode()
    except: return ""

img_data = get_base64_img(IMAGE_URL)

# --- CSS AVANÇADO PARA CENTRALIZAÇÃO E TABELA DE BOTÕES ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');

    /* Fundo Estável */
    [data-testid="stAppViewContainer"] {{
        background-image: url("data:image/png;base64,{img_data}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}

    [data-testid="stHeader"] {{ display: none !important; }}

    /* CAIXA DE TEXTO REFORMULADA (Evita cortes) */
    .stTextInput > div > div > input {{
        background-color: rgba(255, 255, 255, 0.95) !important;
        border: 4px solid #1A237E !important;
        border-radius: 20px !important;
        height: 110px !important; /* Altura generosa para não cortar */
        font-size: 28px !important;
        text-align: center !important; /* Centralizado Horizontalmente */
        color: #1A237E !important;
        padding: 20px !important;
        display: flex;
        align-items: center; /* Centralizado Verticalmente */
    }}

    /* Container do Nome */
    .name-box {{
        margin-top: 25vh;
        padding: 0 10%;
    }}

    /* TABELA DE BOTÕES (LADO A LADO SEMPRE) */
    .button-table {{
        display: flex;
        flex-direction: row;
        justify-content: center;
        gap: 15px;
        margin-top: 30px;
        padding: 0 10%;
    }}

    /* Estilo dos Botões Injetados */
    .custom-btn {{
        flex: 1;
        height: 70px;
        background-color: white;
        border: 4px solid #1A237E;
        border-radius: 15px;
        color: #1A237E;
        font-family: 'Poppins', sans-serif;
        font-weight: bold;
        font-size: 18px;
        cursor: pointer;
        box-shadow: 0 6px 12px rgba(0,0,0,0.2);
    }}
    
    .custom-btn:active {{ transform: scale(0.95); background-color: #1A237E; color: white; }}
    </style>
    """, unsafe_allow_html=True)

# --- ESTADO ---
if 'ecra' not in st.session_state: st.session_state.ecra = 1
if 'nome' not in st.session_state: st.session_state.nome = ""

# --- ECRÃ 1: IDENTIFICAÇÃO ---
if st.session_state.ecra == 1:
    st.markdown('<div class="name-box">', unsafe_allow_html=True)
    # Input de Nome
    nome = st.text_input("", value=st.session_state.nome, placeholder="Escreve o teu nome aqui", label_visibility="collapsed")
    st.session_state.nome = nome
    st.markdown('</div>', unsafe_allow_html=True)

    # Criamos a tabela de botões usando colunas nativas mas com CSS flex forçado
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("SUBMETER", use_container_width=True):
            if st.session_state.nome:
                st.session_state.ecra = 2
                st.rerun()
    
    with col2:
        if st.button("LIMPAR", use_container_width=True):
            st.session_state.nome = ""
            st.rerun()

# --- ECRÃ 2: INTERAÇÃO ---
elif st.session_state.ecra == 2:
    st.markdown('<style>[data-testid="stAppViewContainer"] { background-image: none !important; background-color: white !important; }</style>', unsafe_allow_html=True)
    st.markdown(f"<h1 style='text-align:center; color:#1A237E;'>Bem-vindo, {st.session_state.nome}!</h1>", unsafe_allow_html=True)
    
    if st.button("Voltar ao Ecrã 1"):
        st.session_state.ecra = 1
        st.rerun()
