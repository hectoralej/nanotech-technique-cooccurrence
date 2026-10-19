"""Comprobacion determinista: ¿el texto completo menciona un medio cerca de DLS/zeta en articulos donde el LLM dijo 'no declarado'?

Se usa para no perder articulos por un paquete recortado o por un falso 'no_declarado'. Un hallazgo NO cambia la puerta por si solo: va a arbitraje
(frase citada) y solo se acepta si el arbitro confirma que el medio corresponde a esa medicion.
"""
from __future__ import annotations

import re

from curation import textprep

MEASURE = re.compile(r"zeta|zetasizer|dynamic light|\bDLS\b|hydrodynamic|particle size|z-average|laser doppler|\bPCS\b|photon correlation", re.I)
MEDIUM = re.compile(r"\b(?:deionized|deionised|distilled|ultrapure|milli-?q|purified)?\s*water\b|\bPBS\b|phosphate[- ]buffered|saline|\bHEPES\b|\bTris\b|\bKCl\b|\bNaCl\b|"
                    r"\bserum\b|\bFBS\b|culture medium|\bDMEM\b|\bRPMI\b|citrate buffer|acetate buffer|\bbuffer\b|\bpH\s*\d", re.I)
SENT = re.compile(r"(?<=[.!?])\s+(?=[A-Z(\[])")


def medium_sentences(pmcid: str, limit: int = 4) -> list[str]:
    d = textprep.article_text(pmcid)
    paras = [p for _, p in d["methods"] + d["results"] + d["other"]] + [c for _, c in d["figures"]] + [f"{cap} {foot}" for _, cap, _, foot in d["tables"]]
    out = []
    for p in paras:
        for s in SENT.split(p):
            if MEASURE.search(s) and MEDIUM.search(s):
                out.append(s.strip()[:300])
                if len(out) >= limit:
                    return out
    return out
