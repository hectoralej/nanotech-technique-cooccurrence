"""Hoja de verificacion humana (~80 articulos) y calculo de acuerdo entre revisores y contra el modelo.

  python -m curation.human_sheet make [N]                 -> curation/verificacion_humana_80.csv (plantilla) + curation/work/clave_modelo.csv (NO abrir hasta terminar)
  python -m curation.human_sheet agreement a.csv b.csv    -> acuerdo y kappa entre dos copias completadas por dos personas
  python -m curation.human_sheet vs_model a.csv           -> acuerdo de una copia completada contra la clave del modelo

La plantilla NO muestra lo que dijo el modelo. Cada revisor trabaja en su propia copia (verificacion_humana_80_<nombre>.csv) sin ver la del otro.
"""
from __future__ import annotations

import json
import sys

import numpy as np
import pandas as pd

from src.common import ROOT
from curation import equivalence as eq

CUR = ROOT / "curation"
FIELDS = ["micrografia_util", "variante_micrografia", "dls_util", "dls_medio", "zeta_util", "zeta_medio", "misma_muestra", "pasa_puerta",
          "tecnicas_complementarias", "pertinente", "licencia_ok", "notas"]
CATEGORICAL = ["micrografia_util", "variante_micrografia", "dls_util", "dls_medio", "zeta_util", "zeta_medio", "misma_muestra", "pasa_puerta", "pertinente", "licencia_ok"]

GUIDE = """# Guía de verificación humana

Archivo de trabajo: `curation/verificacion_humana_80.csv` (80 artículos). **Cada persona hace su propia copia** con su nombre
(`verificacion_humana_80_hector.csv`, `..._carlos.csv`, …) y la llena **sin mirar la copia del otro**. No miren `work/clave_modelo.csv`: es lo que dijo el modelo.

Cómo se trabaja, artículo por artículo:
1. Copien el enlace de la columna `doi_link` (es `https://doi.org/...`) en el navegador. Se abre el artículo.
2. Busquen en el texto, las figuras y las tablas lo que pide cada columna.
3. Rellenen **solo** las columnas con fondo vacío, con los valores permitidos.

| Columna | Valores permitidos |
|---|---|
| `micrografia_util` | `si` / `no`. «Sí» = hay una figura de la **partícula del nanoportador** (no de un control ni de un componente), con la técnica identificable y ligada a una formulación concreta |
| `variante_micrografia` | `cryoTEM`, `TEM_negstain`, `TEM_posstain`, `TEM_dried_unstained`, `TEM_prep_not_declared`, `HRTEM`, `STEM`, `SEM`, `cryoSEM`, `ESEM`, `ninguna` |
| `dls_util` | `si` / `no`. «Sí» = valor numérico de tamaño con el **medio indicado** (agua, PBS, tampón, suero…), de una muestra identificable |
| `dls_medio` | `agua`, `PBS`, `tampon`, `suero`, `medio_cultivo`, `otro`, `no_declarado`, `sin_dls` |
| `zeta_util` | `si` / `no`. «Sí» = valor numérico con **medio o pH indicado**, de una muestra identificable |
| `zeta_medio` | igual que `dls_medio` (`sin_zeta` si no hay zeta) |
| `misma_muestra` | `si` / `no`. «Sí» = la micrografía, el DLS y el zeta son de la **misma formulación** |
| `pasa_puerta` | `si` solo si `micrografia_util`, `dls_util`, `zeta_util` y `misma_muestra` son `si` |
| `tecnicas_complementarias` | lista separada por `;` de: `UVVis_intrinseca`, `FTIR`, `XRD`, `EDS`, `DSC`, `TGA`, `Raman`, `NMR`, `XPS`, `NTA`, `SAXS`. Solo si se aplican a la **partícula**, no a un componente puro ni a un ensayo |
| `pertinente` | `si` / `no`. «Sí» = es un artículo de investigación donde el nanoportador es el objeto de estudio (no solo una herramienta) y no es AAV ni virus |
| `licencia_ok` | `si` / `no`. «Sí» = en la página del editor dice CC BY o CC0 |
| `notas` | dudas o casos raros |

Regla: **si dudan, `no` / `no_declarado`**.

Cuando las dos copias estén completas: `python -m curation.human_sheet agreement a.csv b.csv` (acuerdo y kappa por campo).
"""


def _split_complementary(final: dict) -> str:
    return ";".join(sorted(set(final.get("complementary_confirmed", []))))


