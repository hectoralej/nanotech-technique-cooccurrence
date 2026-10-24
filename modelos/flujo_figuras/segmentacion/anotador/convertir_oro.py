"""Convierte las cajas humanas (v1, 24-oct) al esquema v2 de INSTRUCCIONES_CAJAS.md sin tocar el archivo original.

Cambios (documentados en cajas_humano_Hector_v2.json → _meta.conversion):
- Una caja contenida (≥ 80 % de su área) en otra mucho mayor (área < 50 % de la del padre) pasa a hija: "padre": k, "rel": "inset".
- PMC10005067|Figure 5: las 6 bandas (espectros en cascada de muestras distintas) estaban marcadas «micro» (tipo por omisión); pasan a «espectro» con "cascada": true,
  según la decisión de Héctor (24-oct): se separan porque cada curva es una sustancia distinta.
Uso: python modelos/flujo_figuras/segmentacion/anotador/convertir_oro.py
"""
import json
from pathlib import Path

D = Path(__file__).resolve().parent
h = json.loads((D / "cajas_humano_Hector.json").read_text(encoding="utf-8-sig"))
meta = h.pop("_meta")
log = []


def area(c):
    return (c[2] - c[0]) * (c[3] - c[1])


def dentro(a, b):
    ix = max(0, min(a[2], b[2]) - max(a[0], b[0])); iy = max(0, min(a[3], b[3]) - max(a[1], b[1]))
    return ix * iy / area(a) if area(a) > 0 else 0


for fid, paneles in h.items():
    if fid == "PMC10005067|Figure 5":
        for k, p in enumerate(paneles[:6], 1):
            p["tipo"] = "espectro"; p["cascada"] = True
        log.append(f"{fid}: cajas 1–6 → espectro en cascada")
    for k, p in enumerate(paneles, 1):
        padres = [(area(q["caja"]), j) for j, q in enumerate(paneles, 1)
                  if j != k and "padre" not in q and area(p["caja"]) < 0.5 * area(q["caja"]) and dentro(p["caja"], q["caja"]) >= 0.8]
        if padres:
            p["padre"] = min(padres)[1]; p["rel"] = "inset"
            log.append(f"{fid}: caja {k} → hija (inset) de la caja {p['padre']}")
meta["conversion"] = log
h["_meta"] = meta
(D / "cajas_humano_Hector_v2.json").write_text(json.dumps(h, ensure_ascii=False), encoding="utf-8")
print("\n".join(log))
