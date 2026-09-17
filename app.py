import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(
    page_title="Dashboard de Homologação de Diplomas",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 Dashboard de Emissão de Diplomas")
st.write("Faça o upload da sua planilha para gerar automaticamente o painel de gestão.")

# Sidebar - Upload de arquivo
st.sidebar.header("📁 Enviar Planilha")
uploaded_file = st.sidebar.file_uploader("Selecione o arquivo (.xlsx ou .csv)", type=["csv", "xlsx"])

if uploaded_file is not None:
    try:
        # Leitura dos dados
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
            
        st.sidebar.success("Arquivo carregado com sucesso!")

        # Mapeamento dinâmico automático de colunas
        cols = list(df.columns)
        
        st.sidebar.markdown("---")
        st.sidebar.subheader("⚙️ Mapeamento de Colunas")
        
        idx_curso = next((i for i, c in enumerate(cols) if 'curso' in c.lower()), 0)
        idx_campus = next((i for i, c in enumerate(cols) if 'campus' in c.lower()), 0)
        idx_data = next((i for i, c in enumerate(cols) if 'homologa' in c.lower() or 'data' in c.lower() or 'mes' in c.lower()), 0)

        col_curso = st.sidebar.selectbox("Coluna de Cursos", cols, index=idx_curso)
        col_campus = st.sidebar.selectbox("Coluna de Campus", cols, index=idx_campus)
        col_data = st.sidebar.selectbox("Coluna de Data/Mês", cols, index=idx_data)

        # Conversão de Datas
        df[col_data] = pd.to_datetime(df[col_data], dayfirst=True, errors='coerce')

        # --- SEÇÃO 1: CARTÕES NUMÉRICOS (KPIs) ---
        st.markdown("### 📊 Visão Geral")
        kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
        
        with kpi_col1:
            st.metric(label="Total de Diplomas Emitidos", value=f"{len(df):,}".replace(",", "."))
        with kpi_col2:
            st.metric(label="Total de Cursos Atendidos", value=df[col_curso].nunique())
        with kpi_col3:
            st.metric(label="Total de Campus Atendidos", value=df[col_campus].nunique())

        st.markdown("---")

        # Configuração estética
        sns.set_theme(style="whitegrid")

        # --- SEÇÃO 2: GRÁFICOS DO DASHBOARD ---
        row1_col1, row1_col2 = st.columns(2)

        # 1. Diplomas por Curso (Barras Horizontais - Top 15)
        with row1_col1:
            st.subheader("Diplomas emitidos por Curso (Top 15)")
            fig1, ax1 = plt.subplots(figsize=(8, 6))
            curso_counts = df[col_curso].value_counts().reset_index()
            curso_counts.columns = [col_curso, 'Qtd']
            
            sns.barplot(data=curso_counts.head(15), y=col_curso, x='Qtd', palette="Blues_r", ax=ax1)
            ax1.set_xlabel("Quantidade de Diplomas")
            ax1.set_ylabel("")
            st.pyplot(fig1)

        # 2. Diplomas por Campus (Colunas Verticais)
        with row1_col2:
            st.subheader("Diplomas emitidos por Campus")
            fig2, ax2 = plt.subplots(figsize=(8, 6))
            campus_counts = df[col_campus].value_counts().reset_index()
            campus_counts.columns = [col_campus, 'Qtd']
            
            sns.barplot(data=campus_counts, x=col_campus, y='Qtd', palette="viridis", ax=ax2)
            ax2.set_xlabel("")
            ax2.set_ylabel("Quantidade de Diplomas")
            plt.xticks(rotation=45, ha='right')
            st.pyplot(fig2)

        # 3. Diplomas por Mês de Homologação (Série Temporal)
        st.markdown("---")
        st.subheader("Diplomas por Mês de Homologação")
        
        fig3, ax3 = plt.subplots(figsize=(12, 4))
        df['AnoMes'] = df[col_data].dt.to_period('M').astype(str)
        temporal_counts = df['AnoMes'].value_counts().sort_index().reset_index()
        temporal_counts.columns = ['Mês', 'Qtd']

        sns.lineplot(data=temporal_counts, x='Mês', y='Qtd', marker='o', linewidth=2.5, color='#1f77b4', ax=ax3)
        sns.barplot(data=temporal_counts, x='Mês', y='Qtd', alpha=0.3, color='#1f77b4', ax=ax3)
        ax3.set_xlabel("Mês/Ano")
        ax3.set_ylabel("Quantidade Emitida")
        plt.xticks(rotation=45)
        st.pyplot(fig3)

        # Visualização opcional da planilha
        with st.expander("📋 Ver planilha de dados completa"):
            st.dataframe(df)

    except Exception as e:
        st.error(f"Erro ao processar a planilha: {e}")
else:
    st.info("Aguardando upload de planilha (.xlsx ou .csv)...")
