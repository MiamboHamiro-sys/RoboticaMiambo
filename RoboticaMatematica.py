import streamlit as st
import time
from groq import Groq
from gtts import gTTS
import base64
import io
import json

# --- CONFIGURAÇÃO DA INTERFACE E CSS ---
st.set_page_config(page_title="SmartProf", layout="wide")

# Barra de rolagem grossa e estilo de imagem 1/8
st.markdown("""
    <style>
    /* Barra de rolagem muito grossa */
    ::-webkit-scrollbar { width: 50px; }
    ::-webkit-scrollbar-track { background: #f1f1f1; }
    ::-webkit-scrollbar-thumb { background: #007bff; border-radius: 5px; }
    
    /* Imagem do robô (1/8 da largura da tela) */
    .robot-container {
        display: flex;
        justify-content: center;
        width: 100%;
    }
    .robot-img {
        width: 12.5%; /* 1/8 da tela */
        min-width: 100px;
    }
    
    /* Botões inferiores fixos */
    .footer {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: white;
        padding: 10px;
        border-top: 2px solid #ddd;
        z-index: 1000;
    }
    div.stButton > button {
        width: 100%;
        height: 60px;
        font-weight: bold;
    }
    /* Padding para o conteúdo não ficar por baixo dos botões */
    .main-content { padding-bottom: 100px; }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZAÇÃO DA IA (GROQ) ---
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("Erro: Configure a GROQ_API_KEY no Streamlit Cloud.")

# --- PROMPT INVIOLÁVEL ---
SYSTEM_PROMPT = """
És o "SmartProf", um robô especializado APENAS em Matemática.
REGRAS:
1. Se o assunto NÃO for Matemática, responde: "Sou um especialista em Matemática. Não posso avançar com outros conteúdos." e interrompe.
2. NUNCA dês a solução do exercício original (E1) do aluno.
3. Cria um exercício similar (ES1) com valores diferentes.
4. Explica ES1 passo a passo (Passo 1, 2... n).
5. Retorna obrigatoriamente um JSON com este formato:
{
  "resultado_e1": "valor_numérico_ou_final",
  "passos": [
    {"expressao": "fórmula_latex", "explicacao": "texto_didatico"},
    ...
  ]
}
"""

# --- FUNÇÕES DE VOZ ---
def play_voice(text):
    if text:
        try:
            tts = gTTS(text=text, lang='pt', slow=False)
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            b64 = base64.base64encode(fp.read()).decode()
            md = f'<audio autoplay="true" src="data:audio/mp3;base64,{b64}">'
            st.markdown(md, unsafe_allow_html=True)
        except:
            pass

# --- GESTÃO DE ESTADO (SESSION STATE) ---
if 'ecra' not in st.session_state: st.session_state.ecra = 1
if 'nome' not in st.session_state: st.session_state.nome = ""
if 'passo_atual' not in st.session_state: st.session_state.passo_atual = -1
if 'memoria_ia' not in st.session_state: st.session_state.memoria_ia = {}
if 'resultado_aluno' not in st.session_state: st.session_state.resultado_aluno = ""

# --- ECRÃ 1 ---
if st.session_state.ecra == 1:
    st.markdown('<div class="robot-container"><img src="https://cdn-icons-png.flaticon.com/512/4712/4712139.png" class="robot-img"></div>', unsafe_allow_html=True)
    nome_aluno = st.text_input("Insira o seu nome:", value=st.session_state.nome)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Submeter Nome"):
            if nome_aluno:
                st.session_state.nome = nome_aluno
                play_voice(f"{nome_aluno}, é um prazer contar consigo nesta jornada de discutirmos assuntos de Matemática")
                # Esperar a voz e processar
                with st.spinner("Processando..."):
                    time.sleep(8) # Tempo para a voz (aprox 3s) + 5 segundos de espera
                st.session_state.ecra = 2
                st.rerun()
    with col2:
        if st.button("Reiniciar"):
            st.session_state.clear()
            st.rerun()

# --- ECRÃ 2 ---
elif st.session_state.ecra == 2:
    st.markdown('<div class="robot-container"><img src="https://cdn-icons-png.flaticon.com/512/4712/4712139.png" class="robot-img"></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    
    # Fase inicial: Pedir exercício
    if st.session_state.passo_atual == -1:
        e1_input = st.text_area("Apresente o seu exercício E1:")
        if st.button("Enviar Exercício"):
            if e1_input:
                with st.spinner("SmartProf a pensar..."):
                    try:
                        completion = client.chat.completions.create(
                            model="llama-3.3-70b-versatile",
                            messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": e1_input}],
                            response_format={"type": "json_object"}
                        )
                        res = json.loads(completion.choices[0].message.content)
                        st.session_state.memoria_ia = res
                        st.session_state.passo_atual = 0
                        time.sleep(2)
                        play_voice("Não vou resolver o exercício que apresentaste, mas vou instruir-te a resolver siga os passos que se seguem")
                        st.rerun()
                    except:
                        st.error("Por favor, envie apenas exercícios de Matemática.")

    # Fase de Mediação: Passos
    else:
        passos = st.session_state.memoria_ia.get('passos', [])
        
        # Mostrar todos os passos até ao atual (sem apagar)
        for i in range(st.session_state.passo_atual + 1):
            if i < len(passos):
                st.markdown(f"### Passo {i+1}")
                st.latex(passos[i]['expressao'])
                st.write(passos[i]['explicacao'])
                
                # Se for o passo atual, mostrar campo de dúvida
                if i == st.session_state.passo_atual:
                    duvida = st.text_input("Tens alguma dúvida neste passo?", key=f"duv_{i}")
                    if duvida:
                        if st.button("Explicar novamente"):
                            play_voice(passos[i]['explicacao'])

        # Se for o último passo, pedir resultado
        if st.session_state.passo_atual == len(passos) - 1:
            st.markdown("---")
            play_voice("siga a lógica e apresenta o resultado final")
            st.session_state.resultado_aluno = st.text_input("Apresenta o resultado do exercício E1:")
            
            if st.button("Validar Resultado"):
                with st.spinner("Analisando..."):
                    time.sleep(2)
                    res_correto = str(st.session_state.memoria_ia.get('resultado_e1', ""))
                    if st.session_state.resultado_aluno.strip() == res_correto.strip():
                        play_voice("parabéns acertou")
                        st.balloons()
                        st.success("Ganhou 10 pontos!")
                    else:
                        play_voice("Infelizmente não é assim, clica no Botão 2 para reiniciarmos o processo ou clica no Botão 4 para recuar a explicação")
                        st.error("Tente novamente.")

    st.markdown('</div>', unsafe_allow_html=True)

    # --- BOTÕES INFERIORES FIXOS ---
    st.markdown('<div class="footer">', unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        if st.button("Ecrã 1"):
            st.session_state.ecra = 1
            st.rerun()
    with c2:
        if st.button("Limpar"):
            st.session_state.passo_atual = -1
            st.rerun()
    with c3:
        st.button("Recuar Expl.") # Botão estético conforme pedido
    with c4:
        if st.button("Recuar Passo"):
            if st.session_state.passo_atual > 0:
                st.session_state.passo_atual -= 1
                st.rerun()
    with c5:
        if st.button("Próximo"):
            passos = st.session_state.memoria_ia.get('passos', [])
            if st.session_state.passo_atual < len(passos) - 1:
                st.session_state.passo_atual += 1
                # Simultanemanete emite a voz do novo passo
                play_voice(passos[st.session_state.passo_atual]['explicacao'])
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
