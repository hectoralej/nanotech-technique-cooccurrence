"""Auditoría v2 de descriptores: mismas filas dudosas, pero con CONTEXTO del artículo completo (tabla completa con encabezados, o ±900 caracteres de texto).
La v1 (solo la cita) fue insuficiente: la cita guardada es un fragmento y los agentes anularon 244 zetas que sí están en el artículo.
Uso: python modelos/descriptores_v02/auditoria/preparar_auditoria_v2.py → lotes_v2/Exxx.json
"""
import html
import json
import os
import re
from pathlib import Path

import pandas as pd

OUT = Path(__file__).resolve().parent
RAIZ = OUT.parents[2]
POR_LOTE = 15
plan = pd.read_csv(OUT / "plan_auditoria.csv", encoding="utf-8-sig", dtype={"pmcid": str})


def limpio(s):
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s).replace("−", "-").replace(" ", " ")
    return re.sub(r"[ \t]+", " ", s).strip()


def tablas(xml):
    out = []
    for m in re.finditer(r"<table-wrap\b.*?</table-wrap>", xml, re.S):
        w = m.group(0)
        cap = limpio(re.search(r"<caption>(.*?)</caption>", w, re.S).group(1)) if re.search(r"<caption>", w) else ""
        filas = []
        for tr in re.findall(r"<tr\b.*?</tr>", w, re.S):
            celdas = [limpio(c) for c in re.findall(r"<t[hd]\b[^>]*>(.*?)</t[hd]>", tr, re.S)]
            filas.append(" | ".join(celdas))
        pie = limpio(re.search(r"<table-wrap-foot>(.*?)</table-wrap-foot>", w, re.S).group(1)) if re.search(r"<table-wrap-foot>", w) else ""
        out.append((cap, filas, pie))
    return out


cache = {}


def contexto(pm, muestra, cita):
    f = RAIZ / f"data/cache/fulltext/{pm}.xml"
    if not f.exists():
        return "(texto completo no disponible)"
    if pm not in cache:
        xml = f.read_text(encoding="utf-8", errors="ignore")
        cache[pm] = (xml, tablas(xml), re.sub(r"\s+", " ", limpio(re.sub(r"<table-wrap\b.*?</table-wrap>", " ", xml, flags=re.S))))
    xml, tbs, texto = cache[pm]
    lab = str(muestra).strip()
    for cap, filas, pie in tbs:                       # primero: la tabla cuya fila contiene la etiqueta
        if any(lab and lab in fila.split(" | ")[0] or (lab and lab in fila) for fila in filas):
            cuerpo = "\n".join(filas[:40])
            return f"TABLA: {cap[:300]}\n{cuerpo}\nNOTAS: {pie[:300]}"[:3000]
    t = texto.replace("−", "-")
    k = t.find(str(cita)[:45]) if cita else -1
    if k < 0 and lab:
        k = t.find(lab)
    if k < 0:
        return "(no se encontró la cita ni la muestra en el texto)"
    return "TEXTO: ..." + t[max(0, k - 900): k + 900] + "..."


(OUT / "lotes_v2").mkdir(exist_ok=True); (OUT / "resultados_v2").mkdir(exist_ok=True)
plan["lote_v2"] = [f"E{i // POR_LOTE + 1:03d}" for i in range(len(plan))]
for lote, g in plan.groupby("lote_v2"):
    filas = [{"id": r.id, "pmcid": r.pmcid, "muestra": r._4 if hasattr(r, "_4") else None} for r in []]
    filas = []
    for _, r in g.iterrows():
        filas.append({"id": r.id, "pmcid": r.pmcid, "muestra": r["sample"], "tamano_nm": None if pd.isna(r.size_nm) else r.size_nm, "pdi": None if pd.isna(r.pdi) else r.pdi,
                      "zeta_mV": None if pd.isna(r.zeta_mV) else r.zeta_mV, "medio": r.medium, "fuente": r.source, "cita": str(r.quote)[:600],
                      "contexto_del_articulo": contexto(r.pmcid, r["sample"], r.quote)})
    (OUT / "lotes_v2" / f"{lote}.json").write_text(json.dumps({"lote": lote, "filas": filas}, ensure_ascii=False, indent=1), encoding="utf-8")
print(len(plan), "filas en", plan.lote_v2.nunique(), "lotes (E001…)")
