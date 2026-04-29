import streamlit as st
import pandas as pd
import plotly.express as px
import io
import requests
import time
import plotly.graph_objects as go
from datetime import datetime

# 1. Configuração da Página
st.set_page_config(page_title="TECADI - TV Operacional", page_icon="📺", layout="wide")

# --- CONTROLE DE ESTADO ---
if 'aba_atual' not in st.session_state:
    st.session_state.aba_atual = 0

# --- CORES E ESTILO TECADI ---
AZUL_TECADI = "#1D569B"
AZUL_ESCURO = "#133A68"
AZUL_CLARO_TECADI = "#009FE3"
CINZA_FUNDO = "#F8FAFC"

def formatar_br(valor):
    try:
        return f"{valor:,.0f}".replace(",", ".")
    except:
        return "0"

# --- BLOCO DE CSS ÚNICO E DINÂMICO ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #FFFFFF; padding-top: 0.5rem; }}
    .dash-header {{ border-left: 10px solid {AZUL_TECADI}; padding-left: 20px; margin-bottom: 20px; margin-top: -50px; }}
    .dash-title {{ color: {AZUL_ESCURO}; font-size: 32px !important; font-weight: 800 !important; }}

    /* SIDEBAR */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {AZUL_ESCURO} 0%, {AZUL_TECADI} 100%);
        min-width: 260px !important;
    }}
    [data-testid="stSidebar"] p, label, .stMarkdown p, .stCheckbox span, h3 {{ color: white !important; }}

    /* --- ESTILIZAÇÃO DOS CARDS (VERSÃO ORIGINAL RESTAURADA) --- */
    div[data-testid="stMetric"] {{
        background-color: {CINZA_FUNDO} !important;
        border: 1px solid #E2E8F0 !important;
        padding: 10px !important;
        border-radius: 12px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
    }}
    div[data-testid="stMetric"]:hover {{
        transform: translateY(-5px) !important;
        border-color: {AZUL_CLARO_TECADI} !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
    }}
    div[data-testid="stMetric"] label p {{
        color: {AZUL_ESCURO} !important;
        font-size: 13px !important;
        font-weight: 600 !important;
    }}
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {{
        color: {AZUL_TECADI} !important;
        font-size: 22px !important;
        font-weight: 800 !important;
    }}
    
    /* Redução para caber tudo na tela */
    div[data-testid="stMetric"] div[data-testid="stMetricDelta"] {{
        font-size: 11px !important;
    }}
    .stMarkdown h4 {{
        margin-bottom: 5px !important;
        font-size: 18px !important;
    }}
    .stMarkdown h5 {{
        margin-bottom: 3px !important;
        margin-top: 8px !important;
        font-size: 15px !important;
    }}
    div[data-testid="stVerticalStack"] {{
        gap: 3px !important;
    }}
    /* Reduzir espaçamento entre seções */
    .stMarkdown {{
        margin-bottom: 0px !important;
        padding-bottom: 0px !important;
    }}
   
    /* Estilo PADRÃO para os botões de ABA */
    .stButton > button {{
        width: 100%;
        border-radius: 5px;
        height: 3.5em;
        font-weight: bold;
        background-color: #f0f2f6 !important;
        color: {AZUL_ESCURO} !important;
        border: 1px solid #d1d5db !important;
        transition: all 0.3s ease;
    }}

    /* ESTILO DINÂMICO DA ABA ATIVA (Sem desalinhamento) */
    div[data-testid="stHorizontalBlock"] > div:nth-child({st.session_state.aba_atual + 1}) button {{
        background-color: {AZUL_TECADI} !important;
        color: white !important;
        border: 3px solid {AZUL_CLARO_TECADI} !important;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.2) !important;
    }}
    </style>
