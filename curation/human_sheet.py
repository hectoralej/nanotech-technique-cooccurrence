"""hoja_revision_humana.csv (60 articulos, dos revisores) y calculo de acuerdo (kappa) cuando esten completas.

  python -m curation.human_sheet make      -> curation/hoja_revision_humana.csv + GUIA_REVISION.md
  python -m curation.human_sheet agreement -> acuerdo entre revisores y contra el LLM (cuando haya etiquetas)
Los revisores NO ven la salida del LLM ni el tipo de articulo (candidato o casi) en la hoja.
"""
from __future__ import annotations

import sys

import numpy as np
import pandas as pd

from src.common import ROOT

CUR = ROOT / "curation"
FIELDS = ["micrografia_util", "variante_micrografia", "estado_preparacion", "dls_util", "dls_medio", "zeta_util", "zeta_medio",
          "identidad_muestra", "pasa_puerta", "tecnicas_complementarias_sobre_particula", "licencia_color", "notas"]
CATEGORICAL = ["micrografia_util", "variante_micrografia", "estado_preparacion", "dls_util", "dls_medio", "zeta_util", "zeta_medio",
               "identidad_muestra", "pasa_puerta", "licencia_color"]

GUIDE = """# Guía de revisión humana (Bryan y Carlos)

Revisen **de forma independiente** los 60 artículos de `hoja_revision_humana.csv` (no comenten entre ustedes hasta terminar). Abran el artículo con el enlace
(texto completo en Europe PMC) y rellenen **solo** las columnas con sufijo de su revisor (`_r1` o `_r2`). No miren la salida del modelo.

Valores permitidos:

| Columna | Valores |
|---|---|
| `micrografia_util` | `si` / `no`. «Sí» = hay figura de la **partícula del nanoportador** (no un control ni un componente), con técnica identificable y que se puede enlazar a una formulación concreta |
| `variante_micrografia` | `cryoTEM`, `TEM_negstain`, `TEM_posstain`, `TEM_dried_unstained`, `TEM_prep_not_declared`, `HRTEM`, `STEM`, `SEM`, `cryoSEM`, `ESEM`, `ninguna` |
| `estado_preparacion` | `negstain`, `posstain`, `seco_sin_teñir`, `vitrificado`, `recubierto_SEM`, `no_declarado`, `ninguna` |
| `dls_util` | `si` / `no`. «Sí» = valor numérico de tamaño con **medio indicado**, de una muestra identificable |
| `dls_medio` | `agua`, `PBS`, `tampon`, `suero`, `medio_cultivo`, `otro`, `no_declarado`, `sin_dls` |
| `zeta_util` | `si` / `no`. «Sí» = valor numérico con **medio o pH indicado**, de una muestra identificable |
| `zeta_medio` | igual que `dls_medio` (`sin_zeta` si no hay zeta) |
| `identidad_muestra` | de la muestra principal medida: `nanoparticle_loaded`, `nanoparticle_empty`, `pure_component`, `physical_mixture`, `process_intermediate`, `unclear` |
| `pasa_puerta` | `si` solo si `micrografia_util`, `dls_util` y `zeta_util` son `si` |
| `tecnicas_complementarias_sobre_particula` | lista separada por `;` de: `UVVis_intrinseca`, `FTIR`, `XRD`, `EDS`, `DSC`, `TGA`, `Raman`, `NMR`, `XPS`, `NTA`, `SAXS` (solo si se aplican a la **partícula**, no a componentes puros ni a ensayos) |
| `licencia_color` | `verde` (CC BY, CC0), `amarillo` (CC BY-NC, -ND, -SA), `rojo` (otra o sin licencia), según la página del editor |
| `notas` | dudas, casos raros |

Regla: **si dudan, `no` / `no_declarado` / `unclear`**. Cuando terminen: `python -m curation.human_sheet agreement`.
"""


def make() -> None:
    man = pd.read_csv(CUR / "work" / "manifest.csv", dtype={"pmcid": str})
    hs = pd.read_csv(CUR / "data" / "human_set.csv", dtype={"pmcid": str})
    cand = pd.read_csv(CUR / "data" / "candidates.csv", dtype={"pmcid": str})
    allc = pd.read_csv(ROOT / "data" / "articles.csv", dtype={"pmcid": str}, low_memory=False)
    meta = allc.set_index("pmcid")
    df = hs.sample(frac=1, random_state=7).reset_index(drop=True)          # orden aleatorio: no revela el tipo
    out = pd.DataFrame({"pmcid": df.pmcid, "doi": df.pmcid.map(meta["doi"]), "familia": df.primary_family, "titulo": df.title,
                        "enlace": "https://europepmc.org/article/PMC/" + df.pmcid})
    for r in ("r1", "r2"):
        for c in FIELDS:
            out[f"{c}_{r}"] = ""
    out.to_csv(CUR / "hoja_revision_humana.csv", index=False, encoding="utf-8-sig")
    (CUR / "GUIA_REVISION.md").write_text(GUIDE, encoding="utf-8")
    print(out.shape)


def kappa(a, b) -> float:
    a, b = pd.Series(a).astype(str), pd.Series(b).astype(str)
    cats = sorted(set(a) | set(b))
    po = (a.values == b.values).mean()
    pe = sum((a == c).mean() * (b == c).mean() for c in cats)
    return float("nan") if pe == 1 else (po - pe) / (1 - pe)


def agreement() -> None:
    sh = pd.read_csv(CUR / "hoja_revision_humana.csv", dtype=str).fillna("")
    done = sh[(sh["pasa_puerta_r1"] != "") & (sh["pasa_puerta_r2"] != "")]
    if done.empty:
        print("La hoja aun no esta completada por los dos revisores: todas las metricas siguen siendo provisionales.")
        return
    rows = []
    for c in CATEGORICAL:
        a, b = done[f"{c}_r1"], done[f"{c}_r2"]
        rows.append(dict(campo=c, n=len(done), acuerdo=(a == b).mean(), kappa=kappa(a, b)))
    res = pd.DataFrame(rows)
    res.to_csv(CUR / "acuerdo_revisores.csv", index=False)
    print(res.round(3).to_string(index=False))


if __name__ == "__main__":
    {"make": make, "agreement": agreement}[sys.argv[1]]()
