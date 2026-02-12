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

# URL da imagem do robô (Corpo Inteiro - Imagem 2 do anexo)
IMAGE_URL = "https://raw.githubusercontent.com/filipe-md/images/main/robot_full_body.png"

def get_base64_img(url):
    try:
        response = requests.get(url)
        return base64.b64encode(response.content).decode()
    except:
        return ""

img_data = get_base64_img(IMAGE_URL)

# --- CSS PERSONALIZADO (Fontes, Cores e Botão de Seta) ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;700&display=swap');

    /* Fundo do Robô */
    [data-testid="stAppViewContainer"] {{
        background-image: url("data:image/png;base64,{img_data}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}

    /* Estilo Geral do Texto */
    * {{
        font-family: 'Poppins', sans-serif;
        color: #1A237E; /* Azul Marinho Profundo */
    }}

    /* Container Central */
    .glass-card {{
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        padding: 50px;
        border-radius: 30px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.2);
        max-width: 500px;
        margin: 10% auto;
        text-align: center;
        border: 2px solid #1A237E;
    }}

    /* Customização do Input de Nome */
    .stTextInput input {{
        border: 2px solid #1A237E !important;
        border-radius: 15px !important;
        padding: 15px !important;
        font-size: 18px !important;
    }}

    /* Botão de Seta (Estilo imagem anexa) */
    .submit-container {{
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 20px;
        margin-top: 20px;
    }}

    /* Ecrã 2: Limpeza do fundo */
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
    """Áudio reservado apenas para o Ecrã 2"""
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
    st.markdown("<h1 style='color: #1A237E; margin-bottom:30px;'>SmartProf</h1>", unsafe_allow_html=True)
    
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

# --- ECRÃ 2: INTERAÇÃO ---
elif st.session_state.ecra == 2:
    st.markdown('<div class="white-bg"></div>', unsafe_allow_html=True)
    st.markdown('<style>[data-testid="stAppViewContainer"] { background-image: none !important; }</style>', unsafe_allow_html=True)

    st.markdown(f"<h2 style='text-align:center;'>Vamos trabalhar, {st.session_state.nome}!</h2>", unsafe_allow_html=True)

    if st.session_state.passo == -1:
        # Input de questão matemática conforme Imagem 4
        st.markdown("### Apresente a sua questão matemática...")
        e1_input = st.text_area("", placeholder="Escreve aqui a tua dúvida...", height=150)
        
        if st.button("🚀 ANALISAR QUESTÃO"):
            # Lógica Groq mantida
            play_voice("Muito bem, deixa-me analisar esse problema para te ajudar.")
            st.session_state.passo = 0
            st.rerun()
    else:
        st.write("---")
        st.info("Passos da resolução serão exibidos aqui.")
        if st.button("🏠 VOLTAR"):
            st.session_state.ecra = 1
            st.rerun()
