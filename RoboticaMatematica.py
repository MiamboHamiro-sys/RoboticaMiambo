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
    .main-content { padding-bottom: 150px; }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZAÇÃO IA ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

SYSTEM_PROMPT = """
És o "SmartProf", um software educativo de Matemática. 
REGRAS CRÍTICAS:
1. Se o input não for Matemática, responde: {"erro": "assunto_proibido"}.
2. NÃO resolvas o exercício E1 para o aluno.
3. Cria um exercício ES1 idêntico mas com valores diferentes.
4. Resolve E1 internamente e guarda APENAS o valor numérico ou simplificado no campo "resultado_e1".
5. Retorna um JSON estrito:
{
  "resultado_e1": "valor_final_de_E1_ex_3_ou_-5",
  "passos_similares": [
    {"expressao": "latex_aqui", "explicacao": "texto_didatico"}
  ]
}
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

# --- ESTADOS DA SESSÃO ---
if 'ecra' not in st.session_state: st.session_state.ecra = 1
if 'passo_atual' not in st.session_state: st.session_state.passo_atual = -1
if 'dados_ia' not in st.session_state: st.session_state.dados_ia = {}
if 'pontos' not in st.session_state: st.session_state.pontos = 0

# --- ECRÃ 1 ---
if st.session_state.ecra == 1:
    st.markdown('<div class="robot-container"><img src="https://cdn-icons-png.flaticon.com/512/4712/4712139.png" class="robot-img"></div>', unsafe_allow_html=True)
    nome = st.text_input("Introduza o seu nome:", key="user_name_input")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Submeter Nome"):
            if nome:
                st.session_state.nome = nome
                play_voice(f"{nome}, é um prazer contar consigo nesta jornada de discutirmos assuntos de Matemática")
                with st.spinner("A preparar sistema..."): time.sleep(8)
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

    # INPUT DO EXERCÍCIO
    if st.session_state.passo_atual == -1:
        e1_input = st.text_area("Apresente o seu exercício E1:")
        if st.button("Enviar para o SmartProf"):
            with st.spinner("O Robô está a analisar..."):
                try:
                    chat = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": e1_input}],
                        response_format={"type": "json_object"}
                    )
                    res = json.loads(chat.choices[0].message.content)
                    if "erro" in res:
                        st.error("Sou um especialista em Matemática, não posso avançar com outros conteúdos.")
                    else:
                        st.session_state.dados_ia = res
                        st.session_state.passo_atual = 0
                        time.sleep(2)
                        play_voice("Não vou resolver o exercício que apresentaste, mas vou instruir-te a resolver. Siga os passos que se seguem")
                        st.rerun()
                except: st.error("Erro na ligação com a IA. Tente novamente.")

    # MEDIAÇÃO POR PASSOS
    else:
        passos = st.session_state.dados_ia.get('passos_similares', [])
        for i in range(st.session_state.passo_atual + 1):
            if i < len(passos):
                st.info(f"**Passo {i+1} (Exercício Similar)**")
                st.latex(passos[i]['expressao'])
                st.write(passos[i]['explicacao'])
                
                if i == st.session_state.passo_atual:
                    duvida = st.text_input(f"Dúvida no Passo {i+1}?", key=f"dv_{i}")
                    if duvida:
                        if st.button("Explique de novo"): play_voice(passos[i]['explicacao'])

        # RESULTADO FINAL (Apenas no último passo)
        if st.session_state.passo_atual == len(passos) - 1:
            st.markdown("---")
            play_voice("Siga a lógica e apresente o resultado final")
            res_aluno = st.text_input("Qual o resultado final do teu exercício original E1?", key="res_final")
            
            if st.button("Validar Resposta"):
                with st.spinner("A comparar..."):
                    time.sleep(2)
                    # Limpeza de strings para comparação justa (remove espaços e x=)
                    correto = str(st.session_state.dados_ia.get('resultado_e1', "")).lower().replace("x=","").strip()
                    aluno = res_aluno.lower().replace("x=","").strip()
                    
                    if aluno == correto:
                        play_voice("Parabéns acertou")
                        st.balloons()
                        st.session_state.pontos += 10
                        st.success(f"Excelente! Ganhaste 10 pontos. Total: {st.session_state.pontos}")
                    else:
                        play_voice("Infelizmente não é assim, clica no Botão 2 para reiniciarmos o processo ou clica no Botão 4 para recuar a explicação")
                        st.error("Resposta incorreta. Analise o similar novamente.")

    st.markdown('</div>', unsafe_allow_html=True)

    # --- BARRA DE BOTÕES INFERIOR ---
    st.markdown('<div class="footer">', unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: 
        if st.button("🏠 Ecra 1"): st.session_state.ecra = 1; st.rerun()
    with c2:
        if st.button("🗑️ Limpar"): st.session_state.passo_atual = -1; st.rerun()
    with c3:
        if st.button("🔊 Voz"): play_voice("Estou aqui para ajudar.")
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
    
