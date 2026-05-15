# Checagem de Oferta — Max Brain 2.1

- **URL:** https://mabrai.com/ztes21-fpnp-maxbrai21-prodmaxbra21-caps-pit12-utm-leand/
- **Data:** 2026-05-15
- **Produto:** Max Brain 2.1 - FB
- **Funis mapeados:** 3 (A, B, C)
- **Ofertas auditadas:** 18 (3 LP + 15 funil)
- **Gateway:** Pagamerican (`pay.pagamerican.app`)
- **Modo:** Test (`?pag_test_4=true`)

---

## 📍 Landing Page

| Pack            | Por bottle | De      | Por      | You save | % off |
| :-------------- | ---------: | ------: | -------: | -------: | ----: |
| 6 bottles (3+3) | $49.00     | ~~$534~~| **$294** | $240     | 45%   |
| 3 bottles (2+1) | $69.00     | ~~$267~~| **$207** | $60      | 22%   |
| 1 bottle        | $89.00     | ~~$99~~ | **$89**  | $10      | 10%   |

**Mapeamento botão → checkout → funil:**
- `.oferta-um` (6 bottles) → `ZPar1z02` → **FUNIL C**
- `.oferta-dois` (3 bottles) → `ng1b02JI` → **FUNIL B**
- `.oferta-tres` (1 bottle) → `0x1CBayi` → **FUNIL A**

---

## 🔻 FUNIL A — entrada: 1 bottle ($89)

| Etapa             | Qtd × $/un      | De        | Por  | You save |
| :---------------- | :-------------- | --------: | ---: | -------: |
| Upsell var.1      | 6 × $19.00      | ~~$594~~  | $114 | $480     |
| Upsell var.2      | 4 × $24.50      | ~~$396~~  | $98  | $298     |
| Upsell var.3      | 2 × $29.00      | ~~$198~~  | $58  | $140     |
| Downsell 1 (1+1)  | 2 × $24.50      | $99/un    | $49  | $149*    |
| Downsell 2        | 1 × $59.00      | $99/un    | $59  | $40*     |

\* You save calculado (não exibido na página).

**Detalhes:**
- OfferCodes: `70dmh5hF` / `h4O00KHF` / `70tLMhbl` / `BEgdGXhx` / `hxIIZrg8`
- Headline D1: "U$80 Discount"
- Páginas: `mabrn21fv.online/up1-...-funil8-a/`, `.../down1-up1-...-funil8-a/`, `.../down2-up1-...-funil8-a/`

---

## 🔻 FUNIL B — entrada: 3 bottles ($207)

| Etapa             | Qtd × $/un       | De         | Por  | You save |
| :---------------- | :--------------- | ---------: | ---: | -------: |
| Upsell var.1      | 12 × $16.50      | ~~$1188~~  | $198 | $990     |
| Upsell var.2      | 9 × $19.00       | ~~$891~~   | $171 | $720     |
| Upsell var.3      | 6 × $24.50       | ~~$594~~   | $147 | $447     |
| Downsell 1 (3+1)  | 4 × $36.75       | $99/un     | $147 | $249*    |
| Downsell 2        | 2 × $49.00       | $99/un     | $98  | $100*    |

\* You save calculado. D1 exibe "$37/bottle" — ver flag #1.

**Detalhes:**
- OfferCodes: `a1H77iFk` / `0cx87tas` / `eCQn5dl2` / `iqOefl9z` / `y75otaRz`
- Headline D1: "U$200 Discount"

---

## 🔻 FUNIL C — entrada: 6 bottles ($294)

| Etapa             | Qtd × $/un       | De         | Por  | You save |
| :---------------- | :--------------- | ---------: | ---: | -------: |
| Upsell var.1      | 12 × $29.00      | ~~$1188~~  | $348 | $840     |
| Upsell var.2      | 9 × $37.00       | ~~$891~~   | $333 | $558     |
| Upsell var.3      | 6 × $49.00       | ~~$594~~   | $294 | $300     |
| Downsell 1        | 6 × $29.00       | $99/un     | $174 | $420*    |
| Downsell 2        | 3 × $39.00       | $99/un     | $117 | $180*    |

\* You save calculado.

**Detalhes:**
- OfferCodes: `XhoKxCvg` / `iqdarP7K` / `zp5OfrKp` / `OokSGx6O` / `3v91xHXo`
- Headline D1: "U$320 Discount"

---

## 🚨 Flags / Divergências

