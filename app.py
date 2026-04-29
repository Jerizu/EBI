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
    if not isinstance(texto, str): return "Livro não identificado"
    # Padroniza numerais romanos e espaços
    t = texto.upper().replace("I ", "1 ").replace("II ", "2 ").replace("III ", "3 ")
    for livro in LIVROS_66:
        if livro.upper() in t:
            return livro
    return "Livro não especificado"

st.set_page_config(page_title="Relatórios - EBI", layout="wide")
st.title("📊 Sistema de Relatórios Bíblicos")

arquivo = st.file_uploader("Arraste aqui o seu arquivo do Excel ou CSV", type=["xlsx", "csv"])

if arquivo:
    try:
        # Carregamento robusto
        if arquivo.name.endswith('csv'):
            df = pd.read_csv(arquivo)
        else:
            df = pd.read_excel(arquivo)

        # Limpeza de dados críticos
        df['Comum Congregação'] = df['Comum Congregação'].fillna('Não Informado').astype(str)
        df['História Contada'] = df['História Contada'].fillna('').astype(str)
        df['Livro'] = df['História Contada'].apply(identificar_livro)
        
        # Sidebar - Filtros
        st.sidebar.header("Configurações")
        # O segredo para o erro não voltar: converter para set, depois lista, e garantir que tudo é string
        lista_locais = sorted(list(df['Comum Congregação'].unique()))
        localidades = ["Geral (Todas as Congregações)"] + lista_locais
        opcao = st.sidebar.selectbox("Selecione a Localidade", localidades)
        
        dados_finais = df if opcao == "Geral (Todas as Congregações)" else df[df['Comum Congregação'] == opcao]
        
        # Dashboard Visual
        st.subheader(f"Análise: {opcao}")
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            st.metric("Total de Histórias", len(dados_finais))
        
        # Gráfico de Livros (Discrimina todos os identificados)
        st.write("---")
        c1, c2 = st.columns(2)
        
        with c1:
            st.subheader("Frequência por Congregação")
            st.bar_chart(dados_finais['Comum Congregação'].value_counts())
            
        with c2:
            st.subheader("Distribuição por Livro lido")
            # Agrupa por livro e conta
            contagem_livros = dados_finais['Livro'].value_counts().reset_index()
            contagem_livros.columns = ['Livro', 'Qtd']
            fig = px.pie(contagem_livros, values='Qtd', names='Livro', hole=0.4)
            st.plotly_chart(fig, use_container_width=True)

        # Tabela Detalhada de Capítulos
        st.subheader("📖 Lista de Capítulos e Histórias Registradas")
        st.dataframe(
            dados_finais[['Data', 'Comum Congregação', 'Livro', 'História Contada']], 
            use_container_width=True
        )

        # Exportação
        st.sidebar.markdown("---")
        st.sidebar.info("Para salvar o relatório, utilize o botão de imprimir do navegador ou as opções de download do Streamlit.")

    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")
else:
    st.info("👋 Olá! Por favor, suba a planilha excel para gerar os gráficos e relatórios.")
