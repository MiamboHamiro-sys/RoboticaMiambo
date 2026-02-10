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
    ::-webkit-scrollbar { width: 55px; }
    ::-webkit-scrollbar-track { background: #f1f1f1; }
    ::-webkit-scrollbar-thumb { background: #007bff; border: 4px solid white; }
    .robot-container { display: flex; justify-content: center; width: 100%; padding: 10px; }
    .robot-img { width: 12.5%; min-width: 120px; }
    .footer { position: fixed; bottom: 0; left: 0; width: 100%; background: white; padding: 15px; border-top: 3px solid #007bff; z-index: 1000; }
    div.stButton > button { width: 100%; height: 65px; font-weight: bold; font-size: 18px; border-radius: 10px; }
    .main-content { padding-bottom: 160px; }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZAÇÃO IA ---
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    st.error("Erro fatal: Verifique a GROQ_API_KEY nas Secrets do Streamlit.")

# PROMPT INVIOLÁVEL E REGRAS DE JSON
SYSTEM_PROMPT = """
És o "SmartProf", um robô software de Matemática.
REGRAS:
1. Responde APENAS em formato JSON. Não escrevas texto fora do JSON.
2. Se o input não for Matemática, retorna: {"erro": "não_matematica"}.
3. Resolve o exercício E1 do aluno internamente e guarda o valor simplificado em "resultado_e1".
4. Cria um exercício ES1 similar e divide em passos.
FORMATO OBRIGATÓRIO:
{"resultado_e1": "valor", "passos_similares": [{"expressao": "latex", "explicacao": "texto"}]}
"""

def play_voice(text):
    if text:
        try:
            clean_text = re.sub(r'[\$\{\}\\]', '', text).replace('*', ' vezes ')
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
if 'dados_ia' not in st.session_state: st.session_state.dados_ia = {}
if 'nome' not in st.session_state: st.session_state.nome = ""

# --- ECRÃ 1 ---
if st.session_state.ecra == 1:
    st.markdown('<div class="robot-container"><img src="https://cdn-icons-png.flaticon.com/512/4712/4712139.png" class="robot-img"></div>', unsafe_allow_html=True)
    nome = st.text_input("Introduza o seu nome:", key="name_input")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Submeter Nome"):
            if nome:
                st.session_state.nome = nome
                play_voice(f"{nome}, é um prazer contar consigo nesta jornada de discutirmos assuntos de Matemática")
                with st.spinner("Sincronizando voz..."): time.sleep(8)
                st.session_state.ecra = 2
                st.rerun()
    with col2:
        if st.button("Reiniciar Tudo"):
            st.session_state.clear()
            st.rerun()

# --- ECRÃ 2 ---
elif st.session_state.ecra == 2:
    st.markdown('<div class="robot-container"><img src="https://cdn-icons-png.flaticon.com/512/4712/4712139.png" class="robot-img"></div>', unsafe_allow_html=True)
    st.markdown('<div class="main-content">', unsafe_allow_html=True)

    if st.session_state.passo_atual == -1:
        e1_input = st.text_area("Insira o seu exercício E1 (ex: x^2-9=0):")
        if st.button("Enviar Exercício"):
            with st.spinner("SmartProf a pensar..."):
                try:
                    chat = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": e1_input}],
                        response_format={"type": "json_object"}
                    )
                    # Tratamento robusto do JSON
                    res_raw = chat.choices[0].message.content
                    res = json.loads(res_raw)
                    
                    if res.get("erro"):
                        st.error("Sou um especialista em Matemática. Conteúdo bloqueado.")
                    else:
                        st.session_state.dados_ia = res
                        st.session_state.passo_atual = 0
                        time.sleep(2)
                        play_voice("Não vou resolver o exercício que apresentaste, mas vou instruir-te a resolver siga os passos que se seguem")
                        st.rerun()
                except Exception as e:
                    st.error(f"Erro de processamento: Tente descrever o exercício de outra forma.")

    else:
        # Exibição dos passos sem apagar
        passos = st.session_state.dados_ia.get('passos_similares', [])
        for i in range(st.session_state.passo_atual + 1):
            if i < len(passos):
                st.info(f"**Passo {i+1}**")
                st.latex(passos[i]['expressao'])
                st.write(passos[i]['explicacao'])
                
                if i == st.session_state.passo_atual:
                    duvida = st.text_input("Dúvida neste passo?", key=f"dv_{i}")
                    if duvida:
                        if st.button("Explique de novo"): play_voice(passos[i]['explicacao'])

        # Validação Final
        if st.session_state.passo_atual == len(passos) - 1:
            st.markdown("---")
            play_voice("siga a lógica e apresenta o resultado final")
            res_aluno = st.text_input("Apresenta o resultado de E1:", key="final_res")
            
            if st.button("Validar Resposta"):
                with st.spinner("Validando..."):
                    # Comparação numérica e de texto flexível
                    correto = str(st.session_state.dados_ia.get('resultado_e1', "")).lower().replace(" ","")
                    aluno = res_aluno.lower().replace(" ","")
                    
                    # Remove "x=" caso o aluno escreva
                    correto = correto.split('=')[-1]
                    aluno = aluno.split('=')[-1]

                    if aluno == correto:
                        play_voice("parabéns acertou")
                        st.balloons()
                        st.success("Nota: 10 Pontos!")
                    else:
                        play_voice("Infelizmente não é assim, clica no Botão 2 para reiniciarmos o processo ou clica no Botão 4 para recuar a explicação")
                        st.error("Resposta incorreta.")

    st.markdown('</div>', unsafe_allow_html=True)

    # --- BARRA DE BOTÕES ---
    st.markdown('<div class="footer">', unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: 
        if st.button("🏠 Ecra 1"): st.session_state.ecra = 1; st.rerun()
    with c2:
        if st.button("🗑️ Limpar"): st.session_state.passo_atual = -1; st.rerun()
    with c3: st.button("Ajuda")
    with c4:
        if st.button("◀ Recuar"):
            if st.session_state.passo_atual > 0: st.session_state.passo_atual -= 1; st.rerun()
    with c5:
        if st.button("▶ Próximo"):
            p_lista = st.session_state.dados_ia.get('passos_similares', [])
            if st.session_state.passo_atual < len(p_lista) - 1:
                st.session_state.passo_atual += 1
                play_voice(p_lista[st.session_state.passo_atual]['explicacao'])
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
