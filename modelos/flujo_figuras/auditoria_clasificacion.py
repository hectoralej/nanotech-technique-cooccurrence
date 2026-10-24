"""Auditoría a ciegas de la clasificación visual: muestra estratificada por destino y por revisor (Claude/Haiku vs Codex).
Genera hojas de contacto con numeración nueva (sin etiquetas) en auditoria/hojas/ y la clave oculta auditoria/clave.csv.
Un auditor independiente cuenta los paneles de cada figura; luego `auditoria_clasificacion.py --comparar respuestas.json` calcula la exactitud.
Uso: python modelos/flujo_figuras/auditoria_clasificacion.py            (crea la muestra)
     python modelos/flujo_figuras/auditoria_clasificacion.py --comparar modelos/flujo_figuras/auditoria/respuestas.json
"""
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from preparar_lotes import RAIZ, hoja  # noqa: E402

OUT = Path(__file__).resolve().parent / "auditoria"
CUPO = {"simple": 8, "pareja": 10, "compuesta": 14, "superpuesto": 8, "excluir": 8}


def crear():
    v = pd.read_csv(OUT.parent / "figuras_vision.csv", dtype=str, encoding="utf-8-sig")
    v["paneles"] = v.paneles.astype(int)
    partes = []
    for d, k in CUPO.items():
        g = v[v.destino_vision == d]
        # mitad por revisor cuando hay de ambos
        sel = [x.sample(min(len(x), k // 2 if x.revisor.nunique() else k), random_state=20261024) for _, x in g.groupby("revisor")]
        s = pd.concat(sel)
        if len(s) < k:
            s = pd.concat([s, g.drop(s.index).sample(min(k - len(s), len(g) - len(s)), random_state=7)])
        partes.append(s)
    m = pd.concat(partes).sample(frac=1, random_state=11).reset_index(drop=True)
    m["id_aud"] = m.index + 1
    (OUT / "hojas").mkdir(parents=True, exist_ok=True)
    for h in range(0, len(m), 6):
        sub = m.iloc[h:h + 6]
        hoja([(int(i) % 6 or 6, RAIZ / im) for i, im in zip(sub.id_aud, sub.imagen)], OUT / "hojas" / f"A{h // 6 + 1}.jpg")
    m[["id_aud", "fig_id", "revisor", "destino_vision", "estado", "paneles", "n_micro", "n_espectro", "n_otro", "curvas_superpuestas", "confianza", "destino_pie"]].to_csv(
        OUT / "clave.csv", index=False, encoding="utf-8-sig")
    print(len(m), "figuras;", (len(m) + 5) // 6, "hojas en", OUT / "hojas")


def destino(p, mi, es, ot, sup):
    if mi + es == 0:
        return "excluir"
    if p == 1:
        return "superpuesto" if (es == 1 and sup == "si") else "simple"
    if p == 2 and ot == 0:
        return "pareja"
    return "compuesta"


def comparar(ruta):
    r = json.loads(Path(ruta).read_text(encoding="utf-8"))                   # {"1": [paneles, n_micro, n_espectro, n_otro, curvas]}
    k = pd.read_csv(OUT / "clave.csv", dtype={"id_aud": str}, encoding="utf-8-sig")
    k["a_paneles"] = k.id_aud.map(lambda i: r[i][0]); k["a_destino"] = k.id_aud.map(lambda i: destino(*r[i][:1], r[i][1], r[i][2], r[i][3], r[i][4]))
    k["ok_paneles"] = k.paneles == k.a_paneles
    k["ok_destino"] = k.destino_vision == k.a_destino
    k["dif_paneles"] = k.paneles - k.a_paneles
    print("Global: paneles exactos", round(k.ok_paneles.mean(), 3), "| destino", round(k.ok_destino.mean(), 3), "| |dif|<=1:", round((k.dif_paneles.abs() <= 1).mean(), 3))
    print(k.groupby("destino_vision")[["ok_paneles", "ok_destino"]].mean().round(2).assign(n=k.groupby("destino_vision").size()))
    print(k.groupby("revisor")[["ok_paneles", "ok_destino"]].mean().round(2).assign(n=k.groupby("revisor").size()))
    print(k.groupby("estado")[["ok_paneles", "ok_destino"]].mean().round(2).assign(n=k.groupby("estado").size()))
    k.to_csv(OUT / "resultado_auditoria.csv", index=False, encoding="utf-8-sig")


if __name__ == "__main__":
    comparar(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[1] == "--comparar" else crear()
