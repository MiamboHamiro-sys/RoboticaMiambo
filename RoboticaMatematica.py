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
        bottom: 0; left: 0; width: 100%;
        background-color: white; padding: 15px;
        border-top: 3px solid #007bff; z-index: 9999;
    }
    
    .content-area { padding-bottom: 220px; }
    
    div.stButton > button {
        width: 100%; height: 60px;
        font-weight: bold; font-size: 14px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- IA ---
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Configure a GROQ_API_KEY no painel do Streamlit.")

SYSTEM_PROMPT = """
És o SmartProf. Atua APENAS em Matemática.
REGRAS:
1. NUNCA resolvas E1.
2. Cria um ES1 (exercício similar) com valores diferentes.
3. Resolve E1 internamente e guarda o valor em 'resultado_e1'.
4. Retorna APENAS o JSON. Não fales nada fora do JSON.
JSON FORMAT:
{
  "resultado_e1": "valor",
  "passos_es1": [{"math": "latex", "txt": "explicação"}]
}
"""

def falar(texto):
    if texto:
        try:
            # Limpa símbolos matemáticos para a voz soar natural
            limpo = re.sub(r'[\$\{\}\\]', '', texto).replace('*', ' vezes ').replace('^2', ' ao quadrado')
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
            with st.spinner("O SmartProf está a analisar..."):
                try:
                    res = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": e1_input}],
                        response_format={"type": "json_object"}
                    )
                    # Tentativa de carregar o JSON
                    conteudo = res.choices[0].message.content
                    st.session_state.memoria = json.loads(conteudo)
                    st.session_state.passo = 0
                    time.sleep(2)
                    falar("Não vou resolver o exercício que apresentaste, mas vou instruir-te a resolver siga os passos que se seguem")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro na ligação: Certifique-se que o conteúdo é matemática. Detalhe: {str(e)}")
    else:
        passos = st.session_state.memoria.get('passos_es1', [])
        for i in range(st.session_state.passo + 1):
            if i < len(passos):
                st.subheader(f"Passo {i+1} (Similiar)")
                st.latex(passos[i]['math'])
                st.write(passos[i]['txt'])
                
                if i == st.session_state.passo:
                    duv = st.text_input(f"Dúvida no Passo {i+1}?", key=f"d{i}")
                    if duv:
                        if st.button("ESCLARECER", key=f"b{i}"):
                            with st.spinner("A gerar explicação clara..."):
                                prompt_d = f"Explica com muita clareza este passo: {passos[i]['txt']}. O aluno tem esta dúvida: {duv}. Responde em JSON: {{'resp': 'texto'}}"
                                r_d = client.chat.completions.create(
                                    model="llama-3.3-70b-versatile",
                                    messages=[{"role": "user", "content": prompt_d}],
                                    response_format={"type": "json_object"}
                                )
                                expl = json.loads(r_d.choices[0].message.content)['resp']
                                falar(expl)
                                st.info(expl)

        if st.session_state.passo == len(passos) - 1:
            st.markdown("---")
            falar("siga a lógica e apresenta o resultado final")
            res_aluno = st.text_input("Apresenta o resultado final de E1:")
            if st.button("VALIDAR"):
                correto = str(st.session_state.memoria.get('resultado_e1', "")).lower().replace(" ","").replace("x=","")
                aluno = res_aluno.lower().replace(" ","").replace("x=","")
                if aluno == correto:
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
        if st.button("LIMPAR"): st.session_state.passo = -1; st.rerun()
    with b3:
        if st.button("REPETIR"): 
            if st.session_state.passo >= 0: falar(st.session_state.memoria['passos_es1'][st.session_state.passo]['txt'])
    with b4:
        if st.button("RECUAR"):
            if st.session_state.passo > 0: st.session_state.passo -= 1; st.rerun()
    with b5:
        if st.button("PRÓXIMO"):
            if st.session_state.passo < len(passos) - 1:
                st.session_state.passo += 1
                falar(passos[st.session_state.passo]['txt'])
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

