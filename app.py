import streamlit as st
import google.generativeai as genai
import json
import pandas as pd

# Configuração visual da página do seu site
st.set_page_config(page_title="Extrator de Reuniões IA", page_icon="📝", layout="wide")

st.title("📝 Extrator de Reuniões com IA")
st.subheader("Transforme transcrições brutas em planos de ação organizados em segundos")

# Busca a chave secreta do Gemini (de forma oculta e segura)
api_key = st.secrets.get("GEMINI_API_KEY", "")

# Se o site não tiver a chave salva de forma segura nas configurações dele, permite digitar na tela
if not api_key:
    st.sidebar.warning("Chave da API do Gemini não configurada nos bastidores do site.")
    api_key = st.sidebar.text_input("Insira sua Gemini API Key:", type="password")

if api_key:
    genai.configure(api_key=api_key)
else:
    st.info("💡 Insira sua Gemini API Key na barra lateral para ativar o aplicativo.")

# Campo para o usuário colar a transcrição do Granola
transcricao = st.text_area("Cole aqui a transcrição da reunião:", height=250, placeholder="Cole o texto bruto exportado do Granola...")

# Botão principal
if st.button("🚀 Extrair Plano de Ação", type="primary"):
    if not api_key:
        st.error("Por favor, insira sua chave de API do Gemini para continuar.")
    elif not transcricao.strip():
        st.warning("Por favor, cole um texto antes de processar.")
    else:
        with st.spinner("Analisando transcrição e mapeando responsáveis..."):
            try:
                # Usando o modelo rápido e de uso gratuito para desenvolvedores
                model = genai.GenerativeModel("gemini-2.5-flash")
                
                # O prompt que dita as regras para a Inteligência Artificial
                prompt = (
                    "Você é um assistente especialista em gerenciamento de projetos.\n"
                    "Sua tarefa é analisar a transcrição de reunião abaixo e extrair EXCLUSIVAMENTE as ações práticas acordadas.\n\n"
                    "Para cada ação identificada, você deve extrair exatamente estes 4 parâmetros:\n"
                    "1. TEMA: O assunto ou projeto ao qual a ação pertence.\n"
                    "2. ACAO: O que precisa ser feito (sempre iniciando com verbo no infinitivo).\n"
                    "3. RESPONSAVEL: Quem se comprometeu a realizar a tarefa (se não for mencionado explicitamente, preencha com 'Não atribuído').\n"
                    "4. PRAZO: O limite de entrega acordado (se não mencionado, preencha com 'Não definido').\n\n"
                    "Sua resposta deve ser estritamente um JSON válido, no seguinte formato de lista:\n"
                    "[\n"
                    "  {\"TEMA\": \"Nome do Tema\", \"ACAO\": \"O que fazer\", \"RESPONSAVEL\": \"Nome\", \"PRAZO\": \"Data/Prazo\"}\n"
                    "]\n"
                    "Não inclua nenhuma introdução, nenhuma conclusão e nenhum bloco de código markdown. Apenas o JSON puro.\n\n"
                    f"[TRANSCRIÇÃO DA REUNIÃO]:\n{transcricao}"
                )
                
                response = model.generate_content(prompt)
                resposta_texto = response.text.strip()
                
                # Remove formatações adicionais que a IA às vezes retorna por engano
                if resposta_texto.startswith("```json"):
                    resposta_texto = resposta_texto.replace("```json", "").replace("```", "").strip()
                elif resposta_texto.startswith("```"):
                    resposta_texto = resposta_texto.replace("```", "").strip()

                # Converte o texto JSON em dados organizados (Dataframe)
                dados_acoes = json.loads(resposta_texto)
                
                if dados_acoes:
                    df = pd.DataFrame(dados_acoes)
                    st.success("🎉 Plano de ação gerado com sucesso!")
                    
                    # Exibe a tabela linda e formatada no site
                    st.dataframe(df, use_container_width=True)
                    
                    # Gera um botão para baixar os dados direto para o Excel
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Baixar como arquivo do Excel (CSV)",
                        data=csv,
                        file_name="plano_de_acao_reuniao.csv",
                        mime="text/csv"
                    )
                else:
                    st.info("Nenhuma ação explícita ou tarefa com responsável foi identificada na transcrição fornecida.")
            except Exception as e:
                st.error(f"Ocorreu um erro ao processar: {e}")
