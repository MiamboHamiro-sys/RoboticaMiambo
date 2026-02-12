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

# --- CSS AVANÇADO (ORIGINAL MANTIDO) ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');

    [data-testid="stAppViewContainer"] {{
        background-image: url("data:image/png;base64,{img_data}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}

    [data-testid="stHeader"] {{ display: none !important; }}

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

    .stTextInput > div > div > input {{
        background-color: rgba(255, 255, 255, 0.95) !important;
        border: 4px solid #1A237E !important;
        border-radius: 20px !important;
        height: 100px !important; 
        font-size: 26px !important;
        text-align: center !important;
        color: #1A237E !important;
        padding: 0 !important; 
        line-height: 100px !important;
    }}

    ::placeholder {{ 
        color: #1A237E !important; 
        opacity: 0.7 !important; 
    }}

    .name-box {{
        padding: 0 10%;
    }}

    [data-testid="stHorizontalBlock"] {{ display: flex !important;
        flex-direction: row !important; 
        flex-wrap: nowrap !important; 
        gap: 5px !important; margin-top: 
        20px !important; padding: 0 10% !important;
        width: 80% !important;
    }}

    .stButton > button {{
        width: 100% !important;
        height: 40px !important;
        background-color: white !important;
        border: 4px solid #1A237E !important;
        border-radius: 15px !important;
        color: #1A237E !important;
        font-weight: bold !important;
        font-size: 18px !important;
        box-shadow: 0 6px 12px rgba(0,0,0,0.2);
    }}
    
    .stButton > button:active {{ transform: scale(0.95); background-color: #1A237E !important; color: white !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- ESTADO DO SISTEMA ---
if 'ecra' not in st.session_state: st.session_state.ecra = 1
if 'nome' not in st.session_state: st.session_state.nome = ""
if 'mensagens' not in st.session_state: st.session_state.mensagens = []
if 'memoria_oculta' not in st.session_state: st.session_state.memoria_oculta = ""
if 'exercicio_ativo' not in st.session_state: st.session_state.exercicio_ativo = False

SYSTEM_PROMPT = """Você é o Robô ProfSmart, um tutor baseado no construtivismo. 
MISSÃO: Ensinar o aluno a partir de exercícios similares. NUNCA dê a resolução do exercício original (E1) do aluno.

REGRAS:
1. Quando receber um exercício (E1), resolva-o ocultamente e guarde o resultado final na sua memória.
2. Não mostre a resolução de E1 ao aluno, sob nenhuma circunstância.
3. Gere um exercício similar (ES1) e resolva-o detalhadamente em passos (Passo 1, Passo 2...).
4. Se o aluno acertar o resultado de E1, diga: "Parabéns, pelo empenho" e dê nota 10.
5. Se o resultado for equivalente mas incompleto: "estás num bom caminho continua, reveja os passo".
6. Se o resultado for errado: "Infelizmente, errou, reveja os passo".
7. Questões teóricas: Use analogias da cultura moçambicana (machamba, chapa, mercados, locais). Avalie com % (se < 95%, peça para melhorar).
8. Matemática: Use LaTeX entre $ $ em linhas únicas. Use $\implies$ ou $\iff$.
9. Não avance para nova questão até o aluno terminar a atual ou reiniciar.
"""

# --- ECRÃ 1: IDENTIFICAÇÃO ---
if st.session_state.ecra == 1:
    st.markdown("""
        <div class="instrucao-container">
            <div class="legenda-texto">Clica e escreva teu nome</div>
            <div class="seta">↓</div>
        </div>
    """, unsafe_allow_html=True)

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
    # Reset Estilo Chat
    st.markdown('<style>[data-testid="stAppViewContainer"] { background-image: none !important; background-color: white !important; }</style>', unsafe_allow_html=True)
    
    # Topo Fixo
    st.markdown(f"<h2 style='text-align:center; color:#1A237E;'>Bem-vindo(a)! Sou o {st.session_state.nome}! Sou o Robô ProfSmart.</h2>", unsafe_allow_html=True)
    
    # Botão Reiniciar conversa
    if st.button("🔄 Reiniciar Conversa (Limpar Tudo)"):
        st.session_state.mensagens = []
        st.session_state.memoria_oculta = ""
        st.session_state.exercicio_ativo = False
        st.rerun()

    # Histórico do Chat
    for m in st.session_state.mensagens:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    # Input do Aluno
    if prompt := st.chat_input("Insira seu exercício ou resposta..."):
        
        # Bloqueio Construtivista
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
                    
                    # Logica de detecção de novo exercício
                    if "Passo 1" in resposta:
                        st.session_state.exercicio_ativo = True
                    
                    st.markdown(resposta)
                    st.session_state.mensagens.append({"role": "assistant", "content": resposta})
                    
                    # Voz (gTTS)
                    tts = gTTS(text=re.sub(r'[*$]', '', resposta[:250]), lang='pt')
                    b = io.BytesIO()
                    tts.write_to_fp(b)
                    st.markdown(f'<audio src="data:audio/mp3;base64,{base64.b64encode(b.getvalue()).decode()}" autoplay></audio>', unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error("Erro na comunicação com o cérebro do robô.")
