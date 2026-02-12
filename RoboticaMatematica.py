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

# CSS Avançado para Robô, Barra de Rolagem e Rodapé Fixo
st.markdown("""
    <style>
    /* Barra de rolagem lateral muito grossa */
    ::-webkit-scrollbar { width: 55px; }
    ::-webkit-scrollbar-track { background: #f1f1f1; }
    ::-webkit-scrollbar-thumb { background: #007bff; border: 5px solid white; }
    
    /* Imagem do Robô (1/8 da largura da tela) */
    .robot-container { display: flex; justify-content: center; width: 100%; padding: 10px; }
    .robot-img { width: 12.5%; min-width: 110px; border-radius: 10px; }

    /* Rodapé Fixo na parte inferior para PC e Celular */
    .footer-fixed {
        position: fixed;
        bottom: 0; left: 0; width: 100%;
        background-color: #ffffff; padding: 10px 0px;
        border-top: 3px solid #007bff; z-index: 9999;
    }
    
    /* Forçar botões na mesma linha e do mesmo tamanho */
    .footer-fixed .stButton > button {
        width: 100%; height: 60px;
        font-size: 10px !important;
        font-weight: bold; border-radius: 8px;
        display: flex; align-items: center; justify-content: center;
        text-transform: uppercase;
    }

    .main-content { padding-bottom: 200px; }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZAÇÃO DA IA ---
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    st.error("ERRO: GROQ_API_KEY não encontrada nas Secrets do Streamlit.")

def play_voice(text):
    """Gera áudio e usa JavaScript para forçar a reprodução em APKs/Celulares"""
    if text:
        try:
            # Limpeza de texto para voz natural
            clean_text = re.sub(r'[\$\{\}\\]', '', text).replace('*', ' vezes ').replace('^', ' elevado a ')
            tts = gTTS(text=clean_text, lang='pt', slow=False)
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            b64 = base64.b64encode(fp.read()).decode()
            
            audio_id = f"audio_{int(time.time())}"
            audio_html = f"""
                <audio id="{audio_id}">
                    <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                </audio>
                <script>
                    var audio = document.getElementById("{audio_id}");
                    audio.play().catch(function(e) {{
                        console.log("Bloqueio de áudio removido no próximo clique.");
                        document.addEventListener('click', function() {{ audio.play(); }}, {{ once: true }});
                    }});
                </script>
            """
            st.components.v1.html(audio_html, height=0)
        except: pass

# --- ESTADO DA SESSÃO ---
if 'ecra' not in st.session_state: st.session_state.ecra = 1
if 'passo' not in st.session_state: st.session_state.passo = -1
if 'memoria' not in st.session_state: st.session_state.memoria = {}
if 'nome' not in st.session_state: st.session_state.nome = ""

# --- ECRÃ 1: INICIAL ---
if st.session_state.ecra == 1:
    st
