import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(
    page_title=" Homologação de Diplomas - 2026",
    page_icon="🎓",
    layout="wide"
)

# Estilo CSS para formatar a página, tabelas e modo de impressão
st.markdown("""
    <style>
    /* Aumenta nitidez e tamanho do texto nas tabelas do Streamlit */
    [data-testid="stDataFrame"] {
        font-size: 15px !important;
    }
    
    @media print {
        /* Esconde a barra lateral (Sidebar) na impressão */
        [data-testid="stSidebar"] {
            display: none !important;
        }
        /* Esconde o cabeçalho superior e botões da interface */
        header, [data-testid="stHeader"], footer, button, iframe {
            display: none !important;
        }
        /* Ajusta as margens para ocupar o papel todo */
        .main .block-container {
            padding: 0.5rem !important;
            max-width: 100% !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

st.title("🎓  Emissão de Diplomas Digitais  ")
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

        # --- BOTÃO DE IMPRESSÃO / SALVAR PDF NA SIDEBAR ---
        with st.sidebar:
            components.html(
                """
                <button onclick="window.parent.print()" style="
                    background-color: #0d6efd;
                    color: white;
                    padding: 10px 14px;
                    border: none;
                    border-radius: 8px;
                    font-size: 14px;
                    font-weight: bold;
                    cursor: pointer;
                    width: 100%;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                ">
                    🖨️ Imprimir / Salvar PDF
                </button>
                """,
                height=50
            )

        st.sidebar.markdown("---")
        st.sidebar.subheader("⚙️ Mapeamento de Colunas")

        # Mapeamento dinâmico automático de colunas
        cols = list(df.columns)
        idx_curso = next((i for i, c in enumerate(cols) if 'curso' in c.lower()), 0)
        idx_campus = next((i for i, c in enumerate(cols) if 'campus' in c.lower()), 0)
        idx_data = next((i for i, c in enumerate(cols) if 'homologa' in c.lower() or 'data' in c.lower() or 'mes' in c.lower()), 0)
        idx_livro = next((i for i, c in enumerate(cols) if 'livro' in c.lower()), 0)
        idx_registro = next((i for i, c in enumerate(cols) if 'registro' in c.lower() or 'num' in c.lower()), 0)

        col_curso = st.sidebar.selectbox("Coluna de Cursos", cols, index=idx_curso)
        col_campus = st.sidebar.selectbox("Coluna de Campus", cols, index=idx_campus)
        col_data = st.sidebar.selectbox("Coluna de Data/Mês", cols, index=idx_data)
        col_livro = st.sidebar.selectbox("Coluna de Livro", cols, index=idx_livro)
        col_registro = st.sidebar.selectbox("Coluna de N° Registro", cols, index=idx_registro)

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

        # --- SEÇÃO 2: QUADRO RESUMO DE REGISTROS POR LIVRO ---
        st.subheader("Quadro Resumo de Registros por Livro")
        
        if col_livro in df.columns and col_registro in df.columns:
            df[col_registro] = pd.to_numeric(df[col_registro], errors='coerce')
            
            resumo_list = []
            for livro, group in df.groupby(col_livro):
                qtd = len(group)
                min_reg = group[col_registro].min()
                max_reg = group[col_registro].max()
                
                if pd.notna(min_reg) and pd.notna(max_reg):
                    min_reg = int(min_reg)
                    max_reg = int(max_reg)
                    if min_reg == max_reg:
                        intervalo = f"{min_reg}"
                    else:
                        intervalo = f"{min_reg} a {max_reg}"
                else:
                    intervalo = "N/A"
                    
                resumo_list.append({
                    "Livro": str(livro),
                    "Registros": qtd,
                    "Intervalo": intervalo
                })
            
            df_resumo = pd.DataFrame(resumo_list)
            
            total_row = pd.DataFrame([{
                "Livro": "Total",
                "Registros": df_resumo["Registros"].sum(),
                "Intervalo": ""
            }])
            df_resumo_final = pd.concat([df_resumo, total_row], ignore_index=True)
            
            st.dataframe(df_resumo_final, hide_index=True, use_container_width=True)
        else:
            st.warning("Selecione as colunas corretas de 'Livro' e 'N° Registro' na barra lateral para exibir esta tabela.")

        st.markdown("---")

        # Configuração estética padrão
        sns.set_theme(style="whitegrid")

        # --- SEÇÃO 3: GRÁFICOS EMPILHADOS VERTICALMENTE ---

        # 1. Diplomas emitidos por Curso (Top 15)
        st.subheader("Diplomas emitidos por Curso (Top 15)")
        fig1, ax1 = plt.subplots(figsize=(12, 6), dpi=300)
        curso_counts = df[col_curso].value_counts().reset_index()
        curso_counts.columns = [col_curso, 'Qtd']
        top_cursos = curso_counts.head(15)

        sns.barplot(data=top_cursos, y=col_curso, x='Qtd', palette="Blues_r", ax=ax1)
        ax1.set_xlabel("Quantidade de Diplomas", fontsize=12, fontweight='bold')
        ax1.set_ylabel("", fontsize=12)
        ax1.tick_params(axis='both', labelsize=11)
        
        for p in ax1.patches:
            width = p.get_width()
            if width > 0:
                ax1.annotate(f"{int(width)}",
                             (width + 0.5, p.get_y() + p.get_height() / 2.),
                             ha='left', va='center', fontsize=11, fontweight='bold', color='#111111')
                             
        ax1.set_xlim(0, top_cursos['Qtd'].max() * 1.1)
        st.pyplot(fig1)

        st.markdown("---")

        # 2. Diplomas emitidos por Campus
        st.subheader("Diplomas emitidos por Campus")
        fig2, ax2 = plt.subplots(figsize=(12, 5), dpi=300)
        campus_counts = df[col_campus].value_counts().reset_index()
        campus_counts.columns = [col_campus, 'Qtd']

        sns.barplot(data=campus_counts, x=col_campus, y='Qtd', palette="viridis", ax=ax2)
        ax2.set_xlabel("", fontsize=12)
        ax2.set_ylabel("Quantidade de Diplomas", fontsize=12, fontweight='bold')
        ax2.tick_params(axis='both', labelsize=11)
        plt.xticks(rotation=30, ha='right', fontsize=11)

        for p in ax2.patches:
            height = p.get_height()
            if height > 0:
                ax2.annotate(f"{int(height)}",
                             (p.get_x() + p.get_width() / 2., height + 2),
                             ha='center', va='bottom', fontsize=11, fontweight='bold', color='#111111')

        ax2.set_ylim(0, campus_counts['Qtd'].max() * 1.12)
        st.pyplot(fig2)

        st.markdown("---")

        # 3. Diplomas por Mês de Homologação
        st.subheader("Diplomas por Mês de Homologação")
        fig3, ax3 = plt.subplots(figsize=(12, 4.5), dpi=300)
        df['AnoMes'] = df[col_data].dt.to_period('M').astype(str)
        temporal_counts = df['AnoMes'].value_counts().sort_index().reset_index()
        temporal_counts.columns = ['Mês', 'Qtd']

        sns.lineplot(data=temporal_counts, x='Mês', y='Qtd', marker='o', linewidth=2.5, color='#1f77b4', ax=ax3)
        sns.barplot(data=temporal_counts, x='Mês', y='Qtd', alpha=0.3, color='#1f77b4', ax=ax3)

        ax3.tick_params(axis='both', labelsize=11)
        for i, row in temporal_counts.iterrows():
            ax3.annotate(
                f"{int(row['Qtd'])}", 
                (i, row['Qtd']), 
                textcoords="offset points", 
                xytext=(0, 8), 
                ha='center', 
                va='bottom', 
                fontsize=11, 
                fontweight='bold',
                color='#003366'
            )

        ax3.set_ylim(0, temporal_counts['Qtd'].max() * 1.15)
        ax3.set_xlabel("Mês/Ano", fontsize=12, fontweight='bold')
        ax3.set_ylabel("Quantidade Emitida", fontsize=12, fontweight='bold')
        plt.xticks(rotation=45, fontsize=11)
        st.pyplot(fig3)

        # Visualização opcional da planilha
        with st.expander("📋 Ver planilha de dados completa"):
            st.dataframe(df)

    except Exception as e:
        st.error(f"Erro ao processar a planilha: {e}")
else:
    st.info("Aguardando upload de planilha (.xlsx ou .csv)...")
