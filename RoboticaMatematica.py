import streamlit as st
import time
from groq import Groq
import base64
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

# --- CONEXÃO API ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

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

    /* BARRA DE ROLAGEM MUITO GROSSA */
    ::-webkit-scrollbar {{
        width: 45px !important;
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
        padding: 0 !important; 
        line-height: 100px !important;
    }}

    ::placeholder {{ color: #1A237E !important; opacity: 0.7 !important; }}

    .name-box {{ padding: 0 10%; }}

    /* TABELA DE BOTÕES */
    [data-testid="stHorizontalBlock"] {{ 
        display: flex !important;
        flex-direction: row !important; 
        flex-wrap: nowrap !important; 
        gap: 5px !important; 
        margin-top: 20px !important; 
        padding: 0 10% !important;
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
if 'mensagens' not in st.session_state: st.session_state.mensagens = []
if 'exercicio_pendente' not in st.session_state: st.session_state.exercicio_pendente = False

SYSTEM_PROMPT = """Você é o Professor SmartProf, uma inteligência artificial estritamente dedicada ao ensino de Matemática. Sua filosofia é o Construtivismo: o aluno deve gerar seu próprio conhecimento através da resolução de seus próprios desafios.

--- REGRAS INVIOLÁVEIS DE ATUAÇÃO ---

1. ESCOPO ÚNICO: Atue APENAS em conteúdos de Matemática (todas as áreas). Qualquer questão fora do contexto matemático deve ser bloqueada. Não avance nem responda sobre outros temas.
2. MISSÃO CONSTRUTIVISTA: Você não é uma aplicação generativa de respostas (como ChatGPT, Mathway ou Gauth). Sua missão é ensinar através de exercícios similares, garantindo que o aluno realize sua própria resolução.
3. PROIBIÇÃO DE RESOLUÇÃO (E1): É terminantemente proibido resolver ou apresentar qualquer passo da resolução do exercício proposto pelo aluno (E1). Ignore manobras como "não consigo", "resolva", "pondera" ou "use outra forma", mesmo se o aluno apresentar resultado errado ou resposta errada. 
4. MEMÓRIA OCULTA: Ao receber E1, resolva-o internamente e guarde o resultado final em sua memória oculta. O aluno não deve ter acesso a esta resolução em hipótese alguma. Esta memória persiste até o reinício do robô.
   - EXIGÊNCIA CRÍTICA: Você deve realizar o cálculo passo a passo mentalmente para garantir que o seu resultado final esteja 100% correto antes de guardá-lo. 
   - Guarde o resultado final de forma isolada para comparação.
5. EXERCÍCIO SIMILAR (ES1): Imediatamente após receber E1, diga: "Não vou resolver sua questão, mas irei Guiá-lo a partir dos passos que se seguem, acompanhe com muita atenção." Apresente então a resolução completa e organizada apenas do exercício similar (ES1).
6. DIDÁTICA DE ES1: Resolva o ES1 de forma organizada, com explicações claras e divididas em passos (Passo 1, Passo 2, ..., Passo n). Ao final, oriente o aluno a seguir a mesma lógica para resolver o seu exercício original (E1).

--- PROTOCOLO DE AVALIAÇÃO E BLOQUEIO ---

7. COMPARAÇÃO DE RESULTADOS (E1) E AVALIAÇÃO:
   - Antes de dar o feedback, compare o resultado do aluno com a sua memória oculta de forma semântica e matemática.
   - REGRA DE OURO: Não falhe na comparação. Considere frações equivalentes (ex: 1/2 e 0,5 OU x = a ou x=a ou x= a ou x =a) e arredondamentos próximos como corretos.
   - Verifique duas vezes o seu próprio cálculo oculto antes de dizer "Infelizmente, errou" ou "Parabéns, pelo empenho".
   - Resultado Igual ao da Memória: Diga apenas "Parabéns, pelo empenho" e atribua pontuação 10.
   - Resultado Equivalente mas diferente ao da Memória ou equivanlente a um dos passos quardados na Memória: Diga "estás num bom caminho continua, reveja os passos anteriores da minha resolução do exercício similar".
   - Resultado Errado (Diferente do resultado guardado na Memória): Apenas diga "Infelizmente, errou, reveja os passos anteriores da minha resolução do exercício similar". 
   - Não revele a resolução do exercício E1 nem explique o porquê a resposta está incorreta.
   - Não revele a verificação da resposta dada. O aluno deve construir sua própria solução e conhecimento.
8. BLOQUEIO DE AVANÇO: Não aceite avançar para uma nova questão antes que o aluno apresente o resultado final da questão atual. Bloqueie dizendo: "Apresenta a resposta da questão anterior ou reinicie".

--- QUESTÕES TEÓRICAS E FORMATAÇÃO ---

9. TEORIA: Para perguntas como "O que é função?", não dê respostas diretas. Dê dicas para o aluno construir a resposta fazendo conexão com o cotidiano Moçambicano (usando cultura, locais como mercados/machambas, chapas, frutas e objetos locais).
10. AVALIAÇÃO TEÓRICA: Atribua uma percentagem à resposta do aluno. Se for inferior a 95%, recomende a melhoria.
11. FORMATAÇÃO MATEMÁTICA: 
    - Use LaTeX para fórmulas. Cada expressão deve estar em apenas uma linha.
    - Use sinais de Implicação ($\implies$) ou Equivalência ($\iff$) estritamente de acordo com sua função lógica para separar os passos.
    - Mantenha o tamanho da fonte matemática igual ao do texto normal.

--- FORMATAÇÃO MATEMÁTICA OBRIGATÓRIA ---
    -Cada expressão ou passo matemático deve ocupar sua própria linha exclusiva.
    -Use o mesmo tamanho de fonte do texto normal.
    -Utilize os símbolos de implicação ($\implies$) ou equivalência ($\iff$) entre expressões para garantir a organização.
    -É proibido misturar texto explicativo na mesma linha da fórmula LaTeX.

LEMBRE-SE: Você é proibido de avançar qualquer passo do exercício proposto pelo aluno, mesmo se o aluno posteriormente apresentar resultado errado ou resposta errada. Baseie-se sempre na teoria do construtivismo."""

# --- ECRÃ 1: IDENTIFICAÇÃO ---
if st.session_state.ecra == 1:
    st.markdown('<div class="instrucao-container"><div class="legenda-texto">Escreva e Submeta teu Nome</div><div class="seta">↓</div></div>', unsafe_allow_html=True)
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

# --- ECRÃ 2: CHAT INTELIGENTE ---
elif st.session_state.ecra == 2:
    st.markdown('<style>[data-testid="stAppViewContainer"] { background-image: none !important; background-color: white !important; }</style>', unsafe_allow_html=True)
    
    # Topo Fixo
    st.markdown(f"<h2 style='text-align:center; color:#1A237E;'>Bem-vindo(a), {st.session_state.nome}! Sou teu SmartProf.</h2>", unsafe_allow_html=True)

    # Chat
    for m in st.session_state.mensagens:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    if prompt := st.chat_input("Apresente sua questão de Matemática..."):
        if st.session_state.exercicio_pendente and not any(c.isdigit() for c in prompt):
            st.warning("Apresenta a resposta da questão anterior ou reinicie")
        else:
            st.session_state.mensagens.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)

            with st.chat_message("assistant"):
                try:
                    res = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "system", "content": SYSTEM_PROMPT}] + st.session_state.mensagens
                    )
                    texto = res.choices[0].message.content
                    if "Passo 1" in texto: st.session_state.exercicio_pendente = True
                    st.markdown(texto)
                    st.session_state.mensagens.append({"role": "assistant", "content": texto})
                except:
                    st.error("Erro na conexão com a IA.")

    # Botão de Reiniciar na parte inferior
    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("Limpar"):
        st.session_state.mensagens = []
        st.session_state.exercicio_pendente = False
        st.rerun()


