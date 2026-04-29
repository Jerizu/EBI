import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re

# --- CONFIGURAÇÕES E MAPEAMENTO ---
LIVROS_BIBLIA = [
    "Gênesis", "Êxodo", "Levítico", "Números", "Deuteronômio", "Josué", "Juízes", "Rute",
    "1 Samuel", "2 Samuel", "1 Reis", "2 Reis", "1 Crônicas", "2 Crônicas", "Esdras", "Neemias", "Ester",
    "Jó", "Salmos", "Provérbios", "Eclesiastes", "Cantares", "Isaías", "Jeremias", "Lamentações", "Ezequiel", "Daniel",
    "Oseias", "Joel", "Amós", "Obadias", "Jonas", "Miqueias", "Naum", "Habacuque", "Sofonias", "Ageu", "Zacarias", "Malaquias",
    "Mateus", "Marcos", "Lucas", "João", "Atos", "Romanos", "1 Coríntios", "2 Coríntios", "Gálatas", "Efésios", "Filipenses", "Colossenses",
    "1 Tessalonicenses", "2 Tessalonicenses", "1 Timóteo", "2 Timóteo", "Tito", "Filemom", "Hebreus", "Tiago",
    "1 Pedro", "2 Pedro", "1 João", "2 João", "3 João", "Judas", "Apocalipse"
]

MESES_PT = {
    1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr", 5: "Mai", 6: "Jun",
    7: "Jul", 8: "Ago", 9: "Set", 10: "Out", 11: "Nov", 12: "Dez"
}

def identificar_livro(texto):
    if not isinstance(texto, str) or texto == "": return "Outros / Temas Gerais"
    t = texto.upper().replace("I ", "1 ").replace("II ", "2 ")
    for livro in LIVROS_BIBLIA:
        if re.search(r'\b' + re.escape(livro.upper()) + r'\b', t):
            return livro
    return "Outros / Temas Gerais"

st.set_page_config(page_title="Dashboard EBI Profissional", layout="wide")

# --- CABEÇALHO ---
st.title("📊 Relatório de Gestão EBI")
st.markdown("### Dashboard com Linha do Tempo e Médias de Frequência")

arquivo = st.file_uploader("Carregue sua planilha (Excel ou CSV)", type=["xlsx", "csv"])

if arquivo:
    df = pd.read_csv(arquivo) if arquivo.name.endswith('csv') else pd.read_excel(arquivo)
    
    # Tratamento de Datas
    df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
    df = df.dropna(subset=['Data']).sort_values('Data')
    
    # Colunas de Tempo
    df['Ano'] = df['Data'].dt.year
    df['Mes_Num'] = df['Data'].dt.month
    df['Mes_Ano'] = df['Data'].dt.strftime('%Y-%m') # Ex: 2024-02
    df['Livro'] = df['História Contada'].apply(identificar_livro)

    # --- FILTRO DE LINHA DO TEMPO (ESTILO EXCEL) ---
    st.write("---")
    periodos_disponiveis = sorted(df['Mes_Ano'].unique())
    
    st.subheader("📅 Seleção de Período (Linha do Tempo)")
    if len(periodos_disponiveis) > 1:
        inicio, fim = st.select_slider(
            "Arraste para selecionar o intervalo de meses e anos:",
            options=periodos_disponiveis,
            value=(periodos_disponiveis[0], periodos_disponiveis[-1])
        )
        df_f = df[(df['Mes_Ano'] >= inicio) & (df['Mes_Ano'] <= fim)]
    else:
        df_f = df

    # Filtro de Localidade na Sidebar
    locais = ["Geral"] + sorted(df['Comum Congregação'].fillna("Não Informado").unique().tolist())
    loc_sel = st.sidebar.selectbox("Filtro por Casa de Oração", locais)
    if loc_sel != "Geral":
        df_f = df_f[df_f['Comum Congregação'] == loc_sel]

    # --- MÉTRICAS E MÉDIAS ---
    st.write("---")
    
    # Cálculo das Médias
    # Frequência mensal média dentro do período selecionado
    freq_mensal_base = df_f.groupby('Mes_Ano').size()
    media_mensal = freq_mensal_base.mean() if not freq_mensal_base.empty else 0
    
    # Frequência anual média
    freq_anual_base = df_f.groupby('Ano').size()
    media_anual = freq_anual_base.mean() if not freq_anual_base.empty else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total de Lições", len(df_f))
    col2.metric("Média Mensal", f"{media_mensal:.1f}")
    col3.metric("Média Anual", f"{media_anual:.1f}")
    col4.metric("Livro + Lido", df_f['Livro'].mode()[0] if not df_f.empty else "-")

    # --- GRÁFICOS ---
    st.write("---")
    
    # 1. Gráfico de Barras com Linha de Média
    st.subheader("📈 Frequência por Mês vs Média do Período")
    
    # Preparar dados do gráfico
    resumo_mensal = df_f.groupby(['Mes_Ano']).size().reset_index(name='Total')
    
    fig_barras = go.Figure()
    # Barras
    fig_barras.add_trace(go.Bar(
        x=resumo_mensal['Mes_Ano'], y=resumo_mensal['Total'],
        name='Lições no Mês', marker_color='#3498db'
    ))
    # Linha de Média Mensal
    fig_barras.add_trace(go.Scatter(
        x=resumo_mensal['Mes_Ano'], y=[media_mensal]*len(resumo_mensal),
        mode='lines', name='Média Mensal', line=dict(color='red', dash='dash')
    ))
    
    fig_barras.update_layout(xaxis_title="Mês/Ano", yaxis_title="Quantidade")
    st.plotly_chart(fig_barras, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("📚 Distribuição por Livro")
        fig_pizza = px.pie(df_f, names='Livro', hole=0.3)
        st.plotly_chart(fig_pizza, use_container_width=True)
    
    with c2:
        st.subheader("📋 Últimos Registros Filtrados")
        st.dataframe(df_f[['Data', 'Comum Congregação', 'Livro', 'História Contada']].tail(10), use_container_width=True)

else:
    st.info("👋 Bem-vindo! Por favor, carregue sua planilha Excel para visualizar a linha do tempo e as médias.")
