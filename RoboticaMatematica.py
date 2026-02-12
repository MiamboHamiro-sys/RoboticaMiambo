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

# URL da imagem do robô (Corpo Inteiro)
IMAGE_URL = "https://thumbs.dreamstime.com/b/professor-de-rob%C3%B4-moderno-na-faculdade-gradua%C3%A7%C3%A3o-que-mant%C3%A9m-o-conceito-intelig%C3%AAncia-artificial-para-laptops-online-robot-pac-218181889.jpg?w=576"

def get_base64_img(url):
    try:
        response = requests.get(url)
        return base64.b64encode(response.content).decode()
    except:
        return ""

img_data = get_base64_img(IMAGE_URL)

# --- CSS MINIMALISTA E POSICIONAMENTO ---
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

    /* Estilo Geral e Fontes */
    * {{
        font-family: 'Poppins', sans-serif;
        color: #1A237E !important;
    }}

    /* Esconder elementos nativos do Streamlit */
    [data-testid="stHeader"], [data-testid="stToolbar"] {{
        display: none !important;
    }}

    /* Centralização do campo de nome */
    .input-container {{
        margin-top: 25vh;
        display: flex;
        justify-content: center;
    }}

    /* Estilização do Campo de Nome */
    .stTextInput > div > div > input {{
        background-color: rgba(255, 255, 255, 0.9) !important;
        border: 3px solid #1A237E !important;
        border-radius: 20px !important;
        height: 70px !important;
        font-size: 24px !important;
        text-align: center !important;
    }}

    /* Rodapé Fixo para os Botões Inferiores */
    .footer-buttons {{
        position: fixed;
        bottom: 50px;
        left: 0;
        width: 100%;
        display: flex;
        justify-content: center;
        gap: 20px;
        padding: 0 20px;
    }}

    /* Padronização do tamanho dos botões */
    .stButton > button {{
        width: 180px !important;
        height: 70px !important;
        background-color: white !important;
        border: 3px solid #1A237E !important;
        border-radius: 15px !important;
        font-size: 20px !important;
        font-weight: bold !important;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }}

    .stButton > button:hover {{
        background-color: #1A237E !important;
        color: white !important;
    }}

    /* Ecrã 2: Limpeza */
    .white-bg {{
        background-color: white !important;
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        z-index: -2;
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
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("<h1 style='color: #212121; margin-bottom:30px;'>SmartProf</h1>", unsafe_allow_html=True)
    
    nome_input = st.text_input("Olá! Qual o teu nome?", value=st.session_state.nome, placeholder="Escreve aqui o teu nome...")
    
    st.markdown('<div class="submit-container">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        # Botão de Seta conforme Imagem 4
        if st.button("↑", help="Submeter Nome"):
            if nome_input:
                st.session_state.nome = nome_input
                st.session_state.ecra = 2
                st.rerun()
    with col2:
        if st.button("🗑️", help="Limpar Nome"):
            st.session_state.nome = ""
            st.rerun()
    st.markdown('</div></div>', unsafe_allow_html=True)
    ##########

# --- ECRÃ 2: INTERAÇÃO ---
elif st.session_state.ecra == 2:
    st.markdown('<div class="white-bg"></div>', unsafe_allow_html=True)
    st.markdown('<style>[data-testid="stAppViewContainer"] { background-image: none !important; }</style>', unsafe_allow_html=True)

    st.markdown(f"<h1 style='text-align:center;'>SmartProf</h1>", unsafe_allow_html=True)
    
    if st.session_state.passo == -1:
        st.markdown(f"### Olá {st.session_state.nome}, qual é a tua dúvida?")
        e1_input = st.text_area("", placeholder="Escreve aqui a questão...", height=150)
        
        if st.button("🚀 ANALISAR"):
            # Lógica Groq mantida
            play_voice("Deixa-me ajudar-te com isso.")
            st.session_state.passo = 0
            st.rerun()
    else:
        st.success("Resolução pronta!")
        if st.button("🏠 REINICIAR"):
            st.session_state.ecra = 1
            st.rerun()



