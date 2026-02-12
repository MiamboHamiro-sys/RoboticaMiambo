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
# Imagem local com o respectivo o caminho, do ficheiro a seguir
IMAGE_URL = "https://thumbs.dreamstime.com/b/professor-de-rob%C3%B4-moderno-na-faculdade-gradua%C3%A7%C3%A3o-que-mant%C3%A9m-o-conceito-intelig%C3%AAncia-artificial-para-laptops-online-robot-pac-218181889.jpg?w=576"
def get_base64_img(url):
    """Converte a imagem para Base64 para garantir renderização total"""
    try:
        response = requests.get(url)
        return base64.b64encode(response.content).decode()
    except:
        return ""

img_data = get_base64_img(IMAGE_URL)

# --- CSS PERSONALIZADO ---
st.markdown(f"""
    <style>
    /* Fundo do Robô Ocupando Toda a Tela */
    [data-testid="stAppViewContainer"] {{
        background-image: url("data:image/png;base64,{img_data}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}

    /* Container de Vidro para Input do Nome */
    .main-card {{
        background: rgba(255, 255, 255, 0.88);
        backdrop-filter: blur(8px);
        padding: 40px;
        border-radius: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.15);
        max-width: 450px;
        margin: 15% auto;
        text-align: center;
    }}

    /* Estilização do Título e Input */
    h1 {{ color: #1E88E5; font-family: 'Arial', sans-serif; }}
    
    /* Rodapé Fixo para Botões do Ecrã 1 */
    .footer-ecra1 {{
        position: fixed;
        bottom: 50px; left: 0; width: 100%;
        display: flex; justify-content: center; gap: 20px;
        z-index: 999;
    }}

    /* Botão em formato de seta (Submit) e Limpar */
    .stButton > button {{
        border-radius: 50px !important;
        height: 60px !important;
        width: 150px !important;
        font-weight: bold !important;
    }}
    
    /* Ecrã 2: Fundo Branco para estudo */
    .white-bg-active {{
        background-color: white !important;
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        z-index: -2;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZAÇÃO DA IA ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def play_voice(text):
    """Gera áudio apenas para o Ecrã 2 conforme solicitado"""
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

# --- ESTADO DA SESSÃO ---
if 'ecra' not in st.session_state: st.session_state.ecra = 1
if 'passo' not in st.session_state: st.session_state.passo = -1
if 'memoria' not in st.session_state: st.session_state.memoria = {}
if 'nome' not in st.session_state: st.session_state.nome = ""

# --- ECRÃ 1: INICIAL ---
if st.session_state.ecra == 1:
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.markdown("<h1>SmartProf</h1>", unsafe_allow_html=True)
    nome_input = st.text_input("Qual o teu nome?", value=st.session_state.nome, placeholder="Digite aqui...")
    st.markdown('</div>', unsafe_allow_html=True)

    # Botões centralizados: Seta para Avançar e Limpar
    col_l, col_r = st.columns([1, 1])
    with col_l:
        if st.button("➡ SUBMETER"):
            if nome_input:
                st.session_state.nome = nome_input
                # Som removido deste ecrã conforme solicitado
                st.session_state.ecra = 2
                st.rerun()
    with col_r:
        if st.button("🗑 LIMPAR"):
            st.session_state.nome = ""
            st.rerun()

# --- ECRÃ 2: INTERAÇÃO ---
elif st.session_state.ecra == 2:
    # Remove o fundo do robô e aplica fundo branco
    st.markdown('<div class="white-bg-active"></div>', unsafe_allow_html=True)
    st.markdown('<style>[data-testid="stAppViewContainer"] { background-image: none !important; }</style>', unsafe_allow_html=True)

    st.title(f"Bem-vindo, {st.session_state.nome}!")
    
    if st.session_state.passo == -1:
        e1_input = st.text_area("Insira o seu exercício de Matemática (E1):")
        if st.button("🚀 INICIAR EXPLICAÇÃO"):
            # Lógica Groq para gerar passos (Mantida do código original)
            play_voice("Vamos começar a resolver o seu exercício.")
            st.session_state.passo = 0
            st.rerun()
    else:
        st.info("Aqui aparecerão os passos da resolução...")
        # Adicione aqui o loop de exibição dos passos do código anterior
