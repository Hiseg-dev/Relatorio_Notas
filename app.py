import streamlit as st
import pandas as pd
import os
import subprocess

# --- Configuração da Página ---
st.set_page_config(
    page_title="Relatório de Notas Interativo",
    page_icon="📊",
    layout="wide"
)

# --- Carregamento dos Dados ---
@st.cache_data
def load_data():
    """Carrega os dados do arquivo CSV consolidado."""
    csv_path = os.path.join('output', 'relatorio_consolidado.csv')
    if os.path.exists(csv_path):
        return pd.read_csv(csv_path)
    else:
        return None

df = load_data()

# --- Título Principal ---
st.title("📊 Painel de Análise de Notas")

# --- Lógica da Aplicação ---
if df is not None:
    # --- Barra Lateral com Filtros ---
    st.sidebar.header("Filtros")
    
    # Filtro por curso
    cursos = ['Todos'] + sorted(df['Curso'].unique().tolist())
    curso_selecionado = st.sidebar.selectbox("Selecione o Curso:", cursos)

    # Filtro por disciplina (condicionado ao curso)
    if curso_selecionado == 'Todos':
        disciplinas = ['Todos'] + sorted(df['Disciplina'].unique().tolist())
    else:
        disciplinas = ['Todos'] + sorted(df[df['Curso'] == curso_selecionado]['Disciplina'].unique().tolist())
    
    disciplina_selecionada = st.sidebar.selectbox("Selecione a Disciplina:", disciplinas)

    # Filtra o DataFrame com base na seleção
    if curso_selecionado == 'Todos':
        df_filtrado = df
    else:
        df_filtrado = df[df['Curso'] == curso_selecionado]

    if disciplina_selecionada != 'Todas':
        df_filtrado = df_filtrado[df_filtrado['Disciplina'] == disciplina_selecionada]

    # --- Abas ---
    tab1, tab2, tab3 = st.tabs(["Análise Geral", "Dados Detalhados", "Manutenção"])

    with tab1:
        st.header(f"Exibindo Dados para: {curso_selecionado} - {disciplina_selecionada}")

        # Métricas
        col1, col2, col3 = st.columns(3)
        if not df_filtrado.empty:
            media_geral = df_filtrado['MediaFinal'].mean()
            num_alunos = len(df_filtrado)
            aprovados = len(df_filtrado[df_filtrado['MediaFinal'] >= 6.0]) # Exemplo: Média de aprovação 7.0
            reprovados = num_alunos - aprovados
        else:
            media_geral = 0
            num_alunos = 0
            aprovados = 0
            reprovados = 0

        col1.metric("Média Geral da Turma", f"{media_geral:.2f}")
        col2.metric("Número de Alunos", num_alunos)
        col3.metric("Alunos Aprovados (Média >= 6)", aprovados)

        st.markdown("---")

        # Gráfico de comparação de médias
        if not df_filtrado.empty:
            st.subheader("Comparativo das Médias (AV1, AV2, Média Final)")
            media_av1 = df_filtrado['AV1'].mean()
            media_av2 = df_filtrado['AV2'].mean()
            media_final = df_filtrado['MediaFinal'].mean()

            df_medias = pd.DataFrame({
                'Avaliação': ['AV1', 'AV2', 'Média Final'],
                'Média': [media_av1, media_av2, media_final]
            })
            st.bar_chart(df_medias.set_index('Avaliação'))
        
        st.markdown("---")
        
        # Tabela de notas da disciplina
        st.subheader("Notas da Disciplina")
        st.dataframe(df_filtrado[['Aluno', 'AV1', 'AV2', 'MediaFinal']])

        st.markdown("---")
        
        # Resumo de aprovados e reprovados
        st.subheader("Resumo de Aprovação")
        if not df_filtrado.empty:
            df_situacao = pd.DataFrame({
                'Situação': ['Aprovados', 'Reprovados'],
                'Quantidade': [aprovados, reprovados]
            })
            st.bar_chart(df_situacao.set_index('Situação'))

    with tab2:
        st.header("Dados Detalhados dos Alunos")
        st.dataframe(df_filtrado)

        # Botão de download
        @st.cache_data
        def convert_df(df):
            return df.to_csv(index=False).encode('utf-8')

        csv = convert_df(df_filtrado)

        st.download_button(
            label="Baixar dados em CSV",
            data=csv,
            file_name='dados_filtrados.csv',
            mime='text/csv',
        )

    with tab3:
        st.header("Manutenção")
        st.subheader("Atualizar Dados")
        st.info("Clique no botão abaixo para executar o script `relatorio.py` e atualizar os dados do relatório.")
        
        if st.button("Atualizar Dados"):
            with st.spinner("Executando o script `relatorio.py`..."):
                try:
                    subprocess.run(["python", "relatorio.py"], check=True)
                    st.success("Script executado com sucesso! Os dados foram atualizados.")
                    # Limpa o cache para recarregar os dados
                    st.cache_data.clear()
                except subprocess.CalledProcessError as e:
                    st.error(f"Erro ao executar o script: {e}")
                except FileNotFoundError:
                    st.error("Script `relatorio.py` não encontrado.")

else:
    st.error("Arquivo 'relatorio_consolidado.csv' não encontrado!")
    st.info("Por favor, execute o script 'relatorio.py' primeiro para gerar o arquivo de dados.")