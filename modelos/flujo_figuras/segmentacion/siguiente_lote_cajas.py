"""Lotes de cajas pendientes de un revisor (un lote está hecho si existe cajas/resultados/<revisor>/Cxxx.json).
Uso: python modelos/flujo_figuras/segmentacion/siguiente_lote_cajas.py claude|codex [cuantos=5]
"""
import json
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent / "cajas"
quien = sys.argv[1] if len(sys.argv) > 1 else "claude"
k = int(sys.argv[2]) if len(sys.argv) > 2 else 5
pend = [json.loads(f.read_text(encoding="utf-8")) for f in sorted((OUT / "lotes").glob("C*.json"))]
pend = [lt for lt in pend if lt["asignado"] == quien and not (OUT / "resultados" / quien / f"{lt['lote']}.json").exists()]
print(f"{quien}: {len(pend)} lotes de cajas pendientes")
for lt in pend[:k]:
    print(f"  {lt['lote']} ({len(lt['figuras'])} figuras) -> cajas/resultados/{quien}/{lt['lote']}.json")
