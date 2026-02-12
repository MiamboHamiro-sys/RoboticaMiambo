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

# URL da imagem de fundo do Robô
IMAGE_URL = "https://thumbs.dreamstime.com/b/professor-de-rob%C3%B4-moderno-na-faculdade-gradua%C3%A7%C3%A3o-que-mant%C3%A9m-o-conceito-intelig%C3%AAncia-artificial-para-laptops-online-robot-pac-218181889.jpg?w=576"

def get_base64_img(url):
    try:
        response = requests.get(url)
        return base64.b64encode(response.content).decode()
    except:
        return ""

img_data = get_base64_img(IMAGE_URL)

# --- CSS PERSONALIZADO ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');

    /* Fundo Estável no Ecrã 1 */
    .stApp {{
        background-image: url("data:image/png;base64,{img_data}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}

    /* Estilo Geral */
    * {{ font-family: 'Poppins', sans-serif; }}

    /* Esconder Header e Toolbar */
    [data-testid="stHeader"], [data-testid="stToolbar"] {{ display: none !important; }}

    /* Centralização e Estilo do Input */
    .input-container {{
        margin-top: 30vh;
        display: flex;
        justify-content: center;
        padding: 0 10%;
    }}

    .stTextInput > div > div > input {{
        background-color: rgba(255, 255, 255, 0.9) !important;
        border: 3px solid #1A237E !important;
        border-radius: 15px !important;
        height: 70px !important;
        font-size: 24px !important;
        text-align: center !important;
        color: #1A237E !important;
    }}

    /* Forçar Botões na Mesma Linha (Comportamento de Tabela/Flexbox) */
    [data-testid="stHorizontalBlock"] {{
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        justify-content: center !important;
        align-items: center !important;
        gap: 10px !important;
        margin-top: 20px !important;
    }}

    .stButton > button {{
        width: 100% !important;
        height: 60px !important;
        background-color: white !important;
        border: 2px solid #1A237E !important;
        border-radius: 12px !important;
        color: #1A237E !important;
        font-weight: bold !important;
        font-size: 18px !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    }}

    .stButton > button:hover {{
        background-color: #1A237E !important;
        color: white !important;
    }}

    /* Ecrã 2: Fundo Limpo */
    .white-bg {{
        background-color: white !important;
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        z-index: -1;
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
if 'passo_atual' not in st.session_state: st.session_state.passo_atual = -1
if 'memoria_ia' not in st.session_state: st.session_state.memoria_ia = {}

# --- ECRÃ 1: IDENTIFICAÇÃO ---
if st.session_state.ecra == 1:
    # Campo de Nome Centralizado
    st.markdown('<div class="input-container">', unsafe_allow_html=True)
    nome = st.text_input("", value=st.session_state.get('nome', ""), placeholder="TEU NOME", label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

    # Botões Lado a Lado (Linha 1: Coluna 1 e Coluna 2)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("SUBMETER"):
            if nome:
                st.session_state.nome = nome
                play_voice(f"{nome}, é um prazer contar contigo nesta jornada.")
                st.session_state.ecra = 2
                st.rerun()
    with c2:
        if st.button("LIMPAR"):
            st.session_state.nome = ""
            st.rerun()

# --- ECRÃ 2: INTERAÇÃO ---
elif st.session_state.ecra == 2:
    st.markdown('<div class="white-bg"></div>', unsafe_allow_html=True)
    # Mantém a lógica original do seu Ecrã 2 a partir daqui...
    st.title(f"Olá, {st.session_state.nome}!")
    if st.button("Voltar"):
        st.session_state.ecra = 1
        st.rerun()
