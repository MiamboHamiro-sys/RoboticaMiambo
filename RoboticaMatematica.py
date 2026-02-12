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

# Imagem de fundo solicitada
IMAGE_URL = "https://thumbs.dreamstime.com/b/professor-de-rob%C3%B4-moderno-na-faculdade-gradua%C3%A7%C3%A3o-que-mant%C3%A9m-o-conceito-intelig%C3%AAncia-artificial-para-laptops-online-robot-pac-218181889.jpg?w=576"

def get_base64_img(url):
    try:
        response = requests.get(url)
        return base64.b64encode(response.content).decode()
    except:
        return ""

img_data = get_base64_img(IMAGE_URL)

# --- CSS PARA FORÇAR TABELA HORIZONTAL (LINHA 1, COL 1 E 2) ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');

    /* Fundo Estável */
    [data-testid="stAppViewContainer"] {{
        background-image: url("data:image/png;base64,{img_data}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}

    /* Esconder elementos nativos */
    [data-testid="stHeader"], [data-testid="stToolbar"] {{ display: none !important; }}

    /* Input de Nome - Ajuste para não cortar texto */
    .stTextInput > div > div > input {{
        background-color: rgba(255, 255, 255, 0.95) !important;
        border: 4px solid #1A237E !important;
        border-radius: 15px !important;
        height: 80px !important;
        font-size: 28px !important;
        text-align: center !important;
        color: #1A237E !important;
        font-family: 'Poppins', sans-serif !important;
    }}

    .stTextInput {{ margin-top: 25vh !important; }}

    /* ESTRUTURA DE TABELA PARA OS BOTÕES (LADO A LADO) */
    [data-testid="stHorizontalBlock"] {{
        display: flex !important;
        flex-direction: row !important; /* Força horizontal */
        flex-wrap: nowrap !important; /* Impede que o botão suma ou desça */
        justify-content: center !important;
        align-items: center !important;
        gap: 10px !important;
        margin-top: 30px !important;
    }}

    /* Estilo dos Botões (Células da Tabela) */
    .stButton > button {{
        width: 100% !important;
        height: 65px !important;
        background-color: white !important;
        border: 4px solid #1A237E !important; /* Borda forte para ver a 'célula' */
        border-radius: 12px !important;
        color: #1A237E !important;
        font-weight: bold !important;
        font-size: 18px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
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
            clean_text = re.sub(r'[\$\{\}\\]', '', text)
            tts = gTTS(text=clean_text, lang='pt', slow=False)
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            b64 = base64.b64encode(fp.read()).decode()
            md = f'<audio autoplay="true" style="display:none;"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
            st.markdown(md, unsafe_allow_html=True)
        except: pass

# --- ESTADO ---
if 'ecra' not in st.session_state: st.session_state.ecra = 1

# --- ECRÃ 1: IDENTIFICAÇÃO ---
if st.session_state.ecra == 1:
    # Campo de Nome
    nome = st.text_input("", value=st.session_state.get('nome', ""), placeholder="ESCREVA O SEU NOME", label_visibility="collapsed")

    # TABELA DE BOTÕES: Linha 1
    col1, col2 = st.columns(2)
    
    with col1: # Célula 1 (L1C1)
        if st.button("SUBMETER"):
            if nome:
                st.session_state.nome = nome
                play_voice(f"{nome}, vamos começar!")
                st.session_state.ecra = 2
                st.rerun()
    
    with col2: # Célula 2 (L1C2)
        if st.button("LIMPAR"):
            st.session_state.nome = ""
            st.rerun()

# --- ECRÃ 2: INTERAÇÃO ---
elif st.session_state.ecra == 2:
    st.markdown('<style> .stApp { background-image: none !important; background-color: white !important; } </style>', unsafe_allow_html=True)
    st.title(f"Bem-vindo, {st.session_state.nome}!")
    if st.button("Voltar ao Ecrã 1"):
        st.session_state.ecra = 1
        st.rerun()
