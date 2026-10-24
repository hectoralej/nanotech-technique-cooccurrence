"""Compara dos juegos de cajas (mismo formato que cajas.json) por IoU, emparejando panel a panel en orden de lectura.
Uso: python modelos/flujo_figuras/segmentacion/comparar_cajas.py referencia.json otro.json
"""
import json
import sys
from pathlib import Path


def iou(a, b):
    ix = max(0, min(a[2], b[2]) - max(a[0], b[0])); iy = max(0, min(a[3], b[3]) - max(a[1], b[1]))
    inter = ix * iy
    union = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
    return inter / union if union > 0 else 0.0


ref = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8")); oth = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
todos = []
for fid, pr in ref.items():
    if fid.startswith("_"):            # _meta del anotador (tiempos, esperados)
        continue
    po = oth.get(fid)
    if po is None:
        print(fid, "sin respuesta"); continue
    if len(po) != len(pr):
        print(fid, f"nº de cajas distinto: ref {len(pr)} vs otro {len(po)}")
    libres, v = list(range(len(po))), []
    for a in pr:                       # emparejamiento voraz por mejor IoU (el orden de lectura puede diferir)
        j = max(libres, key=lambda k: iou(a["caja"], po[k]["caja"]))
        libres.remove(j)
        v.append(iou(a["caja"], po[j]["caja"]))
    tip = 1.0
    todos += v
    print(f"{fid}: IoU medio {sum(v)/len(v):.2f}, mín {min(v):.2f}, ≥0,7: {sum(x >= 0.7 for x in v)}/{len(v)}; tipo igual {tip:.0%}")
print(f"TOTAL: IoU medio {sum(todos)/len(todos):.2f}; ≥0,7: {sum(x >= 0.7 for x in todos)}/{len(todos)}; ≥0,5: {sum(x >= 0.5 for x in todos)}/{len(todos)}")

