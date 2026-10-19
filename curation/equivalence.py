"""Grupos de equivalencia de mediciones (brief 5.2): clave estricta calculada por codigo, nunca por el modelo.

Dos mediciones son del mismo grupo solo si coinciden en tecnica, variante, magnitud, clase de identidad de la muestra y en las condiciones que cambian su
interpretacion. Una condicion no declarada vale 'nd' y SEPARA el grupo (no se asume que coincida con otra). Si hay duda, se separa.
"""
from __future__ import annotations

import re

MICRO_VARIANTS = {"cryoTEM", "TEM_negstain", "TEM_posstain", "TEM_dried_unstained", "TEM_prep_not_declared", "HRTEM", "STEM", "SEM", "cryoSEM", "ESEM"}
USEFUL_IDENTITY = {"nanoparticle_loaded", "nanoparticle_empty"}
MEDIA = {"water", "agua", "pbs", "buffer", "tampon", "serum", "suero", "culture_medium"}


def _num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def medium_class(v) -> str:
    if v is None:
        return "nd"
    s = str(v).strip().lower()
    if s in ("", "not_declared", "no_declarado", "null", "none", "nd", "unspecified"):
        return "nd"
    if s in ("agua", "water", "ultrapure water", "deionized water", "milli-q water", "distilled water") or re.fullmatch(r"(milli-?q|di|deionized|distilled|ultrapure)\s*water", s):
        return "water"
    if "pbs" in s or "phosphate" in s and "saline" in s:
        return "pbs"
    if s in ("tampon", "buffer") or any(k in s for k in ("hepes", "tris", "citrate", "acetate", "mes ", "buffer", "nacl", "kcl", "saline")):
        return "buffer:" + re.sub(r"[^a-z0-9]+", "", s)[:20]
    if "serum" in s or "suero" in s or "fbs" in s or "plasma" in s:
        return "serum"
    if "medium" in s or "dmem" in s or "rpmi" in s or "culture" in s:
        return "culture_medium"
    return "other:" + re.sub(r"[^a-z0-9]+", "", s)[:20]


def _bucket(x, step=1.0):
    n = _num(x)
    return "nd" if n is None else str(round(n / step) * step if step != 1 else round(n))


def identity_of(m: dict, samples: dict) -> str:
    s = samples.get(m.get("sample_id"), {})
    return s.get("identity") or "unclear"


def equivalence_group(m: dict, samples: dict) -> str:
    t = m.get("technique", "?")
    v = (m.get("variant") or "nd").strip()
    ident = identity_of(m, samples)
    c = m.get("conditions") or {}
    meas = re.sub(r"[^a-z0-9]+", "_", (m.get("measurand") or "nd").lower())[:30]
    if t == "micrograph":
        scale = {True: "scale", False: "noscale"}.get(c.get("scale_bar_present"), "scale_nd")
        vals = m.get("values") or {}
        sized = "sized_n" if _num(vals.get("n_particles_measured")) else ("sized" if _num(vals.get("size_nm")) else "nosize")
        return f"micrograph|{v}|{ident}|{scale}|{sized}"
    if t == "DLS":
        return f"DLS|{v}|{meas}|{ident}|med:{medium_class(c.get('medium'))}|T:{_bucket(c.get('temperature_C'))}|ang:{_bucket(c.get('angle_deg'))}|dil:{re.sub(r'[^a-z0-9:]+', '', str(c.get('dilution') or 'nd').lower())[:16]}"
    if t == "zeta":
        return (f"zeta|{v}|{ident}|med:{medium_class(c.get('medium'))}|pH:{_bucket(c.get('pH'), 0.5)}|I:{re.sub(r'[^a-z0-9.]+', '', str(c.get('ionic_strength') or 'nd').lower())[:12]}"
                f"|model:{(c.get('model') or 'nd')}")
    if t == "UVVis":
        return f"UVVis|{v}|{ident}"
    if t == "FTIR":
        return f"FTIR|{v}|{ident}|state:{(c.get('sample_state') or 'nd')}"
    if t == "XRD":
        return f"XRD|{v}|{ident}|rad:{(c.get('radiation') or 'nd')}"
    if t == "EDS":
        return f"EDS|{v}|{ident}"
    return f"{t}|{v}|{ident}"


