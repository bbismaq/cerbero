# Checagem de Oferta — Skill para Claude Code

Skill que audita VSLs/LPs com checkout no **Pagamerican** (`pay.pagamerican.app`) e seus funis de upsell/downsell **sem precisar assistir o vídeo nem comprar nada**.

Ela puxa o HTML cru das páginas em modo simulação (`?pag_test_4=true`), extrai todos os preços direto do payload do Next.js, mapeia a estrutura completa do funil (3 funis × 5 ofertas cada, tipicamente), e gera um relatório Markdown com:

- Tabelas de preço (LP + cada funil)
- Preço por bottle, "De", "You save", % off
- 🚨 Flags de erro e inconsistências
- ✅ Sanity checks que passaram
- 📋 Elementos ativos do checkout (timer, exit popup, live buyers)
- 📎 Anexo JSON com estrutura completa pra rastreabilidade

## Como usar

Depois de instalar (ver abaixo), abre o Claude Code e digita:

```
/Checagem-de-oferta <URL da LP>
```

Exemplo:

```
/Checagem-de-oferta https://mabrai.com/ztes21-fpnp-maxbrai21-prodmaxbra21-caps-pit12-utm-leand/
```

A skill executa, mostra um resumo na conversa e **salva o relatório completo em `~/Documents/Check-Offer/reports/<slug>-<data>.md`**.

Veja um exemplo de output em [`examples/max-brain-2.1-report.md`](examples/max-brain-2.1-report.md).

## Instalação

### Pré-requisitos

- [Claude Code](https://claude.com/claude-code) instalado
- `git` e `curl` disponíveis no PATH (em qualquer SO moderno já vem)

### Windows

```powershell
git clone https://github.com/<seu-usuario>/check-offer.git
cd check-offer
.\install.ps1
```

### macOS / Linux

```bash
git clone https://github.com/<seu-usuario>/check-offer.git
cd check-offer
chmod +x install.sh
./install.sh
```

### O que o instalador faz

1. Copia `SKILL.md` para `~/.claude/skills/Checagem-de-oferta/SKILL.md` (lugar onde o Claude Code descobre skills globais).
2. Cria a pasta `~/Documents/Check-Offer/reports/` onde os relatórios serão salvos.

### Instalação manual

Se preferir não rodar o script, basta copiar o arquivo:

**Windows (PowerShell):**
```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.claude\skills\Checagem-de-oferta" | Out-Null
Copy-Item SKILL.md "$env:USERPROFILE\.claude\skills\Checagem-de-oferta\SKILL.md"
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\Documents\Check-Offer\reports" | Out-Null
```

**macOS / Linux:**
```bash
mkdir -p ~/.claude/skills/Checagem-de-oferta
cp SKILL.md ~/.claude/skills/Checagem-de-oferta/SKILL.md
mkdir -p ~/Documents/Check-Offer/reports
```

Depois, **reinicie o Claude Code** (skills são carregadas no boot da sessão) e digite `/Checagem-de-oferta` pra confirmar que a skill apareceu.

## O que a skill checa hoje

13 checks automáticos, todos rodam em toda execução (sem omissão):

1. `originalUnitPrice: 0` no payload Pagamerican ≠ vazio na página (extrai do HTML do funil)
2. Downsell 2 mais caro (total ou por bottle) que Downsell 1
3. Preço por bottle inconsistente entre packs do mesmo funil
4. Outlier de per-bottle (menor e maior do funil)
5. Nomes de nós clonados sem renomear no admin
6. Upsell e downsell com mesmo total
7. Upsell var.3 com mesmo preço da entrada do funil
8. `priceDiscountPercentage` declarado bate com `(1 - unit/original)`
9. Pack "X + Y FREE" — calcular per-bottle considerando `X+Y`
10. Per-bottle exibido (`TODAY: $X per bottle`) vs. calculado (`total ÷ qtd`)
11. Headline `U$X Discount` (downsells) vs. desconto real
12. "De" presente em uns upsells e ausente em outros
13. Elementos ativos do checkout (timer, exit popup, live buyers) — confirmar presença e consistência entre os 3 checkouts da LP

## Como melhorar a skill

A skill é um arquivo Markdown — basta editar `SKILL.md`, dar commit e mandar PR.

Sugestões de melhoria são bem-vindas. Áreas para expandir:
- Suportar outros gateways (Stripe, Hotmart, Kiwify, etc.)
- Detectar VSL com vídeo em iframe (e capturar duração)
- Validar fluxo end-to-end com browser automation (Playwright)

## Limitações conhecidas

- Funciona apenas com checkouts **Pagamerican** (`pay.pagamerican.app`) por enquanto.
- **Não simula o clique** em "Iniciar simulação de compra" — extrai dados do payload, que é a mesma fonte que o front renderiza e o backend cobra. Preços são confiáveis, mas o **fluxo end-to-end** (botão funciona, redirect dispara) não é validado.
- Páginas de funil com domínios customizados (ex.: `mabrn21fv.online`) — a skill descobre o domínio dinamicamente, mas se mudar o formato de URL pode quebrar.

## Licença

Uso interno. Não distribuir publicamente sem autorização do autor.
