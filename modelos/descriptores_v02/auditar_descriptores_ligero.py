"""Depuración ligera de curation/ext_descriptores.csv (sin tocar el original).

Añade columnas derivadas (via, tabla_n, metodo_tamano, tamano_es_radio, meV, medio_norm, fuera_rango, duplicado, usable_modelo_prelim) y escribe
modelos/descriptores_v02/descriptores_v02_base.csv con las MISMAS filas y columnas originales en el mismo orden.
La verificación de la columna contra el encabezado de la tabla (XML) queda para la tarea R5 de Codex.
Uso: python modelos/descriptores_v02/auditar_descriptores_ligero.py
"""
import re
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
SALIDA = Path(__file__).resolve().parent
orig = pd.read_csv(RAIZ / "curation/ext_descriptores.csv", encoding="utf-8-sig")
d = orig.copy()
src = d.source.fillna("").astype(str)
quote = d.quote.fillna("").astype(str)
txt = (quote + " | " + src).str.lower()

# --- vía y tabla --------------------------------------------------------------------------------------
d["via"] = np.where(src.str.contains(r"table|tab\s?\d|tabla", case=False, regex=True), "tabla",
                    np.where(src.str.contains(r"fig", case=False, regex=True), "figura", "texto"))
d["tabla_n"] = pd.to_numeric(src.str.extract(r"(?:table|tab)\s*\.?\s*(\d+)", flags=re.I)[0], errors="coerce").astype("Int64")

# --- método del tamaño --------------------------------------------------------------------------------
PAT = {
    "DLS": r"\bdls\b|dynamic light|zetasizer|zeta ?sizer|hydrodynamic|z-?average|photon correlation|\bpcs\b|malvern|laser light scattering|particle size analy[sz]er|laser particle",
    "TEM": r"\btem\b|transmission electron|cryo-?tem|hrtem|\bstem\b",
    "SEM": r"\bsem\b|fe-?sem|scanning electron",
    "XRD": r"\bxrd\b|scherrer|crystallite|crystal size|diffraction",
    "AFM": r"\bafm\b|atomic force",
    "imagen": r"image-derived|from (the )?images?|imagej|measured (from|by) (tem|sem)|image analysis",
}
hits = pd.DataFrame({k: txt.str.contains(p, regex=True) for k, p in PAT.items()})
has_size = d.size_nm.notna()
tmp = hits.copy()
d["metodo_tamano"] = "desconocido"
for k in ("AFM", "XRD", "SEM", "TEM", "imagen"):          # métodos de imagen/cristalografía: solo si la cita NO menciona DLS
    d.loc[tmp[k] & ~tmp["DLS"], "metodo_tamano"] = k
d.loc[tmp["DLS"], "metodo_tamano"] = "DLS"
d["metodo_ambiguo"] = (tmp[["DLS", "TEM", "SEM", "XRD", "AFM", "imagen"]].sum(axis=1) > 1)
d.loc[~has_size, ["metodo_tamano", "metodo_ambiguo"]] = ["", False]
# si el tamaño aparece junto a PDI o zeta en la misma fila y no hay método contrario, casi seguro es DLS (el PDI y el zeta salen del mismo equipo)
d["metodo_tamano_inferido"] = d.metodo_tamano
d.loc[has_size & (d.metodo_tamano == "desconocido") & (d.pdi.notna() | d.zeta_mV.notna()), "metodo_tamano_inferido"] = "DLS_inferido"
d["tamano_es_radio"] = has_size & txt.str.contains(r"\bradius\b|\br_?h\b|hydrodynamic radius", regex=True)
d["zeta_meV"] = d.zeta_mV.notna() & txt.str.contains(r"\bmev\b", regex=True)

# --- medio normalizado ---------------------------------------------------------------------------------
def medio(m):
    s = str(m).lower().strip() if pd.notna(m) else ""
    if s in ("", "not_declared", "nan"):
        return "no_declarado"
    if re.search(r"culture|serum|dmem|rpmi|fbs|milk|plasma|medium", s):
        return "medio_cultivo_suero"
    if re.search(r"dmso|heptane|oil|ethanol|toluene|hexane|chloroform|aot", s):
        return "organico"
    if re.search(r"pbs|buffer|tris|hepes|phosphate|tamp", s):
        return "PBS_tampon"
    if re.search(r"kcl|kno3|nacl|saline|ionic|\bmm\b|electrolyte", s):
        return "salino_ionico"
    if re.search(r"water|aqueous|deioni|ultrapure|milli-?q|distilled|colloid|suspension|dispersion|solution", s):
        return "agua"
    return "otro"
d["medio_norm"] = d.medium.map(medio)

# --- rangos, duplicados y filas por artículo ----------------------------------------------------------
d["fuera_rango"] = ((d.size_nm < 5) | (d.size_nm > 5000) | (d.pdi > 1) | (d.zeta_mV.abs() > 100)).fillna(False)
d["duplicado"] = d.duplicated(["pmcid", "sample", "size_nm", "zeta_mV", "pdi"], keep=False)
d["n_filas_articulo"] = d.groupby("pmcid").pmcid.transform("size")
d["usable_modelo_prelim"] = (~d.fuera_rango) & (~d.tamano_es_radio) & (~d.zeta_meV) & (d.metodo_tamano.isin(["DLS", "desconocido", ""]))

d["usable_estricto"] = d.usable_modelo_prelim & (d.metodo_tamano_inferido.isin(["DLS", "DLS_inferido"]) | ~has_size)
# --- comprobaciones: mismas filas y columnas originales ------------------------------------------------
assert len(d) == len(orig) and list(d.columns[: orig.shape[1]]) == list(orig.columns)
assert d[orig.columns].equals(orig), "las columnas originales cambiaron"
d.to_csv(SALIDA / "descriptores_v02_base.csv", index=False, encoding="utf-8-sig")

# --- resumen ---------------------------------------------------------------------------------------------
L = []
L.append(f"filas {len(d)} | artículos {d.pmcid.nunique()}")
L.append("vía: " + ", ".join(f"{k} {v}" for k, v in d.via.value_counts().items()))
L.append("método del tamaño (filas con tamaño): " + ", ".join(f"{k} {v}" for k, v in d[has_size].metodo_tamano.value_counts().items()))
L.append("método inferido: " + ", ".join(f"{k} {v}" for k, v in d[has_size].metodo_tamano_inferido.value_counts().items()))
L.append(f"método ambiguo (cita nombra más de un método): {int(d.metodo_ambiguo.sum())} | tamaño en radio: {int(d.tamano_es_radio.sum())} | zeta en meV: {int(d.zeta_meV.sum())}")
L.append("medio normalizado: " + ", ".join(f"{k} {v}" for k, v in d.medio_norm.value_counts().items()))
L.append(f"fuera de rango: {int(d.fuera_rango.sum())} | duplicados: {int(d.duplicado.sum())}")
L.append(f"usable_estricto (DLS explícito o inferido, o sin tamaño): {int(d.usable_estricto.sum())} de {len(d)} ({d.usable_estricto.mean():.1%})")
L.append(f"usable_modelo_prelim: {int(d.usable_modelo_prelim.sum())} de {len(d)} ({d.usable_modelo_prelim.mean():.1%})")
print("\n".join(L))
(SALIDA / "RESUMEN_LIGERO.txt").write_text("\n".join(L), encoding="utf-8")




