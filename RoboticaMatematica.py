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

# --- CSS REFINADO (BOTÕES EM TABELA HORIZONTAL) ---
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
    [data-testid="stHeader"], [data-testid="stToolbar"] {{
        display: none !important;
    }}

    /* CAMPO DE NOME: Aumento de altura para não cortar (Ana) */
    .stTextInput > div > div > input {{
        background-color: rgba(255, 255, 255, 0.95) !important;
        border: 4px solid #1A237E !important;
        border-radius: 25px !important;
        height: 100px !important; 
        font-size: 35px !important;
        text-align: center !important;
        color: #1A237E !important;
        padding: 15px !important;
        font-family: 'Poppins', sans-serif !important;
    }}

    /* Forçar centralização do container do input */
    .stTextInput {{
        margin-top: 30vh;
        padding: 0 5% !important;
    }}

    /* ESTRUTURA DE TABELA/FLEX PARA BOTÕES (IMPEDE COLUNA NO CELULAR) */
    [data-testid="stHorizontalBlock"] {{
        display: flex !important;
        flex-direction: row !important; /* Força linha sempre */
        flex-wrap: nowrap !important; /* Impede quebra para coluna */
        justify-content: center !important;
        align-items: center !important;
        gap: 10px !important;
        position: fixed !important;
        bottom: 50px !important;
        left: 0 !important;
        width: 100% !important;
        padding: 0 10px !important;
        z-index: 1000 !important;
    }}

    /* Estilização dos Botões */
    .stButton > button {{
        width: 100% !important; /* Ocupa a 'célula' da coluna */
        min-width: 118px !important;
        height: 50px !important;
        background-color: white !important;
        border: 3px solid #1A237E !important;
        border-radius: 18px !important;
        font-size: 16px !important;
        font-weight: 700 !important;
        color: #1A237E !important;
        box-shadow: 0 8px 15px rgba(0,0,0,0.2);
    }}

    .stButton > button:hover {{
        background-color: #1A237E !important;
        color: white !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZAÇÃO DA IA ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def play_voice(text):
    if text:
        try:
            clean_text = re.sub(r'[\$\{\}\\]', '', text).replace('*', ' vezes ').replace('^', ' elevado a ')
            tts = gTTS(text=clean_text, lang='pt', slow=False)
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            b64 = base64.b64encode(fp.read()).decode()
            audio_html = f'<audio autoplay="true" style="display:none;"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
            st.components.v1.html(audio_html, height=0)
        except: pass

# --- ESTADO ---
if 'ecra' not in st.session_state: st.session_state.ecra = 1
if 'passo' not in st.session_state: st.session_state.passo = -1
if 'memoria' not in st.session_state: st.session_state.memoria = {}
if 'nome' not in st.session_state: st.session_state.nome = ""

# --- ECRÃ 1: IDENTIFICAÇÃO ---
if st.session_state.ecra == 1:
    # Campo de Nome (Ajustado para o centro)
    nome_input = st.text_input("", value=st.session_state.nome, placeholder="Escreve aqui a tua questão...", label_visibility="collapsed")

    # Botões em Colunas (Simulando Tabela Linha 1: Cel1 e Cel2)
    # O CSS acima garante que estas colunas fiquem sempre lado a lado no celular
    c1, c2 = st.columns(2)
    
    with c1: # Linha 1, Coluna 1
        if st.button("SUBMETER"):
            if nome_input:
                st.session_state.nome = nome_input
                st.session_state.ecra = 2
                st.rerun()

    with c2: # Linha 1, Coluna 2
        if st.button("LIMPAR"):
            st.session_state.nome = ""
            st.rerun()

# --- ECRÃ 2: INTERAÇÃO ---
elif st.session_state.ecra == 2:
    st.markdown('<style>[data-testid="stAppViewContainer"] { background-image: none !important; background-color: white; }</style>', unsafe_allow_html=True)
    st.markdown(f"<h1 style='text-align:center;'>SmartProf</h1>", unsafe_allow_html=True)
    
    if st.session_state.passo == -1:
        st.markdown(f"### Olá {st.session_state.nome}, qual é a tua dúvida?")
        e1_input = st.text_area("", placeholder="Escreve aqui a tua questão...", height=150)
        
        if st.button("🚀 ANALISAR"):
            play_voice("Muito bem, vou ajudar-te.")
            st.session_state.passo = 0
            st.rerun()
    else:
        if st.button("🏠 REINICIAR"):
            st.session_state.ecra = 1
            st.rerun()