def shown_class(m: dict) -> str:
    return m.get("shown_as") or "nd"


def is_micro_useful(m: dict, samples: dict) -> bool:
    return (m.get("technique") == "micrograph" and (m.get("variant") in MICRO_VARIANTS) and shown_class(m) in ("figure_panel", "raw_curve")
            and identity_of(m, samples) in USEFUL_IDENTITY and ((m.get("formulation_link") or {}).get("confidence") in ("explicit", "inferred")))


def is_dls_useful(m: dict, samples: dict) -> tuple[bool, bool]:
    """(util, dudoso): util = valor numerico + medio declarado + muestra identificable; dudoso = valor pero medio no declarado."""
    if m.get("technique") != "DLS" or identity_of(m, samples) not in USEFUL_IDENTITY:
        return False, False
    has_val = _num((m.get("values") or {}).get("size_nm")) is not None
    med = medium_class((m.get("conditions") or {}).get("medium")) != "nd"
    return (has_val and med), (has_val and not med)


def is_zeta_useful(m: dict, samples: dict) -> tuple[bool, bool]:
    if m.get("technique") != "zeta" or identity_of(m, samples) not in USEFUL_IDENTITY:
        return False, False
    c = m.get("conditions") or {}
    has_val = _num((m.get("values") or {}).get("zeta_mV")) is not None
    med = medium_class(c.get("medium")) != "nd" or _num(c.get("pH")) is not None
    return (has_val and med), (has_val and not med)


def gate(rec: dict) -> dict:
    """Puerta derivada por codigo de los campos de UNA pasada (o del registro final)."""
    samples = {s["id"]: s for s in rec.get("samples", []) or []}
    ms = rec.get("measurements", []) or []
    ctx = rec.get("context", {}) or {}
    micro = any(is_micro_useful(m, samples) for m in ms)
    dls_u = any(is_dls_useful(m, samples)[0] for m in ms)
    dls_d = any(is_dls_useful(m, samples)[1] for m in ms)
    z_u = any(is_zeta_useful(m, samples)[0] for m in ms)
    z_d = any(is_zeta_useful(m, samples)[1] for m in ms)
    research = ctx.get("article_kind") == "research"
    obj = bool(ctx.get("nanocarrier_is_object_of_study"))
    viral = bool(ctx.get("depends_on_pcr_or_virus")) or ctx.get("carrier_type") == "virus_or_VLP"
    return dict(micro=micro, dls=dls_u, dls_dudoso=dls_d and not dls_u, zeta=z_u, zeta_dudoso=z_d and not z_u, research=research, object=obj, viral_pcr=viral,
                gate=bool(micro and dls_u and z_u and research and obj and not viral))


RULES = {
    "micrograph": "variante + clase de identidad + escala presente + tamano medido (con n o sin n); el estado de preparacion esta en la variante",
    "DLS": "variante (z_average|intensity|number|volume|unspecified) + magnitud + identidad + medio + temperatura + angulo + dilucion; 'nd' separa",
    "zeta": "metodo (ELS|PALS|unspecified) + identidad + medio + pH (0.5) + fuerza ionica + modelo; 'nd' separa",
    "UVVis": "variante (a intrinseca | b cuantificacion | c ensayo | d turbidez) + identidad",
    "FTIR": "variante (ATR|KBr|transmision) + identidad + estado de la muestra",
    "XRD": "variante + identidad + radiacion",
    "EDS": "variante (SEM|TEM|independiente) + identidad",
    "otras": "tecnica + variante + identidad",
}
