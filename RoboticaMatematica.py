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

# --- CSS REFINADO: FOCO NA CAIXA DE TEXTO E VISIBILIDADE DO PLACEHOLDER ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');

    [data-testid="stAppViewContainer"] {{
        background-image: url("data:image/png;base64,{img_data}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}

    [data-testid="stHeader"] {{ display: none !important; }}

    /* CAIXA DE TEXTO: Centralização Vertical e Horizontal */
    .stTextInput > div > div > input {{
        background-color: rgba(255, 255, 255, 0.95) !important;
        border: 4px solid #1A237E !important;
        border-radius: 20px !important;
        height: 100px !important; /* Altura ideal para evitar cortes */
        font-size: 24px !important;
        text-align: center !important; /* Centraliza horizontalmente */
        color: #1A237E !important;
        font-family: 'Poppins', sans-serif !important;
        line-height: 100px !important; /* Força centralização vertical do texto digitado */
    }}

    /* FORÇAR VISIBILIDADE DO TEXTO "Escreva o teu nome aqui" (Placeholder) */
    ::placeholder {{ /* Chrome, Firefox, Opera, Safari 10.1+ */
        color: #1A237E !important;
        opacity: 0.7 !important; /* Visível mesmo sem tocar */
    }}
    :-ms-input-placeholder {{ /* Internet Explorer 10-11 */
        color: #1A237E !important;
    }}
    ::-ms-input-placeholder {{ /* Microsoft Edge */
        color: #1A237E !important;
    }}

    .name-box {{
        margin-top: 30vh;
        padding: 0 10%;
    }}

    /* Mantendo a Tabela de Botões intacta conforme solicitado */
    [data-testid="stHorizontalBlock"] {{
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        justify-content: center !important;
        align-items: center !important;
        gap: 15px !important;
        margin-top: 25px !important;
        padding: 0 10% !important;
    }}

    .stButton > button {{
        width: 100% !important;
        height: 70px !important;
        background-color: white !important;
        border: 4px solid #1A237E !important;
        border-radius: 15px !important;
        color: #1A237E !important;
        font-weight: bold !important;
        font-size: 18px !important;
        box-shadow: 0 6px 12px rgba(0,0,0,0.2);
    }}
    </style>
    """, unsafe_allow_html=True)

# --- ESTADO ---
if 'ecra' not in st.session_state: st.session_state.ecra = 1
if 'nome' not in st.session_state: st.session_state.nome = ""

# --- ECRÃ 1: IDENTIFICAÇÃO ---
if st.session_state.ecra == 1:
    st.markdown('<div class="name-box">', unsafe_allow_html=True)
    # Placeholder definido aqui para aparecer sempre
    nome = st.text_input("", value=st.session_state.nome, placeholder="Escreve o teu nome aqui", label_visibility="collapsed")
    st.session_state.nome = nome
    st.markdown('</div>', unsafe_allow_html=True)

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
    st.markdown(f"<h1 style='text-align:center; color:#1A237E; margin-top:50px;'>Bem-vindo, {st.session_state.nome}!</h1>", unsafe_allow_html=True)
    
    if st.button("Voltar ao Ecrã 1"):
        st.session_state.ecra = 1
        st.rerun()
