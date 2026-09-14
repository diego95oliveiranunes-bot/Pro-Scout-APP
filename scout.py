import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os

st.set_page_config(page_title="Modo Carreira Manager", layout="wide", page_icon="⚽")

# --- SISTEMA DE ARMAZENAMENTO ---
DB_FILE = "database_carreira.csv"

def carregar_dados():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame()

def salvar_dados(df_novo):
    df_novo.to_csv(DB_FILE, index=False)

# --- CONFIGURAÇÕES TÁTICAS ---
SUGESTOES_POSICAO = {
    "Atacante": ["Finalização", "Velocidade", "Agilidade", "Controle de Bola", "Posicionamento", "Força"],
    "Zagueiro": ["Posicionamento", "Força", "Impulsão", "Cabeceio", "Divididas", "Desarme"],
    "Meio-Campo": ["Visão", "Passe", "Controle de Bola", "Resistência", "Interceptação", "Agilidade"],
    "Lateral": ["Velocidade", "Cruzamento", "Resistência", "Desarme", "Drible", "Passe Curto"],
    "Goleiro": ["Reflexo", "Elasticidade", "Saída de Gol", "Posicionamento", "Jogo com os Pés", "Comunicação"]
}

TODOS_ATRIBUTOS = list(set([item for sublist in SUGESTOES_POSICAO.values() for item in sublist] + 
                           ["Resistência", "Interceptação", "Divididas", "Passe Curto", "Drible", "Cruzamento"]))

ESTILOS_TATICOS = {
    "Gegenpressing (Pressão)": ["Resistência", "Agilidade", "Divididas", "Velocidade", "Interceptação"],
    "Tiki-Taka (Posse de Bola)": ["Passe", "Visão", "Controle de Bola", "Passe Curto", "Posicionamento"],
    "Goleiro Líbero (Saída Curta)": ["Jogo com os Pés", "Passe Curto", "Visão", "Posicionamento", "Saída de Gol"],
    "Jogo de Pontas (Cruzamentos)": ["Velocidade", "Cruzamento", "Drible", "Agilidade", "Finalização"],
    "Jogo Direto (Longas)": ["Força", "Impulsão", "Cabeceio", "Passe", "Finalização"],
    "Contra-Ataque Rápido": ["Velocidade", "Agilidade", "Finalização", "Drible", "Visão"]
}

# --- INTERFACE LATERAL (REGISTRO) ---
st.sidebar.header("📝 Registrar / Atualizar Atleta")

status_in = st.sidebar.radio("Status no Modo Carreira", ["Meu Elenco", "Alvo de Transferência"])
nome_in = st.sidebar.text_input("Nome do Atleta").strip()
pos_in = st.sidebar.selectbox("Posição", list(SUGESTOES_POSICAO.keys()))

st.sidebar.subheader("Dados de Carreira")
col1, col2 = st.sidebar.columns(2)
idade_in = col1.number_input("Idade", min_value=15, max_value=45, value=22)
ovr_in = col2.number_input("OVR (Geral)", min_value=1, max_value=99, value=75)
pot_in = col1.number_input("Potencial", min_value=1, max_value=99, value=85)
valor_in = col2.number_input("Valor (€ Mi)", min_value=0.0, value=10.0, step=0.5)

attrs_val = {}
st.sidebar.subheader("Atributos Físicos/Técnicos (0-99)")
with st.sidebar.expander("Preencher Atributos Chave", expanded=False):
    for a in SUGESTOES_POSICAO[pos_in]:
        attrs_val[a] = st.number_input(a, min_value=0, max_value=99, value=ovr_in, step=1, key=f"p_{a}")
        
    comp = [a for a in TODOS_ATRIBUTOS if a not in SUGESTOES_POSICAO[pos_in]]
    for a in comp:
        attrs_val[a] = st.number_input(a, min_value=0, max_value=99, value=ovr_in-10, step=1, key=f"c_{a}")

if st.sidebar.button("💾 Salvar Atleta"):
    if nome_in:
        df_atual = carregar_dados()
        
        dados_completos = {a: 50 for a in TODOS_ATRIBUTOS}
        dados_completos.update(attrs_val)
        dados_completos.update({
            'Nome': nome_in, 'Status': status_in, 'Posição': pos_in, 
            'Idade': idade_in, 'OVR': ovr_in, 'Potencial': pot_in, 'Valor (€M)': valor_in
        })
        
        if not df_atual.empty:
            df_atual = df_atual[df_atual['Nome'] != nome_in]
            
        df_novo = pd.concat([df_atual, pd.DataFrame([dados_completos])], ignore_index=True)
        salvar_dados(df_novo)
        st.sidebar.success(f"{nome_in} salvo no banco de dados!")
        st.rerun()

