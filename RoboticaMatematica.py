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
    st.markdown('<div class="robot-container"><img src="https://cdn-icons-png.flaticon.com/512/4712/4712139.png" class="robot-img"></div>', unsafe_allow_html=True)
    st.session_state.nome = st.text_input("Introduz o teu nome:", value=st.session_state.nome)
    
    st.markdown('<div class="footer-fixed">', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("✅ SUBMETER"):
            if st.session_state.nome:
                play_voice(f"{st.session_state.nome}, é um prazer contar consigo nesta jornada de discutirmos assuntos de Matemática")
                with st.spinner("A sintonizar voz..."): time.sleep(8)
                st.session_state.ecra = 2
                st.rerun()
    with c2:
        if st.button("🔄 REINICIAR"):
            st.session_state.clear()
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- ECRÃ 2: INTERAÇÃO DIDÁTICA ---
elif st.session_state.ecra == 2:
    st.markdown('<div class="robot-container"><img src="https://cdn-icons-png.flaticon.com/512/4712/4712139.png" class="robot-img"></div>', unsafe_allow_html=True)
    st.markdown('<div class="main-content">', unsafe_allow_html=True)

    if st.session_state.passo == -1:
        e1_input = st.text_area("Apresenta o teu exercício E1:")
        if st.button("🚀 ENVIAR PARA O ROBÔ"):
            with st.spinner("O SmartProf está a preparar um exercício similar..."):
                try:
                    # IA gera ES1 similar e resolve E1 ocultamente
                    prompt = f"""Exercício do aluno: {e1_input}. 
                    1. Atue APENAS se for matemática. 
                    2. NÃO resolva este exercício para o aluno.
                    3. Crie um exercício ES1 similar.
                    4. Retorne APENAS JSON: {{"resultado_e1": "valor", "passos_es1": [{{"math": "latex", "txt": "explicação"}}]}}"""
                    
                    chat = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "system", "content": "Robô matemático didático. Responde apenas JSON."},
                                  {"role": "user", "content": prompt}],
                        response_format={"type": "json_object"}
                    )
                    st.session_state.memoria = json.loads(chat.choices[0].message.content)
                    st.session_state.passo = 0
                    time.sleep(2)
                    play_voice("Não vou resolver o exercício que apresentaste, mas vou instruir-te a resolver siga os passos que se seguem")
                    st.rerun()
                except: st.error("Erro na conexão com IA. Verifica se o conteúdo é Matemática.")
    else:
        # Exibição progressiva dos passos do ES1
        passos = st.session_state.memoria.get('passos_es1', [])
        for i in range(st.session_state.passo + 1):
            if i < len(passos):
                st.info(f"**Passo {i+1} (Similar)**")
                st.latex(passos[i]['math'])
                st.write(passos[i]['txt'])
                
                if i == st.session_state.passo:
                    duvida = st.text_input(f"Alguma dúvida no Passo {i+1}?", key=f"d{i}")
                    if duvida:
                        if st.button("🎙️ ESCLARECER"):
                            with st.spinner("A explicar..."):
                                d_chat = client.chat.completions.create(
                                    model="llama-3.3-70b-versatile",
                                    messages=[{"role": "user", "content": f"Explica com clareza o passo {passos[i]['txt']} sabendo que a dúvida é: {duvida}"}]
                                )
                                resposta = d_chat.choices[0].message.content
                                play_voice(resposta)
                                st.success(resposta)

        # Validação Final do Exercício E1
        if st.session_state.passo == len(passos) - 1:
            st.markdown("---")
            play_voice("Siga a lógica e apresenta o resultado final")
            res_aluno = st.text_input("Apresenta o resultado final do teu exercício (E1):")
            if st.button("🏆 VALIDAR"):
                # Limpeza para comparação infalível
                correto = str(st.session_state.memoria.get('resultado_e1')).lower().strip().replace("x=","").replace(" ","")
                aluno = res_aluno.lower().strip().replace("x=","").replace(" ","")
                
                if aluno == correto:
                    play_voice("parabéns acertou")
                    st.balloons()
                    st.success("Ganhaste 10 pontos!")
                else:
                    play_voice("Infelizmente não é assim, clica no Botão 2 para reiniciarmos o processo ou clica no Botão 4 para recuar a explicação")
                    st.error("Tenta novamente ou recua um passo.")

    st.markdown('</div>', unsafe_allow_html=True)

    # RODAPÉ FIXO: 5 Botões Alinhados para PC e Celular
    st.markdown('<div class="footer-fixed">', unsafe_allow_html=True)
    b1, b2, b3, b4, b5 = st.columns(5)
    with b1:
        if st.button("🏠\nECRÃ 1"): st.session_state.ecra = 1; st.rerun()
    with b2:
        if st.button("🔄\nBOTÃO 2"): st.session_state.passo = -1; st.rerun()
    with b3:
        if st.button("🔊\nRECUAR EX"): 
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
