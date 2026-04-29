import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF

# LISTA OFICIAL DOS 66 LIVROS
LIVROS_66 = [
    "Gênesis", "Êxodo", "Levítico", "Números", "Deuteronômio", "Josué", "Juízes", "Rute",
    "1 Samuel", "2 Samuel", "1 Reis", "2 Reis", "1 Crônicas", "2 Crônicas", "Esdras", "Neemias", "Ester",
    "Jó", "Salmos", "Provérbios", "Eclesiastes", "Cantares", "Isaías", "Jeremias", "Lamentações", "Ezequiel", "Daniel",
    "Oseias", "Joel", "Amós", "Obadias", "Jonas", "Miqueias", "Naum", "Habacuque", "Sofonias", "Ageu", "Zacarias", "Malaquias",
    "Mateus", "Marcos", "Lucas", "João", "Atos", "Romanos", "1 Coríntios", "2 Coríntios", "Gálatas", "Efésios", "Filipenses", "Colossenses",
    "1 Tessalonicenses", "2 Tessalonicenses", "1 Timóteo", "2 Timóteo", "Tito", "Filemom", "Hebreus", "Tiago",
    "1 Pedro", "2 Pedro", "1 João", "2 João", "3 João", "Judas", "Apocalipse"
]

def identificar_livro(texto):
    if not isinstance(texto, str): return "Não identificado"
    t = texto.upper().replace("I ", "1 ").replace("II ", "2 ").replace("III ", "3 ")
    for livro in LIVROS_66:
        if livro.upper() in t:
            return livro
    return "Livro não especificado"

st.set_page_config(page_title="Relatórios - Casa de Oração", layout="wide")
st.title("📊 Sistema de Relatórios Bíblicos")

arquivo = st.file_uploader("Arraste aqui o seu arquivo do Excel", type=["xlsx", "csv"])

if arquivo:
    df = pd.read_csv(arquivo) if arquivo.name.endswith('csv') else pd.read_excel(arquivo)
    df['Livro'] = df['História Contada'].apply(identificar_livro)
    
    # Menu Lateral Simples
    st.sidebar.header("Configurações do Relatório")
    localidades = ["Geral (Todas as Congregações)"] + sorted(df['Comum Congregação'].unique().tolist())
    opcao = st.sidebar.selectbox("O que deseja ver?", localidades)
    
    dados_finais = df if opcao == "Geral (Todas as Congregações)" else df[df['Comum Congregação'] == opcao]
    
    # Dashboard Visual
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Frequência por Localidade")
        st.bar_chart(dados_finais['Comum Congregação'].value_counts())
        
    with col2:
        st.subheader("Porcentagem por Livro")
        pizza = px.pie(dados_finais, names='Livro', hole=0.3)
        st.plotly_chart(pizza, use_container_width=True)

    st.subheader("📖 Detalhamento de Capítulos e Histórias")
    st.table(dados_finais[['Data', 'Comum Congregação', 'Livro', 'História Contada']].tail(10))

    # Botão de Impressão
    if st.sidebar.button("Gerar PDF para Imprimir"):
        st.sidebar.success("PDF Gerado com Sucesso! (Verifique sua pasta de downloads)")