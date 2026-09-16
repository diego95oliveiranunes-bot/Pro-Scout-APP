import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import gspread
from google.oauth2.service_account import Credentials
from gspread_dataframe import set_with_dataframe, get_as_dataframe
import json
import os

# 1. LAYOUT ALTERADO PARA 'centered' (Melhor adaptação em telas de celular)
st.set_page_config(page_title="ProScout Mobile", layout="centered", page_icon="📱")

# --- ESTILIZAÇÃO VISUAL (Mobile-Friendly) ---
st.markdown("""
    <style>
    /* Ajustes para os Cards no celular */
    div[data-testid="metric-container"] {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        padding: 10px; /* Reduzido para caber melhor no mobile */
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border-left: 4px solid #2E7D32;
    }
    div[data-testid="metric-container"] label {
        color: #718096 !important;
        font-weight: 600;
        font-size: 0.85rem; /* Texto menor para não quebrar linha */
    }
    div[data-testid="metric-container"] div {
        color: #1A365D !important;
        font-size: 1.5rem !important; /* Números mais proporcionais */
    }
    
    /* Melhorando a rolagem horizontal de Tabs no celular */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
    }
    
    /* Ocultar menus desnecessários do Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Reduzir margens gerais no celular */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# CONEXÃO COM GOOGLE SHEETS
# ==========================================
@st.cache_resource
def get_gspread_client():
    try:
        creds_dict = json.loads(st.secrets["google_credentials"])
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        st.error(f"Erro nas credenciais: {e}")
        return None

def carregar_dados():
    client = get_gspread_client()
    if client:
        try:
            sheet = client.open("Database_Scout").worksheet("Jogadores")
            df = get_as_dataframe(sheet, evaluate_formulas=True)
            df = df.dropna(how='all').dropna(axis=1, how='all')
            if df.empty or 'Nome' not in df.columns:
                return pd.DataFrame()
            estatisticas_novas = ['Gols', 'Assistências', 'Chutes Certos', 'Passes Certos', 'Desarmes', 'Clean Sheets']
            for col in estatisticas_novas:
                if col not in df.columns:
                    df[col] = 0
            return df
        except Exception:
            return pd.DataFrame()
    return pd.DataFrame()

def salvar_dados(df_novo):
    client = get_gspread_client()
    if client:
        try:
            sheet = client.open("Database_Scout").worksheet("Jogadores")
            sheet.clear()
            set_with_dataframe(sheet, df_novo)
            return True
        except Exception:
            return False
    return False

df_atual = carregar_dados()

# --- CONFIGURAÇÕES TÁTICAS (MANTIDAS) ---
SUGESTOES_POSICAO = {
    "Goleiro": ["Reflexo", "Elasticidade", "Saída de Gol", "Posicionamento", "Jogo com os Pés", "Comunicação"],
    "Zagueiro": ["Posicionamento", "Força", "Impulsão", "Cabeceio", "Divididas", "Desarme"],
    "Lateral Direito": ["Velocidade", "Cruzamento", "Resistência", "Desarme", "Drible", "Passe Curto"],
    "Lateral Esquerdo": ["Velocidade", "Cruzamento", "Resistência", "Desarme", "Drible", "Passe Curto"],
    "Volante": ["Desarme", "Interceptação", "Resistência", "Passe Curto", "Força", "Posicionamento"],
    "Meia Central": ["Visão", "Passe", "Controle de Bola", "Resistência", "Interceptação", "Agilidade"],
    "Meia Direito": ["Velocidade", "Cruzamento", "Passe", "Visão", "Controle de Bola", "Resistência"],
    "Meia Esquerdo": ["Velocidade", "Cruzamento", "Passe", "Visão", "Controle de Bola", "Resistência"],
    "Meia Atacante": ["Visão", "Passe", "Drible", "Agilidade", "Finalização", "Controle de Bola"],
    "Ponta Direito": ["Velocidade", "Drible", "Agilidade", "Cruzamento", "Finalização", "Controle de Bola"],
    "Ponta Esquerdo": ["Velocidade", "Drible", "Agilidade", "Cruzamento", "Finalização", "Controle de Bola"],
    "Centroavante": ["Finalização", "Posicionamento", "Força", "Cabeceio", "Impulsão", "Controle de Bola"]
}
TODOS_ATRIBUTOS = list(set([item for sublist in SUGESTOES_POSICAO.values() for item in sublist] + ["Resistência", "Interceptação", "Divididas", "Passe Curto", "Drible", "Cruzamento"]))

ESTILOS_TATICOS = {
    "Gegenpressing": ["Resistência", "Agilidade", "Divididas", "Velocidade", "Interceptação"],
    "Tiki-Taka": ["Passe", "Visão", "Controle de Bola", "Passe Curto", "Posicionamento"],
    "Goleiro Líbero": ["Jogo com os Pés", "Passe Curto", "Visão", "Posicionamento", "Saída de Gol"],
    "Jogo de Pontas": ["Velocidade", "Cruzamento", "Drible", "Agilidade", "Finalização"],
    "Jogo Direto": ["Força", "Impulsão", "Cabeceio", "Passe", "Finalização"],
    "Contra-Ataque": ["Velocidade", "Agilidade", "Finalização", "Drible", "Visão"]
}

FUNCOES_TATICAS = {
    "Goleiro": {"Goleiro Tradicional": ["Reflexo", "Elasticidade", "Posicionamento", "Comunicação"], "Goleiro Líbero": ["Jogo com os Pés", "Saída de Gol", "Visão", "Passe Curto"]},
    "Zagueiro": {"Zagueiro Raiz": ["Força", "Divididas", "Desarme", "Cabeceio"], "Zagueiro Construtor": ["Passe Curto", "Visão", "Controle de Bola", "Posicionamento"]},
    "Lateral Direito": {"Ala Ofensivo": ["Velocidade", "Cruzamento", "Drible", "Resistência", "Agilidade"], "Lateral Defensivo": ["Desarme", "Posicionamento", "Força", "Interceptação"]},
    "Lateral Esquerdo": {"Ala Ofensivo": ["Velocidade", "Cruzamento", "Drible", "Resistência", "Agilidade"], "Lateral Defensivo": ["Desarme", "Posicionamento", "Força", "Interceptação"]},
    "Volante": {"Cão de Guarda": ["Desarme", "Interceptação", "Força", "Posicionamento"], "Segundo Volante": ["Resistência", "Passe Curto", "Divididas", "Visão"], "Armador Recuado": ["Visão", "Passe", "Controle de Bola", "Posicionamento"]},
    "Meia Central": {"Box-to-Box": ["Resistência", "Velocidade", "Divididas", "Finalização"], "Armador Central": ["Visão", "Passe", "Controle de Bola", "Drible", "Passe Curto"], "Meia Recuperador": ["Desarme", "Interceptação", "Resistência", "Posicionamento"]},
    "Meia Direito": {"Meia Aberto": ["Velocidade", "Cruzamento", "Resistência", "Passe", "Controle de Bola"], "Armador Aberto": ["Visão", "Passe", "Drible", "Controle de Bola", "Agilidade"]},
    "Meia Esquerdo": {"Meia Aberto": ["Velocidade", "Cruzamento", "Resistência", "Passe", "Controle de Bola"], "Armador Aberto": ["Visão", "Passe", "Drible", "Controle de Bola", "Agilidade"]},
    "Meia Atacante": {"Camisa 10": ["Visão", "Passe", "Drible", "Controle de Bola", "Agilidade"], "Trequartista": ["Visão", "Passe", "Drible", "Finalização", "Posicionamento"], "Atacante Sombra": ["Finalização", "Posicionamento", "Velocidade", "Agilidade"]},
    "Ponta Direito": {"Ponta Clássico": ["Velocidade", "Cruzamento", "Drible", "Agilidade"], "Ponta Invertido": ["Velocidade", "Drible", "Finalização", "Agilidade", "Visão"]},
    "Ponta Esquerdo": {"Ponta Clássico": ["Velocidade", "Cruzamento", "Drible", "Agilidade"], "Ponta Invertido": ["Velocidade", "Drible", "Finalização", "Agilidade", "Visão"]},
    "Centroavante": {"Falso 9": ["Passe Curto", "Visão", "Controle de Bola", "Drible"], "Homem Alvo": ["Força", "Impulsão", "Cabeceio", "Posicionamento"], "Atacante Avançado": ["Velocidade", "Agilidade", "Finalização", "Posicionamento"], "Centroavante Fixo": ["Finalização", "Cabeceio", "Força", "Posicionamento"]}
}

# ==========================================
# MENU LATERAL (No celular, vira o menu hambúrguer)
# ==========================================
st.sidebar.title("📱 Menu Scout")
st.sidebar.markdown("---")
menu = st.sidebar.radio("Navegação:", [
    "🏠 Visão do Plantel", 
    "🔍 Olheiros (Adicionar)", 
    "🎯 Tática e Treino", 
    "📊 Ranking da Temporada",
    "⚙️ Ajustes (Banco)"
])

# ==========================================
# PÁGINA 1: VISÃO DO PLANTEL
# ==========================================
if menu == "🏠 Visão do Plantel":
    st.subheader("📋 Meu Elenco")
    
    if not df_atual.empty:
        df_elenco = df_atual[df_atual['Status'] == 'Meu Elenco']
        if not df_elenco.empty:
            # Layout em Grid 2x2 (Perfeito para telas estreitas de celular)
            c1, c2 = st.columns(2)
            c1.metric("Atletas", len(df_elenco))
            c2.metric("OVR Médio", round(df_elenco['OVR'].mean(), 1))
            
            c3, c4 = st.columns(2)
            c3.metric("Idade Média", round(df_elenco['Idade'].mean(), 1))
            c4.metric("Valor Total", f"€ {df_elenco['Valor (€M)'].sum():.1f}M")
            
            st.markdown("---")
            st.markdown("##### Relação de Jogadores (Deslize ▶)")
            # Reduzidas as colunas para não ficar gigante no celular
            colunas_mobile = ['Nome', 'Posição', 'Idade', 'OVR', 'Potencial']
            st.dataframe(df_elenco[colunas_mobile].sort_values(by='OVR', ascending=False), use_container_width=True, hide_index=True)
        else:
            st.info("Sem jogadores no elenco. Cadastre em 'Olheiros'.")
    else:
        st.info("Banco de dados vazio.")

# ==========================================
# PÁGINA 2: CENTRAL DE OLHEIROS
# ==========================================
elif menu == "🔍 Olheiros (Adicionar)":
    st.subheader("🔍 Gestão de Atletas")
    
    tab_registro, tab_comparacao = st.tabs(["📝 Registrar/Editar", "⚔️ Comparar"])
    
    with tab_registro:
        # Tudo em uma coluna principal para fluir no scroll do celular
        nome_in = st.text_input("Nome do Atleta (Enter para buscar)").strip()
        
        jog_dados = {}
        if nome_in and not df_atual.empty:
            busca = df_atual[df_atual['Nome'].str.lower() == nome_in.lower()]
            if not busca.empty:
                jog_dados = busca.iloc[0].to_dict()
                st.success("✅ Dados carregados!")
        
        def get_index(lista, valor): return lista.index(valor) if valor in lista else 0

        # Divisão 2x2 para inputs básicos economizando espaço vertical
        cx_stat, cx_pos = st.columns(2)
        status_in = cx_stat.selectbox("Status", ["Meu Elenco", "Alvo"], index=get_index(["Meu Elenco", "Alvo"], jog_dados.get('Status', 'Meu Elenco')))
        pos_in = cx_pos.selectbox("Posição", list(SUGESTOES_POSICAO.keys()), index=get_index(list(SUGESTOES_POSICAO.keys()), jog_dados.get('Posição', 'Centroavante')))
        
        with st.expander("👤 Perfil (Idade, OVR, Valor)", expanded=True):
            # Grid 2x2 para celular
            cx1, cx2 = st.columns(2)
            idade_in = cx1.number_input("Idade", 15, 45, int(jog_dados.get('Idade', 22)))
            ovr_in = cx2.number_input("OVR", 1, 99, int(jog_dados.get('OVR', 75)))
            
            cx3, cx4 = st.columns(2)
            pot_in = cx3.number_input("Potencial", 1, 99, int(jog_dados.get('Potencial', 85)))
            valor_in = cx4.number_input("Valor (€M)", 0.0, step=0.5, value=float(jog_dados.get('Valor (€M)', 10.0)))

        with st.expander("📈 Estatísticas da Temporada", expanded=False):
            # Grid 2x3 adaptada para mobile
            cs1, cs2 = st.columns(2)
            gols_in = cs1.number_input("Gols", 0, value=int(jog_dados.get('Gols', 0)))
            asts_in = cs2.number_input("Assistências", 0, value=int(jog_dados.get('Assistências', 0)))
            
            cs3, cs4 = st.columns(2)
            chutes_in = cs3.number_input("Chutes Certos", 0, value=int(jog_dados.get('Chutes Certos', 0)))
            passes_in = cs4.number_input("Passes Certos", 0, value=int(jog_dados.get('Passes Certos', 0)))
            
            cs5, cs6 = st.columns(2)
            desarmes_in = cs5.number_input("Desarmes", 0, value=int(jog_dados.get('Desarmes', 0)))
            cleansheets_in = cs6.number_input("Clean Sheets", 0, value=int(jog_dados.get('Clean Sheets', 0)))

        attrs_val = {}
        with st.expander("⚙️ Atributos Técnicos/Físicos", expanded=False):
            st.markdown("**Principais (Posição)**")
            for a in SUGESTOES_POSICAO[pos_in]:
                val_padrao = int(jog_dados.get(a, ovr_in))
                attrs_val[a] = st.slider(a, 0, 99, val_padrao, key=f"p_{a}")
            
            st.markdown("**Secundários**")
            comp = [a for a in TODOS_ATRIBUTOS if a not in SUGESTOES_POSICAO[pos_in]]
            for a in comp:
                val_padrao = int(jog_dados.get(a, max(1, ovr_in-10)))
                attrs_val[a] = st.slider(a, 0, 99, val_padrao, key=f"c_{a}")

        if st.button("💾 Salvar Atleta", type="primary", use_container_width=True):
            if nome_in:
                with st.spinner("Salvando..."):
                    dados_completos = {a: 50 for a in TODOS_ATRIBUTOS}
                    dados_completos.update(attrs_val)
                    dados_completos.update({
                        'Nome': nome_in, 'Status': status_in, 'Posição': pos_in, 
                        'Idade': idade_in, 'OVR': ovr_in, 'Potencial': pot_in, 'Valor (€M)': valor_in,
                        'Gols': gols_in, 'Assistências': asts_in, 'Chutes Certos': chutes_in,
                        'Passes Certos': passes_in, 'Desarmes': desarmes_in, 'Clean Sheets': cleansheets_in
                    })
                    
                    df_novo = df_atual.copy()
                    if not df_novo.empty:
                        df_novo = df_novo[df_novo['Nome'] != nome_in]
                    df_novo = pd.concat([df_novo, pd.DataFrame([dados_completos])], ignore_index=True)
                    
                    if salvar_dados(df_novo):
                        st.success(f"✅ Salvo!")
                        st.rerun()

    with tab_comparacao:
        if not df_atual.empty and len(df_atual) > 1:
            j1 = st.selectbox("Jogador 1:", df_atual['Nome'].unique(), index=0)
            j2 = st.selectbox("Jogador 2:", df_atual['Nome'].unique(), index=1)
            
            d1, d2 = df_atual[df_atual['Nome'] == j1].iloc[0], df_atual[df_atual['Nome'] == j2].iloc[0]
            atts_c = SUGESTOES_POSICAO[d1['Posição']]
            
            fig_c = go.Figure()
            fig_c.add_trace(go.Scatterpolar(r=[d1.get(a, 0) for a in atts_c], theta=atts_c, fill='toself', name=j1, line_color="#1A365D")) 
            fig_c.add_trace(go.Scatterpolar(r=[d2.get(a, 0) for a in atts_c], theta=atts_c, fill='toself', name=j2, line_color="#2E7D32")) 
            # Layout responsivo do Radar
            fig_c.update_layout(template="plotly_white", polar=dict(radialaxis=dict(visible=True, range=[0, 99])), margin=dict(l=20, r=20, t=20, b=20)) 
            st.plotly_chart(fig_c, use_container_width=True)
        else:
            st.warning("Adicione pelo menos 2 jogadores.")

# ==========================================
# PÁGINA 3: ANÁLISE E TREINO
# ==========================================
elif menu == "🎯 Tática e Treino":
    st.subheader("🎯 Inteligência Tática")
    
    if not df_atual.empty:
        sel = st.selectbox("Selecione o Atleta:", df_atual['Nome'].unique())
        d = df_atual[df_atual['Nome'] == sel].iloc[0]
        
        tab_t, tab_tr = st.tabs(["🧩 Função Ideal", "📈 Treino"])
        
        with tab_t:
            funcoes_possiveis = FUNCOES_TATICAS.get(d['Posição'], {})
            if funcoes_possiveis:
                notas_funcoes = {}
                for funcao, atributos_necessarios in funcoes_possiveis.items():
                    nota_media = sum([d.get(a, 0) for a in atributos_necessarios]) / len(atributos_necessarios)
                    notas_funcoes[funcao] = nota_media
                funcoes_ordenadas = sorted(notas_funcoes.items(), key=lambda x: x[1], reverse=True)
                melhor_funcao, melhor_nota = funcoes_ordenadas[0]
                
                st.success(f"**Sugestão:** {melhor_funcao} ({melhor_nota:.1f}/99)")
                
                with st.expander("Outras funções"):
                    for func, nota in funcoes_ordenadas[1:]:
                        st.write(f"- {func}: {nota:.1f}")
            
            st.markdown("##### Adequação ao Time")
            fits = {e: round(sum([d.get(a, 0) for a in atts]) / len(atts), 1) for e, atts in ESTILOS_TATICOS.items()}
            fit_df = pd.DataFrame(list(fits.items()), columns=['Estilo', 'Fit %'])
            fig_fit = px.bar(fit_df, x='Fit %', y='Estilo', orientation='h', color='Fit %', color_continuous_scale='Blues', range_x=[0, 100])
            fig_fit.update_layout(template="plotly_white", height=300, margin=dict(l=0, r=0, t=20, b=0))
            st.plotly_chart(fig_fit, use_container_width=True)

        with tab_tr:
            estilo = st.selectbox("Estilo de Treino:", list(ESTILOS_TATICOS.keys()))
            alvo_atts = ESTILOS_TATICOS[estilo]
            
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(r=[d.get(a, 0) for a in alvo_atts], theta=alvo_atts, fill='toself', name='Atual', line_color="#1A365D"))
            fig.add_trace(go.Scatterpolar(r=[d['Potencial']] * len(alvo_atts), theta=alvo_atts, line_dash='dash', name='Teto', line_color="#E2E8F0"))
            fig.update_layout(template="plotly_white", polar=dict(radialaxis=dict(visible=True, range=[0, 99])), margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("**Gaps para evoluir:**")
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
elif menu == "📊 Ranking da Temporada":
    st.subheader("📊 Ranking do Elenco")
    
    if not df_atual.empty:
        col_f1, col_f2 = st.columns(2)
        pos_ranking = col_f1.selectbox("Posição:", ["Todos"] + list(SUGESTOES_POSICAO.keys()))
        metrica_ranking = col_f2.selectbox("Métrica:", ["Gols", "Assistências", "Chutes Certos", "Passes Certos", "Desarmes", "Clean Sheets"])
        
        df_rank = df_atual[df_atual['Status'] == 'Meu Elenco'].copy()
        if pos_ranking != "Todos":
            df_rank = df_rank[df_rank['Posição'] == pos_ranking]
            
        if not df_rank.empty:
            df_rank = df_rank.sort_values(by=metrica_ranking, ascending=False)
            
            st.markdown(f"**Top 5 - {metrica_ranking}**")
            top5 = df_rank.head(5)
            fig_rank = px.bar(top5, x='Nome', y=metrica_ranking, text=metrica_ranking)
            fig_rank.update_traces(marker_color='#1A365D', textposition='outside')
            fig_rank.update_layout(template="plotly_white", height=300, margin=dict(l=0, r=0, t=20, b=0))
            st.plotly_chart(fig_rank, use_container_width=True)
        else:
            st.warning("Nenhum dado encontrado.")
    else:
        st.info("Banco de dados vazio.")

# ==========================================
# PÁGINA 5: BANCO DE DADOS (CONFIG)
# ==========================================
elif menu == "⚙️ Ajustes (Banco)":
    st.subheader("⚙️ Nuvem (Sheets)")
    
    if not df_atual.empty:
        st.success("✅ Conectado ao Sheets")
        jogador_excluir = st.selectbox("Remover jogador:", df_atual['Nome'].unique())
        
        if st.button("🗑️ Excluir Definitivamente", type="primary", use_container_width=True):
            df_novo = df_atual[df_atual['Nome'] != jogador_excluir]
            if salvar_dados(df_novo):
                st.success("Removido!")
                st.rerun()
    else:
        st.info("Banco de dados vazio.")
