"""Detector de tecnicas por diccionarios, aplicado por seccion (Metodos / Resultados / pie de figura / otras).

Entrada: dict de secciones {"methods", "results", "caption", "intro", "discussion", "conclusion", "other",
         "abstract"} -> texto. Salida: por tecnica, banderas por seccion + evidencia (<= 25 palabras).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from functools import lru_cache

from .common import load_yaml

SECTION_ORDER = ["methods", "results", "caption", "other", "abstract"]
# prioridad para escoger el fragmento de evidencia
EVIDENCE_PRIORITY = ["results", "caption", "methods", "other", "abstract"]
CONTEXT_CHARS = 80
NOT_NEAR_BEFORE, NOT_NEAR_AFTER = 40, 25
MAX_EVIDENCE_WORDS = 25


@dataclass
class Pattern:
    mode: str
    rx: re.Pattern
    ctx: re.Pattern | None = None
    not_near: re.Pattern | None = None
    only_in: frozenset[str] | None = None     # p. ej. magnitudes derivadas que solo valen en Resultados/pies


@dataclass
class Technique:
    name: str
    tier: str
    category: str
    mask: bool
    patterns: list[Pattern]
    subflags: dict[str, re.Pattern] = field(default_factory=dict)


@lru_cache(maxsize=1)
def load_techniques() -> tuple[list[re.Pattern], list[Technique]]:
    cfg = load_yaml("techniques.yaml")
    premask = [re.compile(p, re.I) for p in cfg.get("premask", [])]
    techs = []
    for name, t in cfg["techniques"].items():
        pats = []
        for p in t["patterns"]:
            pats.append(Pattern(
                mode=p["mode"],
                rx=re.compile(p["re"], re.I),
                ctx=re.compile(p["ctx"], re.I) if p.get("ctx") else None,
                not_near=re.compile(p["not_near"], re.I) if p.get("not_near") else None,
                only_in=frozenset(p["only_in"]) if p.get("only_in") else None,
            ))
        techs.append(Technique(
            name=name, tier=t["tier"], category=t["category"], mask=bool(t.get("mask", False)), patterns=pats,
            subflags={k: re.compile(v, re.I) for k, v in (t.get("subflags") or {}).items()},
        ))
    return premask, techs


def technique_names(tier: str | None = None) -> list[str]:
    return [t.name for t in load_techniques()[1] if tier is None or t.tier == tier]


_DASHES = dict.fromkeys(map(ord, "‐‑‒–—―−­"), "-")


def normalize(text: str) -> str:
    """Unifica guiones Unicode (p. ej. 'UV‐Vis', 'cryo‑TEM') a '-'; conserva la longitud (offsets validos)."""
    return text.translate(_DASHES)


def _blank(text: str, spans: list[tuple[int, int]]) -> str:
    if not spans:
        return text
    chars = list(text)
    for a, b in spans:
        chars[a:b] = " " * (b - a)
    return "".join(chars)


def evidence_snippet(text: str, start: int, end: int) -> str:
    """Fragmento de <= 25 palabras centrado en la coincidencia."""
    left = text[:start].split()
    mid = text[start:end].split()
    right = text[end:].split()
    budget = MAX_EVIDENCE_WORDS - len(mid)
    if budget < 0:
        return " ".join(mid[:MAX_EVIDENCE_WORDS])
    lb = min(len(left), budget // 2)
    rb = min(len(right), budget - lb)
    lb = min(len(left), budget - rb)
    words = (left[-lb:] if lb else []) + mid + right[:rb]
    return " ".join(words)


def _accept(p: Pattern, text: str, m: re.Match, has_strong: bool) -> bool:
    if p.not_near is not None:
        win = text[max(0, m.start() - NOT_NEAR_BEFORE): m.end() + NOT_NEAR_AFTER]
        if p.not_near.search(win):
            return False
    if p.mode == "strong":
        return True
    if p.mode == "weak" and has_strong:
        return True
    if p.ctx is None:
        return False
    # el contexto excluye la propia coincidencia para no auto-satisfacerse
    before = text[max(0, m.start() - CONTEXT_CHARS): m.start()]
    after = text[m.end(): m.end() + CONTEXT_CHARS]
    return bool(p.ctx.search(before + " | " + after))


def detect(sections: dict[str, str]) -> dict[str, dict]:
    """sections: claves en SECTION_ORDER + intro/discussion/conclusion (se funden en 'other')."""
    premask, techs = load_techniques()
    work: dict[str, str] = {}
    orig: dict[str, str] = {}
    merged = dict(sections)
    other = " \n ".join(merged.get(k, "") or "" for k in ("other", "intro", "discussion", "conclusion"))
    for k in ("methods", "results", "caption", "abstract"):
        orig[k] = normalize(merged.get(k, "") or "")
    orig["other"] = normalize(other)
    for k, txt in orig.items():
        spans = [(m.start(), m.end()) for rx in premask for m in rx.finditer(txt)]
        work[k] = _blank(txt, spans)

    out: dict[str, dict] = {}
    for t in techs:
        # primera pasada: coincidencias candidatas por patron y seccion; has_strong a nivel de articulo
        cands: list[tuple[str, Pattern, re.Match]] = []
        has_strong = False
        for sec, txt in work.items():
            if not txt:
                continue
            for p in t.patterns:
                if p.only_in is not None and sec not in p.only_in:
                    continue
                for m in p.rx.finditer(txt):
                    cands.append((sec, p, m))
                    if p.mode == "strong" and (p.not_near is None or not p.not_near.search(
                            txt[max(0, m.start() - NOT_NEAR_BEFORE): m.end() + NOT_NEAR_AFTER])):
                        has_strong = True
        rec = {s: False for s in SECTION_ORDER}
        rec.update(n_mentions=0, evidence="", evidence_section="")
        best_rank = len(EVIDENCE_PRIORITY)
        mask_spans: dict[str, list[tuple[int, int]]] = {k: [] for k in work}
        for sec, p, m in cands:
            txt = work[sec]
            if not _accept(p, txt, m, has_strong):
                continue
            rec[sec] = True
            rec["n_mentions"] += 1
            rank = EVIDENCE_PRIORITY.index(sec)
            if rank < best_rank:
                best_rank = rank
                rec["evidence"] = evidence_snippet(orig[sec], m.start(), m.end())
                rec["evidence_section"] = sec
            if t.mask and p.mode == "strong":
                mask_spans[sec].append((m.start(), m.end()))
        # subbanderas: solo si la tecnica fue detectada en alguna seccion del cuerpo
        detected_body = any(rec[s] for s in ("methods", "results", "caption", "other"))
        rec["subflags"] = {}
        for sub, rx in t.subflags.items():
            rec["subflags"][sub] = bool(detected_body and any(rx.search(work[s]) for s in ("methods", "results", "caption", "other")))
        out[t.name] = rec
        if t.mask:
            for sec, spans in mask_spans.items():
                work[sec] = _blank(work[sec], spans)
    # subbandera de tincion: solo informativa si hay TEM o cryoEM; ya depende de detected_body del padre
    return out


# ----------------------------------------------------------------------------------------------
# Definiciones de "tecnica reportada" (brief 4.4)
# ----------------------------------------------------------------------------------------------

def definition(rec: dict, which: str = "primary") -> bool:
    m, r, c, o = rec["methods"], rec["results"], rec["caption"], rec["other"]
    if which == "primary":
        return bool(m and (r or c))
    if which == "body_any":            # usada o mostrada al menos una vez en Metodos/Resultados/pies (sin Intro/Discusion)
        return bool(m or r or c)
    if which == "methods_only":
        return bool(m)
    if which == "any":
        return bool(m or r or c or o or rec["abstract"])
    if which == "caption_only":
        return bool(c)
    raise ValueError(which)


DEFINITIONS = ["primary", "body_any", "methods_only", "any", "caption_only"]
