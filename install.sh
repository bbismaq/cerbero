#!/usr/bin/env bash
# Cerbero — instalador macOS/Linux
# Uso: ./install.sh

set -e

SKILL_SRC="$(dirname "$0")/SKILL.md"
SKILL_DEST_DIR="$HOME/.claude/skills/Cerbero"
SKILL_DEST="$SKILL_DEST_DIR/SKILL.md"
REPORTS_DIR="$HOME/Documents/Cerbero/reports"

if [ ! -f "$SKILL_SRC" ]; then
  echo "ERRO: SKILL.md nao encontrado em $SKILL_SRC"
  echo "Rode este script da pasta raiz do repo (onde esta o SKILL.md)."
  exit 1
fi

echo "Instalando skill Cerbero..."

mkdir -p "$SKILL_DEST_DIR"
cp -f "$SKILL_SRC" "$SKILL_DEST"
echo "  [OK] Skill copiada para: $SKILL_DEST"

mkdir -p "$REPORTS_DIR"
echo "  [OK] Pasta de relatorios pronta: $REPORTS_DIR"

echo ""
echo "Instalacao concluida."
echo "Proximos passos:"
echo "  1. Reinicie o Claude Code (skills sao carregadas no boot)."
echo "  2. Digite /Cerbero <URL da LP> para auditar uma oferta."
echo "  3. Relatorios serao salvos em: $REPORTS_DIR"
