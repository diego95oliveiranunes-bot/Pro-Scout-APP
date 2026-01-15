import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="ProScout Elite v6", layout="wide")

# --- CONFIGURAÇÃO DE ATRIBUTOS E ESTILOS ---
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

if 'db_tactical' not in st.session_state:
    st.session_state.db_tactical = pd.DataFrame()

# --- SIDEBAR ---
st.sidebar.header("📝 Registo de Atleta")
nome = st.sidebar.text_input("Nome").strip()
posicao = st.sidebar.selectbox("Posição", list(SUGESTOES_POSICAO.keys()))

attrs_input = {}
st.sidebar.subheader(f"Principais: {posicao}")
for attr in SUGESTOES_POSICAO[posicao]:
    attrs_input[attr] = st.sidebar.slider(attr, 0, 100, 50, key=f"main_{attr}")

with st.sidebar.expander("Atributos Complementares"):
    outros_attrs = [a for a in TODOS_ATRIBUTOS if a not in SUGESTOES_POSICAO[posicao]]
    for attr in outros_attrs:
        attrs_input[attr] = st.sidebar.slider(attr, 0, 100, 30, key=f"comp_{attr}")

if st.sidebar.button("Gravar Atleta"):
    if nome:
        dados_completos = {a: 0 for a in TODOS_ATRIBUTOS}
        dados_completos.update(attrs_input)
        novo_perfil = {"Nome": nome, "Posição": posicao, **dados_completos}
        if not st.session_state.db_tactical.empty and nome in st.session_state.db_tactical['Nome'].values:
            st.session_state.db_tactical = st.session_state.db_tactical[st.session_state.db_tactical['Nome'] != nome]
        st.session_state.db_tactical = pd.concat([st.session_state.db_tactical, pd.DataFrame([novo_perfil])],
                                                 ignore_index=True)
        st.success(f"Perfil de {nome} atualizado!")

# --- DASHBOARD ---
if not st.session_state.db_tactical.empty:
    df = st.session_state.db_tactical.copy()
    st.title("⚽ ProScout Elite: Sistema de Recrutamento")

    tab1, tab2, tab3 = st.tabs(["🎯 Encaixe Tático", "🏋️ Plano de Treino", "⚔️ Comparação de Mercado"])

    with tab1:
        jogador_sel = st.selectbox("Analisar Jogador:", df['Nome'].unique(), key="sel_tab1")
        dados_j = df[df['Nome'] == jogador_sel].iloc[0]
        fit_results = {e: round(sum([dados_j.get(a, 0) for a in attrs]) / len(attrs), 1) for e, attrs in
                       ESTILOS_TATICOS.items()}
        fit_df = pd.DataFrame(list(fit_results.items()), columns=['Estilo', 'Fit %'])
        st.plotly_chart(
            px.bar(fit_df, x='Fit %', y='Estilo', orientation='h', color='Fit %', color_continuous_scale='RdYlGn',
                   range_x=[0, 100]), use_container_width=True)

    with tab2:
        estilo_alvo = st.selectbox("Otimizar para estilo:", list(ESTILOS_TATICOS.keys()), key="sel_tab2")
        attrs_alvo = ESTILOS_TATICOS[estilo_alvo]
        col1, col2 = st.columns(2)
        with col1:
            fig_pdi = go.Figure()
            fig_pdi.add_trace(
                go.Scatterpolar(r=[dados_j.get(a, 0) for a in attrs_alvo], theta=attrs_alvo, fill='toself',
                                name='Atual'))
            fig_pdi.add_trace(
                go.Scatterpolar(r=[90] * len(attrs_alvo), theta=attrs_alvo, line_dash='dash', name='Meta'))
            fig_pdi.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])))
            st.plotly_chart(fig_pdi, use_container_width=True)
        with col2:
            st.write("**Gaps Críticos:**")
            for a in attrs_alvo:
                if dados_j.get(a, 0) < 80: st.write(f"- {a}: {dados_j.get(a, 0)} (Alvo: 85+)")

    with tab3:
        st.subheader("Frente a Frente: Plantel vs Alvo")
        c1, c2 = st.columns(2)
        j1 = c1.selectbox("Jogador do Plantel (Referência):", df['Nome'].unique(), index=0)
        j2 = c2.selectbox("Alvo de Mercado (Contratação):", df['Nome'].unique(), index=min(1, len(df) - 1))

        # Comparação de radar
        d1 = df[df['Nome'] == j1].iloc[0]
        d2 = df[df['Nome'] == j2].iloc[0]
        # Usamos os atributos da posição do jogador de referência para comparar
        atts_comp = SUGESTOES_POSICAO[d1['Posição']]

        fig_comp = go.Figure()
        fig_comp.add_trace(go.Scatterpolar(r=[d1.get(a, 0) for a in atts_comp], theta=atts_comp, fill='toself', name=j1,
                                           line_color='#00FFCC'))
        fig_comp.add_trace(go.Scatterpolar(r=[d2.get(a, 0) for a in atts_comp], theta=atts_comp, fill='toself', name=j2,
                                           line_color='#FF4B4B'))
        fig_comp.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                               title=f"Perfil Técnico: {j1} vs {j2}")
        st.plotly_chart(fig_comp, use_container_width=True)

        # Tabela de Diferencial
        st.write("**Diferencial de Atributos (Alvo vs Plantel):**")
        diff_data = []
        for a in atts_comp:
            diff = d2.get(a, 0) - d1.get(a, 0)
            diff_data.append({"Atributo": a, j1: d1.get(a, 0), j2: d2.get(a, 0), "Diferença": diff})

        diff_df = pd.DataFrame(diff_data)


        def color_diff(val):
            color = 'green' if val > 0 else 'red' if val < 0 else 'white'
            return f'color: {color}'


        st.dataframe(diff_df.style.applymap(color_diff, subset=['Diferença']), use_container_width=True)

else:
    st.info("Adicione pelo menos dois jogadores para comparar as suas qualidades técnicas.")