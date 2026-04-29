import streamlit as st
import pandas as pd
import plotly.express as px
import re

# 1. MAPEAMENTO DE LIVROS E PALAVRAS-CHAVE (Melhorado)
MAPA_TEMATICO = {
    "Gênesis": ["Criação", "Adão", "Eva", "Caim", "Abel", "Noé", "Arca", "Dilúvio", "Babel", "Abraão", "Isaque", "Jacó", "José do Egito", "Sonhos de José"],
    "Êxodo": ["Moisés", "Pragas", "Mar Vermelho", "Egito", "Mandamentos", "Tabernáculo", "Bezalel"],
    "Juízes": ["Sansão", "Gideão", "Débora", "Dalila", "Baraque"],
    "1 Samuel": ["Davi", "Golias", "Samuel", "Saul", "Jônatas"],
    "2 Samuel": ["Bate-Seba", "Absalão"],
    "1 Reis": ["Salomão", "Elias", "Rainha de Sabá"],
    "2 Reis": ["Eliseu", "Naamã", "Jezabel"],
    "Daniel": ["Cova", "Leões", "Fornalha", "Nabucodonosor", "Sadraque", "Mesaque", "Abednego"],
    "Mateus": ["Sermão do Monte", "Beatitudes", "Magos", "Estrela de Belém"],
    "Marcos": ["Tempestade", "Cego de Jericó"],
    "Lucas": ["Zaqueu", "Bom Samaritano", "Filho Pródigo", "Marta", "Maria", "Nascimento de Jesus", "Anunciação"],
    "João": ["Nicodemos", "Samaritana", "Lázaro", "Canaã", "Bodas"],
    "Atos": ["Pentecostes", "Damasco", "Paulo", "Estêvão", "Cornélio"],
    "Ester": ["Hamã", "Mordecai", "Rei Assuero"],
    "Jonas": ["Peixe", "Nínive"]
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

MESES_PT = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}

def identificar_livro(texto):
    if not isinstance(texto, str) or texto == "": return "Outros / Temas Gerais"
    t = texto.upper().replace("I ", "1 ").replace("II ", "2 ")
    
    # 1. Busca direta por nome do livro
    for livro in LIVROS_BIBLIA:
        if re.search(r'\b' + re.escape(livro.upper()) + r'\b', t):
            return livro
            
    # 2. Busca por temas/personagens
    for livro, palavras in MAPA_TEMATICO.items():
        for p in palavras:
            if p.upper() in t:
                return livro
                
    return "Outros / Temas Gerais"

st.set_page_config(page_title="Relatórios EBI", layout="wide")
st.title("📊 Painel de Controle EBI - Relatórios Locais")

arquivo = st.file_uploader("Suba sua planilha Excel", type=["xlsx", "csv"])

if arquivo:
    df = pd.read_csv(arquivo) if arquivo.name.endswith('csv') else pd.read_excel(arquivo)
    
    # Tratamento de Datas
    df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
    df = df.dropna(subset=['Data']).sort_values('Data')
    
    df['Ano'] = df['Data'].dt.year
    df['Mes_Num'] = df['Data'].dt.month
    df['Mes_Nome'] = df['Mes_Num'].map(MESES_PT)
    df['Livro'] = df['História Contada'].apply(identificar_livro)

    # Filtros Laterais
    st.sidebar.header("Filtros de Navegação")
    
    # Filtro de Ano
    anos = sorted(df['Ano'].unique())
    ano_sel = st.sidebar.multiselect("Anos", anos, default=anos)
    
    # Filtro de Localidade
    locais = ["Geral"] + sorted(df['Comum Congregação'].fillna("Não Informado").unique().tolist())
    loc_sel = st.sidebar.selectbox("Localidade", locais)

    # Aplicação dos Filtros
    df_f = df[df['Ano'].isin(ano_sel)]
    if loc_sel != "Geral":
        df_f = df_f[df_f['Comum Congregação'] == loc_sel]

    # --- DASHBOARD VISUAL ---
    
    # 1. Gráfico de Barras por Mês (Ordem Crescente)
    st.subheader("📈 Frequência Mensal de Lições")
    freq_mensal = df_f.groupby(['Mes_Num', 'Mes_Nome']).size().reset_index(name='Total')
    # Garantir ordem de Janeiro a Dezembro
    freq_mensal = freq_mensal.sort_values('Mes_Num')
    
    fig_barras = px.bar(freq_mensal, x='Mes_Nome', y='Total', 
                        text='Total', color_discrete_sequence=['#3498db'],
                        labels={'Mes_Nome': 'Mês', 'Total': 'Quantidade de Histórias'})
    st.plotly_chart(fig_barras, use_container_width=True)

    # 2. Linha do Tempo e Livros
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("⏳ Linha do Tempo (Evolução)")
        # Mostra o acumulado por dia para ver o intervalo
        timeline_data = df_f.groupby(df_f['Data'].dt.date).size().reset_index(name='Contagem')
        fig_line = px.line(timeline_data, x='Data', y='Contagem', title="Atividades ao longo do tempo")
        st.plotly_chart(fig_line, use_container_width=True)

    with col2:
        st.subheader("📖 Cobertura Bíblica (%)")
        fig_pizza = px.pie(df_f, names='Livro', hole=0.3, color_discrete_sequence=px.colors.qualitative.Safe)
        st.plotly_chart(fig_pizza, use_container_width=True)

    # 3. Tabela de Conferência
    st.subheader("📋 Lista Detalhada do Período")
    st.dataframe(df_f[['Data', 'Comum Congregação', 'Livro', 'História Contada']], use_container_width=True)

    # Botão de Exportação (Dica)
    st.sidebar.markdown("---")
    st.sidebar.write("💡 Para salvar o relatório, clique com o botão direito nos gráficos ou use o comando de imprimir do seu navegador (Ctrl+P).")

else:
    st.info("Aguardando upload da planilha para gerar as análises...")
