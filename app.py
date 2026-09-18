import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(
    page_title="Dashboard de Homologação de Diplomas",
    page_icon="🎓",
    layout="wide"
)

# --- REGRAS DE ESTILO E QUEBRA DE PÁGINA PARA IMPRESSÃO / PDF ---
st.markdown("""
    <style>
    /* Estilização da tabela HTML nativa na tela */
    .tabela-relatorio {
        width: 100%;
        border-collapse: collapse;
        font-family: sans-serif;
        font-size: 15px;
        margin-bottom: 20px;
    }
    .tabela-relatorio th {
        background-color: #1f77b4;
        color: white;
        text-align: left;
        padding: 10px;
        font-weight: bold;
    }
    .tabela-relatorio td {
        padding: 8px 10px;
        border-bottom: 1px solid #ddd;
    }
    .tabela-relatorio tr:nth-child(even) {
        background-color: #f9f9f9;
    }
    .tabela-relatorio tr.linha-total {
        font-weight: bold;
        background-color: #e6f2ff !important;
        border-top: 2px solid #1f77b4;
    }

    /* REGRAS EXCLUSIVAS DE IMPRESSÃO (@media print) */
    @media print {
        /* Oculta sidebar, headers e botões */
        [data-testid="stSidebar"], header, [data-testid="stHeader"], footer, button, iframe, .stButton {
            display: none !important;
        }
        
        /* Ajusta margens da página principal */
        .main .block-container {
            padding: 0.5cm !important;
            max-width: 100% !important;
        }

        /* Define quebras de página explícitas */
        .quebra-pagina {
            page-break-after: always !important;
            break-after: page !important;
        }

        /* Garante cor de fundo e textos pretos para impressão legível */
        body, .main {
            background-color: white !important;
            color: black !important;
        }
        
        .tabela-relatorio th {
            background-color: #333 !important;
            color: white !important;
        }
        .tabela-relatorio td {
            color: black !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

st.title("🎓 Dashboard de Emissão de Diplomas Digitais")
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

        # --- BOTÃO DE IMPRESSÃO NA SIDEBAR ---
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

        # Mapeamento dinâmico de colunas
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

        # ==========================================
        # PÁGINA 1: KPIs + TABELA COMPLETA POR LIVRO
        # ==========================================
        st.markdown("### 📊 Visão Geral")
        kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
        
        with kpi_col1:
            st.metric(label="Total de Diplomas Emitidos", value=f"{len(df):,}".replace(",", "."))
        with kpi_col2:
            st.metric(label="Total de Cursos Atendidos", value=df[col_curso].nunique())
        with kpi_col3:
            st.metric(label="Total de Campus Atendidos", value=df[col_campus].nunique())

        st.markdown("---")

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
            total_registros = df_resumo["Registros"].sum()

            # Construção da Tabela HTML sem rolagem (Exibe 100% das linhas)
            html_tabela = """<table class="tabela-relatorio">
                <thead>
                    <tr>
                        <th>Livro</th>
                        <th>Registros</th>
                        <th>Intervalo</th>
                    </tr>
                </thead>
                <tbody>"""
            
            for _, row in df_resumo.iterrows():
                html_tabela += f"""<tr>
                    <td>{row['Livro']}</td>
                    <td>{row['Registros']}</td>
                    <td>{row['Intervalo']}</td>
                </tr>"""
                
            # Linha final de Total
            html_tabela += f"""<tr class="linha-total">
                    <td>Total</td>
                    <td>{total_registros}</td>
                    <td></td>
                </tr>
                </tbody>
            </table>"""

            st.markdown(html_tabela, unsafe_allow_html=True)
        else:
            st.warning("Selecione as colunas de 'Livro' e 'N° Registro' na barra lateral.")

        # FORÇA QUEBRA DE PÁGINA APÓS A PÁGINA 1
        st.markdown('<div class="quebra-pagina"></div>', unsafe_allow_html=True)

        # Estilo dos Gráficos
        sns.set_theme(style="whitegrid")

        # ==========================================
        # PÁGINA 2: GRÁFICO POR CURSO
        # ==========================================
        st.subheader("Diplomas emitidos por Curso (Top 15)")
        fig1, ax1 = plt.subplots(figsize=(12, 7), dpi=300)
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

        # FORÇA QUEBRA DE PÁGINA APÓS O GRÁFICO 1
        st.markdown('<div class="quebra-pagina"></div>', unsafe_allow_html=True)

        # ==========================================
        # PÁGINA 3: GRÁFICO POR CAMPUS
        # ==========================================
        st.subheader("Diplomas emitidos por Campus")
        fig2, ax2 = plt.subplots(figsize=(12, 6), dpi=300)
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

        # FORÇA QUEBRA DE PÁGINA APÓS O GRÁFICO 2
        st.markdown('<div class="quebra-pagina"></div>', unsafe_allow_html=True)

        # ==========================================
        # PÁGINA 4: EVOLUÇÃO MENSAL (SÉRIE TEMPORAL)
        # ==========================================
        st.subheader("Diplomas por Mês de Homologação")
        fig3, ax3 = plt.subplots(figsize=(12, 5.5), dpi=300)
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

        # Tabela expansível na tela (opcional)
        with st.expander("📋 Ver planilha de dados completa"):
            st.dataframe(df)

    except Exception as e:
        st.error(f"Erro ao processar a planilha: {e}")
else:
    st.info("Aguardando upload de planilha (.xlsx ou .csv)...")
