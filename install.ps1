# Checagem de Oferta — instalador Windows
# Uso: .\install.ps1

$ErrorActionPreference = "Stop"

$skillSrc = Join-Path $PSScriptRoot "SKILL.md"
$skillDestDir = Join-Path $env:USERPROFILE ".claude\skills\Checagem-de-oferta"
$skillDest = Join-Path $skillDestDir "SKILL.md"
$reportsDir = Join-Path $env:USERPROFILE "Documents\Check-Offer\reports"

if (-not (Test-Path $skillSrc)) {
    Write-Host "ERRO: SKILL.md nao encontrado em $skillSrc" -ForegroundColor Red
    Write-Host "Rode este script da pasta raiz do repo (onde esta o SKILL.md)." -ForegroundColor Red
    exit 1
}

Write-Host "Instalando skill Checagem-de-oferta..."

New-Item -ItemType Directory -Force -Path $skillDestDir | Out-Null
Copy-Item -Force $skillSrc $skillDest
Write-Host "  [OK] Skill copiada para: $skillDest" -ForegroundColor Green

New-Item -ItemType Directory -Force -Path $reportsDir | Out-Null
Write-Host "  [OK] Pasta de relatorios pronta: $reportsDir" -ForegroundColor Green

Write-Host ""
Write-Host "Instalacao concluida." -ForegroundColor Green
Write-Host "Proximos passos:" -ForegroundColor Yellow
Write-Host "  1. Reinicie o Claude Code (skills sao carregadas no boot)."
Write-Host "  2. Digite /Checagem-de-oferta <URL da LP> para auditar uma oferta."
Write-Host "  3. Relatorios serao salvos em: $reportsDir"
