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

# --- REGRAS DE ESTILO E CONTRASTE PARA TELA E IMPRESSÃO / PDF ---
st.markdown("""
    <style>
    /* 1. TELA: Tabela limpa, sem faixas/zebrado branco e sem bordas internas */
    .tabela-relatorio {
        width: 100%;
        border-collapse: collapse;
        font-family: sans-serif;
        font-size: 14px;
        margin-bottom: 25px;
        background-color: transparent !important;
    }
    .tabela-relatorio th {
        background-color: #1f77b4 !important;
        color: #ffffff !important;
        text-align: left;
        padding: 10px;
        font-weight: bold;
        border: none !important;
    }
    .tabela-relatorio td {
        padding: 8px 10px;
        border: none !important;
        color: inherit;
    }
    .tabela-relatorio tr {
        background-color: transparent !important;
    }
    .tabela-relatorio tr.linha-total {
        font-weight: bold;
        background-color: rgba(31, 119, 180, 0.2) !important;
        border-top: 2px solid #1f77b4 !important;
    }

    /* 2. IMPRESSÃO / PDF: Ajuste de Layout, Contraste Limpo e Ocultação do Expander */
    @media print {
        /* Oculta sidebar, headers, botões e o expander de planilha */
        [data-testid="stSidebar"], header, [data-testid="stHeader"], footer, button, iframe, .stButton, .stExpander, details {
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

        /* Força fundo branco e textos pretos no PDF sem sombras */
        html, body, .main, [data-testid="stAppViewContainer"] {
            background-color: #ffffff !important;
            color: #000000 !important;
        }

        h1, h2, h3, h4, h5, h6, p, label, span, div {
            color: #000000 !important;
            text-shadow: none !important;
            -webkit-print-color-adjust: exact !important;
            print-color-adjust: exact !important;
        }

        [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {
            color: #000000 !important;
            text-shadow: none !important;
        }

        /* Tabela no papel/PDF com bordas limpas */
        .tabela-relatorio th {
            background-color: #222222 !important;
            color: #ffffff !important;
            border-bottom: 2px solid #000000 !important;
        }
        .tabela-relatorio td {
            color: #000000 !important;
            border-bottom: 1px solid #d0d0d0 !important;
        }
        .tabela-relatorio tr:nth-child(even) {
            background-color: #f8f9fa !important;
        }
        .tabela-relatorio tr.linha-total {
            background-color: #eaeff5 !important;
            color: #000000 !important;
            border-top: 2px solid #000000 !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

st.title("🎓 Dashboard de Diplomas Digitais")
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
        idx_data_homol = next((i for i, c in enumerate(cols) if 'homologa' in c.lower() or 'data' in c.lower() or 'mes' in c.lower()), 0)
        idx_data_concl = next((i for i, c in enumerate(cols) if 'conclu' in c.lower() or 'fim' in c.lower()), 0)
        idx_livro = next((i for i, c in enumerate(cols) if 'livro' in c.lower()), 0)
        idx_registro = next((i for i, c in enumerate(cols) if 'registro' in c.lower() or 'num' in c.lower()), 0)
        idx_processo = next((i for i, c in enumerate(cols) if 'processo' in c.lower() or 'proc' in c.lower() or 'protocolo' in c.lower()), 0)

        col_curso = st.sidebar.selectbox("Coluna de Cursos", cols, index=idx_curso)
        col_campus = st.sidebar.selectbox("Coluna de Campus", cols, index=idx_campus)
        col_data_homol = st.sidebar.selectbox("Coluna Data da Homologação", cols, index=idx_data_homol)
        col_data_concl = st.sidebar.selectbox("Coluna Concluído Em", cols, index=idx_data_concl)
        col_livro = st.sidebar.selectbox("Coluna de Livro", cols, index=idx_livro)
        col_registro = st.sidebar.selectbox("Coluna de N° Registro", cols, index=idx_registro)
        col_processo = st.sidebar.selectbox("Coluna N° do Processo", cols, index=idx_processo)

        # Conversão de Datas e Cálculo do Ciclo de Vida
        df[col_data_homol] = pd.to_datetime(df[col_data_homol], dayfirst=True, errors='coerce')
        df[col_data_concl] = pd.to_datetime(df[col_data_concl], dayfirst=True, errors='coerce')
        df['Ciclo_em_Dias'] = (df[col_data_concl] - df[col_data_homol]).dt.days

        # ==========================================
        # PÁGINA 1: KPIs + TABELAS DE RESUMO
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

        # 1. QUADRO RESUMO DE REGISTROS POR LIVRO
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

            html_tabela_livro = """<table class="tabela-relatorio">
                <thead>
                    <tr>
                        <th>Livro</th>
                        <th>Registros</th>
                        <th>Intervalo</th>
                    </tr>
                </thead>
                <tbody>"""
            
            for _, row in df_resumo.iterrows():
                html_tabela_livro += f"""<tr>
                    <td>{row['Livro']}</td>
                    <td>{row['Registros']}</td>
                    <td>{row['Intervalo']}</td>
                </tr>"""
                
            html_tabela_livro += f"""<tr class="linha-total">
                    <td>Total</td>
                    <td>{total_registros}</td>
                    <td></td>
                </tr>
                </tbody>
            </table>"""

            st.markdown(html_tabela_livro, unsafe_allow_html=True)
        else:
            st.warning("Selecione as colunas de 'Livro' e 'N° Registro' na barra lateral.")

        st.markdown("---")

        # 2. DISTRIBUIÇÃO DOS 20 MAIORES PRAZOS / CICLOS (FREQUÊNCIA)
        st.subheader("Distribuição dos 20 Maiores Prazos de Conclusão")
        
        df_valid_ciclo = df.dropna(subset=['Ciclo_em_Dias']).copy()
        df_valid_ciclo = df_valid_ciclo[df_valid_ciclo['Ciclo_em_Dias'] >= 0]
        
        if not df_valid_ciclo.empty:
            prazos_freq = df_valid_ciclo['Ciclo_em_Dias'].value_counts().reset_index()
            prazos_freq.columns = ['Ciclo (dias)', 'Quantidade de registros']
            prazos_top20 = prazos_freq.sort_values(by='Ciclo (dias)', ascending=False).head(20)

            html_tabela_prazos = """<table class="tabela-relatorio">
                <thead>
                    <tr>
                        <th>Ciclo (dias)</th>
                        <th>Quantidade de registros</th>
                    </tr>
                </thead>
                <tbody>"""
            
            for _, row in prazos_top20.iterrows():
                html_tabela_prazos += f"""<tr>
                    <td><b>{int(row['Ciclo (dias)'])} dias</b></td>
                    <td>{int(row['Quantidade de registros'])}</td>
                </tr>"""
                
            html_tabela_prazos += "</tbody></table>"
            st.markdown(html_tabela_prazos, unsafe_allow_html=True)
        else:
            st.info("Não foi possível calcular os prazos. Verifique as colunas de datas na barra lateral.")

        st.markdown("---")

        # 3. TOP 30 PROCESSOS COM MAIOR CICLO DE VIDA (EM DIAS)
        st.subheader("Top 30 Processos com Maior Ciclo de Vida (em dias)")
        
        top30_ciclo = df_valid_ciclo.sort_values(by='Ciclo_em_Dias', ascending=False).head(30)

        if not top30_ciclo.empty:
            html_tabela_ciclo = """<table class="tabela-relatorio">
                <thead>
                    <tr>
                        <th>#</th>
                        <th>N° do Processo</th>
                        <th>Homologação</th>
                        <th>Concluído Em</th>
                        <th>Ciclo de Vida (Dias)</th>
                    </tr>
                </thead>
                <tbody>"""
            
            for rank, (_, row) in enumerate(top30_ciclo.iterrows(), 1):
                data_h_str = row[col_data_homol].strftime('%d/%m/%Y') if pd.notna(row[col_data_homol]) else '-'
                data_c_str = row[col_data_concl].strftime('%d/%m/%Y') if pd.notna(row[col_data_concl]) else '-'
                proc_str = str(row[col_processo]) if pd.notna(row[col_processo]) else '-'
                
                html_tabela_ciclo += f"""<tr>
                    <td><b>{rank}</b></td>
                    <td>{proc_str}</td>
                    <td>{data_h_str}</td>
                    <td>{data_c_str}</td>
                    <td><b>{int(row['Ciclo_em_Dias'])} dias</b></td>
                </tr>"""
                
            html_tabela_ciclo += "</tbody></table>"
            st.markdown(html_tabela_ciclo, unsafe_allow_html=True)
        else:
            st.info("Não foi possível calcular o ciclo de vida. Verifique as colunas de datas e processo na barra lateral.")

        # FORÇA QUEBRA DE PÁGINA APÓS AS TABELAS
        st.markdown('<div class="quebra-pagina"></div>', unsafe_allow_html=True)

        # Configuração de Estilo Nítido e Limpo para os Gráficos
        plt.rcdefaults()
        sns.set_theme(style="whitegrid")

        # =======================================================
        # GRÁFICOS (PÁGINAS SEGUINTES)
        # =======================================================

        # 1. Diplomas por Curso (Top 15)
        st.subheader("Diplomas emitidos por Curso (Top 15)")
        fig1, ax1 = plt.subplots(figsize=(10, 4.2), dpi=300)
        fig1.patch.set_facecolor('white')
        ax1.set_facecolor('white')

        curso_counts = df[col_curso].value_counts().reset_index()
        curso_counts.columns = [col_curso, 'Qtd']
        top_cursos = curso_counts.head(15)

        sns.barplot(data=top_cursos, y=col_curso, x='Qtd', palette="Blues_r", ax=ax1)
        ax1.set_xlabel("Quantidade de Diplomas", fontsize=10, fontweight='bold', color='black')
        ax1.set_ylabel("", fontsize=10)
        ax1.tick_params(axis='both', labelsize=9, colors='black')
        
        for p in ax1.patches:
            width = p.get_width()
            if width > 0:
                ax1.annotate(f"{int(width)}",
                             (width + 0.5, p.get_y() + p.get_height() / 2.),
                             ha='left', va='center', fontsize=9, fontweight='bold', color='black')
                             
        ax1.set_xlim(0, top_cursos['Qtd'].max() * 1.1)
        st.pyplot(fig1)

        st.markdown("<br>", unsafe_allow_html=True)

        # 2. Diplomas por Campus
        st.subheader("Diplomas emitidos por Campus")
        fig2, ax2 = plt.subplots(figsize=(10, 3.8), dpi=300)
        fig2.patch.set_facecolor('white')
        ax2.set_facecolor('white')

        campus_counts = df[col_campus].value_counts().reset_index()
        campus_counts.columns = [col_campus, 'Qtd']

        sns.barplot(data=campus_counts, x=col_campus, y='Qtd', palette="viridis", ax=ax2)
        ax2.set_xlabel("", fontsize=10)
        ax2.set_ylabel("Quantidade de Diplomas", fontsize=10, fontweight='bold', color='black')
        ax2.tick_params(axis='both', labelsize=9, colors='black')
        plt.xticks(rotation=25, ha='right', fontsize=9, color='black')

        for p in ax2.patches:
            height = p.get_height()
            if height > 0:
                ax2.annotate(f"{int(height)}",
                             (p.get_x() + p.get_width() / 2., height + 2),
                             ha='center', va='bottom', fontsize=9, fontweight='bold', color='black')

        ax2.set_ylim(0, campus_counts['Qtd'].max() * 1.12)
        st.pyplot(fig2)

        # QUEBRA DE PÁGINA PARA O GRÁFICO TEMPORAL
        st.markdown('<div class="quebra-pagina"></div>', unsafe_allow_html=True)

        # 3. Diplomas por Mês de Homologação (SÉRIE TEMPORAL)
        st.subheader("Diplomas por Mês de Homologação")
        fig3, ax3 = plt.subplots(figsize=(10, 4.5), dpi=300)
        fig3.patch.set_facecolor('white')
        ax3.set_facecolor('white')

        df['AnoMes'] = df[col_data_homol].dt.to_period('M').astype(str)
        temporal_counts = df['AnoMes'].value_counts().sort_index().reset_index()
        temporal_counts.columns = ['Mês', 'Qtd']

        sns.lineplot(data=temporal_counts, x='Mês', y='Qtd', marker='o', linewidth=2, color='#1f77b4', ax=ax3)
        sns.barplot(data=temporal_counts, x='Mês', y='Qtd', alpha=0.3, color='#1f77b4', ax=ax3)

        ax3.tick_params(axis='both', labelsize=9, colors='black')
        for i, row in temporal_counts.iterrows():
            ax3.annotate(
                f"{int(row['Qtd'])}", 
                (i, row['Qtd']), 
                textcoords="offset points", 
                xytext=(0, 8), 
                ha='center', 
                va='bottom', 
                fontsize=9, 
                fontweight='bold',
                color='#003366'
            )

        ax3.set_ylim(0, temporal_counts['Qtd'].max() * 1.15)
        ax3.set_xlabel("Mês/Ano", fontsize=10, fontweight='bold', color='black')
        ax3.set_ylabel("Quantidade Emitida", fontsize=10, fontweight='bold', color='black')
        plt.xticks(rotation=45, fontsize=9, color='black')
        st.pyplot(fig3)

        # Tabela expansível na tela (Oculta automaticamente no PDF/Impressão)
        with st.expander("📋 Ver planilha de dados completa"):
            st.dataframe(df)

    except Exception as e:
        st.error(f"Erro ao processar a planilha: {e}")
else:
    st.info("Aguardando upload de planilha (.xlsx ou .csv)...")
