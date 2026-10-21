"""Arma la lista final de verificacion humana a partir de los candidatos con licencia verde.

Entrada: work/verif_candidates.csv, work/final.jsonl (articulos con dos pasadas) y work/llm/B (articulos con una sola pasada).
Salida: work/verif_final.csv (con la clave del modelo), curation/verificacion_excluidas.csv (lo que se quito y por que).
Luego: python -m curation.human_sheet make
"""
from __future__ import annotations

import json

import pandas as pd

from src.common import ROOT
from curation import equivalence as eq, merge

CUR = ROOT / "curation"
# Revision de Claude (pertinencia): el nanoportador no es el objeto de estudio, no es un nanoportador disenado o el articulo esta retractado
MANUAL_OUT = {
    "PMC13289168": "antigeno de vacuna de Echovirus; el LNP es solo vehiculo y el tema es viral",
    "PMC5337964": "mRNA que codifica un anticuerpo; el estudio es la expresion in vivo, no el nanoportador",
    "PMC9118843": "organoides tumorales usados para comparar dos formulaciones comerciales; el objeto es el modelo",
    "PMC13453940": "vesiculas extracelulares modificadas con hierro; no es un nanoportador sintetico de las familias del proyecto",
    "PMC8693049": "nanoparticulas de oro dentro de un hidrogel de matriz extracelular; el objeto es el hidrogel",
    "PMC12190990": "nanoparticulas de oro como sensor colorimetrico; no es un nanoportador",
    "PMC6397290": "articulo retractado",
    "PMC12970522": "quimica de fotopolimerizacion de materiales; no es un nanoportador",
    "PMC12785278": "nanoparticulas de plata de sintesis verde con fin antimicrobiano; no es un nanoportador disenado",
    "PMC10389072": "nanoparticulas de plata de sintesis verde con fin antimicrobiano; no es un nanoportador disenado",
    "PMC11678683": "nanoparticulas de plata de sintesis biologica con fin antimicrobiano; no es un nanoportador disenado",
    "PMC8235414": "nanoparticulas de oro comerciales usadas como material de comparacion; no es un nanoportador disenado",
    "PMC9823929": "nanoparticulas de oxido de hierro estudiadas como radiosensibilizador; no es un nanoportador disenado",
    "PMC9785794": "nanoparticulas de latex con complejos luminiscentes de europio (sonda); no es un nanoportador",
    "PMC13509044": "el estudio es un mezclador milifluidico para producir LNP; el objeto es el equipo",
    "PMC7916496": "nanopolvos de silice comerciales como material; no es un nanoportador disenado",
    "PMC13059125": "andamio de aleacion de Mg con liposomas inmovilizados; el objeto es el andamio",
}
MED = {"water": "agua", "pbs": "PBS", "serum": "suero", "culture_medium": "medio_cultivo"}


def med(m) -> str:
    c = eq.medium_class(m)
    if c == "nd":
        return "no_declarado"
    if c in MED:
        return MED[c]
    return "tampon" if c.startswith("buffer") else "otro"


def main() -> None:
    v = pd.read_csv(CUR / "work" / "verif_candidates.csv", dtype={"pmcid": str}).drop_duplicates("pmcid")
    fin = {}
    for line in open(CUR / "work" / "final.jsonl", encoding="utf-8"):
        r = json.loads(line)
        fin[r["pmcid"]] = r
    B = merge.load("B")
    rows = []
    for r in v.itertuples():
        rec = fin.get(r.pmcid) or B[r.pmcid]
        S = {s["id"]: s for s in rec.get("samples", []) or []}
        g = rec["gate"] if isinstance(rec.get("gate"), dict) and "gate" in rec["gate"] else eq.gate(rec)
        ms = rec.get("measurements", []) or []
        mi = [m for m in ms if eq.is_micro_useful(m, S)]
        dl = [m for m in ms if eq.is_dls_useful(m, S)[0]]
        ze = [m for m in ms if eq.is_zeta_useful(m, S)[0]]
        nm = lambda m: (S.get(m.get("sample_id"), {}).get("name") or str(m.get("sample_id"))).strip().lower()   # noqa: E731
        same = bool({nm(m) for m in mi} & {nm(m) for m in dl} & {nm(m) for m in ze})
        ctx = rec.get("context", {}) or {}
        pert = bool(ctx.get("article_kind") == "research" and ctx.get("nanocarrier_is_object_of_study") and not g["viral_pcr"])
        comp = sorted({m["technique"] for m in ms if m["technique"] not in ("micrograph", "DLS", "zeta") and eq.identity_of(m, S) in eq.USEFUL_IDENTITY})
        rows.append(dict(pmcid=r.pmcid, doi=r.doi, title=r.title, year=r.year, journal=r.journal, family=r.family, source=r.source, license_color=r.license_color,
                         license_xml=r.license_xml, summary=(ctx.get("summary") or "")[:200],
                         model_gate="si" if (g["micro"] and g["dls"] and g["zeta"] and same and not rec.get("disputed") and pert) else "no",
                         model_micro="si" if g["micro"] else "no", model_dls="si" if g["dls"] else "no", model_zeta="si" if g["zeta"] else "no",
                         model_variante=(mi[0].get("variant") if mi else "ninguna"), model_dls_medio=(med((dl[0].get("conditions") or {}).get("medium")) if dl else "sin_dls_util"),
                         model_zeta_medio=(med((ze[0].get("conditions") or {}).get("medium")) if ze else "sin_zeta_util"), model_complementarias=";".join(comp),
                         model_pertinente="si" if pert else "no"))
    d = pd.DataFrame(rows)
    out_rows = []
    for p, why in MANUAL_OUT.items():
        if p in set(d.pmcid):
            out_rows.append(dict(pmcid=p, doi=d.set_index("pmcid").loc[p, "doi"], motivo=why, quien="revision de Claude"))
    for r in d[d.model_pertinente == "no"].itertuples():
        if r.pmcid not in MANUAL_OUT:
            out_rows.append(dict(pmcid=r.pmcid, doi=r.doi, motivo="los modelos y la revision: el nanoportador no es el objeto de estudio o no es investigacion primaria", quien="modelos"))
    ex = pd.DataFrame(out_rows)
    final = d[~d.pmcid.isin(ex.pmcid)].copy()
    final.to_csv(CUR / "work" / "verif_final.csv", index=False)
    ex["doi_link"] = "https://doi.org/" + ex.doi.astype(str)
    ex[["doi_link", "motivo", "quien"]].to_csv(CUR / "verificacion_excluidas.csv", index=False, encoding="utf-8-sig")
    print("candidatos:", len(d), "| excluidos:", len(ex), "| en la lista:", len(final), "| el modelo dice que pasan la puerta:", int((final.model_gate == "si").sum()))
    print(final.groupby("source").size().to_dict())
    print(final.family.value_counts().to_dict())


if __name__ == "__main__":
    main()
