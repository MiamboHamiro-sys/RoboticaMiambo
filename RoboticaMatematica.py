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

st.markdown("""
    <style>
    /* Barra de rolagem grossa */
    ::-webkit-scrollbar { width: 55px; }
    ::-webkit-scrollbar-track { background: #f1f1f1; }
    ::-webkit-scrollbar-thumb { background: #007bff; border: 5px solid white; }
    
    .robot-container { display: flex; justify-content: center; width: 100%; padding: 10px; }
    .robot-img { width: 12.5%; min-width: 110px; }

    /* Rodapé Fixo */
    .footer-fixed {
        position: fixed;
        bottom: 0; left: 0; width: 100%;
        background-color: #ffffff; padding: 10px 5px;
        border-top: 3px solid #007bff; z-index: 9999;
    }
    
    /* Botões na mesma linha */
    .stButton > button {
        width: 100%; height: 65px;
        font-size: 11px !important;
        font-weight: bold; border-radius: 8px;
    }

    .main-content { padding-bottom: 220px; }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZAÇÃO DA IA ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def play_voice(text):
    """Gera áudio em Base64 e injeta no HTML para forçar execução no APK"""
    if text:
        try:
            clean_text = re.sub(r'[\$\{\}\\]', '', text).replace('*', ' vezes ').replace('^', ' elevado a ')
            tts = gTTS(text=clean_text, lang='pt', slow=False)
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            b64 = base64.b64encode(fp.read()).decode()
            
            # Componente de áudio com ID único e script de auto-execução
            audio_html = f"""
                <audio autoplay="true" style="display:none;">
                    <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                </audio>
            """
            st.components.v1.html(audio_html, height=0)
        except: pass

# --- ESTADO ---
if 'ecra' not in st.session_state: st.session_state.ecra = 1
if 'passo' not in st.session_state: st.session_state.passo = -1
if 'memoria' not in st.session_state: st.session_state.memoria = {}
if 'nome' not in st.session_state: st.session_state.nome = ""

# --- ECRÃ 1 ---
if st.session_state.ecra == 1:
    st.markdown('<div class="robot-container"><img src="https://cdn-icons-png.flaticon.com/512/4712/4712139.png" class="robot-img"></div>', unsafe_allow_html=True)
    nome_input = st.text_input("Qual o teu nome?", value=st.session_state.nome)
    
    st.markdown('<div class="footer-fixed">', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("✅ SUBMETER NOME"):
            if nome_input:
                st.session_state.nome = nome_input
                play_voice(f"{nome_input}, é um prazer contar consigo nesta jornada de discutirmos assuntos de Matemática")
                with st.spinner("A processar..."):
                    time.sleep(8)
                st.session_state.ecra = 2
                st.rerun()
    with c2:
        if st.button("🔄 REINICIAR"):
            st.session_state.clear()
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- ECRÃ 2 ---
elif st.session_state.ecra == 2:
    st.markdown('<div class="robot-container"><img src="https://cdn-icons-png.flaticon.com/512/4712/4712139.png" class="robot-img"></div>', unsafe_allow_html=True)
    st.markdown('<div class="main-content">', unsafe_allow_html=True)

    if st.session_state.passo == -1:
        e1_input = st.text_area("Insira o exercício E1:")
        if st.button("🚀 ENVIAR EXERCÍCIO"):
            try:
                res = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "Robô matemático. NÃO resolva E1. Crie ES1 similar. Responda APENAS JSON."},
                        {"role": "user", "content": f"Exercício: {e1_input}. Responda no formato: {{'resultado_e1': 'valor', 'passos_es1': [{{'math': 'latex', 'txt': 'explicação'}}]}}"}
                    ],
                    response_format={"type": "json_object"}
                )
                st.session_state.memoria = json.loads(res.choices[0].message.content)
                st.session_state.passo = 0
                time.sleep(2)
                play_voice("Não vou resolver o exercício que apresentaste, mas vou instruir-te a resolver siga os passos que se seguem")
                st.rerun()
            except:
                st.error("Erro na ligação com a IA.")

    else:
        passos = st.session_state.memoria.get('passos_es1', [])
        for i in range(st.session_state.passo + 1):
            if i < len(passos):
                st.info(f"**Passo {i+1}**")
                st.latex(passos[i]['math'])
                st.write(passos[i]['txt'])
                
                if i == st.session_state.passo:
                    duvida = st.text_input(f"Dúvida no Passo {i+1}?", key=f"d{i}")
                    if duvida:
                        if st.button("🎙️ ESCLARECER DÚVIDA", key=f"btn{i}"):
                            # Explicação clara da dúvida
                            expl = client.chat.completions.create(
                                model="llama-3.3-70b-versatile",
                                messages=[{"role": "user", "content": f"Explique claramente o passo {passos[i]['txt']} para quem tem a dúvida: {duvida}"}]
                            )
                            txt_expl = expl.choices[0].message.content
                            play_voice(txt_expl)
                            st.success(txt_expl)

        if st.session_state.passo == len(passos) - 1:
            st.markdown("---")
            play_voice("Siga a lógica e apresenta o resultado final")
            res_aluno = st.text_input("Resultado de E1:")
            if st.button("🏆 VALIDAR"):
                correto = str(st.session_state.memoria.get('resultado_e1')).lower().strip().replace("x=","").replace(" ","")
                aluno = res_aluno.lower().strip().replace("x=","").replace(" ","")
                if aluno == correto:
                    play_voice("parabéns acertou")
                    st.balloons()
                else:
                    play_voice("Infelizmente não é assim, clica no Botão 2 para reiniciarmos o processo ou clica no Botão 4 para recuar a explicação")

    st.markdown('</div>', unsafe_allow_html=True)

    # RODAPÉ FIXO 5 BOTÕES
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
