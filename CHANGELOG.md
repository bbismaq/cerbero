# Changelog

## [0.2.0] — 2026-05-19

- Renomeado de `Checagem-de-oferta` para `Cerbero`.
- Pasta de relatórios passou de `~/Documents/Check-Offer/reports/` para `~/Documents/Cerbero/reports/`.

## [0.1.0] — 2026-05-15

Versão inicial.

### Funcionalidades

- Audita VSL/LP com checkouts no Pagamerican via `?pag_test_4=true` (sem precisar assistir o vídeo nem comprar).
- Extrai preço, preço por bottle, "De", "You save" e % off de todas as 18 ofertas típicas (3 LP + 15 funil).
- Mapeia estrutura completa do funil: entrada → upsell 1 (3 variantes) → downsell 1 → downsell 2, em cada um dos funis ligados aos botões da LP.
- Identifica as duas fontes de preço corretas:
  - LP: payload Next.js do Pagamerican (`originalUnitPrice`, `unitPrice`, `priceDiscountPercentage`).
  - Funil: HTML hardcoded da página do funil (`line-through`, `NORMALLY/TODAY`, `discount-highlight`).
- 13 checks automáticos em toda execução (sem omissão), incluindo:
  - Per-bottle exibido vs. calculado
  - Headline `U$X Discount` vs. desconto real
  - Outliers de per-bottle (menor e maior do funil)
  - Upsell var.3 == entrada do funil
  - Mesmo total entre ofertas
  - D2 mais caro que D1
  - Nomes de nós clonados sem renomear
  - Elementos ativos do checkout (timer, exit popup, live buyers)
- Gera relatório `.md` em `~/Documents/Cerbero/reports/<slug>-<data>.md` ao final de toda execução.
- Tabelas com no máximo 6 colunas + alinhamento Markdown apropriado pra render limpo em qualquer viewer.

### Limitações

- Apenas Pagamerican (outros gateways planejados).
- Não simula clique em "Iniciar simulação de compra" — confiável pra preços, não valida fluxo end-to-end.
