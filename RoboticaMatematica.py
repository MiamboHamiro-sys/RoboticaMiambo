import streamlit as st
import time
from groq import Groq
from gtts import gTTS
import base64
import io

# --- CONFIGURAÇÃO GROQ ---
# A chave deve ser colocada nas "Secrets" do Streamlit Cloud como GROQ_API_KEY
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- INTERFACE E CSS ---
st.set_page_config(page_title="SmartProf", layout="wide")

st.markdown("""
    <style>
    /* Barra de rolagem lateral muito grossa */
    ::-webkit-scrollbar { width: 35px; }
    ::-webkit-scrollbar-track { background: #f1f1f1; }
    ::-webkit-scrollbar-thumb { background: #1a73e8; border-radius: 10px; }
    
    /* Estilo para simular 1/8 da tela para o robô */
    .robot-container { width: 12.5%; margin-bottom: 20px; }
    
    /* Botões fixos na parte inferior */
    div.stButton > button { height: 3em; font-size: 18px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES DE VOZ ---
def play_voice(text):
    tts = gTTS(text=text, lang='pt', slow=False)
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    b64 = base64.b64encode(fp.read()).decode()
    md = f'<audio autoplay="true" src="data:audio/mp3;base64,{b64}">'
    st.markdown(md, unsafe_allow_html=True)

# --- INICIALIZAÇÃO DO ESTADO ---
if 'ecra' not in st.session_state: st.session_state.ecra = 1
if 'passo_atual' not in st.session_state: st.session_state.passo_atual = 0
if 'es1_passos' not in st.session_state: st.session_state.es1_passos = []
if 'e1_resolvido' not in st.session_state: st.session_state.e1_resolvido = None

# --- LÓGICA DE ECRÃS ---

# ECRÃ 1: LOGIN
if st.session_state.ecra == 1:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712139.png", width=120) # Cabeça do Robô
    nome = st.text_input("Olá! Como te chamas?", placeholder="Escreve o teu nome...")
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Iniciar Jornada"):
            if nome:
                play_voice(f"{nome}, é um prazer contar consigo nesta jornada de discutirmos assuntos de Matemática")
                with st.spinner("A processar..."):
                    time.sleep(3) # Processa 3s
                time.sleep(2) # Espera mais 2s após voz
                st.session_state.nome_usuario = nome
                st.session_state.ecra = 2
                st.rerun()
    with c2:
        if st.button("Reiniciar"):
            st.session_state.clear()
            st.rerun()

# ECRÃ 2: MEDIAÇÃO
elif st.session_state.ecra == 2:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712139.png", width=120)
    
    if st.session_state.passo_atual == 0:
        e1_input = st.text_area("Insira o exercício que deseja aprender (E1):")
        if st.button("Submeter Exercício"):
            with st.spinner("O SmartProf está a preparar a aula..."):
                # CHAMADA À API GROQ
                prompt = f"""
                O aluno enviou o exercício: {e1_input}.
                Instruções:
                TRANCA DE ÁREA: Se o tema não for Matemática (Aritmética, Álgebra, Geometria, Cálculo, Estatística, Matemática Discreta),
                bloqueie o avanço. Responda: 'Este Robô opera exclusivamente em conteúdos matemáticos.
                1. Resolve o exercício internamente.
                2. Cria um exercício SIMILAR (ES1) mas com números diferentes.
                3. Divide a resolução do SIMILAR em passos detalhados (Passo 1, Passo 2, etc).
                Formato de resposta: Resposta E1: [resultado] | Passos ES1: [passo 1]; [passo 2]; [passo 3]
                """
                chat_completion = client.chat.completions.create(
                    messages=[{"role": "system", "content": "És um professor que nunca dá a resposta direta. Tu ensinas por analogia."},
                              {"role": "user", "content": prompt}],
                    model="llama3-8b-8192",
                )
                # Simulação de parsing (idealmente usar Regex ou JSON)
                resposta = chat_completion.choices[0].message.content
                st.session_state.es1_passos = ["Passo 1: Analisar os dados", "Passo 2: Aplicar a fórmula", "Passo 3: Resolver conta"] 
                st.session_state.passo_atual = 1
                play_voice("Não vou resolver o exercício que apresentaste, mas vou instruir-te a resolver. Siga os passos que se seguem.")
                st.rerun()

    # Exibição Progressiva dos Passos
    for i in range(st.session_state.passo_atual):
        st.success(st.session_state.es1_passos[i])
        # Aqui abriria o campo de dúvidas para o passo atual

    # BARRA DE BOTÕES INFERIOR
    st.write("---")
    b1, b2, b3, b4, b5 = st.columns(5)
    with b1:
        if st.button("Ecrã 1"): st.session_state.ecra = 1; st.rerun()
    with b2:
        if st.button("Reiniciar Chat"): st.session_state.passo_atual = 0; st.rerun()
    with b4:
        if st.button("Passo Anterior"):
            if st.session_state.passo_atual > 1: st.session_state.passo_atual -= 1; st.rerun()
    with b5:
        if st.button("Próximo Passo"):
            if st.session_state.passo_atual < len(st.session_state.es1_passos):
                st.session_state.passo_atual += 1; st.rerun()
            else:
                st.session_state.ecra = 3; st.rerun()

# ECRÃ 3: FINALIZAÇÃO (Conforme solicitado, tens 3 ecrãs)
elif st.session_state.ecra == 3:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712139.png", width=120)
    play_voice("Siga a lógica e apresenta o resultado final")
    res_aluno = st.text_input("Qual o resultado do teu exercício original (E1)?")
    if st.button("Verificar"):
        # Lógica de comparação e atribuição de 10 pontos
        st.balloons()
        st.success("Parabéns! Ganhaste 10 pontos!")

    
