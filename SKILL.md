---
name: Cerbero
description: Audita uma VSL/LP e seus checkouts no Pagamerican (3 botões + funil de upsell/downsell) sem precisar assistir o vídeo nem comprar. Extrai preço, preço por bottle, valor "De", "You save" e % de desconto de cada oferta e flagra divergências.
---

# Cerbero — Auditor de Ofertas Pagamerican

Skill para auditar VSLs com checkouts no Pagamerican.app. Em vez de acelerar o vídeo em 2x pra ver os preços e clicar em cada botão manualmente, esta skill puxa o HTML cru das páginas e extrai os preços direto do payload do Next.js (RSC), incluindo as etapas do funil que só apareceriam após "Iniciar simulação de compra" com `?pag_test_4=true`.

## Saudação ao ativar a skill

Quando o usuário invocar `/Cerbero` **sem URL** no comando (ex: digita só `/Cerbero` ou `/Cerbero` seguido de pergunta sem URL), responder **exatamente** com a mensagem:

> Envie a URL do funil a ser auditado.

Sem mais nada — sem explicação extra, sem listar capacidades, sem perguntar mais nada. O usuário já sabe o que a skill faz.

Se o usuário invocar `/Cerbero <URL>` (URL já presente na mensagem), pular essa saudação e iniciar o procedimento de auditoria direto.

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
TOTAL:\s*<span class="line-through[^>]*">[$]([0-9]+)</span>   → "De"
[$]([0-9]+(?:\.[0-9]+)?)<                                      → "Por" (preço final do pack)
YOU SAVE [$]([0-9]+)                                           → "You save"
[$]([0-9]+(?:\.[0-9]+)?)/bottle                                → preço por bottle (renderizado, conferir)
```

**Páginas de DOWNSELL** (formato copy-heavy):
```
<span class="discount-highlight">U[$]([0-9]+) Discount\??</span>   → headline "U$X Discount"
<span class="normal[- ]price">[$]([0-9]+)[^<]*</span>             → "NORMALLY: $X per bottle"
<span class="today[- ]price">[$]([0-9]+(?:\.[0-9]+)?)[^<]*</span> → "TODAY: $X per bottle"
class="total-price">[$]([0-9]+) FOR ([0-9]+) BOTTLES?            → total + qtd (downsell 1 estilo "X+Y free")
```

### 6. Cada botão da LP entra num FUNIL DIFERENTE

Importante: as 3 ofertas da LP costumam apontar pra funis distintos (FUNIL A / B / C), cada um com seus próprios 5 offerCodes (3 upsell variants + 2 downsells). Total: 3 LP + 15 funil = **18 ofertas** a checar.

### 7. Apresentar resultado

Uma tabela por funil, no formato:

```
| Etapa | Qtd | Por bottle | De | Por | You save | % off |
```

**Nomenclatura obrigatória da coluna "Etapa"** — seguir o padrão usado na operação, não inventar abreviações:

- Upsell: `Upsell <N> - <Letra do funil> (front de <qtd entrada>): <qtd do pack> bottles`
- Downsell: `Downsell <N> - <Letra do funil> (front de <qtd entrada>): <qtd do pack> bottles` (ou `<X> + <Y> FREE` se aplicável)

Exemplos:
- `Upsell 1 - C (front de 6): 12 bottles`
- `Upsell 1 - A (front de 1): 4 bottles`
- `Downsell 1 - A (front de 1 e 3): 2 + 1 FREE`
- `Downsell 2 - B (front de 3): 1 bottle`

Onde `front de X` é a quantidade que o lead comprou na LP pra entrar nesse funil. Quando uma variante serve MÚLTIPLOS fronts (caso do Downsell 1-A do Funil 8.0 que atende 1 e 3), juntar: `(front de 1 e 3)`.

**Não usar** abreviações tipo `U1.1`, `D2`, `U1.3` — confunde o usuário porque não bate com o vocabulário da operação.

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

1. **Cabeçalho enxuto** — 2 linhas:
   ```
   # Cerbero — <produto>
   <YYYY-MM-DD> · <URL encurtada: host + "..." + último segmento significativo>
   ```

2. **Status geral** — lista de UMA LINHA por item, com `✅ / ❌ / ⚠️` na frente, no formato:
   ```
   <status> <Aspecto>: <achado curto> — <evidência inline>
   ```
   - **Sem prosa expandida** abaixo de cada item. Tudo cabe na linha. Se a evidência precisa de mais de uma linha, é porque o item está desnecessariamente detalhado — encolha.
   - **Linguagem direta, sem jargão técnico.** PROIBIDO usar as palavras `slug`, `payload`, `frontmatter`, `JSON`, `regex`, `HTML` na linha de status. O usuário lê isso e não tem que pensar "o que é payload?". Em vez disso:
     - Em vez de "slug `semquiz`" → "URL da LP contém `semquiz`" ou "URL diz `semquiz`"
     - Em vez de "payload `PITCH 1.2`" → "nome cadastrado no admin diz `PITCH 1.2`" ou "admin marca como `PITCH 1.2`"
     - Em vez de "no HTML da página" → "na página do funil" ou "na própria página"
   - Itens típicos (a ordem é essa):
     - `✅ Pitch: <X.Y> (<nome>) — URL da LP diz <termo> e nome no admin diz <termo>` (se sinal autoritativo) OU `— preços $A/$B/$C` (sem sinal)
     - `✅ Checkouts da LP: coerentes com Pitch <X.Y> ($A / $B / $C)`
     - `✅ Funil: <N.N> (<nome>)`
     - `❌ Estrutura do funil: <o que falta/sobra>` (só se houver problema; se tá completa, virar `✅ Estrutura do funil: completa (upsell 1 + downsell 1 + downsell 2)`)
     - `✅ Upsell 1: X/X variants batem com catálogo`
     - `⚠️ Downsell N: não catalogado — extraído pra registro` (quando aplicável)
     - `✅ Elementos checkout: timer Xmin · buyers A-B · exit popup Z% (idênticos)` ou `❌ ... (divergem entre checkouts: ...)`
   - **Não usar `---` separador entre o cabeçalho e a lista** — a lista vem direto, dá visual mais limpo.

3. **Seção `## Front e precificação`** — UMA subseção por funil (`### FUNIL A — entrada: <qtd> bottle(s) / $<total>`). Dentro: lista indentada com 2 espaços, uma linha por etapa:
   ```
     <status> <Nome completo da etapa>: <qtd> · $<total> · $<por bottle>/un  (nota opcional entre parênteses)
   ```
   - Nomenclatura obrigatória (`Upsell 1 - C (front de 6): 12 bottles`), nunca abreviar.
   - Indentar com 2 espaços antes do `✅/❌/⚠️`.
   - Etapas AUSENTES viram linha com `❌ <Nome>: AUSENTE` (sem números).
   - Notas entre parênteses só quando precisa de contexto curto (ex: "(não catalogado)"). Sem nota em etapas ✅ sem ressalva.

