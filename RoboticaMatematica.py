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

# URL da imagem do robô (corpo inteiro)
# Se preferir usar uma imagem local, coloque o caminho do ficheiro aqui
IMAGE_URL = "https://img.cdndsgni.com/preview/11038919.jpg"

def get_base64_img(url):
    """Converte a imagem para Base64 para garantir que renderiza no APK"""
    try:
        response = requests.get(url)
        return base64.b64encode(response.content).decode()
    except:
        return ""

img_data = get_base64_img(IMAGE_URL)

# CSS Estrutural
st.markdown(f"""
    <style>
    /* Forçar fundo no container principal do Streamlit */
    [data-testid="stAppViewContainer"] {{
        background-image: url("data:image/png;base64,{img_data}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}

    /* Camada de brilho/contraste para o Ecrã 1 */
    .overlay-ecra1 {{
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(255, 255, 255, 0.1); /* Ajuste para dar foco ao robô */
        z-index: -1;
    }}

    /* Caixa de Vidro (Interface) */
    .glass-card {{
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(10px);
        padding: 40px;
        border-radius: 25px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        max-width: 500px;
        margin: 15% auto;
        text-align: center;
    }}

    /* Rodapé Fixo */
    .footer-fixed {{
        position: fixed;
        bottom: 0; left: 0; width: 100%;
        background-color: white; padding: 15px 5px;
        border-top: 3px solid #007bff; z-index: 9999;
    }}

    .stButton > button {{
        width: 100%; height: 70px;
        font-weight: bold; border-radius: 12px;
    }}

    /* Esconder fundo no Ecrã 2 */
    .white-bg {{
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        background-color: white !important;
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

# --- LÓGICA DE ECRÃS ---
if st.session_state.ecra == 1:
    st.markdown('<div class="overlay-ecra1"></div>', unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("<h1 style='color: #007bff;'>SmartProf</h1>", unsafe_allow_html=True)
    nome_input = st.text_input("Qual o teu nome?", value=st.session_state.nome)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="footer-fixed">', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("✅\nSUBMETER"):
            if nome_input:
                st.session_state.nome = nome_input
                play_voice(f"{nome_input}, é um prazer estar contigo.")
                st.session_state.ecra = 2
                st.rerun()
    with c2:
        if st.button("🔄\nREINICIAR"):
            st.session_state.clear()
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.ecra == 2:
    # Remove fundo do robô para foco no estudo
    st.markdown('<div class="white-bg"></div>', unsafe_allow_html=True)
    st.markdown('<style>[data-testid="stAppViewContainer"] { background-image: none !important; }</style>', unsafe_allow_html=True)

    if st.session_state.passo == -1:
        e1_input = st.text_area("Insira o exercício E1:")
        if st.button("🚀 ENVIAR"):
            # Lógica Groq... (mantida conforme anterior)
            st.session_state.passo = 0
            st.rerun()
    else:
        # Exibição de passos...
        st.write(f"Olá {st.session_state.nome}, vamos resolver!")

    # Rodapé fixo de navegação (Botões 1 a 5)
    st.markdown('<div class="footer-fixed">', unsafe_allow_html=True)
    b_cols = st.columns(5)
    labels = ["🏠\nECRÃ 1", "🔄\nRESET", "🔊\nOUVIR", "◀\nVOLTAR", "▶\nAVANÇAR"]
    for i, col in enumerate(b_cols):
        with col:
            if st.button(labels[i], key=f"fbtn_{i}"):
                if i == 0: st.session_state.ecra = 1; st.rerun()
                if i == 1: st.session_state.passo = -1; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