### 🔴 #1 — Erro de copy: per-bottle exibido errado (Funil B, Downsell 1)
- **Onde:** `mabrn21fv.online/down1-up1-maxbrain12-caps-funil8-b/`
- **Problema:** Página exibe "TODAY: **$37 per bottle**", mas $147 ÷ 4 bottles = **$36.75/bottle**.
- **Impacto:** Cliente vê $0.25 a mais por bottle do que o real.
- **Ação:** Trocar copy pra "$36.75 per bottle" ou ajustar o pack pra fechar em $37/un.

### 🟡 #2 — Headlines "U$X Discount" subestimam o desconto real (todos os 3 D1)
- **Tipo:** Inconsistência

| Funil | Headline anunciado | Desconto real ((Normally × Qtd) − Por) | Diferença |
| :---- | :----------------- | -------------------------------------: | --------: |
| A     | U$80 Discount      | $99 × 2 − $49 = **$149**               | +$69      |
| B     | U$200 Discount     | $99 × 4 − $147 = **$249**              | +$49      |
| C     | U$320 Discount     | $99 × 6 − $174 = **$420**              | +$100     |

- **Impacto:** Cliente vê desconto **menor** do que o ofertado de fato. Você está se prejudicando na copy.
- **Possível explicação:** Pode ser comparação contra outro baseline (ex.: upsell rejeitado). Confirmar com quem escreveu.

### 🟡 #3 — Funil A — Downsell 2 ($59) mais caro que Downsell 1 ($49)
- **Tipo:** A confirmar
- **Detalhes:** D1 oferece 2 bottles a $49 ($24.50/un, com "1+1 free"). D2 oferece 1 bottle a $59. D2 é mais caro no total e MUITO mais caro por bottle ($59 vs $24.50).
- **Possível explicação:** Estratégia escada — D1 melhor desconto; se rejeitado, D2 oferece desconto menor sobre 1 unidade. Comum em funis, mas confirmar intenção.

### 🟡 #4 — Funil B — Upsell var.3 ($147) tem o mesmo total que Downsell 1 ($147)
- **Tipo:** A confirmar (coincidência ou bug?)
- **Detalhes:** Upsell var.3 = 6 bottles por $147. D1 = 3+1 free (4 bottles) também por $147.
- **Impacto:** Se cliente rejeitou pagar $147 por 6 bottles no upsell, dificilmente aceitará $147 por 4 no downsell.

### 🟡 #5 — Funil A — Upsell var.3 (2 bottles, $58) tem o menor preço por bottle do funil inteiro
- **Tipo:** A confirmar (intencional?)
- **Detalhes:** $29/bottle no upsell var.3 do Funil A é mais barato por unidade do que pacote algum do funil C (entrada custa $49/un, downsells custam $29 e $39/un). Detectado como outlier de per-bottle.
- **Ação:** Confirmar se o objetivo é mesmo dar o menor preço/un para clientes que entraram pelo menor pack (1 bottle).

### 🟡 #6 — Funil C — Upsell var.3 ($294 por 6 bottles) tem o mesmo total e mesmo per-bottle da entrada do funil C
- **Tipo:** A confirmar (provavelmente intencional)
- **Detalhes:** Cliente entra comprando 6 bottles por $294 ($49/un). No upsell var.3, vê de novo 6 bottles por $294 ($49/un). Provavelmente é a oferta "leva mais 6 ao mesmo valor", mas vale confirmar que não é cópia indevida da entrada.

### 🟡 #7 — Nomes internos dos nós de downsell estão errados nos funis B e C
- **Tipo:** Higiene de configuração no admin
- **Detalhes:** Os upsells estão certos ("UPSELL 1 - A/B/C"), mas todos os downsells dos 3 funis se chamam "DOWN1 DO UP1 - **A**" e "DOWN2 DO UP1 - **A**". O sufixo "A" está fixo em B e C também.
- **Impacto:** Nenhum pro cliente; confunde quem gerencia o admin (sintoma de funil clonado sem renomear).
- **Ação:** Renomear pra "DOWN1/DOWN2 DO UP1 - B" no funil B e "...- C" no funil C.

---

## ✅ Sanity checks que passaram

