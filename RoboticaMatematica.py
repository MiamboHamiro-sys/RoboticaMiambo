import streamlit as st
import time
from groq import Groq
from gtts import gTTS
import base64
import io
import json
import re

# --- CONFIGURAÇÃO VISUAL ---
st.set_page_config(page_title="SmartProf", layout="wide")

st.markdown("""
    <style>
    ::-webkit-scrollbar { width: 60px; }
    ::-webkit-scrollbar-track { background: #f1f1f1; }
    ::-webkit-scrollbar-thumb { background: #007bff; border: 5px solid white; }
    
    .robot-container { display: flex; justify-content: center; width: 100%; padding-top: 10px; }
    .robot-img { width: 12.5%; min-width: 100px; }
    
    .footer-fixed {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: white;
        padding: 15px;
        border-top: 3px solid #007bff;
        z-index: 9999;
    }
    
    .content-area { padding-bottom: 200px; }
    
    div.stButton > button {
        width: 100%;
        height: 60px;
        font-weight: bold;
        font-size: 14px;
        white-space: nowrap;
    }
    </style>
    """, unsafe_allow_html=True)

# --- IA ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

SYSTEM_PROMPT = """
És o SmartProf, robô de Matemática.
REGRAS:
1. NUNCA dês a solução de E1 nem expliques usando os dados de E1.
2. Cria um ES1 similar e explica APENAS o ES1.
3. Guarda o resultado de E1 em 'resultado_e1'.
4. Retorna JSON: {"resultado_e1": "valor", "passos_es1": [{"math": "latex", "txt": "explicação"}]}
"""

def falar(texto):
    if texto:
        try:
            limpo = re.sub(r'[\$\{\}\\]', '', texto).replace('*', ' vezes ')
            tts = gTTS(text=limpo, lang='pt', slow=False)
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            b64 = base64.b64encode(fp.read()).decode()
            st.markdown(f'<audio autoplay="true" src="data:audio/mp3;base64,{b64}">', unsafe_allow_html=True)
        except: pass

# --- ESTADO ---
if 'ecra' not in st.session_state: st.session_state.ecra = 1
if 'passo' not in st.session_state: st.session_state.passo = -1
if 'memoria' not in st.session_state: st.session_state.memoria = {}
if 'nome' not in st.session_state: st.session_state.nome = ""

# --- ECRÃ 1 ---
if st.session_state.ecra == 1:
    st.markdown('<div class="robot-container"><img src="https://cdn-icons-png.flaticon.com/512/4712/4712139.png" class="robot-img"></div>', unsafe_allow_html=True)
    nome_in = st.text_input("Escreve o teu nome:", value=st.session_state.nome)
    
    st.markdown('<div class="footer-fixed">', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("SUBMETER NOME"):
            if nome_in:
                st.session_state.nome = nome_in
                falar(f"{nome_in}, é um prazer contar consigo nesta jornada de discutirmos assuntos de Matemática")
                with st.spinner("Processando..."): time.sleep(8)
                st.session_state.ecra = 2
                st.rerun()
    with c2:
        if st.button("REINICIAR TUDO"):
            st.session_state.clear()
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- ECRÃ 2 ---
elif st.session_state.ecra == 2:
    st.markdown('<div class="robot-container"><img src="https://cdn-icons-png.flaticon.com/512/4712/4712139.png" class="robot-img"></div>', unsafe_allow_html=True)
    st.markdown('<div class="content-area">', unsafe_allow_html=True)

    if st.session_state.passo == -1:
        e1_input = st.text_area("Apresente o seu exercício E1:")
        if st.button("SUBMETER EXERCÍCIO"):
            with st.spinner("A preparar ES1..."):
                try:
                    res = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": e1_input}],
                        response_format={"type": "json_object"}
                    )
                    st.session_state.memoria = json.loads(res.choices[0].message.content)
                    st.session_state.passo = 0
                    time.sleep(2)
                    falar("Não vou resolver o exercício que apresentaste, mas vou instruir-te a resolver siga os passos que se seguem")
                    st.rerun()
                except: st.error("Erro na ligação.")
    else:
        passos = st.session_state.memoria.get('passos_es1', [])
        for i in range(st.session_state.passo + 1):
            if i < len(passos):
                st.subheader(f"Passo {i+1} (Exercício Similar)")
                st.latex(passos[i]['math'])
                st.write(passos[i]['txt'])
                
                # CAMPO DE DÚVIDA PARA O PASSO ATUAL
                if i == st.session_state.passo:
                    duvida_input = st.text_input(f"Tens alguma dúvida no Passo {i+1}? Escreve aqui:", key=f"duvida_input_{i}")
                    if duvida_input:
                        if st.button("ESCLARECER DÚVIDA", key=f"btn_duvida_{i}"):
                            with st.spinner("O SmartProf está a preparar um esclarecimento claro..."):
                                prompt_duvida = f"O aluno tem uma dúvida no passo '{passos[i]['txt']}' do exercício. A dúvida é: '{duvida_input}'. Esclareça com muita clareza usando apenas voz. Responda em JSON: {{'esclarecimento': 'texto_claro'}}"
                                res_d = client.chat.completions.create(
                                    model="llama-3.3-70b-versatile",
                                    messages=[{"role": "system", "content": "És o SmartProf. Explica de forma clara e simples."}, {"role": "user", "content": prompt_duvida}],
                                    response_format={"type": "json_object"}
                                )
                                esclarecimento = json.loads(res_d.choices[0].message.content)['esclarecimento']
                                falar(esclarecimento)
                                st.info(f"🎙️ **Esclarecimento:** {esclarecimento}")

        if st.session_state.passo == len(passos) - 1:
            st.markdown("---")
            falar("siga a lógica e apresenta o resultado final")
            res_aluno = st.text_input("Resultado do exercício E1:")
            if st.button("VALIDAR RESULTADO"):
                correto = str(st.session_state.memoria.get('resultado_e1')).lower().strip()
                if res_aluno.lower().strip() == correto:
                    falar("parabéns acertou")
                    st.balloons()
                else:
                    falar("Infelizmente não é assim, clica no Botão 2 para reiniciarmos ou Botão 4 para recuar")

    st.markdown('</div>', unsafe_allow_html=True)

    # BOTÕES INFERIORES
    st.markdown('<div class="footer-fixed">', unsafe_allow_html=True)
    b1, b2, b3, b4, b5 = st.columns(5)
    with b1:
        if st.button("ECRÃ 1"): st.session_state.ecra = 1; st.rerun()
    with b2:
        if st.button("REINICIAR"): st.session_state.passo = -1; st.rerun()
    with b3:
        if st.button("RECUAR EXPL."): falar(st.session_state.memoria['passos_es1'][st.session_state.passo]['txt'])
    with b4:
        if st.button("RECUAR PASSO"):
            if st.session_state.passo > 0: st.session_state.passo -= 1; st.rerun()
    with b5:
        if st.button("PRÓXIMO"):
            if st.session_state.passo < len(passos) - 1:
                st.session_state.passo += 1
                falar(passos[st.session_state.passo]['txt'])
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
