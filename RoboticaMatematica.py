import streamlit as st
import time
from groq import Groq
from gtts import gTTS
import base64
import io
import json
import re

# --- CONFIGURAÇÃO DA INTERFACE ---
st.set_page_config(page_title="SmartProf", layout="wide")

# URL de uma imagem de robô de corpo inteiro (Link estável)
IMAGE_URL = "https://img.freepik.com/fotos-premium/um-robo-branco-com-um-corpo-inteiro-e-um-fundo-branco_115803-569.jpg"

st.markdown(f"""
    <style>
    /* Barra de rolagem grossa */
    ::-webkit-scrollbar {{ width: 55px; }}
    ::-webkit-scrollbar-track {{ background: #f1f1f1; }}
    ::-webkit-scrollbar-thumb {{ background: #007bff; border: 5px solid white; }}
    
    /* FUNDO DO ECRÃ 1 - FORÇADO PARA OCUPAR TUDO */
    [data-testid="stAppViewContainer"] {{
        background-image: url("{IMAGE_URL}");
        background-size: cover;
        background-position: center top;
        background-repeat: no-repeat;
    }}

    /* Ajuste para o Ecrã 2 ficar branco e limpo */
    .stApp {{
        background-attachment: fixed;
    }}

    /* Container de Vidro para os inputs do Ecrã 1 */
    .glass-box {{
        background: rgba(255, 255, 255, 0.85);
        padding: 40px;
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.3);
        margin-top: 20%;
        text-align: center;
    }}

    /* Rodapé Fixo com botões na mesma linha */
    .footer-fixed {{
        position: fixed;
        bottom: 0; left: 0; width: 100%;
        background-color: white; padding: 10px 5px;
        border-top: 3px solid #007bff; z-index: 9999;
    }}
    
    .stButton > button {{
        width: 100%; height: 65px;
        font-size: 11px !important;
        font-weight: bold; border-radius: 8px;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
    }}

    .main-content {{ padding-bottom: 220px; }}
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

# --- ECRÃ 1: INICIAL ---
if st.session_state.ecra == 1:
    # O CSS [data-testid="stAppViewContainer"] já carrega o robô ao fundo
    st.markdown('<div class="glass-box">', unsafe_allow_html=True)
    st.title("🤖 SmartProf")
    nome_input = st.text_input("Qual o teu nome?", value=st.session_state.nome)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="footer-fixed">', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("✅\nSUBMETER NOME"):
            if nome_input:
                st.session_state.nome = nome_input
                play_voice(f"{nome_input}, é um prazer contar consigo nesta jornada.")
                with st.spinner("A processar..."): time.sleep(8)
                st.session_state.ecra = 2
                st.rerun()
    with c2:
        if st.button("🔄\nREINICIAR"):
            st.session_state.clear()
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- ECRÃ 2: INTERAÇÃO ---
elif st.session_state.ecra == 2:
    # Removemos o fundo do robô para o Ecrã 2 ser limpo
    st.markdown('<style>[data-testid="stAppViewContainer"] { background-image: none !important; background-color: white; }</style>', unsafe_allow_html=True)
    
    st.markdown('<div class="main-content">', unsafe_allow_html=True)

    if st.session_state.passo == -1:
        e1_input = st.text_area("Insira o exercício E1:")
        if st.button("🚀 ENVIAR EXERCÍCIO"):
            try:
                res = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "Robô matemático didático. Responda apenas JSON."},
                        {"role": "user", "content": f"Crie ES1 similar a: {e1_input}. Responda: {{'resultado_e1': 'valor', 'passos_es1': [{{'math': 'latex', 'txt': 'explicação'}}]}}"}
                    ],
                    response_format={"type": "json_object"}
                )
                st.session_state.memoria = json.loads(res.choices[0].message.content)
                st.session_state.passo = 0
                play_voice("Não vou resolver o exercício que apresentaste, mas vou instruir-te. Siga os passos.")
                st.rerun()
            except: st.error("Erro na conexão.")
    else:
        passos = st.session_state.memoria.get('passos_es1', [])
        for i in range(st.session_state.passo + 1):
            if i < len(passos):
                st.info(f"**Passo {i+1}**")
                st.latex(passos[i]['math'])
                st.write(passos[i]['txt'])

    st.markdown('</div>', unsafe_allow_html=True)

    # RODAPÉ FIXO 5 BOTÕES (Sempre visíveis no fundo)
    st.markdown('<div class="footer-fixed">', unsafe_allow_html=True)
    b1, b2, b3, b4, b5 = st.columns(5)
    with b1:
        if st.button("🏠\nECRÃ 1"): st.session_state.ecra = 1; st.rerun()
    with b2:
        if st.button("🔄\nBOTÃO 2"): st.session_state.passo = -1; st.rerun()
    with b3:
        if st.button("🔊\nEXPLICA"): 
            if st.session_state.passo >= 0: play_voice(st.session_state.memoria['passos_es1'][st.session_state.passo]['txt'])
    with b4:
        if st.button("◀\nBOTÃO 4"):
            if st.session_state.passo > 0: st.session_state.passo -= 1; st.rerun()
    with b5:
        if st.button("▶\nBOTÃO 5"):
            if st.session_state.passo < len(passos) - 1:
                st.session_state.passo += 1
                play_voice(passos[st.session_state.passo]['txt'])
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
