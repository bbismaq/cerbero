---
name: Cerbero
description: Audita uma VSL/LP e seus checkouts no Pagamerican (3 botões + funil de upsell/downsell) sem precisar assistir o vídeo nem comprar. Extrai preço, preço por bottle, valor "De", "You save" e % de desconto de cada oferta e flagra divergências.
---

# Cerbero — Auditor de Ofertas Pagamerican

Skill para auditar VSLs com checkouts no Pagamerican.app. Em vez de acelerar o vídeo em 2x pra ver os preços e clicar em cada botão manualmente, esta skill puxa o HTML cru das páginas e extrai os preços direto do payload do Next.js (RSC), incluindo as etapas do funil que só apareceriam após "Iniciar simulação de compra" com `?pag_test_4=true`.

## Quando usar

- Usuário cola uma URL de LP (geralmente `mabrai.com/...` ou domínio similar) e pede pra "checar a oferta", "validar os preços", "ver se está certo", "conferir o funil".
- Usuário menciona "VSL", "upsell", "downsell", "funil de oferta", "Pagamerican", "pag_test_4".

## O que extrair pra cada oferta

⚠️ **IMPORTANTE — duas fontes diferentes:**

- **Checkouts da LP** (3 botões iniciais em `pay.pagamerican.app/<slug>`): preço, "De" e "You save" ESTÃO no payload Next.js do Pagamerican (`originalUnitPrice`, `unitPrice`, `priceDiscountPercentage`).
- **Etapas do funil** (upsell/downsell em domínio próprio tipo `mabrn21fv.online/...`): preço base ESTÁ no payload do checkout vinculado ao offerCode, mas **"De" / "You save" / "NORMALLY" / "TODAY" / headlines de desconto estão HARDCODED no HTML da PÁGINA DO FUNIL**, não no Pagamerican. `originalUnitPrice` no payload do Pagamerican costuma vir `0` pros offerCodes de upsell/downsell — isso é normal, não significa que o cliente vê "vazio". O cliente vê o número escrito na página do funil.

Para cada checkout (LP e cada etapa do funil), reportar:

| Campo | Fonte | Como calcular |
|---|---|---|
| Nome do produto | payload Pagamerican: `"name":"..."` | direto |
| Quantidade de bottles | `friendlyName` ou parsear do `name` ("6 bottles") | regex `(\d+)\s*bottles?` |
| Preço total | payload Pagamerican: `"unitPrice":N` | direto (é o total do pack quando `quantity:1`) |
| Preço por bottle | calculado | `unitPrice / qtd_bottles` |
| Preço "De" da LP | payload Pagamerican: `"originalUnitPrice":N` | direto |
| Preço "De" do upsell | HTML da página do funil: `<span class="line-through ...">$N</span>` | direto |
| Preço "De" do downsell | HTML da página do funil: `<span class="normal-price">$N per bottle</span>` ou `<span class="normal">NORMALLY: $N per bottle</span>` | direto |
| You save | upsell: `YOU SAVE $N` no HTML / LP: `originalUnitPrice - unitPrice` | direto/calc |
| Headline "U$X Discount" (downsell) | HTML: `<span class="discount-highlight">U$N Discount?</span>` | direto |
| % de desconto | payload: `"priceDiscountPercentage":N` | direto |
| offerCode | payload: `"offerCode":"..."` | direto |

## Procedimento

### 1. Baixar a LP

```bash
curl -sL "<URL_DA_LP>" -o lp.html
```

### 2. Achar os 3 checkouts da LP

Os botões geralmente apontam pra `#` e têm o href injetado por JS. Procurar no HTML:

```
grep "pay.pagamerican.app" lp.html
```

A LP costuma definir `firstUrl`, `secUrl`, `thirdUrl` num bloco `<script>` mapeando classes CSS `.oferta-um`, `.oferta-dois`, `.oferta-tres`. **Importante**: a ordem das variáveis no JS nem sempre é "menor pack → maior pack" — sempre confirmar a quantidade depois.

### 3. Para cada checkout (e todos os offerCodes do funil): baixar o HTML

```bash
curl -sL "https://pay.pagamerican.app/<slug>?pag_test_4=true" -o "co_<slug>.html"
```

**Regras importantes sobre a URL:**
- A URL real do checkout vem cheia de UTMs (`?utm_source=...&sub18=...&aff_sub2=...`). **Remover todas as UTMs** — só manter `https://pay.pagamerican.app/<slug>`.
- Adicionar **só** `?pag_test_4=true` (esse é o flag do Pagamerican que ativa modo simulação — equivale a clicar "Iniciar simulação de compra" no navegador).
- O slug é o caminho após o domínio (ex.: `ng1b02JI`).

### 4. Extrair dados de cada HTML

O Pagamerican usa Next.js — o JSON da oferta está embutido na resposta, escapado com `\"`. Buscar:

