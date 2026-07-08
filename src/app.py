import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import pandas as pd
from decimal import Decimal
from datetime import datetime
from typing import List, Set, Optional

from src.repositories.recipe_repository import JsonRecipeRepository
from src.clients.albion_data_client import AlbionDataClient, AlbionDataClientException
from src.services.price_service import PriceService, PotionSaleStrategy, PriceServiceError
from src.services.craft_calculator import CraftCalculator
from src.services.potion_scanner import PotionScanner
from src.services.mastery_service import MasteryService
from src.domain.models import CalculationParameters, ProfitCalculation, ScanResult, PlayerMastery

# Configuração da Página do Streamlit
st.set_page_config(
    page_title="Albion Potion Scanner - Analisador",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização Customizada Premium
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    /* Substituição global de fontes */
    html, body, [class*="css"], .stMarkdown {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Cartões de resumo KPI */
    .kpi-card {
        background: linear-gradient(135deg, #1e293b, #0f172a);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        margin-bottom: 20px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
    }
    .best-card {
        background: linear-gradient(135deg, #1e1b4b, #311042);
        border: 1px solid #581c87;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 4px 20px rgba(88, 28, 135, 0.25);
        margin-bottom: 25px;
    }
    .audit-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 15px;
    }
    .kpi-title {
        font-size: 14px;
        color: #94a3b8;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 8px;
    }
    .kpi-value {
        font-size: 28px;
        font-weight: 700;
        color: #f8fafc;
        margin: 0;
    }
    .best-title {
        font-size: 16px;
        color: #d8b4fe;
        font-weight: 600;
        text-transform: uppercase;
        margin-bottom: 10px;
    }
    .best-potion-name {
        font-size: 32px;
        font-weight: 700;
        color: #f3e8ff;
        margin: 0 0 15px 0;
    }
    .best-metric {
        font-size: 24px;
        font-weight: 700;
        color: #4ade80;
    }
    </style>
""", unsafe_allow_html=True)

# Funções auxiliares para formatação na interface
def format_silver(val: Decimal) -> str:
    return f"{val:,.2f} prata"

def format_pct(val: Decimal) -> str:
    return f"{val * 100:.2f}%"

# Caching no Streamlit para Preços de Mercado (reduz requisições ao mexer nos sliders)
@st.cache_data(ttl=120)  # Cache de 2 minutos
def cached_fetch_prices(base_url: str, unique_item_ids: List[str]) -> list:
    client = AlbionDataClient(base_url=base_url)
    try:
        return client.fetch_prices(unique_item_ids)
    finally:
        client.close()

# Menu de Navegação Lateral (Parâmetros)
st.sidebar.markdown("### 🧪 Parâmetros de Análise")

# Controles de Parâmetros
mrr_input = st.sidebar.slider(
    "Taxa de Retorno de Material (MRR)",
    min_value=0.0,
    max_value=50.0,
    value=15.0,
    step=0.1,
    format="%.1f%%"
)

station_fee_input = st.sidebar.number_input(
    "Taxa da Estação de Criação (Prata)",
    min_value=0,
    max_value=100000,
    value=0,
    step=50
)

tax_input = st.sidebar.slider(
    "Taxa de Imposto de Mercado",
    min_value=0.0,
    max_value=10.0,
    value=4.0,
    step=0.5,
    format="%.1f%%"
)

strategy_name = st.sidebar.selectbox(
    "Estratégia de Venda de Poções",
    options=["Ordem de Venda (Menor Preço de Venda)", "Venda Imediata (Maior Ordem de Compra)"]
)

server_region = st.sidebar.selectbox(
    "Região do Servidor Albion",
    options=["Américas / West", "Ásia / East", "Europa"]
)

# Mapeamento do servidor para URL
url_map = {
    "Américas / West": "https://west.albion-online-data.com",
    "Ásia / East": "https://east.albion-online-data.com",
    "Europa": "https://europe.albion-online-data.com"
}
base_url = url_map[server_region]

# Mapeamento da estratégia
sale_strategy = (
    PotionSaleStrategy.SELL_ORDER
    if "Ordem de Venda" in strategy_name
    else PotionSaleStrategy.BUY_ORDER
)

st.sidebar.markdown("---")
recipes_file = st.sidebar.text_input("Caminho do Arquivo de Receitas", value="data/potion-recipes.json")

# Seção de Cabeçalho Principal
st.title("🧪 Albion Online Potion Scanner")
st.markdown("Identifica as poções mais lucrativas para criar em **Brecilien** usando preços de mercado em tempo real da API do **Albion Online Data Project**.")
st.markdown("---")

# Carregar banco de dados de receitas
@st.cache_data
def load_recipes(path: str) -> JsonRecipeRepository:
    return JsonRecipeRepository(path)

try:
    repo = load_recipes(recipes_file)
except Exception as e:
    st.error(f"Falha ao carregar banco de dados de receitas: {e}")
    st.stop()

# Coleta de itens únicos para consulta
recipes = repo.get_all()
if not recipes:
    st.warning("Nenhuma receita carregada do arquivo JSON.")
    st.stop()

unique_item_ids: Set[str] = set()
for recipe in recipes:
    unique_item_ids.add(recipe.potion_item_id)
    for ing in recipe.ingredients:
        unique_item_ids.add(ing.item_id)

# Consulta de preços
with st.spinner("Buscando preços de mercado em tempo real na API do Albion Online Data..."):
    try:
        raw_prices = cached_fetch_prices(base_url, list(unique_item_ids))
    except AlbionDataClientException as e:
        st.error(f"Erro de API ao buscar dados de mercado: {e}")
        st.info("Certifique-se de que os servidores do Albion Online Data Project estão online e tente novamente.")
        st.stop()
    except Exception as e:
        st.error(f"Erro inesperado: {e}")
        st.stop()

# Inicialização de Serviços e Scanner
price_service = PriceService()
calculator = CraftCalculator()
scanner = PotionScanner(
    recipe_repository=repo,
    data_client=None,  # Preços pré-carregados e injetados abaixo
    price_service=price_service,
    calculator=calculator
)

# Conversão de entradas para decimais (ajustando de porcentagem para fração)
parameters = CalculationParameters(
    material_return_rate=Decimal(str(mrr_input)) / Decimal("100"),
    crafting_station_fee=Decimal(str(station_fee_input)),
    marketplace_tax_rate=Decimal(str(tax_input)) / Decimal("100")
)

# Execução do Scanner e Tratamento de Erros
calculations: List[ProfitCalculation] = []
scan_warnings: List[str] = []

for recipe in recipes:
    try:
        potion_price = price_service.select_price(
            raw_prices=raw_prices,
            item_id=recipe.potion_item_id,
            role="potion sale",
            quality=1,
            sale_strategy=sale_strategy
        )

        ingredient_prices = []
        for ing in recipe.ingredients:
            ing_price = price_service.select_price(
                raw_prices=raw_prices,
                item_id=ing.item_id,
                role="ingredient purchase",
                quality=1
            )
            ingredient_prices.append(ing_price)

        calc = calculator.calculate_profitability(
            recipe=recipe,
            ingredient_prices=ingredient_prices,
            potion_sell_price=potion_price,
            parameters=parameters
        )
        calculations.append(calc)
    except PriceServiceError as e:
        scan_warnings.append(f"Receita '{recipe.recipe_id}' ignorada: {e}")
    except ValueError as e:
        scan_warnings.append(f"Receita '{recipe.recipe_id}' ignorada devido a erro de validação: {e}")

valid_count = len(calculations)
skipped_count = len(recipes) - valid_count

# Seleção do Melhor Cálculo usando desempate determinístico (apenas se houver lucro positivo)
best_calc: Optional[ProfitCalculation] = None
if calculations and any(c.profit > Decimal("0") for c in calculations):
    def sort_key(c):
        profit_val = c.profit
        roi_val = c.roi if c.roi is not None else Decimal("-inf")
        return (-profit_val, -roi_val, c.recipe.potion_item_id)
    
    sorted_calcs = sorted(calculations, key=sort_key)
    best_calc = sorted_calcs[0]

# --- ESPECIALIZAÇÃO (MASTERY) BAR ---
mastery_service = MasteryService(file_path="data/player-mastery.json", recipe_repository=repo)
if "masteries" not in st.session_state:
    st.session_state.masteries = mastery_service.load_mastery()

st.markdown("### 🏆 Especialização de Criação (Mastery)")

# Estilos customizados para os cards de maestria
st.markdown("""
    <style>
    /* Estilizar a caixa de container com borda do Streamlit como um card real */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: linear-gradient(135deg, #1e293b, #0f172a) !important;
        border: 1px solid #334155 !important;
        border-radius: 12px !important;
        padding: 10px 8px !important;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.25) !important;
        margin-bottom: 12px !important;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: #3b82f6 !important;
        transform: translateY(-2px);
    }

    /* Centralizar e ajustar o number input dentro do card */
    div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stNumberInput"] {
        width: 100% !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    /* Forçar todos os wrappers gerados pelo widget do Streamlit no card a serem transparentes e sem borda */
    div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stNumberInput"] div,
    div[data-testid="stVerticalBlockBorderWrapper"] div[data-baseweb="base-input"],
    div[data-testid="stVerticalBlockBorderWrapper"] div[data-baseweb="input"] {
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }

    /* Estilizar a caixa de entrada de número de maestria para ser minimalista e transparente */
    div[data-testid="stVerticalBlockBorderWrapper"] input {
        text-align: right !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        background-color: transparent !important;
        color: #f8fafc !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
        width: 100% !important;
    }

    /* Esconder botões de mais/menos do number_input no card */
    div[data-testid="stVerticalBlockBorderWrapper"] button {
        display: none !important;
    }
    </style>
""", unsafe_allow_html=True)

# Coletar poções únicas dos dados carregados
unique_potions = {}
for r in recipes:
    if r.potion_item_id not in unique_potions:
        unique_potions[r.potion_item_id] = r.potion_name

# Renderização do grid horizontal (8 colunas)
cols = st.columns(8)
fallback_svg = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='64' height='64' viewBox='0 0 64 64'><rect width='64' height='64' fill='%231e293b' rx='8' stroke='%23334155'/><text x='50%25' y='65%25' dominant-baseline='middle' text-anchor='middle' font-family='sans-serif' font-size='32' fill='%2394a3b8'>🧪</text></svg>"

for i, (item_id, name) in enumerate(unique_potions.items()):
    col = cols[i % 8]
    m_level = st.session_state.masteries.get(item_id, PlayerMastery(item_id, 0)).mastery_level
    img_url = f"https://render.albiononline.com/v1/item/{item_id}.png"
    
    with col:
        with st.container(border=True):
            st.markdown(f"""
                <div style="text-align: center; margin-bottom: 4px;" title="{name}">
                    <img src="{img_url}" onerror="this.onerror=null; this.src='{fallback_svg}';" width="64" height="64" style="object-fit: contain; margin: 0 auto; display: block;"/>
                </div>
            """, unsafe_allow_html=True)
            
            # Subcolunas para alinhar a caixa minimalista de input com o texto /100 (tamanho reduzido para a entrada)
            sub_col1, sub_col2 = st.columns([3, 4])
            
            with sub_col1:
                # Entrada direta de nível
                new_val = st.number_input(
                    label=f"Especialização de {name}",
                    min_value=0,
                    max_value=100,
                    value=m_level,
                    step=1,
                    key=f"card_input_{item_id}",
                    label_visibility="collapsed"
                )
            
            with sub_col2:
                # Texto fixo de cap
                st.markdown(
                    '<div style="font-size: 15px; font-weight: 700; color: #64748b; line-height: 38px; text-align: left;">/100</div>',
                    unsafe_allow_html=True
                )
            
            # Barra de progresso visual
            st.markdown(f"""
                <div style="background: #334155; border-radius: 4px; height: 6px; margin-top: 4px; margin-bottom: 8px; overflow: hidden; width: 100%;">
                    <div style="background: linear-gradient(90deg, #3b82f6, #10b981); width: {new_val}%; height: 100%;"></div>
                </div>
            """, unsafe_allow_html=True)
            
            if new_val != m_level:
                clamped = max(0, min(100, int(new_val)))
                mastery_service.save_mastery(item_id, clamped)
                st.session_state.masteries[item_id] = PlayerMastery(item_id, clamped)
                st.rerun()

# Painel expander de controle para atualizar os valores de especialização
with st.expander("⚙️ Gerenciar Especializações (Mastery)"):
    sorted_names = sorted(unique_potions.keys(), key=lambda k: unique_potions[k])
    options_map = {unique_potions[k]: k for k in sorted_names}
    
    selected_potion_name = st.selectbox("Selecione a Poção para Ajustar", options=list(options_map.keys()))
    selected_potion_id = options_map[selected_potion_name]
    
    current_level = st.session_state.masteries.get(selected_potion_id, PlayerMastery(selected_potion_id, 0)).mastery_level
    new_level = st.number_input("Nível de Especialização (0-100)", min_value=0, max_value=100, value=current_level, step=1, key=f"number_input_{selected_potion_id}")
    
    if new_level is not None:
        if new_level != current_level:
            clamped = max(0, min(100, int(new_level)))
            mastery_service.save_mastery(selected_potion_id, clamped)
            st.session_state.masteries[selected_potion_id] = PlayerMastery(selected_potion_id, clamped)
            st.rerun()

st.markdown("---")

# --- PAINEL DE METRICAS KPI ---
kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

with kpi_col1:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Total de Receitas</div>
            <div class="kpi-value">{len(recipes)}</div>
        </div>
    """, unsafe_allow_html=True)

with kpi_col2:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Análises Válidas</div>
            <div class="kpi-value">{valid_count}</div>
        </div>
    """, unsafe_allow_html=True)

with kpi_col3:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Receitas Ignoradas</div>
            <div class="kpi-value">{skipped_count}</div>
        </div>
    """, unsafe_allow_html=True)

