import streamlit as st
import time
from groq import Groq
from gtts import gTTS
import base64
import io
import json
import re
import requests

# --- CONEXÃO SEGURA COM A API ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- CONFIGURAÇÃO DA INTERFACE ---
st.set_page_config(page_title="SmartProf", layout="wide")

IMAGE_URL = "https://thumbs.dreamstime.com/b/professor-de-rob%C3%B4-moderno-na-faculdade-gradua%C3%A7%C3%A3o-que-mant%C3%A9m-o-conceito-intelig%C3%AAncia-artificial-para-laptops-online-robot-pac-218181889.jpg?w=576"

def get_base64_img(url):
    try:
        response = requests.get(url)
        return base64.b64encode(response.content).decode()
    except: return ""

img_data = get_base64_img(IMAGE_URL)

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

    /* CAIXA DE TEXTO REFORMULADA */
    .stTextInput > div > div > input {{
        background-color: rgba(255, 255, 255, 0.95) !important;
        border: 4px solid #1A237E !important;
        border-radius: 20px !important;
        height: 100px !important; 
        font-size: 26px !important;
        text-align: center !important;
        color: #1A237E !important;
        padding: 0 !important; 
        line-height: 100px !important; /* Centralização vertical absoluta */
    }}

    /* Visibilidade do Placeholder */
    ::placeholder {{ 
        color: #1A237E !important; 
        opacity: 0.7 !important; 
    }}

    /* Container do Nome */
    .name-box {{
        padding: 0 10%;
    }}

    /* TABELA DE BOTÕES (LADO A LADO) */
    [data-testid="stHorizontalBlock"] {{ display: flex !important; 
        flex-direction: row !important; 
        flex-wrap: nowrap !important; 
        gap: 5px !important; margin-top: 
        20px !important; padding: 0 10% !important;
        width: 80% !important;
    }}

    .stButton > button {{
        width: 118px !important;
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

# --- ESTADO ---
if 'ecra' not in st.session_state: st.session_state.ecra = 1
if 'nome' not in st.session_state: st.session_state.nome = ""
# Estados adicionais para lógica construtivista
if 'mensagens' not in st.session_state: st.session_state.mensagens = []
if 'memoria_oculta' not in st.session_state: st.session_state.memoria_oculta = None
if 'exercicio_pendente' not in st.session_state: st.session_state.exercicio_pendente = False

# --- LÓGICA DO TUTOR ---
SYSTEM_PROMPT = """Você é o Robô ProfSmart, um tutor construtivista. 
Sua missão é ensinar, não resolver.
REGRAS:
1. NUNCA resolva o exercício original (E1) do aluno.
2. Se o aluno enviar um exercício (E1), resolva-o em sua mente (oculto), identifique o resultado final e guarde-o.
3. Crie IMEDIATAMENTE um exercício similar (ES1).
4. Mostre ao aluno apenas a resolução detalhada de ES1 em passos (Passo 1, Passo 2...).
5. Se o aluno insistir ou disser "não consigo", encoraje-o a olhar o exemplo similar.
6. Bloqueie qualquer nova questão até que o aluno responda a atual.
7. Para questões teóricas, use analogias da cultura de Moçambique (mercados, machambas, chapa, frutas locais).
8. Use LaTeX: $equação$. Sinais: $\implies$ ou $\iff$. Cada expressão em uma linha.
9. Respostas do aluno:
   - Igual ao seu resultado oculto: "Parabéns, pelo empenho" e nota 10.
   - Equivalente mas diferente: "estás num bom caminho continua, reveja os passo".
   - Errado: "Infelizmente, errou, reveja os passo".
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
        if st.button("SUBMETER", use_container_width=True):
            if st.session_state.nome:
                st.session_state.ecra = 2
                st.rerun()
    
    with col2:
        if st.button("LIMPAR", use_container_width=True):
            st.session_state.nome = ""
            st.rerun()

# --- ECRÃ 2: INTERAÇÃO (PROFESSOR SMART) ---
elif st.session_state.ecra == 2:
    st.markdown('<style>[data-testid="stAppViewContainer"] { background-image: none !important; background-color: #F8F9FA !important; }</style>', unsafe_allow_html=True)
    
    # Topo Fixo conforme solicitado
    st.markdown(f"<h2 style='text-align:center; color:#1A237E;'>Bem-vindo(a)! Sou o {st.session_state.nome}! Sou o Robô ProfSmart.</h2>", unsafe_allow_html=True)
    
    # Botão que Reinicia a conversa (Limpa tudo)
    if st.button("🔄 Reiniciar e Limpar Tudo"):
        st.session_state.mensagens = []
        st.session_state.memoria_oculta = None
        st.session_state.exercicio_pendente = False
        st.rerun()

    # Área do Chat
    for message in st.session_state.mensagens:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Apresente sua questão ou exercício..."):
        
        # Bloqueio: Não avança sem resposta da anterior
        if st.session_state.exercicio_pendente and "resultado" not in prompt.lower() and not any(char.isdigit() for char in prompt):
            st.warning("Apresenta a resposta da questão anterior ou reinicie")
        else:
            st.session_state.mensagens.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                # Lógica Construtivista via API
                response = client.chat.completions.create(
                    model="llama3-8b-8192",
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "assistant", "content": f"Memória atual: {st.session_state.memoria_oculta}"},
                        *st.session_state.mensagens
                    ]
                )
                
                full_response = response.choices[0].message.content
                
                # Simulação simples de extração de memória (idealmente usar JSON na API)
                if "resultado final guardado" in full_response.lower() or st.session_state.memoria_oculta is None:
                     st.session_state.exercicio_pendente = True
                
                st.markdown(full_response)
                st.session_state.mensagens.append({"role": "assistant", "content": full_response})
                
                # Feedback de voz
                tts = gTTS(text=full_response[:200], lang='pt') # Limitado para velocidade
                audio_io = io.BytesIO()
                tts.write_to_fp(audio_io)
                b64_audio = base64.b64encode(audio_io.getvalue()).decode()
                st.markdown(f'<audio src="data:audio/mp3;base64,{b64_audio}" autoplay></audio>', unsafe_allow_html=True)

    if st.sidebar.button("Voltar ao Início"):
        st.session_state.ecra = 1
        st.rerun()

