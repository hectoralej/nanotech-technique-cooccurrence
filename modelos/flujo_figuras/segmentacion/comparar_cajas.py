"""Compara dos juegos de cajas (mismo formato que cajas.json) por IoU, emparejando cada caja de referencia con la mejor caja libre del otro juego.
Solo se comparan las cajas de nivel superior (sin `padre`). Se informan: IoU medio, % con IoU ≥ 0,7 y ≥ 0,5, cajas sin pareja y % de tipo igual (medido, no fijo).
Si hay menos cajas que en la referencia, las sobrantes de la referencia cuentan como no encontradas (IoU 0).
Uso: python modelos/flujo_figuras/segmentacion/comparar_cajas.py referencia.json otro.json [--solo-comunes]
"""
import json
import sys
from pathlib import Path


def iou(a, b):
    ix = max(0, min(a[2], b[2]) - max(a[0], b[0])); iy = max(0, min(a[3], b[3]) - max(a[1], b[1]))
    inter = ix * iy
    union = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
    return inter / union if union > 0 else 0.0


def cargar(ruta):
    d = json.loads(Path(ruta).read_text(encoding="utf-8-sig"))
    return {k: [p for p in v if "padre" not in p] for k, v in d.items() if not k.startswith("_")}


if __name__ == "__main__":
    ref, oth = cargar(sys.argv[1]), cargar(sys.argv[2])
    todos, tipos, sin_pareja, n_ref = [], [], 0, 0
    for fid, pr in ref.items():
        po = oth.get(fid)
        if po is None:
            if "--solo-comunes" not in sys.argv:
                print(fid, "sin respuesta")
            continue
        n_ref += len(pr)
        if len(po) != len(pr):
            print(fid, f"nº de cajas distinto: ref {len(pr)} vs otro {len(po)}")
        libres, v, tp = list(range(len(po))), [], []
        for a in pr:
            if not libres:
                v.append(0.0); sin_pareja += 1; continue
            j = max(libres, key=lambda k: iou(a["caja"], po[k]["caja"]))
            libres.remove(j)
            v.append(iou(a["caja"], po[j]["caja"])); tp.append(a["tipo"] == po[j]["tipo"])
        todos += v; tipos += tp
        print(f"{fid}: IoU medio {sum(v) / len(v):.2f}, mín {min(v):.2f}, ≥0,7: {sum(x >= 0.7 for x in v)}/{len(v)}")
    if todos:
        print(f"TOTAL ({n_ref} cajas de referencia): IoU medio {sum(todos) / len(todos):.2f}; ≥0,7: {sum(x >= 0.7 for x in todos)}/{len(todos)}; ≥0,5: {sum(x >= 0.5 for x in todos)}/{len(todos)}; "
              f"sin pareja: {sin_pareja}; tipo igual (emparejadas): {sum(tipos)}/{len(tipos)}")
