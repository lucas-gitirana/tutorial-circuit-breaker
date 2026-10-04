#!/usr/bin/env bash
# Chama GET /produtos/1 da vitrine N vezes (padrão: 1) e resume cada resposta:
# status HTTP, tempo total, de onde vieram as recomendações e o estado do circuito.
# Uso: bash tutorial/chamar-vitrine.sh [N]
N="${1:-1}"
for i in $(seq 1 "$N"); do
  saida=$(curl -s -w '\n%{http_code} %{time_total}' localhost:8021/produtos/1)
  python3 - "$i" "$saida" <<'PY'
import json, sys
n, saida = sys.argv[1], sys.argv[2]
corpo, _, meta = saida.rpartition("\n")
status, tempo = meta.split()
try:
    r = json.loads(corpo)
except ValueError:
    r = {}
if not isinstance(r, dict):
    r = {}
if "origem_recomendacoes" in r:
    print(f"#{n:<2} HTTP {status}  {float(tempo):5.2f}s  origem={r['origem_recomendacoes']:<9} circuito={r['circuito']}")
elif status == "000":
    print(f"#{n:<2} sem resposta: a vitrine está rodando? (docker compose ps)")
else:
    print(f"#{n:<2} HTTP {status}  {float(tempo):5.2f}s  {r.get('erro', corpo.strip())}")
PY
done
