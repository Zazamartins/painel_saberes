import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Painel do Projeto 8174", layout="wide")

st.markdown("""
    <style>
    div[data-testid="metric-container"] {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 1px 1px 4px rgba(0,0,0,0.05);
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)


# =============================================================================
# 🟢 1. LOCAL PARA ALTERAR OS DADOS DO CABEÇALHO DO PROJETO
# Altere os textos entre aspas duplas caso precise mudar o nome do gestor, etc.
# =============================================================================
info_projeto = {
    "Cód. Projeto": "8174",
    "Nome Projeto": "MEC/UnB/ICS -Execução Financeira Ação Saberes Indígenas na Escola 13/10/2026",
    "Nome Coordenador": "GERSEM JOSE DOS SANTOS LUCIANO",
    "Nome Gestor": "VIVIAN PAPA PEREIRA PINTO"
}

# =============================================================================
# 🟢 2. LOCAL PARA ALTERAR AS DESPESAS (RUBRICAS)
# Cada bloco entre chaves {...} representa uma linha no gráfico e na tabela.
# PARA ADICIONAR UMA NOVA: Coloque uma vírgula no final da última chave }, 
# pule uma linha e adicione {"Rubrica": "Nome", "Valor Aprovado": 0.0, "Valor Executado": 0.0}
# =============================================================================
dados_rubricas = [
    {"Rubrica": "Despesas Financeiras", "Valor Aprovado": 0.00, "Valor Executado": 54.76},
    
    # Finatec inserida com valor aprovado igual ao executado (Dívida paga / Saldo R$ 0,00)
    {"Rubrica": "Desp. Operac. e Adm. - Finatec", "Valor Aprovado": 116590.91, "Valor Executado": 116590.91},
    
    {"Rubrica": "Diárias", "Valor Aprovado": 279725.00, "Valor Executado": 144090.00},
    {"Rubrica": "Encargos - ISS 5%", "Valor Aprovado": 6136.36, "Valor Executado": 6136.36},
    {"Rubrica": "Material de Consumo (Pagamento de Adiantamento)", "Valor Aprovado": 124996.95, "Valor Executado": 191162.99},
    {"Rubrica": "Passagens e Desp. Locomoção", "Valor Aprovado": 300000.00, "Valor Executado": 136656.49},
    {"Rubrica": "Serv. Terceiros Pessoa Jurídica", "Valor Aprovado": 522550.78, "Valor Executado": 99323.79}
]

# =============================================================================
# 🟢 3. LOCAL PARA ALTERAR O VALOR DAS RECEITAS / RENDIMENTOS
# Este valor será SOMADO ao saldo remanescente disponível no final.
# =============================================================================
total_receitas = 9189.78



# --- CÁLCULOS MATEMÁTICOS (Não é necessário alterar esta parte) ---
df_despesas = pd.DataFrame(dados_rubricas)
df_despesas["Saldo Remanescente"] = df_despesas["Valor Aprovado"] - df_despesas["Valor Executado"]

total_aprovado = df_despesas["Valor Aprovado"].sum()
total_executado = df_despesas["Valor Executado"].sum()
# O saldo remanescente é o que sobrou das rubricas MAIS o que rendeu
total_remanescente = df_despesas["Saldo Remanescente"].sum() + total_receitas

def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


# --- RENDERIZAÇÃO DO CABEÇALHO ---
st.markdown(f"## {info_projeto['Nome Projeto']}")
st.markdown(f"**Cód:** {info_projeto['Cód. Projeto']} | **Coordenador:** {info_projeto['Nome Coordenador']} | **Gestor:** {info_projeto['Nome Gestor']}")
st.markdown("---")

# --- RENDERIZAÇÃO DOS CARTÕES DE KPI ---
col1, col2, col3, col4 = st.columns(4)
col1.metric(label="Total Aprovado", value=formatar_moeda(total_aprovado))
col2.metric(label="Total Executado", value=formatar_moeda(total_executado), delta=f"{(total_executado/total_aprovado)*100:.1f}% do Aprovado", delta_color="inverse")
col3.metric(label="Saldo Remanescente (C/ Rendimentos)", value=formatar_moeda(total_remanescente))
col4.metric(label="Receitas (Rendimentos)", value=formatar_moeda(total_receitas))

st.markdown("<br>", unsafe_allow_html=True)

# --- RENDERIZAÇÃO DOS GRÁFICOS ---

# 1. GRÁFICO DE BARRAS (Linha Inteira)
st.markdown("### Orçamento: Aprovado vs Executado")
    
hover_aprovado = df_despesas['Valor Aprovado'].apply(formatar_moeda)
hover_executado = df_despesas['Valor Executado'].apply(formatar_moeda)
    
fig_barras = go.Figure(data=[
    go.Bar(name='Valor Aprovado', x=df_despesas['Rubrica'], y=df_despesas['Valor Aprovado'], 
           marker_color='#1f77b4', customdata=hover_aprovado,
           hovertemplate='<b>%{x}</b><br>Aprovado: %{customdata}<extra></extra>'),
    go.Bar(name='Valor Executado', x=df_despesas['Rubrica'], y=df_despesas['Valor Executado'], 
           marker_color='#ff7f0e', customdata=hover_executado,
           hovertemplate='<b>%{x}</b><br>Gasto: %{customdata}<extra></extra>')
])
    
fig_barras.update_layout(
    barmode='group', xaxis_tickangle=-45, 
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    margin=dict(t=0, b=0), hoverlabel=dict(font_size=16, font_family="Arial")
)
st.plotly_chart(fig_barras, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True) # Espaço extra entre as linhas de gráficos

# 2. GRÁFICOS CIRCULARES (Nova linha, dividida em 2 colunas)
col_pizza1, col_pizza2 = st.columns(2)

with col_pizza1:
    st.markdown("### Onde foi gasto?")
    df_gastos = df_despesas[df_despesas['Valor Executado'] > 0]
    fig_donut1 = px.pie(df_gastos, values='Valor Executado', names='Rubrica', hole=0.4)
    fig_donut1.update_traces(textposition='inside', textinfo='percent', hovertemplate='<b>%{label}</b><br>%{percent}<extra></extra>')
    fig_donut1.update_layout(showlegend=False, margin=dict(t=0, b=0))
    st.plotly_chart(fig_donut1, use_container_width=True)

with col_pizza2:
    st.markdown("### Status do Orçamento")
    df_status = pd.DataFrame({
        "Status": ["Executado", "Disponível (Saldo)"],
        "Valor": [total_executado, total_remanescente]
    })
    fig_donut2 = px.pie(df_status, values='Valor', names='Status', hole=0.4, 
                        color='Status', color_discrete_map={"Executado": "#ff7f0e", "Disponível (Saldo)": "#2ca02c"})
    fig_donut2.update_traces(textposition='inside', textinfo='percent+label', hovertemplate='<b>%{label}</b><br>%{percent}<extra></extra>')
    fig_donut2.update_layout(showlegend=False, margin=dict(t=0, b=0))
    st.plotly_chart(fig_donut2, use_container_width=True)


# --- TABELA DETALHADA COM RECEITAS E TOTAIS ---
st.markdown("### Detalhamento das Rubricas")

# Criamos uma linha dedicada às Receitas para somar ao saldo na tabela
linha_receitas = pd.DataFrame([{
    "Rubrica": "Receitas (Rendimentos)",
    "Valor Aprovado": 0.00,
    "Valor Executado": 0.00,
    "Saldo Remanescente": total_receitas
}])

# Linha final com os totais
linha_totais = pd.DataFrame([{
    "Rubrica": "TOTAL GERAL",
    "Valor Aprovado": total_aprovado,
    "Valor Executado": total_executado,
    "Saldo Remanescente": total_remanescente
}])

# Juntamos as despesas, as receitas e os totais
df_tabela_completa = pd.concat([df_despesas, linha_receitas, linha_totais], ignore_index=True)

# Formatação visual de moeda
df_visualizacao = df_tabela_completa.copy()
for col in ["Valor Aprovado", "Valor Executado", "Saldo Remanescente"]:
    df_visualizacao[col] = df_visualizacao[col].apply(formatar_moeda)

# Estilização
def colorir_saldos(val):
    if isinstance(val, str):
        if val.startswith("R$ -"):
            return 'background-color: #ffcccc; color: #b30000; font-weight: bold;'
        elif val != "R$ 0,00":
            return 'background-color: #ccffcc; color: #008000; font-weight: bold;'
    return ''

def estilizar_linhas_especiais(row):
    if row['Rubrica'] == 'TOTAL GERAL':
        return ['font-weight: bold; font-size: 16px; background-color: #e6f2ff; color: #000000;'] * len(row)
    elif row['Rubrica'] == 'Receitas (Rendimentos)':
        return ['font-weight: bold; font-style: italic; background-color: #fcfcfa; color: #555555;'] * len(row)
    return [''] * len(row)

tabela_estilizada = (df_visualizacao.style
                     .map(colorir_saldos, subset=['Saldo Remanescente'])
                     .apply(estilizar_linhas_especiais, axis=1))

st.dataframe(tabela_estilizada, use_container_width=True, hide_index=True)