with kpi_col4:
    best_pot_name = best_calc.recipe.potion_name if best_calc else "N/A"
    best_pot_profit = format_silver(best_calc.profit) if best_calc else "N/A"
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Melhor Poção</div>
            <div class="kpi-value" style="font-size: 20px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="{best_pot_name} ({best_pot_profit})">
                {best_pot_name}
            </div>
        </div>
    """, unsafe_allow_html=True)

# --- RECOMENDAÇÃO EM DESTAQUE ---
if best_calc:
    roi_val_pct = format_pct(best_calc.roi) if best_calc.roi is not None else "N/A"
    st.markdown(f"""
        <div class="best-card">
            <div class="best-title">🏆 Melhor Recomendação</div>
            <h1 class="best-potion-name">{best_calc.recipe.potion_name} ({best_calc.recipe.potion_item_id})</h1>
            <div style="display: flex; gap: 40px; margin-top: 10px;">
                <div>
                    <span style="font-size: 14px; color: #c084fc;">Lucro Líquido (Por Ação de Criação)</span>
                    <div class="best-metric">{format_silver(best_calc.profit)}</div>
                </div>
                <div>
                    <span style="font-size: 14px; color: #c084fc;">Retorno sobre Investimento (ROI)</span>
                    <div class="best-metric" style="color: #60a5fa;">{roi_val_pct}</div>
                </div>
                <div>
                    <span style="font-size: 14px; color: #c084fc;">Rendimento de Saída (Yield)</span>
                    <div class="best-metric" style="color: #fca5a5;">{best_calc.recipe.output_quantity} unidades</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
