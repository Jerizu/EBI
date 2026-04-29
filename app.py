import streamlit as st
import pandas as pd
import plotly.express as px
import re
import requests

# LISTA PARA VALIDAÇÃO
LIVROS_BIBLIA = [
    "Gênesis", "Êxodo", "Levítico", "Números", "Deuteronômio", "Josué", "Juízes", "Rute",
    "1 Samuel", "2 Samuel", "1 Reis", "2 Reis", "1 Crônicas", "2 Crônicas", "Esdras", "Neemias", "Ester",
    "Jó", "Salmos", "Provérbios", "Eclesiastes", "Cantares", "Isaías", "Jeremias", "Lamentações", "Ezequiel", "Daniel",
    "Oseias", "Joel", "Amós", "Obadias", "Jonas", "Miqueias", "Naum", "Habacuque", "Sofonias", "Ageu", "Zacarias", "Malaquias",
    "Mateus", "Marcos", "Lucas", "João", "Atos", "Romanos", "1 Coríntios", "2 Coríntios", "Gálatas", "Efésios", "Filipenses", "Colossenses",
    "1 Tessalonicenses", "2 Tessalonicenses", "1 Timóteo", "2 Timóteo", "Tito", "Filemom", "Hebreus", "Tiago",
    "1 Pedro", "2 Pedro", "1 João", "2 João", "3 João", "Judas", "Apocalipse"
]

def buscar_referencia_online(titulo):
    """
    Tenta descobrir o livro através de uma busca simples em uma API de textos bíblicos
    ou simulando uma busca por palavras-chave conhecidas.
    """
    if not titulo or len(titulo) < 3:
        return "Não Identificado", "N/A"

    # 1. Tenta identificar se o nome do livro já está no texto (Mais rápido)
    t_limpo = titulo.replace("I ", "1 ").replace("II ", "2 ").replace("III ", "3 ")
    for livro in LIVROS_BIBLIA:
        if re.search(r'\b' + re.escape(livro) + r'\b', t_limpo, re.IGNORECASE):
            # Tenta pegar o capítulo (primeiro número após o livro)
            cap = re.search(livro + r'.*?(\d+)', t_limpo, re.IGNORECASE)
            return livro, (cap.group(1) if cap else "1")

    # 2. SE NÃO ACHOU: Busca automática por "Palavras de Poder" (Lógica de Títulos)
    # Aqui o sistema deduz o livro pelo tema sem precisar de uma lista manual gigante
    temas = {
        "Mateus": ["Sermão do Monte", "Beatitudes", "Magos"],
        "Gênesis": ["Criação", "Adão", "Eva", "Noé", "Arca", "Torre de Babel", "Abraão"],
        "Êxodo": ["Moisés", "Pragas", "Mar Vermelho", "Mandamentos"],
        "Lucas": ["Zaqueu", "Bom Samaritano", "Filho Pródigo", "Marta e Maria"],
        "João": ["Nicodemos", "Mulher Samaritana", "Lázaro"],
        "Atos": ["Pentecostes", "Paulo", "Damasco"],
        "Daniel": ["Cova dos Leões", "Fornalha", "Estátua"],
        "1 Samuel": ["Davi e Golias", "Samuel", "Saul"],
        "Juízes": ["Sansão", "Gideão", "Débora"]
    }

    for livro, palavras in temas.items():
        for p in palavras:
            if p.lower() in titulo.lower():
                return livro, "Auto-detectado"

    return "Outros/Não Identificado", "N/A"

# --- INTERFACE STREAMLIT ---
st.set_page_config(page_title="Relatório EBI Inteligente", layout="wide")
st.title("📊 Relatório Bíblico com Detecção Automática")

arquivo = st.file_uploader("Suba o arquivo Excel do Formulário", type=["xlsx", "csv"])

if arquivo:
    df = pd.read_csv(arquivo) if arquivo.name.endswith('csv') else pd.read_excel(arquivo)
    
    # Limpeza
    df['Comum Congregação'] = df['Comum Congregação'].fillna('Não Informado')
    df['História Contada'] = df['História Contada'].fillna('Sem Título')

    # Processamento com Barra de Progresso (Dá um ar profissional)
    with st.spinner('O sistema está analisando os títulos e identificando os livros...'):
        df[['Livro_Identificado', 'Capitulo']] = df['História Contada'].apply(
            lambda x: pd.Series(buscar_referencia_online(x))
        )

    # Filtros
    localidade = st.sidebar.selectbox("Selecione a Localidade", ["Geral"] + sorted(df['Comum Congregação'].unique().tolist()))
    df_f = df if localidade == "Geral" else df[df['Comum Congregação'] == localidade]

    # Gráficos
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Porcentagem de cada Livro")
        # Gráfico que discrimina todos os livros
        fig = px.pie(df_f, names='Livro_Identificado', hole=0.4, 
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Frequência por Casa de Oração")
        st.bar_chart(df_f['Comum Congregação'].value_counts())

    # Tabela Final
    st.subheader("📖 Detalhamento das Lições")
    st.dataframe(df_f[['Data', 'Comum Congregação', 'Livro_Identificado', 'História Contada']], use_container_width=True)