- **LP** — "De" / "Por" / "You save" / % off batem com a config do Pagamerican (`originalUnitPrice − unitPrice = save`; % bate com `priceDiscountPercentage`).
- **Per-bottle calculado vs. exibido** nos 9 upsells: todos batem ($114/6=$19 ✓ ; $98/4=$24.50 ✓ ; $58/2=$29 ✓ ; $198/12=$16.50 ✓ ; $171/9=$19 ✓ ; $147/6=$24.50 ✓ ; $348/12=$29 ✓ ; $333/9=$37 ✓ ; $294/6=$49 ✓).
- **YOU SAVE** exibido nos 9 upsells = (De − Por) ✓ em todos.
- **Per-bottle** nos downsells: bate em 5 dos 6 (única exceção: Funil B D1, flag #1).
- **Status `active`** em todas as 18 ofertas no admin.
- **`productId` 527** (Max Brain 2.1 - FB) em todos os offerCodes — sem mistura de produto.
- **"De" presente em todos os 9 upsells e em todos os 6 downsells** — sem inconsistência visual entre ofertas.

---

## 📋 Elementos ativos nos 3 checkouts da LP

| Elemento          | Configuração                                                                                       |
| :---------------- | :------------------------------------------------------------------------------------------------- |
| Timer             | "Offer expires in {timer}" — **5 min**, texto preto, fundo `#f7f7f7`, fonte 14, bold              |
| Exit popup        | "Wait! Don't leave yet!" — desconto adicional de **10%**, botão verde `#00ffaa`, texto preto      |
| Live buyers count | "{buyers} people just bought this product" — random entre **3 e 20**, refresh **5–15s**, verde   |

Os 3 elementos estão ativos e com a MESMA configuração nos 3 checkouts da LP (sem divergência entre 1/3/6 bottles).

---

## 📎 Anexo — estrutura completa

```json
{
  "lp": "https://mabrai.com/ztes21-fpnp-maxbrai21-prodmaxbra21-caps-pit12-utm-leand/",
  "product": "Max Brain 2.1 - FB",
  "funis": {
    "A": {
      "name": "FUNIL A - MAX BRAIN 2.1 - 1 BOTTLE - PITCH 1.2 - FUNIL 8.0",
      "entry": {"slug": "0x1CBayi", "qtd": 1, "total": 89, "de": 99, "save": 10, "pct": 10},
      "upsell1": [
        {"slug": "70dmh5hF", "qtd": 6, "total": 114, "de_total": 594, "save": 480},
        {"slug": "h4O00KHF", "qtd": 4, "total": 98,  "de_total": 396, "save": 298},
        {"slug": "70tLMhbl", "qtd": 2, "total": 58,  "de_total": 198, "save": 140}
      ],
      "downsell1": {"slug": "BEgdGXhx", "qtd": 2, "total": 49, "normally_un": 99, "today_un": 24.50, "headline": "U$80 Discount"},
      "downsell2": {"slug": "hxIIZrg8", "qtd": 1, "total": 59, "normally_un": 99, "today_un": 59}
    },
    "B": {
      "name": "FUNIL B - MAX BRAIN 2.1 - 3 BOTTLES - PITCH 1.2 - FUNIL 8.0",
      "entry": {"slug": "ng1b02JI", "qtd": 3, "total": 207, "de": 267, "save": 60, "pct": 22},
      "upsell1": [
        {"slug": "a1H77iFk", "qtd": 12, "total": 198, "de_total": 1188, "save": 990},
        {"slug": "0cx87tas", "qtd": 9,  "total": 171, "de_total": 891,  "save": 720},
        {"slug": "eCQn5dl2", "qtd": 6,  "total": 147, "de_total": 594,  "save": 447}
      ],
      "downsell1": {"slug": "iqOefl9z", "qtd": 4, "total": 147, "normally_un": 99, "today_un_exibido": 37, "today_un_real": 36.75, "headline": "U$200 Discount"},
      "downsell2": {"slug": "y75otaRz", "qtd": 2, "total": 98, "normally_un": 99, "today_un": 49}
    },
    "C": {
      "name": "FUNIL C - MAX BRAIN 2.1 - 6 BOTTLES - PITCH 1.2 - FUNIL 8.0",
      "entry": {"slug": "ZPar1z02", "qtd": 6, "total": 294, "de": 534, "save": 240, "pct": 45},
      "upsell1": [
        {"slug": "XhoKxCvg", "qtd": 12, "total": 348, "de_total": 1188, "save": 840},
        {"slug": "iqdarP7K", "qtd": 9,  "total": 333, "de_total": 891,  "save": 558},
        {"slug": "zp5OfrKp", "qtd": 6,  "total": 294, "de_total": 594,  "save": 300}
      ],
      "downsell1": {"slug": "OokSGx6O", "qtd": 6, "total": 174, "normally_un": 99, "today_un": 29, "headline": "U$320 Discount"},
      "downsell2": {"slug": "3v91xHXo", "qtd": 3, "total": 117, "normally_un": 99, "today_un": 39}
    }
  }
}
```
