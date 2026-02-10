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

# CSS para Barra de Rolagem Grossa, Imagem 1/8 e Botões Alinhados no Rodapé
st.markdown("""
    <style>
    /* Barra de rolagem muito grossa para precisão */
    ::-webkit-scrollbar { width: 55px; }
    ::-webkit-scrollbar-track { background: #f1f1f1; }
    ::-webkit-scrollbar-thumb { background: #007bff; border: 5px solid white; }
    
    /* Imagem do Robô (1/8 da tela) */
    .robot-container { display: flex; justify-content: center; width: 100%; padding: 10px; }
    .robot-img { width: 12.5%; min-width: 110px; }

    /* Rodapé Fixo e Botões em Linha (PC e Celular) */
    .footer-fixed {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: #ffffff;
        padding: 10px 5px;
        border-top: 3px solid #007bff;
        z-index: 9999;
        display: flex;
        justify-content: space-around;
    }
    
    /* Estilo dos botões do Streamlit dentro do rodapé */
    div.stButton > button {
        width: 100%;
        height: 55px;
        font-size: 12px !important;
        padding: 0px !important;
        font-weight: bold;
        border-radius: 8px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }

    /* Ajuste para o conteúdo não sumir atrás do rodapé */
    .main-content { padding-bottom: 180px; }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZAÇÃO DA IA ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def play_voice(text):
    """Gera áudio e força a reprodução compatível com Celulares"""
    if text:
        try:
            # Limpeza didática para a voz
            clean_text = re.sub(r'[\$\{\}\\]', '', text).replace('*', ' vezes ').replace('^', ' elevado a ')
            tts = gTTS(text=clean_text, lang='pt', slow=False)
            sound_file = io.BytesIO()
            tts.write_to_fp(sound_file)
            sound_file.seek(0)
            b64 = base64.b64encode(sound_file.read()).decode()
            
            # HTML para autoplay compatível com navegadores móveis
            audio_html = f"""
                <audio autoplay>
                    <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                </audio>
            """
            st.markdown(audio_html, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Erro de áudio: {e}")

# --- ESTADO GLOBAL ---
if 'ecra' not in st.session_state: st.session_state.ecra = 1
if 'passo' not in st.session_state: st.session_state.passo = -1
if 'memoria' not in st.session_state: st.session_state.memoria = {}
if 'nome' not in st.session_state: st.session_state.nome = ""

# --- ECRÃ 1: INICIAL ---
if st.session_state.ecra == 1:
    st.markdown('<div class="robot-container"><img src="https://cdn-icons-png.flaticon.com/512/4712/4712139.png" class="robot-img"></div>', unsafe_allow_html=True)
    st.title("🤖 SmartProf")
    st.session_state.nome = st.text_input("Olá Aluno! Digite seu nome:", value=st.session_state.nome)
    
    # Rodapé do Ecrã 1
    st.markdown('<div class="footer-fixed">', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("✅ SUBMETER"):
            if st.session_state.nome:
                play_voice(f"{st.session_state.nome}, é um prazer contar consigo nesta jornada de Matemática.")
                with st.spinner("Iniciando..."): time.sleep(8)
                st.session_state.ecra = 2
                st.rerun()
    with c2:
        if st.button("🔄 REINICIAR"):
            st.session_state.clear()
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- ECRÃ 2: MEDIAÇÃO ---
elif st.session_state.ecra == 2:
    st.markdown('<div class="robot-container"><img src="https://cdn-icons-png.flaticon.com/512/4712/4712139.png" class="robot-img"></div>', unsafe_allow_html=True)
    st.markdown('<div class="main-content">', unsafe_allow_html=True)

    if st.session_state.passo == -1:
        e1_input = st.text_area("Apresente o seu exercício E1:")
        if st.button("🚀 ANALISAR EXERCÍCIO"):
            with st.spinner("O Robô está a criar um similar..."):
                try:
                    prompt = f"Crie um exercício similar a este: {e1_input}. Retorne JSON com 'resultado_e1' e 'passos_es1' (lista com 'math' e 'txt')."
                    chat = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "system", "content": "És o SmartProf. Responde APENAS JSON. Resolve E1 ocultamente."}, {"role": "user", "content": prompt}],
                        response_format={"type": "json_object"}
                    )
                    st.session_state.memoria = json.loads(chat.choices[0].message.content)
                    st.session_state.passo = 0
                    time.sleep(2)
                    play_voice("Não vou resolver o exercício que apresentaste, mas vou instruir-te a resolver. Siga os passos.")
                    st.rerun()
                except: st.error("Erro na conexão com IA.")
    else:
        # Exibição dos passos ES1
        passos = st.session_state.memoria.get('passos_es1', [])
        for i in range(st.session_state.passo + 1):
            if i < len(passos):
                st.markdown(f"### Passo {i+1}")
                st.latex(passos[i]['math'])
                st.write(passos[i]['txt'])
                
                if i == st.session_state.passo:
                    duvida = st.text_input(f"Dúvida no Passo {i+1}?", key=f"d{i}")
                    if duvida:
                        if st.button("❓ ESCLARECER"):
                            prompt_d = f"Explique de forma muito clara este passo: {passos[i]['txt']}. O aluno pergunta: {duvida}."
                            resp_d = client.chat.completions.create(
                                model="llama-3.3-70b-versatile",
                                messages=[{"role": "user", "content": prompt_d}]
                            )
                            texto_d = resp_d.choices[0].message.content
                            play_voice(texto_d)
                            st.info(texto_d)

        # Validação Final
        if st.session_state.passo == len(passos) - 1:
            st.markdown("---")
            play_voice("Siga a lógica e apresenta o resultado final.")
            res_aluno = st.text_input("Qual o resultado de E1?")
            if st.button("🏆 VALIDAR"):
                correto = str(st.session_state.memoria.get('resultado_e1')).lower().strip()
                if res_aluno.lower().strip() in correto:
                    play_voice("Parabéns acertou! Recebeste 10 pontos.")
                    st.balloons()
                else:
                    play_voice("Infelizmente não é assim. Reinicie ou recue o passo.")

    st.markdown('</div>', unsafe_allow_html=True)

    # RODAPÉ FIXO COM 5 BOTÕES (PC E CELULAR)
    st.markdown('<div class="footer-fixed">', unsafe_allow_html=True)
    b1, b2, b3, b4, b5 = st.columns(5)
    with b1:
        if st.button("🏠\nInício"): 
            st.session_state.ecra = 1
            st.rerun()
    with b2:
        if st.button("🗑️\nLimpar"): 
            st.session_state.passo = -1
            st.rerun()
    with b3:
        if st.button("🔊\nVoz"): 
            if st.session_state.passo >= 0:
                play_voice(st.session_state.memoria['passos_es1'][st.session_state.passo]['txt'])
    with b4:
        if st.button("◀\nRecuar"):
            if st.session_state.passo > 0:
                st.session_state.passo -= 1
                st.rerun()
    with b5:
        if st.button("▶\nPróximo"):
            if st.session_state.passo < len(st.session_state.memoria.get('passos_es1', [])) - 1:
                st.session_state.passo += 1
                play_voice(st.session_state.memoria['passos_es1'][st.session_state.passo]['txt'])
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
