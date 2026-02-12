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

# --- CSS REFINADO (Sem retângulo superior, Fonte maior, Botão interno) ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');

    /* Fundo do Robô */
    [data-testid="stAppViewContainer"] {{
        background-image: url("data:image/png;base64,{img_data}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}

    /* Estilo Geral */
    * {{
        font-family: 'Poppins', sans-serif;
        color: #1A237E;
    }}

    /* Esconder o Header padrão do Streamlit e o retângulo indesejado */
    [data-testid="stHeader"], .st-emotion-cache-18ni7ap {{
        display: none !important;
    }}

    /* Container de Identificação */
    .input-wrapper {{
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        padding: 40px;
        border-radius: 25px;
        max-width: 550px;
        margin: 15% auto;
        text-align: center;
        box-shadow: 0 20px 40px rgba(0,0,0,0.3);
    }}

    /* Texto com tamanho aumentado */
    .big-label {{
        font-size: 24px !important;
        font-weight: 600;
        margin-bottom: 20px;
        display: block;
    }}

    /* Estilização do Input de Nome */
    div[data-baseweb="input"] {{
        border: 2px solid #1A237E !important;
        border-radius: 50px !important;
        background: white !important;
        padding-right: 10px; /* Espaço para o botão interno */
    }}

    input {{
        font-size: 20px !important;
        padding: 15px 25px !important;
    }}

    /* Botão de Limpar (Separado) */
    .clear-btn-container {{
        margin-top: 15px;
    }}
    
    /* Ecrã 2: Reset Visual */
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

# --- ECRÃ 1: INÍCIO ---
if st.session_state.ecra == 1:
    st.markdown('<div class="input-wrapper">', unsafe_allow_html=True)
    st.markdown('<span class="big-label">Olá! Como te chamas?</span>', unsafe_allow_html=True)
    
    # Coluna para simular o botão dentro do input
    col_inp, col_btn = st.columns([0.85, 0.15])
    
    with col_inp:
        nome_input = st.text_input("", value=st.session_state.nome, placeholder="Escreve o teu nome...", label_visibility="collapsed")
    
    with col_btn:
        # Botão de Seta (Dentro da linha visual do input)
        if st.button("↑", help="Submeter"):
            if nome_input:
                st.session_state.nome = nome_input
                st.session_state.ecra = 2
                st.rerun()

    # Botão de Limpar separado abaixo
    st.markdown('<div class="clear-btn-container">', unsafe_allow_html=True)
    if st.button("🗑️ Limpar Nome"):
        st.session_state.nome = ""
        st.rerun()
    st.markdown('</div></div>', unsafe_allow_html=True)

# --- ECRÃ 2: MATEMÁTICA ---
elif st.session_state.ecra == 2:
    st.markdown('<div class="white-bg"></div>', unsafe_allow_html=True)
    st.markdown('<style>[data-testid="stAppViewContainer"] { background-image: none !important; }</style>', unsafe_allow_html=True)

    st.markdown(f"<h1 style='text-align:center;'>SmartProf</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center; font-size:22px;'>Muito bem, <b>{st.session_state.nome}</b>! Em que te posso ajudar hoje?</p>", unsafe_allow_html=True)

    if st.session_state.passo == -1:
        e1_input = st.text_area("Apresenta a tua questão matemática...", placeholder="Ex: Resolve x + 5 = 10", height=150)
        if st.button("🚀 Analisar Exercício"):
            # Lógica Groq...
            play_voice("Vamos resolver isso passo a passo.")
            st.session_state.passo = 0
            st.rerun()
    else:
        st.write("---")
        st.info("Resolução em curso...")
        if st.button("🏠 Voltar ao Início"):
            st.session_state.ecra = 1
            st.rerun()