4. **Seção `## Ações`** — bullets curtos. `🔴` pra ❌, `🟡` pra ⚠️. Cada bullet uma linha, sem detalhamento extra. Se tudo ✅, escrever "Nenhuma ação pendente — pode subir."

**O que NÃO entra no relatório:**
- Tabela de "Verdict" / "16 checks" — toda a informação dos checks já tá implícita nos itens de status ou nas linhas do funil.
- Seção "Detalhamento dos pontos flagados" — toda explicação cabe na evidência inline do item de status. Se não cabe, encolha o achado.
- Seção "Tabela da LP" separada — os preços da LP já saem indiretamente do Upsell 1 e dos preços de entrada dos funis.
- Seção "Anexo: estrutura completa" — eliminada. OfferCodes e URLs só entram se forem essenciais; em geral o usuário não precisa.
- Seção "Elementos ativos no checkout" separada — já tá no status geral em uma linha.

**Princípios do formato:**
- **Uma linha por achado.** Se precisa de mais de uma linha, encolheu mal.
- **Sem separadores `---` entre seções.** Apenas o título `##` separa.
- **Sem tabelas Markdown no corpo** — listas com status na frente.
- **Linguagem direta.** Evidência inline em `code` (slug, payload, termos) é ok porque cabe na linha — não é prosa.
- **Quem bate o olho no status geral + ações já sabe se sobe ou não.**

### ⚠️ Regras de formatação das tabelas Markdown

Tabelas com 7+ colunas quebram visualmente em vários renderizadores (incluindo VS Code preview e GitHub mobile). Seguir as regras:

- **Máx 6 colunas em qualquer tabela.** Se precisa de mais campo, separar em uma lista abaixo.
- **Sem `<br>` ou HTML dentro de células.**
- **Strikethrough** com `~~$534~~` (não `<s>`).
- **Combinar colunas correlatas:** "Qtd × $/un" em vez de duas colunas separadas, "You save ($X / Y%)" em vez de duas.
- **Não usar tabela aninhada** (Markdown não suporta).
- Cabeçalho com `:--` pra alinhar esquerda nas colunas de texto e `--:` pra alinhar direita nas colunas de número.

