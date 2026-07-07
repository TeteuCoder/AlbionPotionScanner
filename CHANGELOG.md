# Changelog

Todas as alterações notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado no [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/) e este projeto segue o [SemVer (Versionamento Semântico)](https://semver.org/lang/pt-BR/).

## [1.0.0] - 2026-07-07

Esta é a primeira versão estável oficial (**Brecilien V1**) do **Albion Online Potion Scanner**.

### Adicionado
- **Modelo de Domínio Completo**: Definição de entidades como `PotionRecipe`, `Ingredient`, `MarketPrice`, `CalculationParameters`, `ProfitCalculation` e `ScanResult` com validação de invariantes e regras financeiras robustas.
- **Integração com API Externa**: Cliente HTTP para comunicação e consulta em lote com a API do **Albion Online Data Project** (suportando servidores West, East e Europe).
- **Lógica de Decisão do Scanner**: Orquestração completa de busca de preços e cálculo de rentabilidade. Seletor de estratégia de preço de poção (Ordem de Venda / Venda Imediata).
- **Calculadora de Criação (Crafting)**: Suporte a Taxa de Retorno de Material (MRR), taxa de uso de estação e impostos de mercado, calculando custos efetivos e ROI (Retorno sobre Investimento).
- **Interface Premium Streamlit**:
  - Painel moderno de KPIs com totalizadores de receitas analisadas, válidas e ignoradas.
  - Painel de parametrização interativo na barra lateral com sliders formatados em porcentagem (MRR e impostos de mercado).
  - Aba de **Tabela de Resultados** detalhada e ordenável.
  - Aba de **Explorador de Receita** para auditoria detalhada de custos e receitas de poções individuais.
  - Aba de **Diagnósticos e Avisos** para detecção de dados em falta.
- **Suíte de Testes Unitários**: Cobertura completa de testes usando `pytest` (47 testes unitários validados com sucesso).

### Corrigido
- **Correção da Lógica de Recomendação**: O scanner agora diferencia cenários lucrativos de cenários sem oportunidades reais. O card de melhor recomendação e a KPI de "Melhor Poção" só exibem uma poção quando há lucro positivo (`profit > 0`). Caso contrário, é exibido um aviso amigável ao usuário e a KPI mostra `N/A`.
- **Ajustes de Acentuação e Ortografia**: Correção de vários textos e labels em português na interface e nos logs de warning para assegurar profissionalismo (ex: "Melhor Poção", "Análises Válidas", "validação", etc.).
