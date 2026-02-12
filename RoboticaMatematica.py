import streamlit as st
import time
from groq import Groq
from gtts import gTTS
import base64
import io
import json
import re
import requests

# --- CONFIGURAÇÃO DA INTERFACE ---
st.set_page_config(page_title="SmartProf", layout="wide")

IMAGE_URL = "https://thumbs.dreamstime.com/b/professor-de-rob%C3%B4-moderno-na-faculdade-gradua%C3%A7%C3%A3o-que-mant%C3%A9m-o-conceito-intelig%C3%AAncia-artificial-para-laptops-online-robot-pac-218181889.jpg?w=576"

def get_base64_img(url):
    try:
        response = requests.get(url)
        return base64.b64encode(response.content).decode()
    except: return ""

img_data = get_base64_img(IMAGE_URL)

# --- CONEXÃO API (USANDO SECRETS) ---
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("Erro na Chave API. Verifique os Secrets do Streamlit.")

# --- CSS AVANÇADO ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');

    /* Fundo Estável */
    [data-testid="stAppViewContainer"] {{
        background-image: url("data:image/png;base64,{img_data}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}

    [data-testid="stHeader"] {{ display: none !important; }}

    /* BARRA DE ROLAGEM MUITO GROSSA E EFICIENTE */
    ::-webkit-scrollbar {{
        width: 30px !important;
        height: 30px !important;
    }}
    ::-webkit-scrollbar-track {{
        background: rgba(255, 255, 255, 0.2) !important;
    }}
    ::-webkit-scrollbar-thumb {{
        background: #1A237E !important;
        border-radius: 10px !important;
        border: 5px solid white !important;
    }}

    /* LEGENDA E SETA */
    .instrucao-container {{
        text-align: center;
        margin-top: 15vh;
        margin-bottom: 10px;
    }}
    
    .legenda-texto {{
        background-color: rgba(255, 255, 255, 0.8);
        color: #1A237E;
        padding: 12px 25px;
        border-radius: 15px;
        font-weight: bold;
        font-size: 20px;
        display: inline-block;
        border: 2px solid #1A237E;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }}

    .seta {{
        font-size: 35px;
        color: #1A237E;
        display: block;
        margin-top: 5px;
        font-weight: bold;
        animation: bounce 2s infinite;
    }}

    @keyframes bounce {{
        0%, 20%, 50%, 80%, 100% {{transform: translateY(0);}}
        40% {{transform: translateY(-10px);}}
        60% {{transform: translateY(-5px);}}
    }}

    /* CAIXA DE TEXTO */
    .stTextInput > div > div > input {{
        background-color: rgba(255, 255, 255, 0.95) !important;
        border: 4px solid #1A237E !important;
        border-radius: 20px !important;
        height: 100px !important; 
        font-size: 26px !important;
        text-align: center !important;
        color: #1A237E !important;
        line-height: 100px !important;
    }}

    /* BOTÕES */
    .stButton > button {{
        width: 100% !important;
        height: 45px !important;
        background-color: white !important;
        border: 4px solid #1A237E !important;
        border-radius: 15px !important;
        color: #1A237E !important;
        font-weight: bold !important;
        font-size: 18px !important;
        box-shadow: 0 6px 12px rgba(0,0,0,0.2);
    }}
    
    .stButton > button:active {{ transform: scale(0.95); background-color: #1A237E !important; color: white !important; }}

    /* Posicionamento do Botão de Reiniciar na parte inferior */
    .footer-button {{
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 250px;
        z-index: 1000;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- ESTADO DO SISTEMA ---
if 'ecra' not in st.session_state: st.session_state.ecra = 1
if 'nome' not in st.session_state: st.session_state.nome = ""
if 'mensagens' not in st.session_state: st.session_state.mensagens = []
if 'exercicio_ativo' not in st.session_state: st.session_state.exercicio_ativo = False

SYSTEM_PROMPT = """Você é o Robô ProfSmart, um tutor baseado no construtivismo. 
MISSÃO: Ensinar o aluno a partir de exercícios similares. NUNCA dê a resolução do exercício original (E1) do aluno.

REGRAS CRÍTICAS:
1. Ao receber E1, resolva ocultamente. Guarde o resultado.
2. Gere um exercício SIMILAR (ES1) e resolva-o detalhadamente em passos (Passo 1, Passo 2...).
3. Se o aluno acertar E1: "Parabéns, pelo empenho" e nota 10.
4. Se estiver quase lá: "estás num bom caminho continua, reveja os passo".
5. Se errar: "Infelizmente, errou, reveja os passo".
6. Questões teóricas: Use analogias de Moçambique (machamba, chapa, mercados). Avalie com % (inferior a 95% pede melhoria).
7. Matemática: Use LaTeX entre $ $ em linhas únicas. Use sinais $\implies$ ou $\iff$.
8. Bloqueie novas questões até finalizar a atual ou reiniciar.
"""

# --- ECRÃ 1: IDENTIFICAÇÃO ---
if st.session_state.ecra == 1:
    st.markdown('<div class="instrucao-container"><div class="legenda-texto">Clica e escreva teu nome</div><div class="seta">↓</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="name-box">', unsafe_allow_html=True)
    nome = st.text_input("", value=st.session_state.nome, placeholder="Escreve o teu nome aqui", label_visibility="collapsed")
    st.session_state.nome = nome
    st.markdown('</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("SUBMETER"):
            if st.session_state.nome:
                st.session_state.ecra = 2
                st.rerun()
    with col2:
        if st.button("LIMPAR"):
            st.session_state.nome = ""
            st.rerun()

# --- ECRÃ 2: INTERAÇÃO ---
elif st.session_state.ecra == 2:
    st.markdown('<style>[data-testid="stAppViewContainer"] { background-image: none !important; background-color: white !important; }</style>', unsafe_allow_html=True)
    
    st.markdown(f"<h2 style='text-align:center; color:#1A237E;'>Bem-vindo(a)! Sou o {st.session_state.nome}! Sou o Robô ProfSmart.</h2>", unsafe_allow_html=True)
    
    # Histórico de Chat
    for m in st.session_state.mensagens:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    # Input do Aluno
    if prompt := st.chat_input("Insira seu exercício ou resposta..."):
        if st.session_state.exercicio_ativo and "resultado" not in prompt.lower() and not any(c.isdigit() for c in prompt):
             st.warning("Apresenta a resposta da questão anterior ou reinicie")
        else:
            st.session_state.mensagens.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                try:
                    res = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "system", "content": SYSTEM_PROMPT}] + st.session_state.mensagens
                    )
                    resposta = res.choices[0].message.content
                    if "Passo 1" in resposta: st.session_state.exercicio_ativo = True
                    
                    st.markdown(resposta)
                    st.session_state.mensagens.append({"role": "assistant", "content": resposta})
                    
                    # Áudio
                    tts = gTTS(text=re.sub(r'[*$]', '', resposta[:250]), lang='pt')
                    b = io.BytesIO()
                    tts.write_to_fp(b)
                    st.markdown(f'<audio src="data:audio/mp3;base64,{base64.b64encode(b.getvalue()).decode()}" autoplay></audio>', unsafe_allow_html=True)
                except Exception as e:
                    st.error("Erro na comunicação com a IA.")

    # Botão de Reiniciar na parte Inferior (usando colunas para empurrar para baixo se necessário)
    st.markdown('<div style="margin-top: 100px;"></div>', unsafe_allow_html=True)
    if st.button("🔄 Reiniciar Conversa (Limpar Tudo)"):
        st.session_state.mensagens = []
        st.session_state.exercicio_ativo = False
        st.rerun()
