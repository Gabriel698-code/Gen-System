import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import os
from datetime import datetime, timedelta

# 1. Configuração da Página
st.set_page_config(page_title="Gen System | Dashboard", layout="wide", page_icon="📊")

# 2. Estilo Dark Mode (Gen System Theme)
st.markdown("""
<style>
    /* --- FUNDO E FONTE --- */
    .stApp { background-color: #121214; color: #e1e1e6; font-family: 'Segoe UI', sans-serif; }

    /* --- CABEÇALHO --- */
    header[data-testid="stHeader"] { background-color: #121214 !important; border-bottom: 1px solid #202024; }
    .stDeployButton, footer { display: none !important; }
    .block-container { padding-top: 2rem !important; }

    /* --- CARDS DE MÉTRICAS --- */
    div[data-testid="metric-container"] {
        background: linear-gradient(145deg, #202024, #252529);
        border: 1px solid #323238;
        border-left: 4px solid #8257e5;
        padding: 15px 20px;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    div[data-testid="stMetricLabel"] { color: #a8a8b3; }
    div[data-testid="stMetricValue"] { color: #fff; }

    /* --- ABAS --- */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; border-bottom: 1px solid #323238; }
    .stTabs [data-baseweb="tab"] { background-color: transparent; color: #a8a8b3; border-radius: 8px; }
    .stTabs [aria-selected="true"] { background-color: #8257e5 !important; color: white !important; }

    /* --- BOTÕES GERAIS --- */
    .stButton > button {
        border-radius: 6px; font-weight: bold; transition: 0.3s; border: none;
    }
    
    /* Botão de Excluir (Vermelho sutil) */
    button[kind="secondary"] {
        background-color: rgba(233, 99, 121, 0.1);
        color: #e96379;
        border: 1px solid #e96379;
    }
    button[kind="secondary"]:hover {
        background-color: #e96379;
        color: white;
    }

    /* --- TABELAS CUSTOMIZADAS (LISTA) --- */
    .custom-header {
        display: grid; 
        padding: 12px; 
        border-bottom: 2px solid #323238; 
        font-weight: bold; 
        color: #8257e5;
        background-color: #1a1a1e;
        border-radius: 8px 8px 0 0;
        font-size: 0.9rem;
        margin-top: 15px;
    }
    
    .custom-row {
        padding: 12px;
        border-bottom: 1px solid #202024;
        display: grid;
        align-items: center;
        transition: 0.2s;
        font-size: 0.9rem;
    }
    .custom-row:hover { background-color: #202024; }
    
</style>
""", unsafe_allow_html=True)

# 3. Funções de Backend
def carregar_dados():
    conn = sqlite3.connect('leads.db')
    df_notas = pd.DataFrame()
    df_recibos = pd.DataFrame()
    df_orc = pd.DataFrame()
    df_docs = pd.DataFrame()
    
    try:
        # Notas
        df_geral = pd.read_sql_query("SELECT * FROM notas_fiscais_clientes ORDER BY criado_em DESC", conn)
        if not df_geral.empty:
            df_geral['data_emissao'] = pd.to_datetime(df_geral['data_emissao'])
            df_geral['criado_em_dt'] = pd.to_datetime(df_geral['criado_em']) 
            df_geral['mes'] = df_geral['data_emissao'].dt.strftime('%Y-%m')
            df_recibos = df_geral[df_geral['tipo_nota'] == 'RECIBO'].copy()
            df_notas = df_geral[df_geral['tipo_nota'] != 'RECIBO'].copy()

        # Orçamentos
        df_orc = pd.read_sql_query("SELECT * FROM orcamentos_clientes ORDER BY criado_em DESC", conn)
        if not df_orc.empty:
            df_orc['data_emissao'] = pd.to_datetime(df_orc['data_emissao'])
            df_orc['criado_em_dt'] = pd.to_datetime(df_orc['criado_em']) 
            df_orc['mes'] = df_orc['data_emissao'].dt.strftime('%Y-%m')
            df_orc['validade_dias'] = pd.to_numeric(df_orc['validade'].astype(str).str.replace(' dias',''), errors='coerce').fillna(30)
            df_orc['data_vencimento'] = df_orc['data_emissao'] + pd.to_timedelta(df_orc['validade_dias'], unit='D')
            hoje = pd.to_datetime(datetime.now().date())
            df_orc['status'] = df_orc['data_vencimento'].apply(lambda x: '🔴 Vencido' if x < hoje else '🟢 Válido')

        # Documentos (Histórico Completo)
        df_docs = pd.read_sql_query("SELECT * FROM documentos ORDER BY criado_em DESC", conn)
        if not df_docs.empty:
            df_docs['criado_em'] = pd.to_datetime(df_docs['criado_em'])
            df_docs['data'] = df_docs['criado_em'].dt.strftime('%d/%m/%Y %H:%M')

    except Exception as e: print(f"Erro DB: {e}")
    conn.close()
    return df_notas, df_recibos, df_orc, df_docs