""", unsafe_allow_html=True)

# --- CARGA DE DADOS ---
def converter_link(url):
    if "sharepoint.com" in url and "download=1" not in url:
        return url.split('?')[0] + "?download=1"
    return url

@st.cache_data(ttl=600)
def load_all_data():
    urls = {
        "cortes": "https://tecadi-my.sharepoint.com/:x:/g/personal/luis_avila_tecadi_com_br/IQDLjMQfLyv9S4OOTJtwcU1tAVwF1nq8EGvzlOjKejbdn-o?e=EvKjGx",
        "pulos": "https://tecadi-my.sharepoint.com/:x:/g/personal/luis_avila_tecadi_com_br/IQBdA_Yt563JR4yERPu4o5NwAc0XmKnxbR6NrGQehUHQ35k?e=LPbSFK",
        "integrados": "https://tecadi-my.sharepoint.com/:x:/g/personal/anderson_roza_tecadi_com_br/IQD-TqQsaMvnS6uANxkS-31-ARUWtvdtwyFlby3bS1Vm0os?e=hGZXJQ",
        "realizado": "https://tecadi-my.sharepoint.com/:x:/g/personal/anderson_roza_tecadi_com_br/IQCpXS7IqaNPRpmwTx1-FYuKAWLu5pqlVkA1hpUD-mkCcno?e=CaKWav",
        "pendentes": "https://tecadi-my.sharepoint.com/:x:/g/personal/anderson_roza_tecadi_com_br/IQBS8GhxPJ3wRYIodpxrwD_5AU15pbYrDvzMKaY1kw161vg?e=n3lhO0"
    }
   
    try:
        df_real = pd.read_excel(io.BytesIO(requests.get(converter_link(urls["realizado"])).content))
        df_real['Data'] = pd.to_datetime(df_real['Finalizada em'].astype(str).str.split('-').str[0], dayfirst=True, errors='coerce').dt.date
       
# --- BLOCO INTEGRADOS (VERSÃO FINAL BLINDADA) ---
        response_int = requests.get(converter_link(urls["integrados"]))
        # skiprows=1 pula o título mesclado para ler os cabeçalhos corretamente
        df_int = pd.read_excel(io.BytesIO(response_int.content), skiprows=1)
        
        # 1. Padronização total de nomes
        df_int.columns = [str(c).strip().upper() for c in df_int.columns]
        
        # 2. Mapeamento Inteligente (Procura palavras-chave)
        col_data = next((c for c in df_int.columns if 'DATA' in c), df_int.columns[0])
        col_lin  = next((c for c in df_int.columns if 'LINHA' in c), None)
        col_pec  = next((c for c in df_int.columns if 'PEÇA' in c or 'PECA' in c), None)
        col_ped  = next((c for c in df_int.columns if 'PEDIDO' in c), None)

        # 3. Renomeia e GARANTE que as colunas existam (evita KeyError)
        df_int = df_int.rename(columns={col_data: 'Data'})

        if col_lin: df_int = df_int.rename(columns={col_lin: 'Linhas'})
        else: df_int['Linhas'] = 0

        if col_pec: df_int = df_int.rename(columns={col_pec: 'Peças'})
        else: df_int['Peças'] = 0

        if col_ped: df_int = df_int.rename(columns={col_ped: 'Pedidos'})
        else: df_int['Pedidos'] = 0
        
        # 4. Tratamento final da Data
        df_int['Data'] = pd.to_datetime(df_int['Data'], dayfirst=True, errors='coerce').dt.date
        df_int = df_int.dropna(subset=['Data'])
        # --------------------------------------------
       
        df_pend = pd.read_excel(io.BytesIO(requests.get(converter_link(urls["pendentes"])).content))
       
    # --- CARGA DOS CORTES COM TRATAMENTO DE CÉLULAS MESCLADAS ---
        df_cor = pd.read_excel(io.BytesIO(requests.get(converter_link(urls["cortes"])).content))
       
        # 1. Identifica e limpa colunas duplicadas (prevenção de erro)
        df_cor = df_cor.loc[:, ~df_cor.columns.duplicated()]
        df_cor.columns = df_cor.columns.str.strip()

        # 2. TRATAMENTO DE MESCLADOS: Preenche para baixo os dados das colunas de Pedido e Data
        # Se a coluna de data for a primeira e pedido a segunda:
        df_cor.iloc[:, 0] = df_cor.iloc[:, 0].ffill() # Preenche a Data (1ª coluna)
        df_cor.iloc[:, 1] = df_cor.iloc[:, 1].ffill() # Preenche o Pedido (2ª coluna)
       
        # 3. Converte a data após o preenchimento
        df_cor['Data'] = pd.to_datetime(df_cor.iloc[:, 0], errors='coerce').dt.date
       
        # --- CARGA DOS PULOS (CORRIGIDA) ---
        df_pul = pd.read_excel(io.BytesIO(requests.get(converter_link(urls["pulos"])).content))
       
        # Limpa nomes de colunas para garantir
        df_pul.columns = df_pul.columns.str.strip()
       
        # Se a coluna 'Data' existir, usa ela. Se não, usa a 3ª coluna (índice 2)
        col_data = 'Data' if 'Data' in df_pul.columns else df_pul.columns[2]
       
        # Converte a coluna correta
        df_pul['Data'] = pd.to_datetime(df_pul[col_data], errors='coerce')
       
        # Remove o que não for data de verdade (anos 70, erros, etc) antes de entregar para o app
        df_pul = df_pul.dropna(subset=['Data'])
        df_pul = df_pul[df_pul['Data'].dt.year > 2020]

        return df_real, df_int, df_pend, df_cor, df_pul, None
    except Exception as e:
        return None, None, None, None, None, str(e)

df_f, df_i, df_p_proc, df_c, df_p_pul, erro = load_all_data()

# --- PREPARAÇÃO DOS PENDENTES POR TIPO ---
if df_p_proc is not None:
    df_pendentes = df_p_proc.copy()
    df_pendentes.columns = df_pendentes.columns.str.strip()
    
    # Identificar coluna de tipo (TIPO, Tipo, etc)
    col_tipo = next((c for c in ['TIPO', 'Tipo', 'Type', 'tipo'] if c in df_pendentes.columns), None)
    
    if col_tipo:
        df_pendentes[col_tipo] = df_pendentes[col_tipo].astype(str).str.upper().str.strip()
        df_picking = df_pendentes[df_pendentes[col_tipo].str.contains('PICKING', na=False)]
        df_packing = df_pendentes[df_pendentes[col_tipo].str.contains('PACKING', na=False)]
    else:
        df_picking = None
        df_packing = None
else:
    df_picking = None
    df_packing = None

def proxima_aba():
    st.session_state.aba_atual = (st.session_state.aba_atual + 1) % 6

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://tecadi.com.br/wp-content/uploads/2024/01/LOGO-HORIZONTAL_BRANCA_p.png.webp", width=200)
    st.markdown("---")
    if st.button("🔄 ATUALIZAR DADOS AGORA"):
        st.cache_data.clear()
        st.rerun()
    autoplay = st.checkbox("🚩 Ativar Autoplay (10s)", value=False)
    st.write(f"**Aba Ativa:** {st.session_state.aba_atual + 1} de 7")
    if erro: st.error(f"Erro ao carregar: {erro}")

# --- HEADER ---
st.markdown('<div class="dash-header"><div class="dash-title">Monitor de Fluxo Operacional - ZEN</div></div>', unsafe_allow_html=True)

# --- NAVEGAÇÃO POR ABAS ---
titulos = ["📊 Cards", "📈 Linhas", "📦 Peças", "📋 Pedidos", "🗂️ Backlog", "✂️ Cortes", "🦘 Pulos"]
cols_abas = st.columns(7)

for i, titulo in enumerate(titulos):
    with cols_abas[i]:
        if st.button(titulo, key=f"btn_{i}", use_container_width=True):
            st.session_state.aba_atual = i
            st.rerun()

def criar_figura(df_real, df_int, col_real, col_int, titulo, op="sum"):
    # 1. Realizado
    if op == "sum":
        r = df_real.groupby('Data')[col_real].sum()
    else:
        r = df_real.groupby('Data')[col_real].nunique()
    
    # 2. INTEGRADO (Garantindo que os valores sejam números)
    if col_int in df_int.columns:
        df_int[col_int] = pd.to_numeric(df_int[col_int], errors='coerce').fillna(0)
        i = df_int.groupby('Data')[col_int].sum()
    else:
        i = pd.Series(dtype=float)
    
    # Unir e tratar NaNs
    df_plot = pd.DataFrame({'Realizado': r, 'Integrado': i}).fillna(0)
    df_plot = df_plot.sort_index().tail(12).reset_index()
    
    # Formatação de Data
    meses_en_pt = {'JAN': 'JAN', 'FEB': 'FEV', 'MAR': 'MAR', 'APR': 'ABR', 'MAY': 'MAI', 
                   'JUN': 'JUN', 'JUL': 'JUL', 'AUG': 'AGO', 'SEP': 'SET', 'OCT': 'OUT', 
                   'NOV': 'NOV', 'DEC': 'DEZ'}
    
    df_plot['Data_Label'] = pd.to_datetime(df_plot['Data']).dt.strftime('%d/%b').str.upper()
    for en, pt in meses_en_pt.items():
        df_plot['Data_Label'] = df_plot['Data_Label'].str.replace(en, pt)
    
    fig = px.bar(df_plot, x='Data_Label', y=['Realizado', 'Integrado'], barmode='group',
                 color_discrete_map={'Realizado': AZUL_TECADI, 'Integrado': AZUL_CLARO_TECADI},
                 text_auto='.0f')
    
    fig.update_layout(
        title=dict(text=titulo, font=dict(color=AZUL_TECADI, size=22, weight="bold")),
        plot_bgcolor='white', xaxis_title=None, yaxis_title=None, height=450
    )
    return fig

aba = st.session_state.aba_atual

if df_f is not None:
    if aba == 0: # --- ABA CARDS ---
        st.markdown("<h4 style='color: #1D569B; margin-bottom: 10px;'>📊 Visão Geral - Métricas do Dia</h4>", unsafe_allow_html=True)
        
        # 1. DEFINIÇÃO DAS DATAS
        hoje = datetime.now().date()
        ontem = hoje - pd.Timedelta(days=1)
        
        # Formatação para os títulos (Ex: 27/ABR)
        meses_pt = {1: 'JAN', 2: 'FEV', 3: 'MAR', 4: 'ABR', 5: 'MAI', 6: 'JUN',
                    7: 'JUL', 8: 'AGO', 9: 'SET', 10: 'OUT', 11: 'NOV', 12: 'DEZ'}
        
        label_hoje = f"{hoje.day:02d}/{meses_pt[hoje.month]}"
        label_ontem = f"{ontem.day:02d}/{meses_pt[ontem.month]}"

        # 2. FILTRAGEM
        df_hoje = df_f[df_f['Data'] == hoje]
        df_ontem = df_f[df_f['Data'] == ontem]

        # 3. CÁLCULO
        l_h, l_o = df_hoje['Linhas montadas'].sum(), df_ontem['Linhas montadas'].sum()
        p_h, p_o = df_hoje['Peças montadas'].sum(), df_ontem['Peças montadas'].sum()
        ped_h, ped_o = df_hoje['Código'].nunique(), df_ontem['Código'].nunique()

        # 4. CÁLCULO DAS DIFERENÇAS
        diff_linhas = l_h - l_o
        diff_pecas = p_h - p_o
        diff_pedidos = ped_h - ped_o

        # 5. DEFINIÇÃO DOS SINAIS PARA FORÇAR A COR
        s_lin = "+" if diff_linhas >= 0 else "-"
        s_pec = "+" if diff_pecas >= 0 else "-"
        s_ped = "+" if diff_pedidos >= 0 else "-"
        
        # 6. EXIBIÇÃO DOS CARDS
        c1, c2, c3 = st.columns([1,1,1])
        
        c1.metric(
            label=f"Linhas Realizadas ({label_hoje})",
            value=formatar_br(l_h),
            delta=f"{s_lin} {formatar_br(l_o)} em {label_ontem}"
        )
        
        c2.metric(
            label=f"Peças Realizadas ({label_hoje})",
            value=formatar_br(p_h),
            delta=f"{s_pec} {formatar_br(p_o)} em {label_ontem}"
        )
        
        c3.metric(
            label=f"Pedidos Realizados ({label_hoje})",
            value=formatar_br(ped_h),
            delta=f"{s_ped} {formatar_br(ped_o)} em {label_ontem}"
        )

        # 7. EXIBIÇÃO DOS PENDENTES POR TIPO
        colunas_df = df_p_proc.columns.tolist()
        
        # Buscar coluna de quantidade (QTD, Qtd, etc)
        col_qtd_pend = next((c for c in colunas_df if 'PEÇAS SOLICITADAS' in c.upper() or 'PECAS SOLICITADAS' in c.upper()), None)
        if not col_qtd_pend:
            col_qtd_pend = next((c for c in colunas_df if 'QTD' in c.upper()), colunas_df[2] if len(colunas_df) > 2 else None)
        
        # Buscar coluna de linhas
        col_linhas_pend = next((c for c in colunas_df if 'LINHA' in c.upper()), None)
        
        # Buscar coluna de pedido
        col_pedido_pend = next((c for c in colunas_df if 'PEDIDO' in c.upper() or 'Nº' in c), colunas_df[1] if len(colunas_df) > 1 else None)
        
        # Debug: mostrar colunas disponíveis
        # st.write("Colunas disponíveis:", colunas_df)
        
        # --- PICKING ---
        st.markdown("<h5 style='color: #1D569B; margin-top: 12px;'>🎯 PICKING</h5>", unsafe_allow_html=True)
        if df_picking is not None and not df_picking.empty:
            p1, p2, p3 = st.columns(3)
            with p1:
                val_lin = df_picking[col_linhas_pend].sum() if col_linhas_pend and col_linhas_pend in df_picking.columns else 0
                st.metric("Linhas Pendentes", formatar_br(val_lin))
            with p2:
                val_peca = df_picking[col_qtd_pend].sum() if col_qtd_pend and col_qtd_pend in df_picking.columns else 0
                st.metric("Peças Pendentes", formatar_br(val_peca))
            with p3:
                val_ped = df_picking[col_pedido_pend].nunique() if col_pedido_pend and col_pedido_pend in df_picking.columns else len(df_picking)
                st.metric("Tarefas Pendentes", formatar_br(val_ped))
        else:
            st.info("Nenhum pendiente de PICKING")
        
        # --- PACKING ---
        st.markdown("<h5 style='color: #1D569B; margin-top: 12px;'>📦 PACKING</h5>", unsafe_allow_html=True)
        if df_packing is not None and not df_packing.empty:
            p1, p2, p3 = st.columns(3)
            with p1:
                val_lin = df_packing[col_linhas_pend].sum() if col_linhas_pend and col_linhas_pend in df_packing.columns else 0
                st.metric("Linhas Pendentes", formatar_br(val_lin))
            with p2:
                val_peca = df_packing[col_qtd_pend].sum() if col_qtd_pend and col_qtd_pend in df_packing.columns else 0
                st.metric("Peças Pendentes", formatar_br(val_peca))
            with p3:
                val_ped = df_packing[col_pedido_pend].nunique() if col_pedido_pend and col_pedido_pend in df_packing.columns else len(df_packing)
                st.metric("Pedidos Pendentes", formatar_br(val_ped))
        else:
            st.info("Nenhum pendiente de PACKING")
        
    elif aba == 1: # LINHAS
        # col_int mudou para 'Linhas' (conforme sua imagem)
        st.plotly_chart(criar_figura(df_f, df_i, 'Linhas montadas', 'Linhas', "Linhas: Realizado vs Integrado"), use_container_width=True)
    
    elif aba == 2: # PEÇAS
        # col_int mudou para 'Peças'
        st.plotly_chart(criar_figura(df_f, df_i, 'Peças montadas', 'Peças', "Peças: Realizado vs Integrado"), use_container_width=True)
    
    elif aba == 3: # PEDIDOS
        # col_int mudou para 'Pedidos'
        st.plotly_chart(criar_figura(df_f, df_i, 'Código', 'Pedidos', "Pedidos: Realizado vs Integrado", op="count"), use_container_width=True)
    elif aba == 4: # --- ABA BACKLOG (PENDENTES D+2) ---
        st.subheader("📋 Backlog de Pedidos (Atrasados D+2)")

        # 1. IDENTIFICAÇÃO DINÂMICA E LIMPEZA
        df_backlog = df_p_proc.copy()
        df_backlog.columns = df_backlog.columns.str.strip()

        # Identificar colunas de data e hora
        col_data = next((c for c in ['Data', 'Data Integração', 'Data Pedido'] if c in df_backlog.columns), df_backlog.columns[0])
        col_hora = next((c for c in ['Hora', 'Hora Integração', 'Hora Pedido'] if c in df_backlog.columns), df_backlog.columns[1])
       
        # 2. CRIAR TIMESTAMP E CALCULAR PRAZO (SEM ERRO DE TIMEDELTA)
        # Convertemos para datetime completo do Pandas (Timestamp)
        df_backlog['Data_Hora_Integracao'] = pd.to_datetime(
            df_backlog[col_data].astype(str).str.split(' ').str[0] + ' ' + df_backlog[col_hora].astype(str),
            errors='coerce'
        )
       
        # Pegamos o momento atual como Timestamp para comparação direta
        agora = pd.Timestamp.now().normalize()

        def calcular_limite_v2(dt):
            if pd.isna(dt):
                return pd.NaT
           
            # Racional: Se integrou às 16h ou depois, o "Dia 0" é o dia seguinte
            # Usamos normalize() para garantir que trabalhamos apenas com a data na comparação final
            data_base = dt.normalize() if dt.hour < 16 else (dt + pd.Timedelta(days=1)).normalize()
           
            # Prazo final é Data Base + 2 dias
            return data_base + pd.Timedelta(days=2)

        df_backlog['Data_Limite'] = df_backlog['Data_Hora_Integracao'].apply(calcular_limite_v2)
       
        # Filtro de Backlog: Data Limite é ANTERIOR a hoje
        df_atrasados = df_backlog[df_backlog['Data_Limite'] < agora].copy()

        # 3. CÁLCULO DE DIAS DE ATRASO
        if not df_atrasados.empty:
            df_atrasados['Dias_Atraso'] = (agora - df_atrasados['Data_Limite']).dt.days
        else:
            df_atrasados['Dias_Atraso'] = 0

        # 4. CONTADORES (KPIs)
        col_qtd = next((c for c in ['Qtd', 'QTD Enviada', 'Peças'] if c in df_backlog.columns), None)
        col_linhas = next((c for c in ['Linhas', 'Linhas Enviadas'] if c in df_backlog.columns), None)

        c1, c2, c3 = st.columns(3)
        with c1:
            val_pecas = df_atrasados[col_qtd].sum() if col_qtd else 0
            st.metric("Peças em Backlog", formatar_br(val_pecas))
        with c2:
            st.metric("Pedidos em Backlog", formatar_br(df_atrasados['Nº Pedido'].nunique() if 'Nº Pedido' in df_atrasados.columns else len(df_atrasados)))
        with c3:
            val_linhas = df_atrasados[col_linhas].sum() if col_linhas else 0
            st.metric("Linhas em Backlog", formatar_br(val_linhas))

        st.markdown("---")

        # 5. TABELA COM SIRENE
        if not df_atrasados.empty:
            def categorizar_atraso(dias):
                if dias >= 5: return "🚨 CRÍTICO (5+ dias)"
                if dias >= 3: return "⚠️ ALTO (3-4 dias)"
                return "🕒 MODERADO (1-2 dias)"

            df_atrasados['Status_Atraso'] = df_atrasados['Dias_Atraso'].apply(categorizar_atraso)
            df_atrasados = df_atrasados.sort_values('Dias_Atraso', ascending=False)

            cols_show = ['Status_Atraso', col_data, 'Nº Pedido', 'Dias_Atraso']
            cols_show = [c for c in cols_show if c in df_atrasados.columns]

            st.dataframe(
                df_atrasados[cols_show],
                use_container_width=True,
                hide_index=True,
                column_config={
                    col_data: st.column_config.DateColumn("Integração", format="DD/MM/YYYY"),
                    "Status_Atraso": "Gravidade"
                }
            )
        else:
            st.success("✅ Tudo em dia! Nenhum pedido fora do prazo D+2.")
    elif aba == 5: # --- ABA CORTES ---
       
       
        df_c_clean = df_c.copy()
        df_c_clean = df_c_clean.loc[:, ~df_c_clean.columns.duplicated()]
        df_c_clean.columns = df_c_clean.columns.str.strip()
       
        # Preenchimento de células mescladas
        df_c_clean.iloc[:, 0] = df_c_clean.iloc[:, 0].ffill()
        df_c_clean.iloc[:, 1] = df_c_clean.iloc[:, 1].ffill()
       
        col_data_c = 'DT_FIM_PACKING' if 'DT_FIM_PACKING' in df_c_clean.columns else df_c_clean.columns[1]
        col_qtd_c = 'Qtd Corte' if 'Qtd Corte' in df_c_clean.columns else 'Qtd. Cortada'
       
        if col_qtd_c in df_c_clean.columns:
            df_c_clean[col_data_c] = pd.to_datetime(df_c_clean[col_data_c], errors='coerce')
            df_c_clean[col_qtd_c] = pd.to_numeric(df_c_clean[col_qtd_c], errors='coerce').fillna(0)
           
            df_c_evol = df_c_clean.groupby(col_data_c)[col_qtd_c].sum().reset_index().sort_values(col_data_c).tail(15)
           
            # DICIONÁRIO DE TRADUÇÃO PARA GARANTIR O "ABR"
            meses_en_pt = {'JAN': 'JAN', 'FEB': 'FEV', 'MAR': 'MAR', 'APR': 'ABR', 'MAY': 'MAI', 'JUN': 'JUN',
                           'JUL': 'JUL', 'AUG': 'AGO', 'SEP': 'SET', 'OCT': 'OUT', 'NOV': 'NOV', 'DEC': 'DEZ'}
           
            # Cria a label e substitui o mês para o padrão PT-BR
            df_c_evol['Data_Formatada'] = df_c_evol[col_data_c].dt.strftime('%d/%b').str.upper()
            for en, pt in meses_en_pt.items():
                df_c_evol['Data_Formatada'] = df_c_evol['Data_Formatada'].str.replace(en, pt)
           
            fig_evol_c = go.Figure()
            fig_evol_c.add_trace(go.Scatter(
                x=df_c_evol['Data_Formatada'],
                y=df_c_evol[col_qtd_c],
                mode='lines+markers+text',
                line=dict(color=AZUL_TECADI, width=4), # COR ALTERADA PARA AZUL TECADI
                marker=dict(size=10, color=AZUL_TECADI, line=dict(width=2, color="white")), # COR ALTERADA PARA AZUL TECADI
                text=[f"{v/1000:.1f}k" if v >= 1000 else f"{v:.0f}" for v in df_c_evol[col_qtd_c]],
                textposition="top center",
                textfont=dict(size=12, color=AZUL_ESCURO, family="Arial", weight="bold")
            ))
           
            fig_evol_c.update_layout(
                title=dict(text="Evolução de Peças Cortadas", font=dict(color=AZUL_TECADI, size=22, weight="bold")),
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=False, title=""),
                yaxis=dict(showgrid=True, gridcolor='#F0F0F0', title="Qtd Peças"),
                margin=dict(l=20, r=20, t=60, b=20), height=450
            )
            st.plotly_chart(fig_evol_c, use_container_width=True)

    elif aba == 6: # --- ABA PULOS (RACIONAL FIEL AO PULOS_ZEN.PY) ---
       

        # 1. CÓPIA E PREPARAÇÃO (Racional do Pulos_Zen.py)
        df_f = df_p_pul.copy()
        df_f.columns = df_f.columns.str.strip()

        # Ajuste de Data e Hora para criar o Timestamp completo
        df_f['Timestamp'] = pd.to_datetime(
            df_f['Data'].astype(str).str.split(' ').str[0] + ' ' + df_f['Hora'].astype(str),
            errors='coerce'
        )

        # 2. ORDENAÇÃO E REGRA DE NEGÓCIO (Janela de 5 minutos)
        df_f = df_f.sort_values(by=['Usuario', 'Endereco', 'Timestamp']) #

        # Cálculo da diferença em minutos por Usuário e Endereço
        df_f['Diff_Minutos'] = df_f.groupby(['Usuario', 'Endereco'])['Timestamp'].diff().dt.total_seconds() / 60 #

        # Identifica o que é um "Novo Pulo" (Diferença > 5 minutos ou primeira ocorrência)
        df_f['Novo_Pulo'] = (df_f['Diff_Minutos'].isna()) | (df_f['Diff_Minutos'] > 5) #

        # Filtra apenas os pulos reais
        df_pulos_reais = df_f[df_f['Novo_Pulo'] == True].copy() #

        # 3. AGRUPAMENTO PARA O GRÁFICO
        df_pulos_reais['Data_Dia'] = df_pulos_reais['Timestamp'].dt.date
        df_evol = df_pulos_reais.groupby('Data_Dia').size().reset_index(name='Pulos')
        df_evol = df_evol.sort_values('Data_Dia').tail(15)

        # 4. TRADUÇÃO DOS MESES E FORMATAÇÃO VISUAL
        meses_dict = {
            1: 'JAN', 2: 'FEV', 3: 'MAR', 4: 'ABR', 5: 'MAI', 6: 'JUN',
            7: 'JUL', 8: 'AGO', 9: 'SET', 10: 'OUT', 11: 'NOV', 12: 'DEZ'
        }

        if not df_evol.empty:
            df_evol['Data_Label'] = df_evol['Data_Dia'].apply(
                lambda x: f"{x.day:02d}/{meses_dict[x.month]}"
            )

            # 5. GRÁFICO (Visual original do Scatter com linhas e marcadores)
            fig_pulos = go.Figure()
            fig_pulos.add_trace(go.Scatter(
                x=df_evol['Data_Label'],
                y=df_evol['Pulos'],
                mode='lines+markers+text',
                line=dict(color=AZUL_TECADI, width=4), # COR DEFINIDA COMO AZUL TECADI
                marker=dict(size=10, color=AZUL_TECADI, line=dict(width=2, color='white')), # COR DEFINIDA COMO AZUL TECADI
                text=df_evol['Pulos'],
                textposition="top center",
                textfont=dict(size=12, color=AZUL_ESCURO, weight="bold")
            ))

            fig_pulos.update_layout(
                title=dict(text="Evolução Total de Pulos Reais", font=dict(color=AZUL_TECADI, size=22, weight="bold")),
                plot_bgcolor='white',
                xaxis=dict(showgrid=False, type='category'),
                yaxis=dict(showgrid=True, gridcolor='#F0F0F0'),
                margin=dict(l=20, r=20, t=60, b=20),
                height=450
            )

            st.plotly_chart(fig_pulos, use_container_width=True)
        else:
            st.info("Aguardando carregamento de dados válidos...")

# Fora do bloco das abas (ao final do código principal)
# st.rerun() # Use apenas se necessário para atualizar dados em tempo real

# --- AUTOPLAY ---
if autoplay:
    time.sleep(10)
    proxima_aba()
    st.rerun()
