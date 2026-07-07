import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import argparse
from decimal import Decimal
from typing import List

from src.repositories.recipe_repository import JsonRecipeRepository
from src.clients.albion_data_client import AlbionDataClient, AlbionDataClientException
from src.services.price_service import PriceService, PotionSaleStrategy
from src.services.craft_calculator import CraftCalculator
from src.services.potion_scanner import PotionScanner
from src.domain.models import CalculationParameters, ProfitCalculation, ScanResult

def format_silver(value: Decimal) -> str:
    """Formats a decimal value as silver coins (e.g. 1,234.56)."""
    return f"{value:,.2f}"

def format_percentage(value: Decimal) -> str:
    """Formats a decimal value as a percentage (e.g. 12.34%)."""
    return f"{value * 100:.2f}%"

def print_banner() -> None:
    print("=" * 70)
    print("          ANALISADOR DE LUCRATIVIDADE DE POCOES - ALBION ONLINE          ")
    print("=" * 70)
    print(" Considera Brecilien para compra de ingredientes, criacao e venda.")
    print("-" * 70)

def main() -> None:
    parser = argparse.ArgumentParser(
        description="AlbionPotionScanner - Analisa a lucratividade de criacao de pocoes in Brecilien."
    )
    parser.add_argument(
        "--mrr", "-m",
        type=str,
        default="0.15",
        help="Taxa de Retorno de Material (MRR) como fracao decimal (ex: 0.15 para 15%%). Padrao: 0.15"
    )
    parser.add_argument(
        "--fee", "-f",
        type=str,
        default="0.0",
        help="Taxa da estacao de criacao (fee) em prata por acao de criacao. Padrao: 0.0"
    )
    parser.add_argument(
        "--tax", "-t",
        type=str,
        default="0.04",
        help="Taxa de imposto de mercado como fracao decimal (ex: 0.04 para 4%%). Padrao: 0.04"
    )
    parser.add_argument(
        "--strategy", "-s",
        choices=["sell_order", "buy_order"],
        default="sell_order",
        help="Estrategia de preco para venda de pocoes (sell_order = ordem de venda / buy_order = venda imediata). Padrao: sell_order"
    )
    parser.add_argument(
        "--recipes", "-r",
        type=str,
        default="data/potion-recipes.json",
        help="Caminho para o arquivo JSON de receitas. Padrao: data/potion-recipes.json"
    )
    parser.add_argument(
        "--base-url", "-b",
        type=str,
        default=AlbionDataClient.DEFAULT_BASE_URL,
        help=f"URL base da API do Albion Online Data. Padrao: {AlbionDataClient.DEFAULT_BASE_URL}"
    )

    args = parser.parse_args()

    # Parse and validate numerical parameters
    try:
        mrr = Decimal(args.mrr)
        fee = Decimal(args.fee)
        tax = Decimal(args.tax)
    except ValueError as e:
        print(f"Erro ao processar argumentos: os valores devem ser decimais validos. Detalhes: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        parameters = CalculationParameters(
            material_return_rate=mrr,
            crafting_station_fee=fee,
            marketplace_tax_rate=tax
        )
        parameters.validate()
    except ValueError as e:
        print(f"Erro de validacao nos parametros: {e}", file=sys.stderr)
        sys.exit(1)

    sale_strategy = (
        PotionSaleStrategy.SELL_ORDER
        if args.strategy == "sell_order"
        else PotionSaleStrategy.BUY_ORDER
    )

    print_banner()
    print(f"Carregando receitas de: {args.recipes}")
    
    # Initialize repository
    try:
        repo = JsonRecipeRepository(args.recipes)
    except Exception as e:
        print(f"Erro ao carregar banco de dados de receitas: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Receitas carregadas: {repo.count()}")
    print(f"Consultando API do Albion Online Data Project ({args.base_url})...")

    # Initialize client, services, and scanner
    client = AlbionDataClient(base_url=args.base_url)
    price_service = PriceService()
    calculator = CraftCalculator()
    scanner = PotionScanner(
        recipe_repository=repo,
        data_client=client,
        price_service=price_service,
        calculator=calculator
    )

    try:
        # Run scan
        result = scanner.scan(
            parameters=parameters,
            sale_strategy=sale_strategy
        )
    except AlbionDataClientException as e:
        print(f"\nErro de API: {e}", file=sys.stderr)
        print("Verifique sua conexao com a internet ou o status da API do Albion.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\nErro inesperado durante a analise: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        client.close()

    print("Analise concluida com sucesso.\n")

    # Sort calculations by profit descending
    sorted_calcs = sorted(result.calculations, key=lambda c: c.profit, reverse=True)

    # 1. Print Summary Table
    if sorted_calcs:
        print("+" + "-" * 68 + "+")
        print(f"| {'Nome da Pocao':<28} | {'ID do Item':<20} | {'Lucro':<10} | {'ROI':<8} |")
        print("+" + "-" * 68 + "+")
        for calc in sorted_calcs:
            profit_str = format_silver(calc.profit)
            roi_str = format_percentage(calc.roi) if calc.roi is not None else "N/A"
            # Format rows
            name_cut = calc.recipe.potion_name[:28]
            print(f"| {name_cut:<28} | {calc.recipe.potion_item_id:<20} | {profit_str:>10} | {roi_str:>8} |")
        print("+" + "-" * 68 + "+")
    else:
        print("Nenhum calculo valido ou lucrativo pode ser realizado.")

    # 2. Print Warnings / Skipped Recipes
    if result.skipped_recipe_count > 0:
        print(f"\nReceitas Ignoradas ({result.skipped_recipe_count}):")
        for warning in result.warnings:
            print(f"  * {warning}")

    # 3. Print Best Potion Detail
    if result.best_calculation_id and sorted_calcs:
        best_calc = next(c for c in sorted_calcs if c.calculation_id == result.best_calculation_id)
        recipe = best_calc.recipe

        print("\n" + "=" * 70)
        print(f"MELHOR POCAO PARA CRIACAO: {recipe.potion_name} ({recipe.potion_item_id})")
        print("=" * 70)
        print(f"  Lucro Liquido:       {format_silver(best_calc.profit)} prata (por acao de criacao)")
        roi_val = format_percentage(best_calc.roi) if best_calc.roi is not None else "N/A"
        print(f"  ROI:                 {roi_val}")
        print(f"  Rendimento (Yield):  {recipe.output_quantity} unidades")
        print("-" * 70)
        print("  DETALHES DE CUSTOS:")
        print(f"    Custo Bruto de Ingredientes:   {format_silver(best_calc.gross_ingredient_cost)} prata")
        print(f"    Retorno de Material (MRR):    -{format_silver(best_calc.returned_material_value)} prata (MRR: {format_percentage(mrr)})")
        print(f"    Custo Efetivo de Material:     {format_silver(best_calc.effective_ingredient_cost)} prata")
        print(f"    Taxa da Estacao de Criacao:   +{format_silver(best_calc.crafting_station_fee)} prata")
        print(f"    ---------------------------------------")
        print(f"    CUSTO TOTAL DE CRIACAO:        {format_silver(best_calc.total_cost)} prata")
        print("-" * 70)
        print("  DETALHES DE RECEITA:")
        print(f"    Preco de Venda do Item (un):   {best_calc.potion_sell_price.unit_price} prata (campo: '{best_calc.potion_sell_price.price_field}')")
        print(f"    Receita Bruta (rendimento):    {format_silver(best_calc.gross_revenue)} prata")
        print(f"    Imposto de Mercado:           -{format_silver(best_calc.marketplace_tax)} prata (imposto: {format_percentage(tax)})")
        print(f"    ---------------------------------------")
        print(f"    RECEITA LIQUIDA:               {format_silver(best_calc.net_revenue)} prata")
        print("=" * 70 + "\n")

if __name__ == "__main__":
    main()
