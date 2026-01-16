import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os

st.set_page_config(page_title="ProScout Elite v7", layout="wide")

# --- SISTEMA DE ARMAZENAMENTO EM ARQUIVO (CSV) ---
# Usamos CSV pois é mais fácil de persistir no Cloud do que SQLite sem servidor externo
DB_FILE = "database_scout.csv"


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

TODOS_ATRIBUTOS = list(
    set([item for sublist in SUGESTOES_POSICAO.values() for item in sublist] + ["Resistência", "Interceptação",
                                                                                "Divididas", "Passe Curto", "Drible",
                                                                                "Cruzamento"]))

ESTILOS_TATICOS = {
    "Gegenpressing (Pressão)": ["Resistência", "Agilidade", "Divididas", "Velocidade", "Interceptação"],
    "Tiki-Taka (Posse de Bola)": ["Passe", "Visão", "Controle de Bola", "Passe Curto", "Posicionamento"],
    "Goleiro Líbero (Saída Curta)": ["Jogo com os Pés", "Passe Curto", "Visão", "Posicionamento", "Saída de Gol"],
    "Jogo de Pontas (Cruzamentos)": ["Velocidade", "Cruzamento", "Drible", "Agilidade", "Finalização"],
    "Jogo Direto (Longas)": ["Força", "Impulsão", "Cabeceio", "Passe", "Finalização"],
    "Contra-Ataque Rápido": ["Velocidade", "Agilidade", "Finalização", "Drible", "Visão"]
}

# --- INTERFACE LATERAL ---
st.sidebar.header("📝 Registo de Atleta")
nome_in = st.sidebar.text_input("Nome do Atleta").strip()
pos_in = st.sidebar.selectbox("Posição", list(SUGESTOES_POSICAO.keys()))

attrs_val = {}
st.sidebar.subheader("Atributos (0-100)")
st.sidebar.info("Digite os valores abaixo:")

# Substituído Sliders por Number Input para facilitar digitação
for a in SUGESTOES_POSICAO[pos_in]:
    attrs_val[a] = st.sidebar.number_input(a, min_value=0, max_value=100, value=50, step=1, key=f"p_{a}")

with st.sidebar.expander("Atributos Complementares"):
    comp = [a for a in TODOS_ATRIBUTOS if a not in SUGESTOES_POSICAO[pos_in]]
    for a in comp:
        attrs_val[a] = st.sidebar.number_input(a, min_value=0, max_value=100, value=30, step=1, key=f"c_{a}")

if st.sidebar.button("💾 Salvar Atleta"):
    if nome_in:
        df_atual = carregar_dados()

        dados_completos = {a: 30 for a in TODOS_ATRIBUTOS}
        dados_completos.update(attrs_val)
        dados_completos['Nome'] = nome_in
        dados_completos['Posição'] = pos_in

        # Remove se já existir para atualizar
        if not df_atual.empty:
            df_atual = df_atual[df_atual['Nome'] != nome_in]

        df_novo = pd.concat([df_atual, pd.DataFrame([dados_completos])], ignore_index=True)
        salvar_dados(df_novo)
        st.sidebar.success(f"{nome_in} salvo!")
        st.rerun()

# --- CONTEÚDO PRINCIPAL ---
df = carregar_dados()

if not df.empty:
    tab1, tab2, tab3 = st.tabs(["🎯 DNA Tático", "🏋️ Plano de Treino", "⚔️ Comparação"])

    with tab1:
        sel = st.selectbox("Selecione o Atleta:", df['Nome'].unique())
        d = df[df['Nome'] == sel].iloc[0]
        fits = {e: round(sum([d.get(a, 0) for a in atts]) / len(atts), 1) for e, atts in ESTILOS_TATICOS.items()}
        fit_df = pd.DataFrame(list(fits.items()), columns=['Estilo', 'Fit %'])
        st.plotly_chart(
            px.bar(fit_df, x='Fit %', y='Estilo', orientation='h', color='Fit %', color_continuous_scale='RdYlGn',
                   range_x=[0, 100]), use_container_width=True)

    with tab2:
        estilo = st.selectbox("Estilo Alvo:", list(ESTILOS_TATICOS.keys()))
        alvo_atts = ESTILOS_TATICOS[estilo]
        c1, c2 = st.columns(2)
        with c1:
            fig = go.Figure()
            fig.add_trace(
                go.Scatterpolar(r=[d.get(a, 0) for a in alvo_atts], theta=alvo_atts, fill='toself', name='Atual'))
            fig.add_trace(go.Scatterpolar(r=[90] * len(alvo_atts), theta=alvo_atts, line_dash='dash', name='Elite'))
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            st.write("**Gaps de Evolução:**")
            for a in alvo_atts:
                val = d.get(a, 0)
                if val < 80: st.write(f"- {a}: {val} → Meta 85+")

    with tab3:
        st.subheader("Comparação de Jogadores")
        col_a, col_b = st.columns(2)
        j1 = col_a.selectbox("Jogador 1:", df['Nome'].unique(), index=0)
        j2 = col_b.selectbox("Jogador 2:", df['Nome'].unique(), index=min(1, len(df) - 1) if len(df) > 1 else 0)

        d1, d2 = df[df['Nome'] == j1].iloc[0], df[df['Nome'] == j2].iloc[0]
        atts_c = SUGESTOES_POSICAO[d1['Posição']]

        fig_c = go.Figure()
        fig_c.add_trace(go.Scatterpolar(r=[d1.get(a, 0) for a in atts_c], theta=atts_c, fill='toself', name=j1))
        fig_c.add_trace(go.Scatterpolar(r=[d2.get(a, 0) for a in atts_c], theta=atts_c, fill='toself', name=j2))
        st.plotly_chart(fig_c, use_container_width=True)

        if st.button("🗑️ Excluir Jogador Selecionado"):
            df_atual = carregar_dados()
            df_atual = df_atual[df_atual['Nome'] != sel]
            salvar_dados(df_atual)
            st.rerun()
else:
    st.info("O banco de dados está vazio. Registre atletas na lateral.")