"""
Captura a URL do .m3u8 master de uma VSL hospedada no VTurb simulando play em browser headless.

Uso:
    python extract_m3u8.py --url <URL_DA_LP> --output <output.txt>

Output:
    - Stdout: a URL do .m3u8 master capturada.
    - Arquivo em --output: mesma URL.

Exit codes:
    0 — sucesso, URL capturada
    1 — falhou em capturar dentro do timeout
    2 — Playwright / Chromium nao instalado (rode install.ps1 do Cerbero)
"""

import argparse
import asyncio
import sys
from pathlib import Path

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("ERROR: playwright nao instalado. Rode install.ps1 do Cerbero.", file=sys.stderr)
    sys.exit(2)


async def capture_m3u8(url: str, timeout_seconds: int = 60) -> str:
    """Abre a LP em Chromium headless, clica no player, captura o .m3u8 master."""
    captured: list[str] = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        )
        page = await context.new_page()

        def on_response(response):
            req_url = response.url
            if ".m3u8" in req_url:
                captured.append(req_url)

        page.on("response", on_response)

        print(f"[cerbero] abrindo {url}...", file=sys.stderr)
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)

        # Espera o player renderizar
        await page.wait_for_timeout(2500)

        # Tenta clicar no player VTurb (ou genericos como fallback)
        clicked = False
        for selector in [
            "vturb-smartplayer",
            "[id^='vid_']",
            ".smartplayer-scroll-event",
            "video",
        ]:
            try:
                el = await page.query_selector(selector)
                if el:
                    await el.click(force=True, timeout=3000)
                    print(f"[cerbero] clique no player ({selector})", file=sys.stderr)
                    clicked = True
                    break
            except Exception:
                continue

        if not clicked:
            print("[cerbero] aviso: nao consegui clicar no player; aguardando captura passiva...", file=sys.stderr)

        # Polling ate m3u8 aparecer
        deadline_ms = timeout_seconds * 1000
        poll = 500
        elapsed = 0
        while elapsed < deadline_ms and not captured:
            await page.wait_for_timeout(poll)
            elapsed += poll

        # Se ja capturou, espera mais um pouco pra coletar variantes adicionais
        if captured:
            await page.wait_for_timeout(2000)

        await browser.close()

    if not captured:
        raise RuntimeError("timeout — nenhum .m3u8 capturado")

    # Prefere o master playlist (geralmente nomeado main.m3u8 no VTurb)
    masters = [u for u in captured if "main.m3u8" in u]
    if masters:
        return masters[0]
    return captured[0]


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--url", required=True, help="URL da LP com a VSL embutida")
    p.add_argument("--output", required=True, help="caminho do arquivo onde salvar a URL do m3u8")
    p.add_argument("--timeout", type=int, default=60, help="timeout em segundos (default 60)")
    args = p.parse_args()

    try:
        m3u8_url = asyncio.run(capture_m3u8(args.url, args.timeout))
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(m3u8_url, encoding="utf-8")

    print(m3u8_url)
    print(f"[cerbero] URL salva em {out_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