else:
    if calculations:
        st.info("Nenhuma oportunidade de criação lucrativa foi encontrada usando os preços de mercado atuais de Brecilien.")
    else:
        st.info("Nenhum cálculo pôde ser realizado. Verifique seus parâmetros ou a conexão de dados.")

# Divisão em abas para exibição dos resultados
tab1, tab2, tab3 = st.tabs(["📊 Tabela de Resultados", "🔍 Explorador de Receita", "⚠️ Diagnósticos e Avisos"])

# --- ABA 1: Tabela de Resultados ---
with tab1:
    st.subheader("Todas as Poções Analisadas")
    if calculations:
        data_rows = []
        for calc in calculations:
            data_rows.append({
                "Nome da Poção": calc.recipe.potion_name,
                "ID do Item": calc.recipe.potion_item_id,
                "Rendimento (Yield)": calc.recipe.output_quantity,
                "Custo Total": float(calc.total_cost),
                "Receita Bruta": float(calc.gross_revenue),
                "Imposto": float(calc.marketplace_tax),
                "Lucro Líquido": float(calc.profit),
                "ROI %": float(calc.roi * 100) if calc.roi is not None else None
            })
        df = pd.DataFrame(data_rows)
        df = df.sort_values(by="Lucro Líquido", ascending=False).reset_index(drop=True)
        
        st.dataframe(
            df.style.format({
                "Custo Total": "{:,.2f}",
                "Receita Bruta": "{:,.2f}",
                "Imposto": "{:,.2f}",
                "Lucro Líquido": "{:,.2f}",
                "ROI %": "{:.2f}%"
            }),
            use_container_width=True
        )
    else:
        st.write("Nenhum cálculo disponível.")