```
grep -oE '\\"(name|friendlyName|productName|unitPrice|originalUnitPrice|quantity|offerCode|priceDiscountPercentage)\\":(\\"[^"]{1,80}\\"|[0-9]+)' co_<slug>.html
```

### 5. Mapear o funil

Ainda no payload de cada checkout, vai aparecer a estrutura do funil pós-compra:

- `"type":"upsell_root"` → o nó de upsell 1, com 3 variantes (`offerCode` cada)
- `"type":"downsell"` → nós de downsell (geralmente "DOWN1 DO UP1" e "DOWN2 DO UP1"), com seus próprios `offerCode`
- `"url":"https://<dominio>/up1-..."` → **A URL DA PÁGINA DO FUNIL — BAIXAR também**, porque é dela que sai o "De" / "You save" / headlines de desconto. Não dá pra pular essa etapa.

Coletar todos os offerCodes do funil E todas as URLs das páginas de funil, e repetir passos 3, 4 e o novo passo 5b abaixo.

### 5b. Baixar e extrair das páginas do funil

```bash
curl -sL "<url_da_pagina_do_funil>?pag_test_4=true" -o "fnl_<funil>_<step>.html"
```

Patterns a extrair:

**Páginas de UPSELL** (3 variantes empilhadas na mesma página):
```
TOTAL:\s*<span class="line-through[^>]*">\$([0-9]+)</span>   → "De"
\$([0-9]+(?:\.[0-9]+)?)<                                      → "Por" (preço final do pack)
YOU SAVE \$([0-9]+)                                           → "You save"
\$([0-9]+(?:\.[0-9]+)?)/bottle                                → preço por bottle (renderizado, conferir)
```

**Páginas de DOWNSELL** (formato copy-heavy):
```
<span class="discount-highlight">U\$([0-9]+) Discount\??</span>   → headline "U$X Discount"
<span class="normal[- ]price">\$([0-9]+)[^<]*</span>             → "NORMALLY: $X per bottle"
<span class="today[- ]price">\$([0-9]+(?:\.[0-9]+)?)[^<]*</span> → "TODAY: $X per bottle"
class="total-price">\$([0-9]+) FOR ([0-9]+) BOTTLES?            → total + qtd (downsell 1 estilo "X+Y free")
```

### 6. Cada botão da LP entra num FUNIL DIFERENTE

Importante: as 3 ofertas da LP costumam apontar pra funis distintos (FUNIL A / B / C), cada um com seus próprios 5 offerCodes (3 upsell variants + 2 downsells). Total: 3 LP + 15 funil = **18 ofertas** a checar.

### 7. Apresentar resultado

Uma tabela por funil, no formato:

```
| Etapa | Qtd | Por bottle | De | Por | You save | % off |
```

### 8. SEMPRE gerar relatório .md em disco

⚠️ **Obrigatório em toda execução**: ao final da análise, salvar um arquivo Markdown completo em:

```
C:\Users\bbism\Documents\Cerbero\reports\<slug-da-lp>-<YYYY-MM-DD>.md
```

