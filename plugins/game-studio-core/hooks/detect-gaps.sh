#!/bin/bash
# Game-studio harness SessionStart hook: Detect documentation gaps
# Cross-platform: Windows Git Bash compatible
# 2026-07-09 精简: dropped fresh-project & sparse-design-docs checks — both were
# permanently false on this mature repo and cost two full-tree finds per session
# start. Only the TBD ADR placeholder scan remains.

set +e

echo "=== Checking for Documentation Gaps ==="

# --- Pending "TBD ADR" placeholders awaiting backfill ---
# Counts unresolved placeholders that should be replaced once the corresponding
# ADR is written. Match on full-width punctuation (：（) which is unique to the
# placeholder syntax — avoids self-matching this hook's own ASCII strings.
# See docs/architecture/README.md for the index.
TBD_ADR_PATTERN='TBD ADR[：（]'
TBD_ADR_COUNT=$(grep -rnE "$TBD_ADR_PATTERN" design/ 2>/dev/null | wc -l)
TBD_ADR_COUNT=$(echo "$TBD_ADR_COUNT" | tr -d ' ')

if [ "$TBD_ADR_COUNT" -gt 0 ]; then
  echo ""
  echo "GAP: $TBD_ADR_COUNT 处 \"TBD ADR\" 占位待回填"
  TBD_FILES=$(grep -rlE "$TBD_ADR_PATTERN" design/ 2>/dev/null | tr '\n' ' ')
  echo "  涉及文件: $TBD_FILES"
  if [ -f "docs/architecture/README.md" ]; then
    echo "  追踪清单: docs/architecture/README.md"
  else
    echo "  建议: 建立 docs/architecture/README.md 作为 ADR 索引"
  fi
  echo "  Suggested: 写完对应 ADR 后按清单替换 TBD 占位"
fi

# --- Summary ---
echo ""
echo "To get a comprehensive project analysis, run: /project-stage-detect"
echo "==================================="

exit 0