# --- CONTEÚDO PRINCIPAL ---
st.title("⚽ Dashboard do Manager")
df = carregar_dados()

if not df.empty:
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Meu Elenco", "🎯 DNA Tático", "🏋️ Plano de Treino", "⚔️ Comparação (Scout)"])
    
    with tab1:
        st.header("Visão Geral do Plantel")
        df_elenco = df[df['Status'] == 'Meu Elenco']
        
        if not df_elenco.empty:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total de Jogadores", len(df_elenco))
            c2.metric("OVR Médio", round(df_elenco['OVR'].mean(), 1))
            c3.metric("Idade Média", round(df_elenco['Idade'].mean(), 1))
            c4.metric("Valor Total do Elenco", f"€ {df_elenco['Valor (€M)'].sum():.1f}M")
            
            # Tabela formatada para visualização rápida
            colunas_exibicao = ['Nome', 'Posição', 'Idade', 'OVR', 'Potencial', 'Valor (€M)']
            st.dataframe(df_elenco[colunas_exibicao].sort_values(by='OVR', ascending=False), use_container_width=True, hide_index=True)
        else:
            st.warning("Seu elenco está vazio. Registre jogadores e marque o status como 'Meu Elenco'.")

    with tab2:
        sel = st.selectbox("Selecione o Atleta para Análise Tática:", df['Nome'].unique())
        d = df[df['Nome'] == sel].iloc[0]
        fits = {e: round(sum([d.get(a, 0) for a in atts]) / len(atts), 1) for e, atts in ESTILOS_TATICOS.items()}
        fit_df = pd.DataFrame(list(fits.items()), columns=['Estilo', 'Fit %'])
        st.plotly_chart(px.bar(fit_df, x='Fit %', y='Estilo', orientation='h', color='Fit %', 
                               color_continuous_scale='RdYlGn', range_x=[0, 100]), use_container_width=True)

    with tab3:
        sel_treino = st.selectbox("Atleta para Treino:", df['Nome'].unique(), key='treino_sel')
        d_treino = df[df['Nome'] == sel_treino].iloc[0]
        estilo = st.selectbox("Estilo Tático Alvo:", list(ESTILOS_TATICOS.keys()))
        alvo_atts = ESTILOS_TATICOS[estilo]
        
        c1, c2 = st.columns(2)
        with c1:
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(r=[d_treino.get(a, 0) for a in alvo_atts], theta=alvo_atts, fill='toself', name='Atual'))
            fig.add_trace(go.Scatterpolar(r=[d_treino['Potencial']] * len(alvo_atts), theta=alvo_atts, line_dash='dash', name='Meta (Potencial)'))
            fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 99])))
            st.plotly_chart(fig, use_container_width=True)
            
        with c2:
            st.write(f"**Gaps de Evolução para {estilo}:**")
            for a in alvo_atts:
                val = d_treino.get(a, 0)
                meta = d_treino['Potencial']
                if val < meta:
                    st.progress(int(val), text=f"{a}: {val} (Meta: {meta})")

    with tab4:
        st.subheader("Central de Olheiros - Comparação")
        col_a, col_b = st.columns(2)
        j1 = col_a.selectbox("Jogador 1:", df['Nome'].unique(), index=0)
        j2 = col_b.selectbox("Jogador 2:", df['Nome'].unique(), index=min(1, len(df)-1) if len(df)>1 else 0)
        
        d1, d2 = df[df['Nome'] == j1].iloc[0], df[df['Nome'] == j2].iloc[0]
        atts_c = SUGESTOES_POSICAO[d1['Posição']]
        
        fig_c = go.Figure()
        fig_c.add_trace(go.Scatterpolar(r=[d1.get(a, 0) for a in atts_c], theta=atts_c, fill='toself', name=j1))
        fig_c.add_trace(go.Scatterpolar(r=[d2.get(a, 0) for a in atts_c], theta=atts_c, fill='toself', name=j2))
        fig_c.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 99]))) # Eixo travado em 99 para comparação real
        st.plotly_chart(fig_c, use_container_width=True)

    # Área de Gerenciamento de Dados no final da página
    st.divider()
    with st.expander("⚙️ Gerenciar Banco de Dados"):
        jogador_excluir = st.selectbox("Selecione um jogador para remover do banco:", df['Nome'].unique())
        if st.button("🗑️ Excluir Jogador"):
            df = df[df['Nome'] != jogador_excluir]
            salvar_dados(df)
            st.success(f"{jogador_excluir} foi removido!")
            st.rerun()

else:
    st.info("👋 Bem-vindo ao Gestor de Modo Carreira! Comece adicionando seus jogadores na barra lateral esquerda.")
