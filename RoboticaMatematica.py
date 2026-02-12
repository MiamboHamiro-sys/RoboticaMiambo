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

# Função para converter imagem em Base64 para garantir o carregamento no APK
def get_base64_image(url):
    try:
        response = requests.get(url)
        return base64.b64encode(response.content).decode()
    except:
        return ""

# Imagem do Robô de Corpo Inteiro (Ajustada para o seu anexo)
IMAGE_URL = "https://raw.githubusercontent.com/filipe-md/images/main/robot_full_body.png" # Substitua por um link direto funcional ou use o código abaixo
img_b64 = get_base64_image(IMAGE_URL)

st.markdown(f"""
    <style>
    /* Barra de rolagem grossa para telemóvel */
    ::-webkit-scrollbar {{ width: 55px; }}
    ::-webkit-scrollbar-track {{ background: #f1f1f1; }}
    ::-webkit-scrollbar-thumb {{ background: #007bff; border: 5px solid white; }}
    
    /* FUNDO DINÂMICO DO ECRÃ 1 */
    .stApp {{
        background-image: url("data:image/png;base64,{img_b64}");
        background-size: cover;
        background-position: center center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}

    /* Container "Glass" para legibilidade */
    .glass-box {{
        background: rgba(255, 255, 255, 0.82);
        padding: 35px;
        border-radius: 25px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
        backdrop-filter: blur(12px);
        margin: 10% auto;
        max-width: 500px;
        text-align: center;
        border: 2px solid rgba(255, 255, 255, 0.5);
    }}

    /* Rodapé Fixo e Ajustado */
    .footer-fixed {{
        position: fixed;
        bottom: 0; left: 0; width: 100%;
        background-color: white; padding: 12px 5px;
        border-top: 4px solid #007bff; z-index: 9999;
    }}
    
    .stButton > button {{
        width: 100%; height: 70px;
        font-size: 10px !important;
        font-weight: bold; border-radius: 12px;
        line-height: 1.2;
    }}

    .main-content {{ padding-bottom: 250px; }}
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

# --- CONTROLO DE ESTADO ---
if 'ecra' not in st.session_state: st.session_state.ecra = 1
if 'passo' not in st.session_state: st.session_state.passo = -1
if 'memoria' not in st.session_state: st.session_state.memoria = {}
if 'nome' not in st.session_state: st.session_state.nome = ""

# --- ECRÃ 1: INICIAL (COM ROBÔ) ---
if st.session_state.ecra == 1:
    st.markdown('<div class="glass-box">', unsafe_allow_html=True)
    st.markdown("<h1 style='color: #007bff;'>SmartProf</h1>", unsafe_allow_html=True)
    nome_input = st.text_input("Qual o teu nome?", value=st.session_state.nome)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="footer-fixed">', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("✅\nSUBMETER"):
            if nome_input:
                st.session_state.nome = nome_input
                play_voice(f"{nome_input}, é um prazer contar consigo nesta jornada de Matemática.")
                with st.spinner("Iniciando..."): time.sleep(4)
                st.session_state.ecra = 2
                st.rerun()
    with c2:
        if st.button("🔄\nREINICIAR"):
            st.session_state.clear()
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- ECRÃ 2: INTERAÇÃO (LIMPO PARA ESTUDO) ---
elif st.session_state.ecra == 2:
    # Remove o fundo do robô para foco total na matemática
    st.markdown('<style>.stApp { background-image: none !important; background-color: #f8f9fa; }</style>', unsafe_allow_html=True)
    
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    st.subheader(f"Aluno: {st.session_state.nome}")

    if st.session_state.passo == -1:
        e1_input = st.text_area("Escreve aqui o exercício (E1):", height=150)
        if st.button("🚀 ENVIAR PARA O SMARTPROF"):
            try:
                res = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "Você é um robô matemático. Crie um exercício ES1 similar. Retorne APENAS JSON."},
                        {"role": "user", "content": f"Exercício: {e1_input}. Formato JSON: {{'resultado_e1': 'valor', 'passos_es1': [{{'math': 'latex', 'txt': 'explicação'}}]}}"}
                    ],
                    response_format={"type": "json_object"}
                )
                st.session_state.memoria = json.loads(res.choices[0].message.content)
                st.session_state.passo = 0
                play_voice("Vou instruir-te a resolver. Segue os passos.")
                st.rerun()
            except: st.error("Erro ao conectar com o servidor.")
    else:
        passos = st.session_state.memoria.get('passos_es1', [])
        for i in range(st.session_state.passo + 1):
            if i < len(passos):
                st.success(f"Passo {i+1}")
                st.latex(passos[i]['math'])
                st.write(passos[i]['txt'])

    st.markdown('</div>', unsafe_allow_html=True)

    # RODAPÉ FIXO 5 BOTÕES
    st.markdown('<div class="footer-fixed">', unsafe_allow_html=True)
    b1, b2, b3, b4, b5 = st.columns(5)
    with b1:
        if st.button("🏠\nINÍCIO"): st.session_state.ecra = 1; st.rerun()
    with b2:
        if st.button("🔄\nLIMPAR"): st.session_state.passo = -1; st.rerun()
    with b3:
        if st.button("🔊\nOUVIR"): 
            if st.session_state.passo >= 0: play_voice(st.session_state.memoria['passos_es1'][st.session_state.passo]['txt'])
    with b4:
        if st.button("◀\nANTERIOR"):
            if st.session_state.passo > 0: st.session_state.passo -= 1; st.rerun()
    with b5:
        if st.button("▶\nPRÓXIMO"):
            if st.session_state.passo < len(passos) - 1:
                st.session_state.passo += 1
                play_voice(passos[st.session_state.passo]['txt'])
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
