import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os

st.set_page_config(page_title="ProScout Analyst", layout="wide", page_icon="📊")

# --- ESTILIZAÇÃO VISUAL (Estilo Wyscout/Sofascore) ---
st.markdown("""
    <style>
    /* Cards Brancos e Limpos para Métricas */
    div[data-testid="metric-container"] {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border-left: 5px solid #2E7D32; /* Verde Grama no detalhe */
    }
    
    div[data-testid="metric-container"] label {
        color: #718096 !important;
        font-weight: 600;
        font-size: 0.95rem;
    }
    
    div[data-testid="metric-container"] div {
        color: #1A365D !important; /* Azul Marinho para os números */
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- SISTEMA DE ARMAZENAMENTO ---
DB_FILE = "database_carreira.csv"

def carregar_dados():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        estatisticas_novas = ['Gols', 'Assistências', 'Chutes Certos', 'Passes Certos', 'Desarmes', 'Clean Sheets']
        for col in estatisticas_novas:
            if col not in df.columns:
                df[col] = 0
        return df
    return pd.DataFrame()

def salvar_dados(df_novo):
    df_novo.to_csv(DB_FILE, index=False)

df_atual = carregar_dados()

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

FUNCOES_TATICAS = {
    "Atacante": {"Falso 9": ["Passe Curto", "Visão", "Controle de Bola", "Drible"], "Homem Alvo": ["Força", "Impulsão", "Cabeceio", "Posicionamento"], "Atacante Avançado": ["Velocidade", "Agilidade", "Finalização", "Posicionamento"]},
    "Zagueiro": {"Zagueiro Raiz (Defensivo)": ["Força", "Divididas", "Desarme", "Cabeceio"], "Zagueiro Construtor": ["Passe Curto", "Visão", "Controle de Bola", "Posicionamento"]},
    "Meio-Campo": {"Box-to-Box (Área a Área)": ["Resistência", "Velocidade", "Divididas", "Finalização"], "Armador Avançado": ["Visão", "Passe", "Controle de Bola", "Drible", "Passe Curto"], "Primeiro Volante (Cão de Guarda)": ["Desarme", "Interceptação", "Força", "Posicionamento"]},
    "Lateral": {"Ala Ofensivo": ["Velocidade", "Cruzamento", "Drible", "Resistência", "Agilidade"], "Lateral Defensivo": ["Desarme", "Posicionamento", "Força", "Interceptação"]},
    "Goleiro": {"Goleiro Tradicional": ["Reflexo", "Elasticidade", "Posicionamento", "Comunicação"], "Goleiro Líbero": ["Jogo com os Pés", "Saída de Gol", "Visão", "Passe Curto"]}
}

# ==========================================
# MENU LATERAL (Apenas Navegação)
# ==========================================
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3593/3593539.png", width=60) # Ícone tático genérico
st.sidebar.title("ProScout")
st.sidebar.markdown("---")
menu = st.sidebar.radio("Navegação Principal:", [
    "🏠 Visão do Plantel", 
    "🔍 Central de Olheiros", 
    "🎯 Análise e Treino", 
    "📊 Relatórios e Ranking",
    "⚙️ Banco de Dados"
])

# Recarrega dados sempre que muda de página
df = carregar_dados()

# ==========================================
# PÁGINA 1: VISÃO DO PLANTEL
# ==========================================
if menu == "🏠 Visão do Plantel":
    st.title("📋 Meu Elenco")
    
    if not df.empty:
        df_elenco = df[df['Status'] == 'Meu Elenco']
        if not df_elenco.empty:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Atletas no Plantel", len(df_elenco))
            c2.metric("Rating (OVR) Médio", round(df_elenco['OVR'].mean(), 1))
            c3.metric("Idade Média", round(df_elenco['Idade'].mean(), 1))
            c4.metric("Valor Total", f"€ {df_elenco['Valor (€M)'].sum():.1f}M")
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.subheader("Relação de Jogadores")
            colunas = ['Nome', 'Posição', 'Idade', 'OVR', 'Potencial', 'Valor (€M)', 'Gols', 'Assistências']
            st.dataframe(df_elenco[colunas].sort_values(by='OVR', ascending=False), use_container_width=True, hide_index=True)
        else:
            st.info("Você ainda não tem jogadores marcados como 'Meu Elenco'. Vá em Central de Olheiros para adicionar.")
    else:
        st.info("Banco de dados vazio.")

# ==========================================
# PÁGINA 2: CENTRAL DE OLHEIROS (Cadastro/Busca)
# ==========================================
elif menu == "🔍 Central de Olheiros":
    st.title("🔍 Central de Olheiros")
    
    tab_registro, tab_comparacao = st.tabs(["📝 Registrar / Editar Jogador", "⚔️ Comparar Atletas"])
    
    with tab_registro:
        st.write("Preencha o formulário abaixo para adicionar um jogador ou atualizar os dados de um atleta existente.")
        
        # Estrutura em colunas na tela principal (muito mais limpo)
        col_form1, col_form2 = st.columns(2)
        
        with col_form1:
            nome_in = st.text_input("Nome do Atleta (Digite para carregar dados se já existir)").strip()
            status_in = st.selectbox("Status", ["Meu Elenco", "Alvo de Transferência"])
            pos_in = st.selectbox("Posição Principal", list(SUGESTOES_POSICAO.keys()))
            
            st.markdown("##### Perfil do Atleta")
            cx1, cx2, cx3, cx4 = st.columns(4)
            idade_in = cx1.number_input("Idade", 15, 45, 22)
            ovr_in = cx2.number_input("OVR", 1, 99, 75)
            pot_in = cx3.number_input("Potencial", 1, 99, 85)
            valor_in = cx4.number_input("Valor (€M)", 0.0, step=0.5, value=10.0)

        # Lógica de auto-preenchimento
        def_stats = {'Gols': 0, 'Assistências': 0, 'Chutes Certos': 0, 'Passes Certos': 0, 'Desarmes': 0, 'Clean Sheets': 0}
        if nome_in and not df.empty:
            jogador_existente = df[df['Nome'].str.lower() == nome_in.lower()]
            if not jogador_existente.empty:
                for stat in def_stats.keys():
                    def_stats[stat] = int(jogador_existente.iloc[0].get(stat, 0))
        
        with col_form2:
            st.markdown("##### Estatísticas da Temporada")
            cs1, cs2, cs3 = st.columns(3)
            gols_in = cs1.number_input("Gols", 0, value=def_stats['Gols'])
            asts_in = cs2.number_input("Assistências", 0, value=def_stats['Assistências'])
            chutes_in = cs3.number_input("Chutes Certos", 0, value=def_stats['Chutes Certos'])
            
            cs4, cs5, cs6 = st.columns(3)
            passes_in = cs4.number_input("Passes Certos", 0, value=def_stats['Passes Certos'])
            desarmes_in = cs5.number_input("Desarmes", 0, value=def_stats['Desarmes'])
            cleansheets_in = cs6.number_input("Clean Sheets", 0, value=def_stats['Clean Sheets'])
            
        st.markdown("---")
        st.markdown("##### Relatório de Atributos Técnicos e Físicos")
        attrs_val = {}
        
        # Expander para não poluir a tela se não quiser editar atributos
        with st.expander("Expandir para editar notas de atributos (0-99)", expanded=True):
            cat1, cat2 = st.columns(2)
            with cat1:
                st.write("**Atributos Chave (Posição)**")
                for a in SUGESTOES_POSICAO[pos_in]:
                    attrs_val[a] = st.slider(a, 0, 99, ovr_in, key=f"p_{a}")
            with cat2:
                st.write("**Atributos Complementares**")
                comp = [a for a in TODOS_ATRIBUTOS if a not in SUGESTOES_POSICAO[pos_in]]
                for a in comp:
                    attrs_val[a] = st.slider(a, 0, 99, max(1, ovr_in-10), key=f"c_{a}")

        if st.button("💾 Salvar Relatório do Atleta", type="primary", use_container_width=True):
            if nome_in:
                dados_completos = {a: 50 for a in TODOS_ATRIBUTOS}
                dados_completos.update(attrs_val)
                dados_completos.update({
                    'Nome': nome_in, 'Status': status_in, 'Posição': pos_in, 
                    'Idade': idade_in, 'OVR': ovr_in, 'Potencial': pot_in, 'Valor (€M)': valor_in,
                    'Gols': gols_in, 'Assistências': asts_in, 'Chutes Certos': chutes_in,
                    'Passes Certos': passes_in, 'Desarmes': desarmes_in, 'Clean Sheets': cleansheets_in
                })
                
                if not df.empty:
                    df = df[df['Nome'] != nome_in]
                    
                df_novo = pd.concat([df, pd.DataFrame([dados_completos])], ignore_index=True)
                salvar_dados(df_novo)
                st.success(f"Dados de {nome_in} atualizados no sistema!")
                st.rerun()

    with tab_comparacao:
        if not df.empty and len(df) > 1:
            st.subheader("Análise Comparativa (Radar)")
            col_a, col_b = st.columns(2)
            j1 = col_a.selectbox("Jogador 1:", df['Nome'].unique(), index=0)
            j2 = col_b.selectbox("Jogador 2:", df['Nome'].unique(), index=1)
            
            d1, d2 = df[df['Nome'] == j1].iloc[0], df[df['Nome'] == j2].iloc[0]
            atts_c = SUGESTOES_POSICAO[d1['Posição']]
            
            fig_c = go.Figure()
            fig_c.add_trace(go.Scatterpolar(r=[d1.get(a, 0) for a in atts_c], theta=atts_c, fill='toself', name=j1, line_color="#1A365D")) # Azul
            fig_c.add_trace(go.Scatterpolar(r=[d2.get(a, 0) for a in atts_c], theta=atts_c, fill='toself', name=j2, line_color="#2E7D32")) # Verde
            fig_c.update_layout(template="plotly_white", polar=dict(radialaxis=dict(visible=True, range=[0, 99]))) 
            st.plotly_chart(fig_c, use_container_width=True)
        else:
            st.warning("Adicione pelo menos 2 jogadores no banco de dados para usar a comparação.")

# ==========================================
# PÁGINA 3: ANÁLISE E TREINO
# ==========================================
elif menu == "🎯 Análise e Treino":
    st.title("🎯 Centro de Inteligência Tática")
    
    if not df.empty:
        sel = st.selectbox("Selecione o Atleta:", df['Nome'].unique())
        d = df[df['Nome'] == sel].iloc[0]
        
        tab_t, tab_tr = st.tabs(["🧩 Perfil Tático", "📈 Plano de Desenvolvimento"])
        
        with tab_t:
            st.subheader("Melhor Função na Posição")
            funcoes_possiveis = FUNCOES_TATICAS.get(d['Posição'], {})
            
            if funcoes_possiveis:
                notas_funcoes = {}
                for funcao, atributos_necessarios in funcoes_possiveis.items():
                    nota_media = sum([d.get(a, 0) for a in atributos_necessarios]) / len(atributos_necessarios)
                    notas_funcoes[funcao] = nota_media
                    
                funcoes_ordenadas = sorted(notas_funcoes.items(), key=lambda x: x[1], reverse=True)
                melhor_funcao, melhor_nota = funcoes_ordenadas[0]
                
                st.info(f"**Sugestão Analítica:** O sistema indica a função de **{melhor_funcao}** (Aptidão Técnica: {melhor_nota:.1f}/99)")
                
                with st.expander("Ver outras opções de função"):
                    for func, nota in funcoes_ordenadas[1:]:
                        st.write(f"- {func}: {nota:.1f}")
            
            st.markdown("---")
            st.subheader("Adequação ao Modelo de Jogo")
            fits = {e: round(sum([d.get(a, 0) for a in atts]) / len(atts), 1) for e, atts in ESTILOS_TATICOS.items()}
            fit_df = pd.DataFrame(list(fits.items()), columns=['Estilo', 'Fit %'])
            
            fig_fit = px.bar(fit_df, x='Fit %', y='Estilo', orientation='h', color='Fit %', 
                             color_continuous_scale='Blues', range_x=[0, 100], text='Fit %')
            fig_fit.update_traces(textposition='outside')
            fig_fit.update_layout(template="plotly_white", height=350)
            st.plotly_chart(fig_fit, use_container_width=True)

        with tab_tr:
            estilo = st.selectbox("Selecione o Estilo de Treino:", list(ESTILOS_TATICOS.keys()))
            alvo_atts = ESTILOS_TATICOS[estilo]
            
            c1, c2 = st.columns([2, 1])
            with c1:
                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(r=[d.get(a, 0) for a in alvo_atts], theta=alvo_atts, fill='toself', name='Nível Atual', line_color="#1A365D"))
                fig.add_trace(go.Scatterpolar(r=[d['Potencial']] * len(alvo_atts), theta=alvo_atts, line_dash='dash', name='Teto (Potencial)', line_color="#E2E8F0"))
                fig.update_layout(template="plotly_white", polar=dict(radialaxis=dict(visible=True, range=[0, 99])))
                st.plotly_chart(fig, use_container_width=True)
                
            with c2:
                st.write(f"**Focos de Evolução:**")
                for a in alvo_atts:
                    val = d.get(a, 0)
                    meta = d['Potencial']
                    if val < meta:
                        st.progress(int(val), text=f"{a}: {val}/{meta}")
    else:
        st.warning("Banco de dados vazio.")

# ==========================================
# PÁGINA 4: RELATÓRIOS E RANKING
# ==========================================
elif menu == "📊 Relatórios e Ranking":
    st.title("📊 Relatórios de Desempenho")
    
    if not df.empty:
        col_f1, col_f2 = st.columns(2)
        pos_ranking = col_f1.selectbox("Filtro de Posição:", ["Todos os Jogadores"] + list(SUGESTOES_POSICAO.keys()))
        metrica_ranking = col_f2.selectbox("Métrica Analisada:", ["Gols", "Assistências", "Chutes Certos", "Passes Certos", "Desarmes", "Clean Sheets"])
        
        df_rank = df[df['Status'] == 'Meu Elenco'].copy()
        
        if pos_ranking != "Todos os Jogadores":
            df_rank = df_rank[df_rank['Posição'] == pos_ranking]
            
        if not df_rank.empty:
            df_rank = df_rank.sort_values(by=metrica_ranking, ascending=False)
            
            # Gráfico Top 5 Clean
            st.markdown(f"#### Top 5 - {metrica_ranking}")
            top5 = df_rank.head(5)
            fig_rank = px.bar(top5, x='Nome', y=metrica_ranking, text=metrica_ranking)
            fig_rank.update_traces(marker_color='#1A365D', textposition='outside') # Barras azuis sólidas e profissionais
            fig_rank.update_layout(template="plotly_white", height=350)
            st.plotly_chart(fig_rank, use_container_width=True)
            
            st.markdown("#### Tabela Completa")
            colunas_stats = ['Nome', 'Posição', 'Gols', 'Assistências', 'Chutes Certos', 'Passes Certos', 'Desarmes', 'Clean Sheets']
            st.dataframe(df_rank[colunas_stats], use_container_width=True, hide_index=True)
        else:
            st.warning("Nenhum dado encontrado para o filtro aplicado no seu elenco.")
    else:
        st.info("Banco de dados vazio.")

# ==========================================
# PÁGINA 5: CONFIGURAÇÕES / BANCO DE DADOS
# ==========================================
elif menu == "⚙️ Banco de Dados":
    st.title("⚙️ Gestão do Banco de Dados")
    
    if not df.empty:
        st.warning("Atenção: As exclusões feitas aqui são permanentes.")
        jogador_excluir = st.selectbox("Selecione um jogador para remover do banco:", df['Nome'].unique())
        
        if st.button("🗑️ Excluir Jogador Definitivamente", type="primary"):
            df = df[df['Nome'] != jogador_excluir]
            salvar_dados(df)
            st.success(f"{jogador_excluir} foi removido do sistema!")
            st.rerun()
            
        st.markdown("---")
        st.write("Base de dados bruta (CSV):")
        st.dataframe(df)
    else:
        st.info("O banco de dados já está vazio.")
