import streamlit as st
import pandas as pd
import plotly.express as px
import re
from datetime import datetime

# 1. BASE DE CONHECIMENTO (Expansível)
# O sistema usará isso para "adivinhar" o livro baseado em palavras-chave no título
MAPA_TEMATICO = {
    "Gênesis": ["Criação", "Adão", "Eva", "Caim", "Abel", "Noé", "Arca", "Dilúvio", "Babel", "Abraão", "Isaque", "Jacó", "José do Egito"],
    "Êxodo": ["Moisés", "Pragas", "Mar Vermelho", "Egito", "Mandamentos", "Tabernáculo"],
    "Juízes": ["Sansão", "Gideão", "Débora", "Dalila"],
    "1 Samuel": ["Davi", "Golias", "Samuel", "Saul"],
    "Daniel": ["Cova", "Leões", "Fornalha", "Nabucodonosor", "Sonho"],
    "Mateus": ["Sermão do Monte", "Beatitudes", "Reino dos Céus", "Parábolas de Jesus"],
    "Marcos": ["Milagres de Jesus", "Tempestade"],
    "Lucas": ["Zaqueu", "Bom Samaritano", "Filho Pródigo", "Marta", "Maria", "Nascimento de Jesus"],
    "João": ["Nicodemos", "Samaritana", "Lázaro", "Pão da Vida", "Cego de Nascença"],
    "Atos": ["Pentecostes", "Caminho de Damasco", "Paulo", "Pedro", "Viagens Missionárias"],
    "Salmos": ["Pastor", "Louvor", "Oração de Davi"]
}

LIVROS_BIBLIA = [
    "Gênesis", "Êxodo", "Levítico", "Números", "Deuteronômio", "Josué", "Juízes", "Rute",
    "1 Samuel", "2 Samuel", "1 Reis", "2 Reis", "1 Crônicas", "2 Crônicas", "Esdras", "Neemias", "Ester",
    "Jó", "Salmos", "Provérbios", "Eclesiastes", "Cantares", "Isaías", "Jeremias", "Lamentações", "Ezequiel", "Daniel",
    "Oseias", "Joel", "Amós", "Obadias", "Jonas", "Miqueias", "Naum", "Habacuque", "Sofonias", "Ageu", "Zacarias", "Malaquias",
    "Mateus", "Marcos", "Lucas", "João", "Atos", "Romanos", "1 Coríntios", "2 Coríntios", "Gálatas", "Efésios", "Filipenses", "Colossenses",
    "1 Tessalonicenses", "2 Tessalonicenses", "1 Timóteo", "2 Timóteo", "Tito", "Filemom", "Hebreus", "Tiago",
    "1 Pedro", "2 Pedro", "1 João", "2 João", "3 João", "Judas", "Apocalipse"
]

def identificar_livro_inteligente(texto):
    if not isinstance(texto, str) or texto == "": return "Não Identificado"
    t = texto.upper()
    
    # Busca 1: O nome do livro está escrito? (Ex: "Lucas 19")
    for livro in LIVROS_BIBLIA:
        if livro.upper() in t.replace("I ", "1 ").replace("II ", "2 "):
            return livro
            
    # Busca 2: Palavras-chave (Ex: "Zaqueu" -> Lucas)
    for livro, palavras in MAPA_TEMATICO.items():
        for p in palavras:
            if p.upper() in t:
                return livro
                
    return "Outros / Temas Gerais"

st.set_page_config(page_title="Relatórios EBI - Gestão", layout="wide")

st.title("📊 Gestão de Frequência e Relatórios Bíblicos")

arquivo = st.file_uploader("Suba sua planilha Excel", type=["xlsx", "csv"])

if arquivo:
    # Carregar Dados
    df = pd.read_csv(arquivo) if arquivo.name.endswith('csv') else pd.read_excel(arquivo)
    
    # Converter Coluna de Data
    df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
    df = df.dropna(subset=['Data']) # Remove linhas sem data
    
    # Criar colunas de Mês e Ano para o filtro
    df['Ano'] = df['Data'].dt.year
    df['Mes'] = df['Data'].dt.month_name()
    
    # Identificar Livro Automaticamente
    df['Livro_Identificado'] = df['História Contada'].apply(identificar_livro_inteligente)

    # --- FILTROS NO MENU LATERAL ---
    st.sidebar.header("Filtros de Período")
    
    anos = sorted(df['Ano'].unique())
    ano_sel = st.sidebar.multiselect("Selecione o(s) Ano(s)", anos, default=anos)
    
    meses = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    mes_sel = st.sidebar.multiselect("Selecione o(s) Mês(es)", meses, default=meses)
    
    st.sidebar.header("Filtros de Local")
    localidades = ["Geral"] + sorted(df['Comum Congregação'].fillna("Não Informado").unique().tolist())
    loc_sel = st.sidebar.selectbox("Localidade", localidades)

    # Aplicar Filtros
    df_filtrado = df[df['Ano'].isin(ano_sel) & df['Mes'].isin(mes_sel)]
    if loc_sel != "Geral":
        df_filtrado = df_filtrado[df_filtrado['Comum Congregação'] == loc_sel]

    # --- DASHBOARD ---
    st.subheader(f"Período: {', '.join(map(str, ano_sel))} - Local: {loc_sel}")
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Total de Lições", len(df_filtrado))
    m2.metric("Total Crianças", int(df_filtrado['Total Crianças\n2024-02-11 21:33:02'].sum()) if 'Total Crianças\n2024-02-11 21:33:02' in df.columns else "N/A")
    m3.metric("Livro mais lido", df_filtrado['Livro_Identificado'].mode()[0] if not df_filtrado.empty else "N/A")

    st.write("---")
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Frequência por Mês")
        # Gráfico de linha para ver a evolução no tempo
        freq_mensal = df_filtrado.groupby(['Ano', 'Mes']).size().reset_index(name='Quantidade')
        fig_evolucao = px.line(freq_mensal, x='Mes', y='Quantidade', color='Ano', markers=True)
        st.plotly_chart(fig_evolucao, use_container_width=True)

    with c2:
        st.subheader("Distribuição por Livro")
        fig_pizza = px.pie(df_filtrado, names='Livro_Identificado', hole=0.3)
        st.plotly_chart(fig_pizza, use_container_width=True)

    st.subheader("📖 Registros Detalhados")
    st.dataframe(df_filtrado[['Data', 'Comum Congregação', 'Livro_Identificado', 'História Contada']], use_container_width=True)
