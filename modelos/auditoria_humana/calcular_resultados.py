"""Calcula la precisión humana estimada (con IC de Wilson al 95 %) y el acuerdo entre revisores a partir de los tres libros completados.

Uso: python modelos/auditoria_humana/calcular_resultados.py [carpeta_con_los_tres_libros]
Escribe RESULTADOS_AUDITORIA.md y resultados_auditoria.json en esa carpeta.
Precisión = sí / (sí + no); los «dudoso» se informan aparte y no cuentan como acierto ni como error.
Para las filas COMUN (las ven los tres) se usa el voto de la mayoría (≥ 2 de 3) en la precisión; el acuerdo se calcula sobre ellas.
"""
import json
import sys
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd

D = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent
REV = ["Hector", "Bryan", "Carlos"]
PREG = {"descriptores": ["¿La cita respalda esos valores para esa muestra? (sí/no/dudoso)"],
        "espectros": ["¿Esa figura muestra esa técnica para esa muestra? (sí/no/dudoso)"],
        "micrografias": ["¿Es una micrografía de nanopartículas del artículo? (sí/no/dudoso)", "¿La técnica/variante es correcta? (sí/no/dudoso)"]}
CAT = ["sí", "no", "dudoso"]


def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (c - h, c + h)


def fleiss(m):  # m: filas = ítems, columnas = categorías, valores = nº de revisores
    n = m.sum(axis=1)[0]
    pj = m.sum(axis=0) / m.sum()
    Pi = ((m * (m - 1)).sum(axis=1)) / (n * (n - 1))
    Pe = (pj ** 2).sum()
    return float((Pi.mean() - Pe) / (1 - Pe)) if Pe < 1 else float("nan")


libros = {}
for r in REV:
    f = D / f"Auditoria_{r}.xlsx"
    if f.exists():
        libros[r] = {h: pd.read_excel(f, sheet_name=h) for h in PREG}
if not libros:
    sys.exit("No hay libros Auditoria_<nombre>.xlsx en " + str(D))
out, md = {}, ["# Resultados de la auditoría humana (v0.1)", "", f"Revisores con libro: {', '.join(libros)}. IC 95 % de Wilson. «dudoso» se informa aparte.", ""]
for hoja, preguntas in PREG.items():
    for q in preguntas:
        filas = []
        for r, hojas in libros.items():
            df = hojas[hoja]
            if q not in df.columns:
                continue
            df = df[["id", "grupo", q]].rename(columns={q: "resp"}).assign(revisor=r)
            filas.append(df)
        if not filas:
            continue
        t = pd.concat(filas)
        t["resp"] = t.resp.astype(str).str.strip().str.lower().replace({"si": "sí", "nan": ""})
        t = t[t.resp.isin(["sí", "no", "dudoso"])]
        propias = t[t.grupo != "COMUN"]
        comunes = t[t.grupo == "COMUN"]
        # voto de mayoría en comunes
        votos = comunes.groupby("id").resp.agg(lambda s: s.value_counts().idxmax() if s.value_counts().iloc[0] >= 2 else "dudoso")
        todas = pd.concat([propias.resp, votos])
        si, no, du = int((todas == "sí").sum()), int((todas == "no").sum()), int((todas == "dudoso").sum())
        lo, hi = wilson(si, si + no)
        res = {"n_total": int(len(todas)), "si": si, "no": no, "dudoso": du, "precision": round(si / (si + no), 4) if si + no else None, "ic95": [round(lo, 4), round(hi, 4)]}
        # acuerdo en comunes (solo ítems con las tres respuestas)
        piv = comunes.pivot_table(index="id", columns="revisor", values="resp", aggfunc="first").dropna()
        if len(piv) and piv.shape[1] >= 2:
            pares = [(piv[a] == piv[b]).mean() for a, b in combinations(piv.columns, 2)]
            res["acuerdo_pares_medio"] = round(float(np.mean(pares)), 4)
            res["n_comunes_completos"] = int(len(piv))
            if piv.shape[1] == 3:
                m = np.array([[int((row == c).sum()) for c in CAT] for _, row in piv.iterrows()])
                res["kappa_fleiss"] = round(fleiss(m), 3)
            res["desacuerdos"] = [i for i, row in piv.iterrows() if row.nunique() > 1]
        out[f"{hoja} | {q}"] = res
        md.append(f"## {hoja}: {q}")
        md.append(f"- Respuestas: {res['n_total']} (sí {si}, no {no}, dudoso {du}).")
        md.append(f"- **Precisión: {res['precision']:.1%}** [IC 95 %: {lo:.1%}–{hi:.1%}]" if res["precision"] is not None else "- Sin respuestas sí/no todavía.")
        if "acuerdo_pares_medio" in res:
            md.append(f"- Acuerdo entre revisores en {res['n_comunes_completos']} ítems comunes: {res['acuerdo_pares_medio']:.1%}" + (f"; kappa de Fleiss {res['kappa_fleiss']}" if "kappa_fleiss" in res else "") + f". Desacuerdos: {', '.join(res['desacuerdos']) or 'ninguno'}.")
        md.append("")
(D / "resultados_auditoria.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
(D / "RESULTADOS_AUDITORIA.md").write_text("\n".join(md), encoding="utf-8")
print("\n".join(md))