Depois de salvar, **mostrar ao usuário o caminho do arquivo gerado** e um resumo (não o conteúdo completo — o conteúdo está no arquivo).

## Pitches da operação (catálogo)

A operação roda **vários pitches** (estruturas de oferta da LP) testados em A/B pra encontrar a maior margem. Cerbero deve identificar qual pitch está rodando comparando os preços/qtd dos 3 botões da LP contra o catálogo abaixo e **reportar no cabeçalho do relatório**.

### Pitch 1.2 — Tradicional

| Front | Preço/bottle | Frete |
|:--|:--:|:--|
| **1 bottle** | **$89** | + **$19** de frete |
| **3 bottles** | **$69** | Grátis |
| **6 bottles** | **$49** | Grátis |

**Assinatura:** front de **1 bottle** com frete (~$19). LP **sem quiz** — fronts aparecem direto.

### Pitch 3.2 — Quiz

| Front | Preço/bottle | Frete |
|:--|:--:|:--|
| **1 bottle** | **$89** | + **$19** de frete |
| **3 bottles** | **$69** | Grátis |
| **6 bottles** | **$49** | Grátis |

**Assinatura:** preços **idênticos ao 1.2**. A diferença está na LP: tem um **quiz temporizado** antes dos fronts — as opções de compra só aparecem depois que o lead responde o questionário.

