import streamlit as st
import time
from groq import Groq
from gtts import gTTS
import base64
import io
import json

# --- CONFIGURAÇÃO DA INTERFACE ---
st.set_page_config(page_title="SmartProf", layout="wide")

# CSS: Barra de rolagem grossa, imagem 1/8 e botões inferiores
st.markdown("""
    <style>
    ::-webkit-scrollbar { width: 45px; }
    ::-webkit-scrollbar-track { background: #f1f1f1; }
    ::-webkit-scrollbar-thumb { background: #007bff; border-radius: 5px; }
    .robot-img { width: 12.5%; display: block; margin-left: auto; margin-right: auto; }
    .footer-buttons { position: fixed; bottom: 0; left: 0; width: 100%; background: white; padding: 10px; z-index: 100; border-top: 2px solid #eee; }
    div.stButton > button { width: 100%; height: 60px; font-weight: bold; font-size: 16px; }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZAÇÃO DA IA ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# Prompt Inviolável (System Message)
SYSTEM_PROMPT = """
Sê o "SmartProf", um robô software professor de Matemática.
REGRAS INVIOLÁVEIS:
1. ATUAÇÃO: Responde APENAS sobre Matemática. Se o aluno falar sobre outros temas, diz "Sou um especialista em Matemática, não posso ajudar com esse assunto" e trava a conversa.
2. NÃO RESOLVER: Nunca dês a resolução do exercício original (E1) do aluno.
3. ANALOGIA: Cria um exercício ES1 100% similar em estrutura mas com valores diferentes.
4. DIDÁTICA: Divide a explicação de ES1 em passos (Passo 1, Passo 2... Passo n).
5. FORMATO: Deves retornar SEMPRE um JSON válido com: {"resultado_e1": "valor", "passos": [{"expressao": "...", "explicacao": "..."}, ...]}
"""

# --- FUNÇÕES DE VOZ ---
def play_voice(text):
    if text:
        tts = gTTS(text=text, lang='pt', slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        b64 = base64.b64encode(fp.read()).decode()
        md = f'<audio autoplay="true" src="data:audio/mp3;base64,{b64}">'
        st.markdown(md, unsafe_allow_html=True)

# --- CONTROLO DE ESTADO ---
if 'ecra' not in st.session_state: st.session_state.ecra = 1
if 'nome' not in st.session_state: st.session_state.nome = ""
if 'passo_atual' not in st.session_state: st.session_state.passo_atual = -1 # -1 significa aguardando E1
if 'memoria_ia' not in st.session_state: st.session_state.memoria_ia = {}
if 'chat_historico' not in st.session_state: st.session_state.chat_historico = []

# --- ECRÃ 1: BOAS-VINDAS ---
if st.session_state.ecra == 1:
    st.markdown('<img src="https://cdn-icons-png.flaticon.com/512/4712/4712139.png" class="robot-img">', unsafe_allow_html=True)
    nome_input = st.text_input("Insira o seu nome:", value=st.session_state.nome)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Submeter Nome"):
            if nome_input:
                st.session_state.nome = nome_input
                play_voice(f"{nome_input}, é um prazer contar consigo nesta jornada de discutirmos assuntos de Matemática")
                with st.spinner("Processando..."):
                    time.sleep(3)
                time.sleep(2) # Pausa para concluir voz
                st.session_state.ecra = 2
                st.rerun()
    with col2:
        if st.button("Reiniciar"):
            st.session_state.clear()
            st.rerun()

# --- ECRÃ 2: MEDIAÇÃO ---
elif st.session_state.ecra == 2:
    st.markdown('<img src="https://cdn-icons-png.flaticon.com/512/4712/4712139.png" class="robot-img">', unsafe_allow_html=True)
    
    # Área de Exercício inicial
    if st.session_state.passo_atual == -1:
        e1_input = st.text_area("Apresente o seu exercício de Matemática (E1):")
        if st.button("Submeter Exercício"):
            with st.spinner("Analisando..."):
                try:
                    completion = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "system", "content": SYSTEM_PROMPT},
                                  {"role": "user", "content": e1_input}],
                        response_format={"type": "json_object"}
                    )
                    res = json.loads(completion.choices[0].message.content)
                    st.session_state.memoria_ia = res
                    st.session_state.passo_atual = 0
                    time.sleep(2)
                    play_voice("Não vou resolver o exercício que apresentaste, mas vou instruir-te a resolver. Siga os passos que se seguem")
                    st.rerun()
                except Exception as e:
                    st.error("Erro: Certifica-te que o conteúdo é Matemática.")

    # Exibição dos Passos (Não apaga os anteriores)
    if st.session_state.passo_atual >= 0:
        passos = st.session_state.memoria_ia.get('passos', [])
        for i in range(st.session_state.passo_atual + 1):
            if i < len(passos):
                p = passos[i]
                st.markdown(f"### Passo {i+1}")
                st.latex(p['expressao'])
                st.write(p['explicacao'])
                
        # Dúvida sobre o passo atual
        duvida = st.text_input(f"Dúvida sobre o Passo {st.session_state.passo_atual + 1}?", key=f"duvida_{st.session_state.passo_atual}")
        if duvida:
            if st.button("Explicar Dúvida"):
                play_voice(f"Vou explicar novamente: {passos[st.session_state.passo_atual]['explicacao']}")

    # BOTÕES INFERIORES FIXOS
    st.markdown('<div class="footer-buttons">', unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        if st.button("🏠 Ecra 1"): st.session_state.ecra = 1; st.rerun()
    with c2:
        if st.button("🗑️ Reiniciar"): st.session_state.passo_atual = -1; st.rerun()
    with c3:
        st.button("Recuar Expl.") # Visual
    with c4:
        if st.button("◀ Passo Ant."):
            if st.session_state.passo_atual > 0:
                st.session_state.passo_atual -= 1; st.rerun()
    with c5:
        if st.button("▶ Próximo"):
            if st.session_state.passo_atual < len(st.session_state.memoria_ia.get('passos', [])) - 1:
                st.session_state.passo_atual += 1; st.rerun()
            else:
                st.session_state.ecra = 3; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- ECRÃ 3: RESULTADO FINAL ---
elif st.session_state.ecra == 3:
    st.markdown('<img src="https://cdn-icons-png.flaticon.com/512/4712/4712139.png" class="robot-img">', unsafe_allow_html=True)
    play_voice("Siga a lógica e apresenta o resultado final")
    
    res_aluno = st.text_input("Insira o resultado obtido para o exercício E1:")
    if st.button("Validar Resultado"):
        with st.spinner("Analisando resultado..."):
            time.sleep(2)
            res_correto = str(st.session_state.memoria_ia.get('resultado_e1'))
            if res_aluno.strip() == res_correto.strip():
                play_voice("Parabéns acertou! Ganhou 10 pontos")
                st.balloons()
                st.success("Nota: 10 Pontos!")
            else:
                play_voice("Infelizmente não é assim, clica no Botão 2 para reiniciarmos o processo ou clica no botão 4 para recuar a explicação")
                st.error("Resultado Incorreto.")
    
    if st.button("Voltar para Mediação"):
        st.session_state.ecra = 2; st.rerun()
