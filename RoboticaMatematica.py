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
    ::-webkit-scrollbar { width: 50px; }
    ::-webkit-scrollbar-track { background: #f1f1f1; }
    ::-webkit-scrollbar-thumb { background: #007bff; border-radius: 5px; }
    .robot-container { display: flex; justify-content: center; width: 100%; }
    .robot-img { width: 12.5%; min-width: 100px; }
    .footer { position: fixed; bottom: 0; left: 0; width: 100%; background-color: white; padding: 10px; border-top: 2px solid #ddd; z-index: 1000; }
    div.stButton > button { width: 100%; height: 60px; font-weight: bold; }
    .main-content { padding-bottom: 120px; }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZAÇÃO DA IA ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# PROMPT REFORÇADO PARA RECONHECIMENTO DE EXPRESSÕES
SYSTEM_PROMPT = """
És o "SmartProf", um robô especializado em Matemática. 
O aluno pode enviar expressões como "x^2-9=0", "2/3 + 1/2", ou "sqrt(16)". Isto É MATEMÁTICA.
REGRAS:
1. Se o input contiver números, variáveis (x, y, z) ou operadores (+, -, *, /, ^, sqrt, =), considera como MATEMÁTICA.
2. NUNCA dês a solução do exercício E1 do aluno.
3. Cria um exercício similar ES1.
4. Para as expressões matemáticas, usa obrigatoriamente a sintaxe LaTeX (ex: \\frac{a}{b}, x^{2}, \\sqrt{x}).
5. Retorna um JSON rigoroso:
{
  "resultado_e1": "valor",
  "passos": [
    {"expressao": "comando_latex", "explicacao": "texto_didatico"}
  ]
}
"""

def play_voice(text):
    if text:
        try:
            # Remove símbolos LaTeX da voz para a leitura ser natural
            clean_text = re.sub(r'[\$\{\}\\]', '', text)
            tts = gTTS(text=clean_text, lang='pt', slow=False)
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            b64 = base64.b64encode(fp.read()).decode()
            md = f'<audio autoplay="true" src="data:audio/mp3;base64,{b64}">'
            st.markdown(md, unsafe_allow_html=True)
        except: pass

if 'ecra' not in st.session_state: st.session_state.ecra = 1
if 'passo_atual' not in st.session_state: st.session_state.passo_atual = -1
if 'memoria_ia' not in st.session_state: st.session_state.memoria_ia = {}

# --- ECRÃ 1 ---
if st.session_state.ecra == 1:
    st.markdown('<div class="robot-container"><img src="https://cdn-icons-png.flaticon.com/512/4712/4712139.png" class="robot-img"></div>', unsafe_allow_html=True)
    nome = st.text_input("Nome do aluno:", value=st.session_state.get('nome', ""))
    if st.button("Submeter Nome"):
        if nome:
            st.session_state.nome = nome
            play_voice(f"{nome}, é um prazer contar consigo nesta jornada de discutirmos assuntos de Matemática")
            with st.spinner("A processar..."): time.sleep(8)
            st.session_state.ecra = 2
            st.rerun()

# --- ECRÃ 2 ---
elif st.session_state.ecra == 2:
    st.markdown('<div class="robot-container"><img src="https://cdn-icons-png.flaticon.com/512/4712/4712139.png" class="robot-img"></div>', unsafe_allow_html=True)
    st.markdown('<div class="main-content">', unsafe_allow_html=True)

    if st.session_state.passo_atual == -1:
        e1_input = st.text_area("Insira o exercício (ex: x^2-9=0):")
        if st.button("Enviar Exercício"):
            with st.spinner("O SmartProf está a analisar a expressão..."):
                try:
                    completion = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": e1_input}],
                        response_format={"type": "json_object"}
                    )
                    st.session_state.memoria_ia = json.loads(completion.choices[0].message.content)
                    st.session_state.passo_atual = 0
                    time.sleep(2)
                    play_voice("Não vou resolver o exercício que apresentaste, mas vou instruir-te a resolver. Siga os passos que se seguem")
                    st.rerun()
                except Exception:
                    st.error("Erro ao processar. Certifica-te que escreveste uma expressão matemática clara.")

    else:
        passos = st.session_state.memoria_ia.get('passos', [])
        for i in range(st.session_state.passo_atual + 1):
            if i < len(passos):
                st.markdown(f"#### Passo {i+1}")
                # Renderização de LaTeX para frações e potências
                st.latex(passos[i]['expressao'])
                st.write(passos[i]['explicacao'])
                
                if i == st.session_state.passo_atual:
                    duvida = st.text_input("Dúvida neste passo?", key=f"d_{i}")
                    if duvida:
                        if st.button("Explique-me"): play_voice(passos[i]['explicacao'])

        if st.session_state.passo_atual == len(passos) - 1:
            st.markdown("---")
            play_voice("siga a lógica e apresenta o resultado final")
            res_aluno = st.text_input("Resultado de E1:")
            if st.button("Validar"):
                if res_aluno.strip() == str(st.session_state.memoria_ia.get('resultado_e1')):
                    play_voice("parabéns acertou")
                    st.balloons()
                else:
                    play_voice("Infelizmente não é assim, clica no Botão 2 para reiniciarmos ou botão 4 para recuar")

    st.markdown('</div>', unsafe_allow_html=True)

    # --- RODAPÉ ---
    st.markdown('<div class="footer">', unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: 
        if st.button("Ecrã 1"): 
            st.session_state.ecra = 1
            st.rerun()
    with c2:
        if st.button("Limpar"):
            st.session_state.passo_atual = -1
            st.rerun()
    with c3: st.button("Explicação")
    with c4:
        if st.button("Recuar"):
            if st.session_state.passo_atual > 0:
                st.session_state.passo_atual -= 1
                st.rerun()
    with c5:
        if st.button("Avançar"):
            if st.session_state.passo_atual < len(st.session_state.memoria_ia.get('passos', [])) - 1:
                st.session_state.passo_atual += 1
                play_voice(st.session_state.memoria_ia.get('passos')[st.session_state.passo_atual]['explicacao'])
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
