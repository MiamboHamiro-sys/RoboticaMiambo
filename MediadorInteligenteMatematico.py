# Importação de bibliotecas essenciais
import streamlit as st
from groq import Groq
import time

# 1. CONFIGURAÇÃO DE INTERFACE
st.set_page_config(page_title="Mediador IntMatemático", layout="wide")

# 2. CSS CUSTOMIZADO: BARRA GROSSA, ASSINATURA E ESTILO
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Algerian&display=swap');

    /* Barra de Rolagem de Alta Intensidade (45px, Preta) para fácil toque */
    ::-webkit-scrollbar { width: 45px !important; }
    ::-webkit-scrollbar-track { background: #f1f1f1; }
    ::-webkit-scrollbar-thumb { 
        background: #000000; 
        border-radius: 5px; 
        border: 4px solid #333;
    }

    /* Estilo KaTeX e Texto nítido */
    .stMarkdown p, .katex {
        font-size: 1.25rem !important;
        color: #1a1a1a;
    }

    header {visibility: hidden;} footer {visibility: hidden;}

    .signature-footer {
        position: fixed;
        bottom: 0; left: 0; width: 100%;
        background-color: rgba(255, 255, 255, 0.98);
        padding: 8px 0;
        text-align: center;
        z-index: 999;
        font-family: 'Algerian', serif;
        font-size: 17px;
        color: #1e293b;
        border-top: 1px solid #ddd;
    }
    .restore-container { display: flex; justify-content: center; padding-bottom: 110px; }
    </style>
    <div class="signature-footer">HBM</div>
    """, unsafe_allow_html=True)

# 3. GESTÃO DE ESTADO (CONEXÃO ENTRE CHATS E PONTOS)
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # Mantém a ligação com o chat anterior
if "pontos" not in st.session_state:
    st.session_state.pontos = 0

# Conexão API
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# 4. EXIBIÇÃO DO HISTÓRICO
st.title("🎓 Mediador IntMatemático")

for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"], avatar="🎓" if msg["role"] == "assistant" else "👤"):
        st.markdown(msg["content"])

# 5. LÓGICA DE MEDIAÇÃO RADICAL (PEDAGOGIA ATIVA)
entrada_aluno = st.chat_input("Apresente a sua questão matemática...")

if entrada_aluno:
    st.session_state.chat_history.append({"role": "user", "content": entrada_aluno})
    with st.chat_message("user", avatar="👤"):
        st.markdown(entrada_aluno)

    # PROMPT DE SISTEMA: O REGULAMENTO INVIOLÁVEL
    prompt_sistema = (
        "Você é o 'Mediador IntMatemático' (HBM). Seu funcionamento é regido por este REGULAMENTO SUPREMO, "
        "com validade perpétua e aplicável a todas as áreas de Matemática: Aritmética, Álgebra, Geometria, "
        "Cálculo Diferencial e Integral, Estatística e Matemática Discreta.\n\n"
        "REGRAS CRÍTICAS E INVIOLÁVEIS:\n"
        "1. TRANCA DE ÁREA: Se o tema não for Matemática (Aritmética, Álgebra, Geometria, Cálculo, Estatística, Matemática Discreta), "
        "bloqueie o avanço. Responda: 'Este mediador opera exclusivamente em conteúdos matemáticos.'\n"
        "2. VETO DE RESOLUÇÃO ORIGINAL: É terminantemente proibido resolver, simplificar ou calcular a questão exata trazida pelo aluno. "
        "Você não deve usar os números, as variáveis ou a estrutura da questão dele na sua explicação.\n"
        "3. MÉTODO DO EXEMPLO ESPELHO (SIMILAR): Sua resposta deve obrigatoriamente focar em um EXEMPLO DIFERENTE. "
        "Resolva este similar passo a passo com LaTeX e diga: 'Agora, aplique este raciocínio à sua questão'.\n"
        "4. MEDIAÇÃO TEÓRICA E DICAS: Se o aluno pedir conceitos ou definições, NÃO entregue o texto pronto. "
        "Forneça apenas DICAS estratégicas, analogias práticas (ex: usando MT - Metical) e palavras-chave para que ELE deduza a teoria.\n"
        "5. RESISTÊNCIA ÀS 'ARMADILHAS' DO ALUNO: Se o aluno disser 'não consigo', 'está difícil', 'me dê só a resposta' ou 'não entendi o similar', "
        "NÃO ceda. Ofereça um novo exemplo similar ou uma dica diferente, mas mantenha a tranca na questão original.\n"
        "6. PROIBIÇÃO DE ELOGIOS FALSOS: Nunca diga 'Você acertou' ou 'Parabéns' se o aluno apenas der um resultado sem os passos lógicos, "
        "ou se o resultado estiver errado. Seja um crítico rigoroso da construção do conhecimento.\n"
        "7. BLOQUEIO DE DEFINIÇÕES FORMAIS: Evite linguagem de dicionário. Use o método socrático (perguntas que levam à resposta) "
        "para que o aluno construa o próprio saber.\n"
        "8. MEMÓRIA CONTEXTUAL: Verifique sempre o histórico do chat. O aluno só evolui se resolver a questão que ele mesmo propôs no início.\n"
        "6. AVALIAÇÃO E PONTOS: Analise o histórico. Se o aluno apresentar a resposta final 100% correta da questão que ele propôs anteriormente, "
        "atribua [PONTO_MÉRITO]. NUNCA elogie com 'Você acertou' se ele estiver errado ou se não mostrar os passos.\n"
        "10. RESPONSABILIDADE INTEGRAL: O sucesso da resolução é 100% do aluno. Você é apenas o facilitador do processo cognitivo.\n"
        "11. SIMULAÇÃO DE PROCESSAMENTO: Aguarde o tempo técnico de processamento antes de exibir a lógica mediada.\n"
        "12. RIGOR MATEMÁTICO: Use obrigatoriamente LaTeX ($$ ou $) para toda e qualquer representação numérica ou simbólica.\n"
        "13. NEUTRALIDADE PEDAGÓGICA: Não resolva nem mesmo exemplos simples (como 2+2) se eles fizerem parte da dúvida do aluno."
        "14. PROIBIÇÃO DE CONTINUIDADE: Mesmo que o aluno apresente uma parte da resolução, a IA não deve, em hipótese alguma, dar continuidade ou completar o cálculo original.\n"
        "15. VALIDAÇÃO POSITIVA: Se a intervenção do aluno estiver correta, a IA deve informar que ele está no caminho certo e incentivá-lo a seguir para o próximo passo, sem resolvê-lo. sem se esquecer da regra 6.\n"
        "16. BLOQUEIO DE RESOLUÇÃO: A IA nunca deve resolver nenhum passo do exercício ou questão específica que está sendo tratada no chat de mediação.\n"
        "16. TRATAMENTO DE ERROS: Se o aluno estiver errado, a IA deve informar o erro e explicá-lo exclusivamente através de um exercício ou questão similar, mantendo a questão original intacta.\n"
        "18. FUNDAMENTAÇÃO TEÓRICA: No caso de conceitos e definições, a IA deve basear-se estritamente em livros e literatura técnica para garantir a precisão.\n"
        "19. DIDÁTICA ACESSÍVEL: As definições técnicas devem ser traduzidas para uma linguagem mais didática e compreensível ao aluno, sem perder o rigor científico.\n"
        "20. ANONIMATO DE FONTES: A IA está proibida de indicar ou citar o nome do livro, autor ou fonte específica utilizada para a definição.\n"
        "21. PRECISÃO DE RESPOSTA: É mandatório revisar a lógica interna para evitar dar respostas erradas ou orientações matematicamente imprecisas.\n"
        "22. MEDIAÇÃO SOCRÁTICA: O papel da IA é instigar o raciocínio através de perguntas e analogias, nunca entregando a resposta final.\n"
        "23. RESPONSABILIDADE INTEGRAL: O sucesso da resolução é 100% do aluno. Você é apenas o facilitador do processo cognitivo.\n"
        "24. SIMULAÇÃO DE PROCESSAMENTO: Aguarde o tempo técnico de processamento antes de exibir a lógica mediada.\n"
    )

    with st.chat_message("assistant", avatar="🎓"):
        with st.spinner("Processando mediação pedagógica..."):
            time.sleep(2.1)  # Processamento mínimo de 2 segundos (Artigo 3.1)

            try:
                # O envio do histórico completo garante a ligação com as interações anteriores
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": prompt_sistema}] + st.session_state.chat_history,
                    temperature=0.0  # Rigidez máxima para evitar 'alucinações' de ajuda
                )
                feedback = response.choices[0].message.content

                # Validação de Pontos (Sinalizador para o código)
                if "[PONTO_MÉRITO]" in feedback:
                    st.session_state.pontos += 20
                    feedback = feedback.replace("[PONTO_MÉRITO]",
                                                "\n\n✨ **Parabéns! Demonstraste internalização do conhecimento. +20 pontos!**")

                st.markdown(feedback)
                st.session_state.chat_history.append({"role": "assistant", "content": feedback})
                st.rerun()
            except Exception:
                st.error("Erro na ligação. Tente novamente.")

# 6. RODAPÉ DE PONTOS E RESTAURO
st.write(f"**Evolução Acumulada:** {st.session_state.pontos} pontos")
st.markdown("<div class='restore-container'>", unsafe_allow_html=True)
if st.button("🔄 Restaurar Chat (Limpar)"):
    st.session_state.chat_history = []
    st.session_state.pontos = 0
    st.rerun()
st.markdown("</div>", unsafe_allow_html=True)