- `<slug-da-lp>` = último segmento do path da URL (ex.: `ztes21-fpnp-maxbrai21-prodmaxbra21-caps-pit12-utm-leand`)
- `<YYYY-MM-DD>` = data atual
- Se a pasta `reports\` não existir, criar antes de escrever.
- Se já existir um arquivo com mesmo nome (rodando 2x no mesmo dia), apendar `-<HHMM>` no final.

O conteúdo do .md DEVE ter, em ordem:

1. **Cabeçalho** — URL auditada, data, nome do produto, total de ofertas mapeadas.
2. **Tabela da LP** — MÁX 6 colunas pra renderizar bem: `Pack | Por bottle | De | Por | You save | % off`. Slugs e funil destino vão numa lista compacta logo abaixo.
3. **Uma tabela por funil** — MÁX 5 colunas: `Etapa | Qtd × $/un | De | Por | You save`. Detalhes (offerCode, origem do "De", URLs) vão numa lista enxuta abaixo de cada tabela.
4. **Seção 🚨 Flags / Divergências** — listar TODOS os pontos identificados nos 13 checks, com:
   - Tipo (🔴 erro / 🟡 inconsistência / ⚪ a confirmar)
   - Descrição clara do problema
   - Números envolvidos (esperado vs. encontrado)
   - Sugestão de ação
5. **Seção ✅ Sanity checks que passaram** — listar o que bateu (per-bottle vs. exibido, you save vs. calculado, etc.) pra dar confiança.
6. **Seção 📋 Elementos ativos no checkout** — timer, exit popup (% off), live buyers count, com seus valores configurados nos 3 checkouts da LP.
7. **Anexo: estrutura completa** — JSON mínimo com todos os offerCodes, URLs e preços, pra rastreabilidade.

### ⚠️ Regras de formatação das tabelas Markdown

Tabelas com 7+ colunas quebram visualmente em vários renderizadores (incluindo VS Code preview e GitHub mobile). Seguir as regras:

- **Máx 6 colunas em qualquer tabela.** Se precisa de mais campo, separar em uma lista abaixo.
- **Sem `<br>` ou HTML dentro de células.**
- **Strikethrough** com `~~$534~~` (não `<s>`).
- **Combinar colunas correlatas:** "Qtd × $/un" em vez de duas colunas separadas, "You save ($X / Y%)" em vez de duas.
- **Não usar tabela aninhada** (Markdown não suporta).
- Cabeçalho com `:--` pra alinhar esquerda nas colunas de texto e `--:` pra alinhar direita nas colunas de número.

Depois de salvar, **mostrar ao usuário o caminho do arquivo gerado** e um resumo (não o conteúdo completo — o conteúdo está no arquivo).

## Checks/divergências — TODOS obrigatórios em toda execução

⚠️ **Não pular nenhum**. Cada check abaixo precisa ser explicitamente avaliado e ou listado em "Flags" ou listado em "Sanity checks que passaram". Não omitir flags pra encurtar relatório.

1. **`originalUnitPrice: 0` no payload do Pagamerican ≠ "vazio na página".** Em upsell/downsell isso é normal — o "De" está hardcoded na página do funil. Só flagar como problema se a PÁGINA DO FUNIL também não tiver `line-through` ou `NORMALLY`.
2. **Downsell 2 mais caro (total ou por bottle) que Downsell 1** — pode ser intencional (D1 = melhor desconto, D2 = última tentativa com desconto menor), mas SEMPRE flagar pra confirmar.
3. **Preço por bottle inconsistente entre packs** — ex.: se 6-bottle sai $49/un e 12-bottle sai $58/un, faltou desconto no pack maior.
4. **Outlier de preço por bottle** — identificar a oferta com o MENOR e a com o MAIOR preço por bottle do funil inteiro. Sempre listar ambas com comentário "intencional?". Ajuda a pegar erros de digitação no admin.
5. **Nomes de nós copiados sem renomear** — comparar o sufixo do nome de cada nó (UPSELL 1 - X, DOWN1 DO UP1 - X) com a letra do funil em que está. Se funil B tem nó chamado "...- A", flagar como funil clonado.
6. **Upsell e downsell com mesmo total** — ex.: Upsell 6-bottle $147 e Downsell 3+1 FREE $147. Flagar pra confirmar se é A/B teste ou bug.
7. **Preço de upsell var.3 == preço da entrada do funil** — comum em funis "leva mais N pelo mesmo valor", mas sempre flagar pra confirmar intenção.
8. **% de desconto declarado bate com (1 - unit/original)?** — Pagamerican guarda `priceDiscountPercentage` mas o valor é editado manualmente; recalcular e comparar.
9. **Pack "X + Y FREE"** — sempre considerar `total_bottles = X + Y` ao calcular por bottle, não só X.
10. **Per-bottle exibido vs. calculado** — a página do funil mostra `TODAY: $X per bottle` mas pode ter sido arredondado. Sempre comparar com `total ÷ qtd`. Ex.: $147 ÷ 4 = $36.75/un, mas página mostrou "$37 per bottle".
11. **Headline "U$X Discount" vs. desconto real calculado** — o número no headline grande (`<span class="discount-highlight">U$80 Discount</span>`) é texto manual e pode estar defasado. Comparar com `(normally × qtd) - total` e flagar.
12. **"De" presente em uns upsells e ausente em outros do mesmo funil** — inconsistência visual.
13. **Elementos ativos do checkout** — confirmar presença/valor de timer, exit popup (% off), live buyers count nos 3 checkouts da LP. Se diferente entre eles, flagar.

## Outputs auxiliares (opcionais)

- Listar elementos ativos no checkout: `"type":"timer"`, `"type":"exit_popup"` (e o `discountPercentage` do popup), `"type":"live_buyers_count"` (e `min`/`max` de compradores fake).
- Capturar `friendlyName` cru pra detectar typos no admin.

## Limitações conhecidas

- Esta skill **não** simula o clique em "Iniciar simulação de compra". Os preços extraídos são os configurados no admin (mesma fonte que o front renderiza e o backend cobra), portanto confiáveis. Mas o **fluxo end-to-end** (botão funciona, redirect dispara, sessão é criada) não é validado. Se precisar disso, usar browser automation (Playwright).
- Domínios das páginas de funil mudam por produto (ex.: `mabrn21fv.online`). Sempre extrair do payload, não chutar.

## Exemplo de invocação

> "Checa essa oferta pra mim: https://mabrai.com/ztes21-fpnp-maxbrai21-prodmaxbra21-caps-pit12-utm-leand/"

→ Skill executa todos os passos acima e retorna 4 tabelas (LP + 3 funis) com flags.