# --- ABA 2: Explorador de Receita ---
with tab2:
    st.subheader("Auditoria Detalhada da Receita")
    
    if calculations:
        selected_name = st.selectbox(
            "Selecione a Poção para Auditar",
            options=[calc.recipe.potion_name for calc in sorted(calculations, key=lambda c: c.recipe.potion_name)]
        )
        
        selected_calc = next(c for c in calculations if c.recipe.potion_name == selected_name)
        recipe = selected_calc.recipe
        
        col_audit1, col_audit2 = st.columns(2)
        
        with col_audit1:
            st.markdown(f"""
                <div class="audit-card">
                    <h4 style="margin-top: 0; color: #fca5a5;">Detalhamento de Custos</h4>
                    <p><b>Custo Bruto de Ingredientes:</b> {format_silver(selected_calc.gross_ingredient_cost)}</p>
                    <p><b>Retorno de Material Reciclado (MRR):</b> -{format_silver(selected_calc.returned_material_value)} (MRR: {format_pct(parameters.material_return_rate)})</p>
                    <hr style="border: 0; border-top: 1px solid #475569; margin: 10px 0;">
                    <p><b>Custo Efetivo de Materiais:</b> {format_silver(selected_calc.effective_ingredient_cost)}</p>
                    <p><b>Taxa da Estação de Criação:</b> +{format_silver(selected_calc.crafting_station_fee)}</p>
                    <hr style="border: 0; border-top: 2px solid #475569; margin: 10px 0;">
                    <h5 style="margin: 0; color: #f8fafc;">CUSTO TOTAL DE CRIAÇÃO: {format_silver(selected_calc.total_cost)}</h5>
                </div>
            """, unsafe_allow_html=True)
            
        with col_audit2:
            st.markdown(f"""
                <div class="audit-card">
                    <h4 style="margin-top: 0; color: #86efac;">Detalhamento de Receita</h4>
                    <p><b>Preço Unitário de Mercado:</b> {selected_calc.potion_sell_price.unit_price} prata (campo: '{selected_calc.potion_sell_price.price_field}')</p>
                    <p><b>Receita Bruta (Rendimento: {recipe.output_quantity} un):</b> {format_silver(selected_calc.gross_revenue)}</p>
                    <p><b>Imposto de Venda de Mercado:</b> -{format_silver(selected_calc.marketplace_tax)} (Imposto: {format_pct(parameters.marketplace_tax_rate)})</p>
                    <hr style="border: 0; border-top: 2px solid #475569; margin: 10px 0;">
                    <h5 style="margin: 0; color: #86efac;">RECEITA LÍQUIDA DE VENDAS: {format_silver(selected_calc.net_revenue)}</h5>
                    <h5 style="margin: 5px 0 0 0; color: #4ade80;">LUCRO LÍQUIDO: {format_silver(selected_calc.profit)}</h5>
                </div>
            """, unsafe_allow_html=True)
            
        st.write("#### Ingredientes Necessários")
        ing_rows = []
        prices_map = {p.item_id: p for p in selected_calc.ingredient_prices}
        for ing in recipe.ingredients:
            price_ent = prices_map.get(ing.item_id)
            unit_c = price_ent.unit_price if price_ent else 0
            total_c = unit_c * ing.quantity
            ing_rows.append({
                "Nome do Ingrediente": ing.item_name,
                "ID do Item": ing.item_id,
                "Grau (Tier)": ing.tier if ing.tier is not None else "N/A",
                "Qtd Necessária": ing.quantity,
                "Custo Unitário": float(unit_c),
                "Custo Total": float(total_c)
            })
        st.table(pd.DataFrame(ing_rows).style.format({
            "Custo Unitário": "{:,.2f}",
            "Custo Total": "{:,.2f}"
        }))
        
        # Avisos internos da poção
        if selected_calc.warnings:
            st.warning("Avisos para esta receita:")
            for w in selected_calc.warnings:
                st.write(f"- {w}")
    else:
        st.write("Nenhum cálculo disponível.")

# --- ABA 3: Diagnósticos e Avisos ---
with tab3:
    st.subheader("Avisos de Dados e Receitas Ignoradas")
    if scan_warnings:
        st.write(f"As seguintes {len(scan_warnings)} receitas foram ignoradas por falta de preços de mercado válidos:")
        for w in scan_warnings:
            st.error(w)
    else:
        st.success("Nenhuma receita foi ignorada. Todas as poções foram calculadas com sucesso!")