def excluir_arquivo(id_doc, nome_arquivo):
    conn = sqlite3.connect('leads.db')
    try:
        conn.execute("DELETE FROM documentos WHERE id = ?", (id_doc,))
        conn.commit()
        caminho = os.path.join("documentos", nome_arquivo)
        if os.path.exists(caminho):
            os.remove(caminho)
            st.toast(f"🗑️ Arquivo {nome_arquivo} deletado.", icon="✅")
        else:
            st.toast(f"🗑️ Registro removido.", icon="⚠️")
    except Exception as e: st.error(f"Erro: {e}")
    finally: conn.close()

def encontrar_arquivo_associado(data_criacao_registro, df_documentos):
    """
    Tenta encontrar um arquivo no histórico que foi criado num intervalo de 
    tempo muito próximo ao registro financeiro (margem de 2 minutos).
    CORRIGIDO: Sem walrus operator.
    """
    if df_documentos.empty or pd.isna(data_criacao_registro): return None
    
    # Margem de tempo para linkar o registro do banco com o arquivo físico
    margem = timedelta(minutes=2)
    inicio = data_criacao_registro - margem
    fim = data_criacao_registro + margem
    
    # Filtra docs
    candidatos = df_documentos[
        (df_documentos['criado_em'] >= inicio) & 
        (df_documentos['criado_em'] <= fim)
    ]
    
    if not candidatos.empty:
        return candidatos.iloc[0]
    return None

# --- HEADER ---
c1, c2 = st.columns([4, 1])
with c1:
    st.title("Gen System Dashboard")
    st.markdown("<span style='color: #a8a8b3;'>Controle Financeiro e Documental Inteligente</span>", unsafe_allow_html=True)
with c2:
    if st.button("🔄 REFRESH"): st.rerun()

st.write("") 

df_notas, df_recibos, df_orc, df_docs = carregar_dados()

# --- ABAS ---
tab1, tab2, tab3, tab4 = st.tabs(["🧾 Notas Fiscais", "📝 Recibos", "🤝 Orçamentos", "🗂️ Arquivos (Geral)"])

