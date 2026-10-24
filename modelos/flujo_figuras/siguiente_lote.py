"""Lista los lotes pendientes de un revisor (reanudable: un lote está hecho si existe su .jsonl con todas las figuras).
Uso: python modelos/flujo_figuras/siguiente_lote.py claude|codex [cuantos=3]
"""
import json
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent
quien = sys.argv[1] if len(sys.argv) > 1 else "claude"
k = int(sys.argv[2]) if len(sys.argv) > 2 else 3
pend = []
for f in sorted((OUT / "lotes").glob("L*.json")):
    lote = json.loads(f.read_text(encoding="utf-8"))
    if lote["asignado"] not in (quien, "ambos"):
        continue
    r = OUT / "resultados" / quien / f"{lote['lote']}.jsonl"
    hecho = r.exists() and sum(1 for l in r.read_text(encoding="utf-8").splitlines() if l.strip()) >= len(lote["figuras"])
    if not hecho:
        pend.append(lote)
print(f"{quien}: {len(pend)} lotes pendientes")
for lote in pend[:k]:
    print(f"  {lote['lote']} ({len(lote['figuras'])} figuras, {len(lote['hojas'])} hojas) -> escribir resultados/{quien}/{lote['lote']}.jsonl")
