"""Construye descriptores_v03.csv a partir de descriptores_v02_base.csv y la auditoría v2 (resultados_v2/E*.jsonl).

Política (no destructiva):
 - Los valores originales se conservan siempre (columnas size_nm, pdi, zeta_mV). Los valores auditados van en *_audit.
 - «corregir» solo se aplica (columnas *_final) si el valor nuevo aparece en el texto completo del artículo y la corrección no sale de un rango/punto medio.
 - «descartar» marca la fila (usable_v03 = False) pero no la borra.
 - «no_verificable» y las filas no auditadas se quedan como están (verificadas por cita en v0.1).
 - etiqueta_muestra y metodo_tamano de la auditoría se añaden como columnas.
Uso: python modelos/descriptores_v02/auditoria/consolidar_v03.py
"""
import glob
import json
import os
import re
from pathlib import Path

import pandas as pd

OUT = Path(__file__).resolve().parent
RAIZ = OUT.parents[2]
d = pd.read_csv(RAIZ / "modelos/descriptores_v02/descriptores_v02_base.csv", encoding="utf-8-sig", dtype={"pmcid": str})
d["id"] = [f"DESC-{i:04d}" for i in range(len(d))]
rows = []
for f in sorted(glob.glob(str(OUT / "resultados_v2/E*.jsonl"))):
    rows += [json.loads(l) for l in open(f, encoding="utf-8") if l.strip()]
a = pd.DataFrame(rows).drop_duplicates("id").set_index("id")
cache = {}


def texto(pm):
    if pm not in cache:
        f = RAIZ / f"data/cache/fulltext/{pm}.xml"
        t = f.read_text(encoding="utf-8", errors="ignore") if f.exists() else ""
        t = re.sub(r"<[^>]+>", " ", t).replace("&#x2212;", "-").replace("−", "-").replace("–", "-").replace(",", ".")
        cache[pm] = re.sub(r"\s+", " ", t)
    return cache[pm]


def presente(v, t):
    x = abs(float(v))
    return any(re.search(r"(?<![\d.])" + re.escape(f) + r"(?![\d])", t) for f in {f"{x:g}", f"{x:.1f}", f"{x:.2f}", f"{x:.3f}"})


for c in ("size_nm", "pdi", "zeta_mV"):
    d[c + "_final"] = d[c]
d["audit_veredicto"] = d.id.map(a.veredicto) if len(a) else None
d["etiqueta_muestra"] = d.id.map(a.etiqueta_muestra) if len(a) else None
d["metodo_tamano_audit"] = d.id.map(a.metodo_tamano) if len(a) else None
d["audit_motivo"] = d.id.map(a.motivo) if len(a) else None
d["correccion_aplicada"] = ""
d["correccion_rechazada"] = ""
d["usable_v03"] = d.usable_estricto if "usable_estricto" in d else True
map_c = {"tamano_nm": "size_nm", "pdi": "pdi", "zeta_mV": "zeta_mV"}
for i, r in d[d.audit_veredicto == "corregir"].iterrows():
    x = a.loc[r.id]
    motivo = str(x.get("motivo", "")).lower()
    for k, c in map_c.items():
        nuevo, viejo = x.get(k), r[c]
        if (pd.isna(nuevo) and pd.isna(viejo)) or (pd.notna(nuevo) and pd.notna(viejo) and abs(float(nuevo) - float(viejo)) < 1e-6):
            continue
        if pd.isna(nuevo):
            d.at[i, "correccion_rechazada"] += f"{c}→null (no se anula sin evidencia); "
        elif re.search(r"punto medio|midpoint|rango|range", motivo):
            d.at[i, "correccion_rechazada"] += f"{c}→{nuevo} (sale de un rango); "
        elif presente(nuevo, texto(r.pmcid)):
            d.at[i, c + "_final"] = float(nuevo); d.at[i, "correccion_aplicada"] += f"{c}: {viejo}→{nuevo}; "
        else:
            d.at[i, "correccion_rechazada"] += f"{c}→{nuevo} (no aparece en el artículo); "
desc = d.audit_veredicto == "descartar"
d.loc[desc, "usable_v03"] = False
d["revisar_v03"] = (d.audit_veredicto == "no_verificable") | (d.correccion_rechazada != "") | desc
d.to_csv(RAIZ / "modelos/descriptores_v02/descriptores_v03.csv", index=False, encoding="utf-8-sig")
n = len(a)
resumen = [f"# Descriptores v03 (auditoría v2)", "", f"Filas: {len(d)} · auditadas: {n} (las dudosas por reglas) · artículos: {d.pmcid.nunique()}", "",
           f"Veredictos: {a.veredicto.value_counts().to_dict() if n else {}}", f"Correcciones aplicadas (valor nuevo presente en el artículo): {int((d.correccion_aplicada != '').sum())}",
           f"Correcciones rechazadas (anulación sin evidencia, rango o valor ausente del artículo): {int((d.correccion_rechazada != '').sum())}",
           f"Descartadas (usable_v03 = False): {int(desc.sum())}", f"usable_v03: {int(d.usable_v03.sum())} de {len(d)}", f"Con etiqueta_muestra: {int(d.etiqueta_muestra.notna().sum())}",
           f"Marcadas para revisión humana: {int(d.revisar_v03.sum())}", "", "Los valores originales se conservan en size_nm, pdi y zeta_mV; los finales en *_final."]
(OUT.parent / "DESCRIPTORES_V03.md").write_text("\n".join(resumen), encoding="utf-8")
print("\n".join(resumen))