def make(n: int | None = None) -> None:
    sc = pd.read_csv(CUR / "work" / "verif_final.csv", dtype={"pmcid": str})
    sheet = sc.sample(frac=1, random_state=11).reset_index(drop=True)            # orden aleatorio: no revela de donde sale cada articulo
    motivo = {"conjunto humano (aleatorio)": "Muestra aleatoria de los candidatos (mide precisión y recall de la puerta)",
              "vacio: SAXS (busqueda dirigida)": "Vacío de técnica: SAXS (búsqueda nueva en Europe PMC)",
              "pool: cryo": "Vacío de técnica: cryo-EM", "pool: inorganic": "Vacío de familia: inorgánicas con espectroscopía",
              "pool: liposome": "Micrografía + espectroscopía + DLS/zeta: liposomas", "pool: polymeric": "Micrografía + espectroscopía + DLS/zeta: poliméricas",
              "pool: LNP": "Micrografía + espectroscopía + DLS/zeta: LNP"}
    clean = sheet.title.astype(str).str.replace(r"</?[a-z]+>", "", regex=True).str.replace(r"\s+", " ", regex=True).str.strip()
    out = pd.DataFrame({"n": range(1, len(sheet) + 1), "doi_link": "https://doi.org/" + sheet.doi.astype(str), "doi": sheet.doi, "titulo": clean,
                        "anio": sheet.year, "revista": sheet.journal, "familia": sheet.family, "licencia_verificada": "CC BY (Europe PMC y XML del artículo)",
                        "motivo_de_inclusion": sheet.source.map(motivo).fillna(sheet.source)})
    for c in FIELDS:
        out[c] = ""
    out.to_csv(CUR / "verificacion_humana_80.csv", index=False, encoding="utf-8-sig")
    key = sheet[["pmcid", "doi", "model_gate", "model_micro", "model_dls", "model_zeta", "model_variante", "model_dls_medio", "model_zeta_medio", "model_complementarias", "model_pertinente"]]
    key.insert(0, "n", out.n.values)
    key.to_csv(CUR / "work" / "clave_modelo.csv", index=False, encoding="utf-8-sig")
    (CUR / "GUIA_REVISION.md").write_text(GUIDE, encoding="utf-8")
    print(out.shape, "-> verificacion_humana_80.csv")


def kappa(a, b) -> float:
    a, b = pd.Series(a).astype(str), pd.Series(b).astype(str)
    cats = sorted(set(a) | set(b))
    po = (a.values == b.values).mean()
    pe = sum((a == c).mean() * (b == c).mean() for c in cats)
    return float("nan") if pe == 1 else (po - pe) / (1 - pe)


def _read(path: str) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str, encoding="utf-8-sig").fillna("")


def agreement(fa: str, fb: str) -> None:
    a, b = _read(fa).set_index("n"), _read(fb).set_index("n")
    both = a.index.intersection(b.index)
    done = [i for i in both if a.loc[i, "pasa_puerta"] != "" and b.loc[i, "pasa_puerta"] != ""]
    if not done:
        print("Las copias aun no estan completas: todas las metricas siguen siendo provisionales.")
        return
    rows = [dict(campo=c, n=len(done), acuerdo=float(np.mean([a.loc[i, c] == b.loc[i, c] for i in done])), kappa=kappa([a.loc[i, c] for i in done], [b.loc[i, c] for i in done])) for c in CATEGORICAL]
    res = pd.DataFrame(rows)
    res.to_csv(CUR / "acuerdo_revisores.csv", index=False)
    print(res.round(3).to_string(index=False))


def vs_model(f: str) -> None:
    h = _read(f).set_index("n")
    k = pd.read_csv(CUR / "work" / "clave_modelo.csv", dtype=str, encoding="utf-8-sig").fillna("").set_index("n")
    done = [i for i in h.index if h.loc[i, "pasa_puerta"] != ""]
    if not done:
        print("La copia aun no esta completa.")
        return
    pairs = {"pasa_puerta": "model_gate", "micrografia_util": "model_micro", "dls_util": "model_dls", "zeta_util": "model_zeta", "pertinente": "model_pertinente"}
    rows = []
    for hc, mc in pairs.items():
        rows.append(dict(campo=hc, n=len(done), acuerdo=float(np.mean([h.loc[i, hc] == k.loc[i, mc] for i in done])), kappa=kappa([h.loc[i, hc] for i in done], [k.loc[i, mc] for i in done])))
    tp = sum(1 for i in done if h.loc[i, "pasa_puerta"] == "si" and k.loc[i, "model_gate"] == "si"); fp = sum(1 for i in done if h.loc[i, "pasa_puerta"] == "no" and k.loc[i, "model_gate"] == "si")
    print(pd.DataFrame(rows).round(3).to_string(index=False))
    print(f"precision de la puerta del modelo (los que el modelo dice que pasan y el humano confirma): {tp}/{tp + fp}")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "make":
        make()
    elif cmd == "agreement":
        agreement(sys.argv[2], sys.argv[3])
    elif cmd == "vs_model":
        vs_model(sys.argv[2])
