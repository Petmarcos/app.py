import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configuração da página
st.set_page_config(
    page_title="Gerador de Gráficos Automáticos",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Gerador de Gráficos a partir de Planilhas")
st.write("Faça o upload do seu arquivo Excel ou CSV para gerar visualizações automáticas e personalizadas.")

# Sidebar - Upload
st.sidebar.header("1. Envie sua planilha")
uploaded_file = st.sidebar.file_uploader("Escolha um arquivo (.xlsx ou .csv)", type=["csv", "xlsx"])

if uploaded_file is not None:
    # Leitura dos dados
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        st.sidebar.success("Arquivo carregado com sucesso!")
        
        # Exibição dos Dados
        st.subheader("📋 Previsão dos Dados")
        st.dataframe(df.head())
        
        # Estatísticas Descritivas
        with st.expander("ℹ️ Estatísticas Descritivas"):
            st.write(df.describe(include='all'))

        st.markdown("---")
        st.subheader("📈 Gerador de Gráficos")
        
        columns = df.columns.tolist()
        num_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
        
        col1, col2 = st.columns(2)
        
        with col1:
            chart_type = st.selectbox(
                "Tipo de Gráfico",
                ["Barras", "Linhas", "Dispersão (Scatter)", "Histograma", "Boxplot"]
            )
            x_axis = st.selectbox("Eixo X ( Categoria / Tempo )", columns)
            
        with col2:
            if chart_type in ["Barras", "Linhas", "Dispersão (Scatter)", "Boxplot"]:
                y_axis = st.selectbox("Eixo Y ( Valor Numérico )", num_cols if num_cols else columns)
            else:
                y_axis = None
            
            color_theme = st.selectbox("Tema de Cores", ["viridis", "magma", "muted", "Set2"])

        # Plotagem
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.set_theme(style="whitegrid")
        
        if chart_type == "Barras":
            sns.barplot(data=df, x=x_axis, y=y_axis, palette=color_theme, ax=ax)
            plt.xticks(rotation=45)
        elif chart_type == "Linhas":
            sns.lineplot(data=df, x=x_axis, y=y_axis, marker='o', ax=ax)
            plt.xticks(rotation=45)
        elif chart_type == "Dispersão (Scatter)":
            sns.scatterplot(data=df, x=x_axis, y=y_axis, hue=x_axis, palette=color_theme, ax=ax)
            plt.xticks(rotation=45)
        elif chart_type == "Histograma":
            sns.histplot(data=df, x=x_axis, kde=True, ax=ax)
        elif chart_type == "Boxplot":
            sns.boxplot(data=df, x=x_axis, y=y_axis, palette=color_theme, ax=ax)
            plt.xticks(rotation=45)

        ax.set_title(f"Gráfico de {chart_type}: {x_axis} vs {y_axis if y_axis else ''}")
        st.pyplot(fig)

    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")
else:
    st.info("Aguardando upload de planilha (.xlsx ou .csv)...")