# === ABA 1: NOTAS FISCAIS ===
with tab1:
    if df_notas.empty:
        st.info("Nenhuma Nota Fiscal emitida.")
    else:
        # Métricas
        total = df_notas['valor_total'].sum()
        c1, c2 = st.columns(2)
        c1.metric("Faturamento NFe", f"R$ {total:,.2f}")
        c2.metric("Qtd. Emitida", len(df_notas))
        
        st.divider()
        
        # Cabeçalho da Tabela
        st.markdown("""
        <div class="custom-header" style="grid-template-columns: 1fr 2fr 1fr 1fr 1fr;">
            <div>DATA</div>
            <div>DESTINATÁRIO</div>
            <div>VALOR</div>
            <div>TIPO</div>
            <div>DOWNLOAD</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Linhas
        for idx, row in df_notas.iterrows():
            c1, c2, c3, c4, c5 = st.columns([1, 2, 1, 1, 1])
            
            with c1: st.write(row['data_emissao'].strftime('%d/%m/%Y'))
            with c2: st.write(row['destinatario_nome'])
            with c3: st.write(f"R$ {row['valor_total']:,.2f}")
            with c4: st.caption(row['tipo_nota'])
            with c5:
                # Tenta baixar o XML direto do banco se existir
                if row['xml_completo']:
                    st.download_button("⬇️ XML", row['xml_completo'], file_name=f"nota_{row['chave_acesso']}.xml", key=f"xml_{row['id']}")
                else:
                    st.caption("-")
            
            st.markdown("<div style='border-bottom: 1px solid #202024; margin-bottom: 5px;'></div>", unsafe_allow_html=True)

# === ABA 2: RECIBOS ===
with tab2:
    if df_recibos.empty:
        st.info("Nenhum Recibo gerado.")
    else:
        total_rec = df_recibos['valor_total'].sum()
        c1, c2 = st.columns(2)
        c1.metric("Total Recibos", f"R$ {total_rec:,.2f}")
        c2.metric("Quantidade", len(df_recibos))
        
        st.divider()
        
        # Cabeçalho
        st.markdown("""
        <div class="custom-header" style="grid-template-columns: 1fr 2fr 1fr 1fr;">
            <div>DATA</div>
            <div>PAGADOR</div>
            <div>VALOR</div>
            <div>ARQUIVO</div>
        </div>
        """, unsafe_allow_html=True)
        
        for idx, row in df_recibos.iterrows():
            c1, c2, c3, c4 = st.columns([1, 2, 1, 1])
            
            with c1: st.write(row['data_emissao'].strftime('%d/%m/%Y'))
            with c2: st.write(row['destinatario_nome'])
            with c3: st.write(f"R$ {row['valor_total']:,.2f}")
            with c4:
                # Tenta achar o PDF correspondente no histórico
                doc_assoc = encontrar_arquivo_associado(row['criado_em_dt'], df_docs)
                if doc_assoc is not None:
                    path = os.path.join("documentos", doc_assoc['nome_arquivo'])
                    if os.path.exists(path):
                        with open(path, "rb") as f:
                            st.download_button("⬇️ PDF", f, file_name=doc_assoc['nome_arquivo'], key=f"rec_{row['id']}")
                    else: st.caption("Arquivo movido")
                else:
                    st.caption("Processando...")
            
            st.markdown("<div style='border-bottom: 1px solid #202024; margin-bottom: 5px;'></div>", unsafe_allow_html=True)

# === ABA 3: ORÇAMENTOS ===
with tab3:
    if df_orc.empty:
        st.info("Nenhum Orçamento criado.")
    else:
        total_orc = df_orc['valor_total'].sum()
        c1, c2 = st.columns(2)
        c1.metric("Pipeline Propostas", f"R$ {total_orc:,.2f}")
        c2.metric("Propostas", len(df_orc))
        
        st.divider()
        
        st.markdown("""
        <div class="custom-header" style="grid-template-columns: 1fr 2fr 1fr 1fr 1fr;">
            <div>DATA</div>
            <div>CLIENTE</div>
            <div>VALOR</div>
            <div>STATUS</div>
            <div>ARQUIVO</div>
        </div>
        """, unsafe_allow_html=True)
        
        for idx, row in df_orc.iterrows():
            c1, c2, c3, c4, c5 = st.columns([1, 2, 1, 1, 1])
            
            with c1: st.write(row['data_emissao'].strftime('%d/%m/%Y'))
            with c2: st.write(row['cliente_nome'])
            with c3: st.write(f"R$ {row['valor_total']:,.2f}")
            with c4: st.write(row['status'])
            with c5:
                doc_assoc = encontrar_arquivo_associado(row['criado_em_dt'], df_docs)
                if doc_assoc is not None:
                    path = os.path.join("documentos", doc_assoc['nome_arquivo'])
                    if os.path.exists(path):
                        with open(path, "rb") as f:
                            st.download_button("⬇️ PDF", f, file_name=doc_assoc['nome_arquivo'], key=f"orc_{row['id']}")
                    else: st.caption("Arquivo movido")
                else:
                    st.caption("Processando...")
            
            st.markdown("<div style='border-bottom: 1px solid #202024; margin-bottom: 5px;'></div>", unsafe_allow_html=True)

# === ABA 4: ARQUIVOS (GERENCIADOR) ===
with tab4:
    if df_docs.empty:
        st.info("📭 Nenhum documento no histórico.")
    else:
        # Filtros
        c_tipo, c_search = st.columns([1, 2])
        with c_tipo:
            tipos = ["Todos"] + list(df_docs['tipo'].unique())
            sel_tipo = st.selectbox("Filtrar Tipo:", tipos)
        
        df_show = df_docs if sel_tipo == "Todos" else df_docs[df_docs['tipo'] == sel_tipo]
        
        st.markdown("""
        <div class="custom-header" style="grid-template-columns: 2fr 3fr 1fr 1fr 1fr;">
            <div>DATA/HORA</div>
            <div>NOME DO ARQUIVO</div>
            <div>TIPO</div>
            <div>BAIXAR</div>
            <div>AÇÃO</div>
        </div>
        """, unsafe_allow_html=True)

        for index, row in df_show.iterrows():
            nome_arq = row['nome_arquivo']
            caminho_arq = os.path.join("documentos", nome_arq)
            existe = os.path.exists(caminho_arq)
            
            c1, c2, c3, c4, c5 = st.columns([2, 3, 1, 1, 1])
            
            with c1: st.write(row['data'])
            with c2: st.write(f"📄 {nome_arq}")
            with c3: st.caption(row['tipo'])
            with c4:
                if existe:
                    try:
                        with open(caminho_arq, "rb") as f:
                            st.download_button("⬇️", f, file_name=nome_arq, key=f"down_{row['id']}")
                    except: st.error("Erro")
                else: st.warning("Perdido")
            
            with c5:
                if st.button("🗑️", key=f"del_{row['id']}", type="secondary"):
                    excluir_arquivo(row['id'], nome_arq)
                    st.rerun()
            
            st.markdown("<div style='border-bottom: 1px solid #202024; margin-bottom: 5px;'></div>", unsafe_allow_html=True)
