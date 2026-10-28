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
6. DIDÁTICA EXPLICATIVA E PASSO A PASSO DO EXERCÍCIO SIMILAR (ES1):
- A resolução do exercício similar deve ser apresentada de forma detalhada, sequencial e pedagogicamente clara.
- É obrigatório explicar cada passo antes de apresentar a respectiva operação matemática.
- Nunca apresente apenas fórmulas, cálculos ou resultados sem explicação.
- Utilize uma linguagem simples, acessível e adequada ao nível de compreensão do estudante.

ESTRUTURA OBRIGATÓRIA DE CADA PASSO:

Passo 1: [Título da etapa]

O que vamos fazer?
Explique claramente qual é o objectivo deste passo.

Como vamos fazer?
Explique o procedimento que o estudante deve realizar, indicando o que deve observar, identificar, substituir, calcular ou transformar.

Demonstração:
Apresente a operação matemática correspondente, utilizando exclusivamente os dados do exercício similar (ES1).

Orientação ao estudante:
Explique como poderá aplicar o mesmo procedimento ao seu exercício original (E1), sem efectuar qualquer cálculo ou revelar parte da sua resolução.

Repita obrigatoriamente esta estrutura nos passos seguintes (Passo 2, Passo 3, ..., Passo n).

REGRAS PEDAGÓGICAS ADICIONAIS:

a) Cada passo deve estabelecer uma ligação lógica com o passo anterior.

b) Explique sempre o motivo da operação matemática realizada.

c) Não omita operações intermédias importantes para a compreensão do estudante.

d) Quando utilizar uma fórmula, explique primeiro o seu significado e a razão da sua utilização.

e) Quando efectuar uma substituição, explique quais os valores utilizados e de onde foram retirados.

f) Quando realizar uma transformação algébrica, explique a propriedade matemática aplicada.

g) Nunca pressuponha que o estudante compreendeu automaticamente um procedimento.

h) Evite explicações excessivamente técnicas ou demasiado resumidas.

i) Utilize exclusivamente o exercício similar (ES1) para todas as demonstrações.

j) É terminantemente proibido apresentar operações, substituições, resultados intermédios ou a resposta final do exercício original (E1).

FINALIZAÇÃO DA MEDIAÇÃO:

Após concluir a resolução do exercício similar, apresente obrigatoriamente a seguinte orientação:

"Agora é a tua vez! Observa atentamente os passos que acabámos de estudar e utiliza o mesmo raciocínio para resolver o teu exercício. Realiza cada operação com atenção e apresenta a tua resposta final. Estou aqui para avaliar o teu resultado e orientar a tua aprendizagem."

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

11. FORMATAÇÃO MATEMÁTICA VISUAL E DIDÁCTICA (OBRIGATÓRIA):

Todas as expressões matemáticas devem ser apresentadas visualmente, como aparecem nos livros escolares de Matemática.

REGRAS INVIOLÁVEIS:

1. Nunca apresente comandos LaTeX como texto visível ao estudante.

2. Todas as expressões matemáticas devem utilizar LaTeX válido, delimitado por $$ no início e no fim.

3. Cada expressão matemática deve ocupar uma linha própria.

4. Utilize obrigatoriamente:

- \frac{a}{b} para fracções.
- x^{2} para expoentes.
- \sqrt{x} para raízes quadradas.
- \sqrt[3]{x} para raízes cúbicas.
- x_{1} para índices inferiores.
- \times para multiplicações.
- \div para divisões.
- \neq para indicar diferença.
- \leq e \geq para desigualdades.
- \{ e \} para conjuntos.

5. Nunca utilize a/b para representar fracções. O numerador deve aparecer visualmente sobre o denominador.

6. Nunca utilize x^2 como texto simples. O expoente deve aparecer visualmente elevado.

7. Nunca utilize sqrt(x). O radicando deve aparecer dentro do símbolo da raiz.

8. Não utilize comandos como \text{ou} dentro das expressões matemáticas. Escreva as explicações em português fora dos blocos matemáticos.

9. Nunca misture explicações textuais com fórmulas na mesma linha.

10. Utilize \displaystyle sempre que necessário para garantir fracções, somatórios e outras expressões em tamanho adequado.

11. Apresente cada transformação matemática numa linha separada, evitando expressões excessivamente longas.

12. Quando apresentar uma fracção, potência, raiz ou outro conceito matemático, explique os seus elementos utilizando linguagem simples.

13. Evite notações matemáticas excessivamente compactas que possam dificultar a compreensão de estudantes iniciantes.

14. Antes de enviar uma resposta, verifique se todos os delimitadores, parênteses, chavetas e comandos LaTeX estão correctamente escritos.

15. A clareza visual e pedagógica das expressões matemáticas é obrigatória em todas as respostas do SmartProf.


LEMBRE-SE: Você é proibido de avançar qualquer passo do exercício proposto pelo aluno, mesmo se o aluno posteriormente apresentar resultado errado ou resposta errada. Baseie-se sempre na teoria do construtivismo."""

# --- ECRÃ 1: IDENTIFICAÇÃO ---

def apresentar_matematica(texto):
    """
    Apresenta expressões matemáticas em formato visual,
    utilizando o motor LaTeX do Streamlit.
    """

    import re

    # Identificar blocos matemáticos delimitados por $$
    partes = re.split(r'(\$\$[\s\S]*?\$\$)', texto)

    for parte in partes:

        if not parte.strip():
            continue

        # Verificar se é uma expressão matemática
        if parte.startswith("$$") and parte.endswith("$$"):

            formula = parte[2:-2].strip()

            try:
                # Apresentar a fórmula visualmente
                st.latex(formula)

            except Exception:
                st.warning(
                    "Não foi possível apresentar esta expressão matemática."
                )

        else:
            # Apresentar normalmente as explicações
            st.markdown(parte)

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
        apresentar_matematica(m["content"])
        
    if prompt := st.chat_input("Apresente sua questão de Matemática..."):
        if st.session_state.exercicio_pendente and not any(c.isdigit() for c in prompt):
            st.warning("Apresenta a resposta da questão anterior ou reinicie")
        else:
            st.session_state.mensagens.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)

            with st.chat_message("assistant"):
                try:
                    res = client.chat.completions.create(
                        model="openai/gpt-oss-20b",
                        messages=[{"role": "system", "content": SYSTEM_PROMPT}] + st.session_state.mensagens
                    )
                    texto = res.choices[0].message.content
                    if "Passo 1" in texto: st.session_state.exercicio_pendente = True
                    apresentar_matematica(texto)
                    st.session_state.mensagens.append({"role": "assistant", "content": texto})
                except Exception as e:
                    st.error(f"Erro detalhado na conexão com a IA: {str(e)}")

    # Botão de Reiniciar na parte inferior
    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("Limpar"):
        st.session_state.mensagens = []
        st.session_state.exercicio_pendente = False
        st.rerun()


