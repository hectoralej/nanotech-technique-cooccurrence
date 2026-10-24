"""Valida y consolida los resultados de los revisores visuales y los contrasta con la tipología del pie.

Lee resultados/<revisor>/Lxxx.jsonl, valida el formato, deriva el destino visual (simple / pareja / compuesta / superpuesto / excluir),
compara con el destino estimado por el pie y entre revisores (lotes «ambos»). Escribe:
  figuras_vision.csv · cola_desacuerdos.csv · bases/*.csv · PROGRESO.md
Uso: python modelos/flujo_figuras/consolidar.py
"""
import json
from pathlib import Path

import pandas as pd

OUT = Path(__file__).resolve().parent
CAMPOS = {"n", "paneles", "n_micro", "n_espectro", "n_otro", "curvas_superpuestas", "espectro_limpio", "tecnicas", "calidad", "confianza", "nota"}
SINO = {"si", "no", "na"}
plan = pd.read_csv(OUT / "plan_lotes.csv", dtype={"n": int}, encoding="utf-8-sig")
filas, errores = [], []
for carpeta in sorted((OUT / "resultados").glob("*/")):
    for f in sorted(carpeta.glob("L*.jsonl")):
        for i, linea in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if not linea.strip():
                continue
            try:
                d = json.loads(linea)
                faltan = CAMPOS - set(d)
                if faltan:
                    raise ValueError(f"faltan campos {sorted(faltan)}")
                if d["n_micro"] + d["n_espectro"] + d["n_otro"] != d["paneles"]:
                    raise ValueError("n_micro + n_espectro + n_otro != paneles")
                if d["curvas_superpuestas"] not in SINO or d["espectro_limpio"] not in SINO or d["confianza"] not in (1, 2, 3):
                    raise ValueError("valor fuera de rango")
                d.update(lote=f.stem, revisor=carpeta.name)
                filas.append(d)
            except Exception as e:                                         # noqa: BLE001
                errores.append(f"{carpeta.name}/{f.name} línea {i}: {e}")


def destino_visual(r):
    util = r.n_micro + r.n_espectro
    if util == 0:
        return "excluir"
    if r.paneles == 1:
        return "superpuesto" if (r.n_espectro == 1 and r.curvas_superpuestas == "si") else "simple"
    if r.paneles == 2 and r.n_otro == 0:
        return "pareja"
    return "compuesta"


md = ["# Progreso del flujo de revisión visual", ""]
if not filas:
    md.append("Aún no hay resultados.")
    (OUT / "PROGRESO.md").write_text("\n".join(md), encoding="utf-8"); print("\n".join(md)); raise SystemExit
v = pd.DataFrame(filas).merge(plan[["lote", "n", "fig_id", "pmcid", "figura", "prioridad", "imagen", "tipologia_pie", "destino_pie", "clase_modelo", "fold", "asignado"]], on=["lote", "n"], how="left")
v["destino_vision"] = v.apply(destino_visual, axis=1)
ok = {"simple": {"simple"}, "pareja": {"pareja"}, "compuesta": {"compuesta"}, "superpuesto": {"superpuesto"}, "excluir": {"excluir"}}
v["acuerdo_con_pie"] = [d in ok.get(p, {p}) or (p == "revisar_multiple" and d in ("simple", "pareja", "compuesta")) for d, p in zip(v.destino_vision, v.destino_pie)]
v.to_csv(OUT / "figuras_vision_por_revisor.csv", index=False, encoding="utf-8-sig")

# acuerdo entre revisores (lotes «ambos»)
if v.revisor.nunique() > 1:
    a = v[v.asignado == "ambos"].pivot_table(index="fig_id", columns="revisor", values=["paneles", "destino_vision"], aggfunc="first")
    comp = a.dropna()
    rev = list(v.revisor.unique())[:2]
    if len(comp) and all(("paneles", r) in comp.columns for r in rev):
        acu = {"figuras_comunes": int(len(comp)),
               "mismo_n_paneles": round(float((comp[("paneles", rev[0])] == comp[("paneles", rev[1])]).mean()), 3),
               "mismo_destino": round(float((comp[("destino_vision", rev[0])] == comp[("destino_vision", rev[1])]).mean()), 3)}
        md += [f"## Acuerdo entre revisores ({rev[0]} vs {rev[1]})", "", f"- {acu}", ""]
        dis = comp[comp[("destino_vision", rev[0])] != comp[("destino_vision", rev[1])]].index
    else:
        dis = []
else:
    dis = []
v["desacuerdo_revisores"] = v.fig_id.isin(dis)
# una fila por figura (si dos revisores la hicieron, se toma la de «claude»; el desacuerdo entre ellos manda la figura a la cola)
v["_o"] = (v.revisor != "claude").astype(int)
v["_p"] = (~v.lote.str.startswith("R")).astype(int)          # los lotes R (re-revisión con las reglas nuevas) reemplazan a los L originales
u = v.sort_values(["fig_id", "_p", "_o"]).drop_duplicates("fig_id").drop(columns=["_o", "_p"]).reset_index(drop=True)
u["estado"] = ["aceptada_auto" if (a and c >= 2 and not d) else "cola_revision" for a, c, d in zip(u.acuerdo_con_pie, u.confianza, u.desacuerdo_revisores)]
u.to_csv(OUT / "figuras_vision.csv", index=False, encoding="utf-8-sig")             # todas las figuras clasificadas, una fila cada una
cola = u[u.estado == "cola_revision"]
cola.to_csv(OUT / "cola_desacuerdos.csv", index=False, encoding="utf-8-sig")
(OUT / "bases").mkdir(exist_ok=True)
for d in ["simple", "pareja", "compuesta", "superpuesto", "excluir"]:                 # bases por categoría: todas las clasificadas, con su estado
    u[u.destino_vision == d].to_csv(OUT / "bases" / f"{d}.csv", index=False, encoding="utf-8-sig")
fin = u[u.estado == "aceptada_auto"]

hechas = u
md += [f"Figuras clasificadas: **{len(hechas)}** de {plan.fig_id.nunique()} ({len(hechas)/plan.fig_id.nunique():.0%}). Lotes con resultado: {v.lote.nunique()} de {plan.lote.nunique()}.", "",
       "## Destino según la imagen", "", hechas.destino_vision.value_counts().to_string(), "",
       "## Imagen frente al pie (filas = imagen, columnas = pie)", "", pd.crosstab(hechas.destino_vision, hechas.destino_pie).to_string(), "",
       f"Coinciden imagen y pie: {hechas.acuerdo_con_pie.mean():.1%}. Aceptadas automáticamente (coinciden, confianza ≥ 2): {len(fin)}. En la cola de revisión: {len(cola)}.", "",
       "## Por categoría (aceptadas / cola)", "", pd.crosstab(u.destino_vision, u.estado).to_string(), "",
       f"Panel medio por figura: {hechas.paneles.mean():.2f}; figuras con 1 panel: {(hechas.paneles == 1).mean():.1%}; con 2: {(hechas.paneles == 2).mean():.1%}; con 3 o más: {(hechas.paneles >= 3).mean():.1%}.", ""]
if errores:
    md += ["## Errores de formato (corregir)", ""] + [f"- {e}" for e in errores[:40]] + [""]
(OUT / "PROGRESO.md").write_text("\n".join(md), encoding="utf-8")
print("\n".join(md))