⚠️ **Pelos preços, 1.2 e 3.2 são indistinguíveis.** O que diferencia é a **presença do quiz na LP**. Cerbero detecta pitch pelo preço (que é igual nos dois) — então quando bater 1 bottle $89, **reporte como "Pitch 1.2 ou 3.2"** no cabeçalho e abra flag pedindo pro usuário confirmar se a LP deveria ter quiz ou não (ver check #14).

### Pitch 5.1 — Afiliação BHEver e Instituto X

| Front | Preço/bottle | Frete |
|:--|:--:|:--|
| **2 bottles** | **$79** | + **$19,99** de frete |
| **3 bottles** | **$69** | Grátis |
| **6 bottles** | **$49** | Grátis |

**Assinatura:** front menor é **2 bottles** (não 1) com frete (~$19,99). Usado em afiliações BHEver e Instituto X.

### Como identificar o pitch pelos preços extraídos

1. Olhe os 3 botões da LP (passo 2 do procedimento) e veja qual é o front menor (em qtd de bottles):
   - Front 1 bottle ($89) + frete → **Pitch 1.2 ou 3.2** (ambíguo — flag #14)
   - Front 2 bottles ($79) + frete → **Pitch 5.1**
2. Os preços de 3 ($69) e 6 ($49) são iguais em 1.2 / 3.2 / 5.1 — não diferenciam.
3. Se os preços **não baterem com nenhum pitch**, **não presuma nada** — sinalize **"Pitch não catalogado"** e abra red flag (ver check #15).
4. Sempre inclua **"Pitch utilizado"** no cabeçalho do relatório (junto de URL, data, produto).

## Funis de Upsell/Downsell (catálogo)

Além do pitch da LP, Cerbero também deve identificar **qual funil de upsell/downsell** o cliente entra ao comprar, comparando os preços/qtd de cada etapa do funil contra o catálogo abaixo. Reportar no cabeçalho do relatório como **"Funil utilizado"**.

### Funil 8.0 — EMAGRECIMENTO

#### Upsell 1

**Upsell 1-A** (cliente veio do FRONT 01 — comprou 1 bottle)

| Qtd | $/frasco | Total |
|:--|:--:|:--:|
| 6 bottles | **$19** | **$114** |
| 4 bottles | **$25** | **$98** |
| 2 bottles | **$29** | **$58** |

**Upsell 1-B** (cliente veio do FRONT 03 — comprou 3 bottles)

| Qtd | $/frasco | Total |
|:--|:--:|:--:|
| 12 bottles | **$17** | **$198** |
| 9 bottles | **$19** | **$171** |
| 6 bottles | **$25** | **$147** |

**Upsell 1-C** (cliente veio do FRONT 06 — comprou 6 bottles)

| Qtd | $/frasco | Total |
|:--|:--:|:--:|
| 12 bottles | **$29** | **$348** |
| 9 bottles | **$37** | **$333** |
| 6 bottles | **$49** | **$294** |

#### Downsell 1 do Upsell 1 (em vídeo)

> ⚠️ **Estrutura diferente do Upsell 1.** O Downsell 1-A serve dois fronts (1 e 3) — não há variante separada por front. O Front 06 tem variante própria (B).

**Downsell 1-A** (cliente veio do FRONT 01 ou FRONT 03)

| Qtd | $/frasco | Total |
|:--|:--:|:--:|
| 2 + 1 FREE | **$29** | **$87** |
| 2 bottles | **$39** | **$78** |

**Downsell 1-B** (cliente veio do FRONT 06)

| Qtd | $/frasco | Total |
|:--|:--:|:--:|
| 6 + 3 FREE | **$29** | **$261** |
| 4 bottles | **$39** | **$156** |

**Notas sobre o Downsell 1 do Upsell 1 do Funil 8.0:**
- "$/frasco" é calculado sobre o **total de bottles incluindo os FREE** ($87 ÷ 3 = $29; $261 ÷ 9 = $29). Isso conecta com o check #9 (Pack "X + Y FREE") — usar `total_bottles = X + Y`.
- Downsell 1 do Upsell 1 deste funil é em **vídeo** (página `(página com vídeo)` na planilha). Cerbero deve confirmar que a URL do downsell renderiza vídeo, não só copy estática.

#### Downsell 2 do Upsell 1

> ⚠️ **Mesma estrutura do Downsell 1 do Upsell 1.** Variante A serve dois fronts (1 e 3); variante B serve o Front 6.

**Downsell 2-A** (cliente veio do FRONT 01 ou FRONT 03)

| Qtd | $/frasco | Total |
|:--|:--:|:--:|
| 1 bottle | **$49** | **$49** |

**Downsell 2-B** (cliente veio do FRONT 06)

| Qtd | $/frasco | Total |
|:--|:--:|:--:|
| 3 bottles | **$39** | **$117** |

**Notas sobre o Downsell 2 do Upsell 1 do Funil 8.0:**
- Downsell 2 do Upsell 1 não tem opção "X+Y FREE" — é oferta única por variante.
- A variante A oferece o menor pacote possível (1 unidade a $49); B oferece 3 unidades a $39/und.
- **Relação D2 vs D1 do Upsell 1 — validada em 2026-05-20, NÃO flagar.** A estratégia é intencional: D2 ancora em preço futuro ($89 single-bottle list price, não em desconto vs D1), pra last-ditch AOV bump sem competir com a oferta de pack do D1. Trata-se de produto diferente (1 ou 3 unidades soltas vs pack agressivo do D1). Não disparar o check #2 quando os valores baterem com este catálogo.

#### Upsell 2

> ⚠️ **Estrutura por front.** Variante A serve o Front 1; variante B serve Fronts 3 e 6 com os mesmos preços.

**Upsell 2-A** (cliente veio do FRONT 01)

| Qtd | $/frasco | Total |
|:--|:--:|:--:|
| 9 bottles | **$16** | **$144** |
| 6 bottles | **$17** | **$99** |
| 2 bottles | **$24** | **$48** |

**Upsell 2-B** (cliente veio do FRONT 03 ou FRONT 06)

| Qtd | $/frasco | Total |
|:--|:--:|:--:|
| 12 bottles | **$19** | **$228** |
| 6 bottles | **$29** | **$174** |
| 3 bottles | **$33** | **$99** |

**Notas sobre o Upsell 2 do Funil 8.0:**
- Mesmo padrão de arredondamento do Upsell 1: o `$/frasco` cadastrado é arredondado pra cima; o `total` é o valor real cobrado. Ex.: Upsell 2-A 6 bottles cadastrado como $17/und × 6 = $102 nominal, mas total real é $99 ($16,50/und efetivo). Cerbero deve usar o `total` extraído como fonte de verdade pro check de preço.
- Upsell 2-B atende dois fronts (3 e 6) com os **mesmos preços**. Não há variante separada por front pra esses dois casos.

#### Downsell 1 do Upsell 2

> ⚠️ **Universal — uma única variante atende todos os fronts (1, 3 e 6).**

| Qtd | $/frasco | Total |
|:--|:--:|:--:|
| 3 bottles | **$39** | **$117** |

**Notas sobre o Downsell 1 do Upsell 2 do Funil 8.0:**
- Não há variante por front — é a mesma oferta para FRONT 01, FRONT 03 e FRONT 06.
- Preço/und e total idênticos ao Downsell 2-B do Upsell 1 (3 bottles @ $39 = $117), mas o contexto é diferente: este é último degrau após Upsell 2 ser recusado.
- **Relação D1 do Upsell 2 vs D1/D2 do Upsell 1 — NÃO flagar pelo check #2.** Estes são funis paralelos disparados por etapas diferentes (Upsell 2 vs Upsell 1), não a mesma sequência. Comparação direta não se aplica.

### Como identificar o funil

1. Após mapear o funil (passo 5 do procedimento), liste todos os pares **(qtd × $/frasco × total)** de cada etapa.
2. Compare com o catálogo acima, **separando por front de entrada** (1/3/6 bottles).
3. Se os valores não baterem com nenhum funil cadastrado, **não presuma** — abra red flag (ver check #16).
4. Sempre inclua **"Funil utilizado"** no cabeçalho do relatório.

## Checks/divergências — TODOS obrigatórios em toda execução

⚠️ **Não pular nenhum**. Cada check abaixo precisa ser explicitamente avaliado e ou listado em "Flags" ou listado em "Sanity checks que passaram". Não omitir flags pra encurtar relatório.

1. **`originalUnitPrice: 0` no payload do Pagamerican ≠ "vazio na página".** Em upsell/downsell isso é normal — o "De" está hardcoded na página do funil. Só flagar como problema se a PÁGINA DO FUNIL também não tiver `line-through` ou `NORMALLY`.
2. **Downsell 2 mais caro (total ou por bottle) que Downsell 1** — pode ser intencional (D1 = melhor desconto, D2 = última tentativa com desconto menor). **Exceção:** se o funil está cadastrado E os valores extraídos batem com o catálogo (ex.: Funil 8.0 D2-A / D2-B — validado), **não flagar**. Só flagar quando: (a) funil não cadastrado, OU (b) D2 ≠ catálogo, OU (c) o catálogo não documenta explicitamente a relação D2 vs D1.
3. **Preço por bottle inconsistente entre packs** — ex.: se 6-bottle sai $49/un e 12-bottle sai $58/un, faltou desconto no pack maior.
4. **Outlier de preço por bottle** — identificar a oferta com o MENOR e a com o MAIOR preço por bottle do funil inteiro. Sempre listar ambas com comentário "intencional?". Ajuda a pegar erros de digitação no admin.
5. **Nomes de nós copiados sem renomear** — comparar o sufixo do nome de cada nó (UPSELL 1 - X, DOWN1 DO UP1 - X) com a letra do funil em que está. Se funil B tem nó chamado "...- A", flagar como funil clonado.
6. **Upsell e downsell com mesmo total** — ex.: Upsell 6-bottle $147 e Downsell 3+1 FREE $147. Flagar pra confirmar se é A/B teste ou bug.
7. **Preço de upsell var.3 == preço da entrada do funil** — comum em funis "leva mais N pelo mesmo valor". **Só flagar se o funil NÃO estiver no catálogo cadastrado** ou se o valor bater com a entrada mas não bater com o catálogo. Quando bate certinho com o catálogo do funil (ex: Funil 8.0 — U1.3 do funil C = 6 × $49 = $294 = entrada), é comportamento esperado e NÃO entra no relatório.
8. **% de desconto declarado bate com (1 - unit/original)?** — Pagamerican guarda `priceDiscountPercentage` mas o valor é editado manualmente; recalcular e comparar.
9. **Pack "X + Y FREE"** — sempre considerar `total_bottles = X + Y` ao calcular por bottle, não só X.
10. **Per-bottle exibido vs. calculado** — a página do funil mostra `TODAY: $X per bottle` mas pode ter sido arredondado. Comparar com `total ÷ qtd`. **Ignorar arredondamentos** (diferença ≤ $1 em qualquer direção — ex.: $24.50 real exibido como $24 ou $25 é tolerado e NÃO entra no relatório). Só flagar quando a diferença for ≥ $2 (sinal de erro real de copy, não arredondamento).
11. **Headline "U$X Discount" vs. desconto real calculado** — o número no headline grande (`<span class="discount-highlight">U$80 Discount</span>`) é texto manual e pode estar defasado. Comparar com `(normally × qtd) - total` e flagar.
12. **"De" presente em uns upsells e ausente em outros do mesmo funil** — inconsistência visual.
13. **Elementos ativos do checkout** — confirmar presença/valor de timer, exit popup (% off), live buyers count nos 3 checkouts da LP. Se diferente entre eles, flagar.
14. **Coerência Pitch 1.2 vs. 3.2 (presença/ausência do quiz)** — quando os preços batem com 1.2/3.2 (front 1 bottle $89 + 3×$69 + 6×$49), os dois pitches são indistinguíveis pelos preços isolados. Antes de flagar, **procurar sinais autoritativos**:
    - **Slug da URL da LP** contém `semquiz` / `comquiz` / `quiz`? → usar como autoridade.
    - **Nome do checkout no payload Pagamerican** (`"name":"...PITCH X.Y..."`) cita pitch explicitamente? → usar como autoridade.
    - Se **qualquer** dos dois sinais identifica o pitch, **não flagar** — reportar Pitch 1.2 ou 3.2 confirmado e listar em ✅ Sanity checks com a citação do sinal (ex: "Pitch 1.2 confirmado — slug `semquiz` + payload `PITCH 1.2`").
    - **Só flagar como ambiguidade** quando NENHUM dos dois sinais existe — aí sim pedir pro usuário confirmar manualmente "Esta LP deveria rodar com quiz ou sem?". Esta flag captura erros do tipo "rodou sem quiz mas era pra ser 3.2" e vice-versa.
15. **Pitch não catalogado** — se os preços/qtd dos 3 botões da LP não baterem com nenhum pitch do catálogo (1.2 / 3.2 / 5.1), **não presuma nada**. Reporte: "🚩 Pitch não catalogado — preços encontrados: [lista]. Não bate com 1.2 / 3.2 / 5.1. Pode ser: (a) erro de digitação no admin, (b) preço residual de versão antiga, ou (c) pitch novo a cadastrar. Confirmar com o time antes de subir."
16. **Funil não catalogado** — se os preços/qtd de qualquer etapa do funil (upsell/downsell) não baterem com nenhum funil cadastrado no catálogo (atualmente: Funil 8.0), **não presuma**. Reporte: "🚩 Funil não catalogado — etapas encontradas: [lista]. Não bate com Funil 8.0 (diferença: [qual]). Pode ser: (a) erro de copy/admin; (b) funil novo a cadastrar. Verificar com o time."

## Outputs auxiliares (opcionais)

- Listar elementos ativos no checkout: `"type":"timer"`, `"type":"exit_popup"` (e o `discountPercentage` do popup), `"type":"live_buyers_count"` (e `min`/`max` de compradores fake).
- Capturar `friendlyName` cru pra detectar typos no admin.

## Linguagem do relatório

Escreva o relatório em português conversacional, como se estivesse explicando
pra um colega de marketing direto — **não** pra um colega de tech ou produção
audiovisual. Termos como *hardcoded*, *B-roll*, *asset*, *pipeline*,
*trade-off*, *legacy*, *deploy* confundem o usuário e o time dele.

Traduções por padrão:
- *hardcoded* → "gravado/colado dentro do próprio clipe"
- *B-roll* → "clipe curto de apoio" ou "imagem de apoio"
- *asset* → "arquivo"
- *pipeline* → "fluxo" ou "processo"
- *trade-off* → "contrapartida"
- *legacy* → "antigo" ou "herdado"
- *deploy* → "publicar" ou "subir"

**Vocabulário do negócio (ok usar sem traduzir):** lead, oferta, pitch,
front, upsell, downsell, escassez, packshot, lipsync, frame, checkout,
LP, VSL, VTurb, Pagamerican. Também ok: nomes próprios de pitch/funil
(Pitch 1.2, Funil 8.0, Front 03).

Se precisar usar um termo técnico que não está na lista acima, explique
entre parênteses na primeira ocorrência.

## Limitações conhecidas

- Esta skill **não** simula o clique em "Iniciar simulação de compra". Os preços extraídos são os configurados no admin (mesma fonte que o front renderiza e o backend cobra), portanto confiáveis. Mas o **fluxo end-to-end** (botão funciona, redirect dispara, sessão é criada) não é validado. Se precisar disso, usar browser automation (Playwright).
- Domínios das páginas de funil mudam por produto (ex.: `mabrn21fv.online`). Sempre extrair do payload, não chutar.

## Exemplo de invocação

> "Checa essa oferta pra mim: https://mabrai.com/ztes21-fpnp-maxbrai21-prodmaxbra21-caps-pit12-utm-leand/"

→ Skill executa todos os passos acima e retorna 4 tabelas (LP + 3 funis) com flags.
