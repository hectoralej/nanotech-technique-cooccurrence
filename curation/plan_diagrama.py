"""Diagrama simple del plan de ampliacion del repositorio curado (26 -> 50-60)."""
from __future__ import annotations

import textwrap

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

from src.common import ROOT

BG, INK, MUTED, LINE = "#fcfcfb", "#14181f", "#5b6472", "#d8dce3"
COST = {  # (relleno, borde, etiqueta)
    "code": ("#eef2f8", "#2a62c9", "CÓDIGO · 0 tokens"),
    "haiku": ("#fff1e8", "#eb6834", "HAIKU · en lotes"),
    "sonnet": ("#fde3d3", "#b4501f", "SONNET · solo pocos"),
    "me": ("#e7f6ef", "#1baf7a", "YO · Claude principal"),
}
STEPS = [
    ("1", "Reservorio", "code", "666 candidatos ya leídos y sin procesar. Artículos nuevos solo para tapar un vacío (SAXS, inorgánicos)."),
    ("2", "Filtro barato", "code", "Título, tipo de artículo y palabras clave en el texto ya descargado: DLS, zeta, TEM/SEM y su medio. Descarta sin gastar tokens."),
    ("3", "Primera prueba", "haiku", "Agentes leen solo las frases con palabras clave, no el artículo completo. ¿Pasa micrografía + DLS + zeta con medio?"),
    ("4", "Prueba estricta", "sonnet", "Solo los que pasaron. Cita literal por cada dato; Sonnet decide los casos dudosos."),
    ("5", "Puerta y base", "code", "El código verifica las citas, puntúa, revisa licencia y duplicados. Si cumple, entra a la base."),
    ("6", "Mi revisión", "me", "Reviso lo que los agentes agregaron: muestreo contra el texto original y corrijo errores."),
]


def main() -> None:
    fig, ax = plt.subplots(figsize=(19, 7.6), dpi=130)
    fig.patch.set_facecolor(BG)
    ax.set_xlim(0, 19)
    ax.set_ylim(0, 7.6)
    ax.axis("off")

    ax.text(0.4, 7.1, "Plan: ampliar el repositorio curado, del filtro más barato al más caro", fontsize=19, fontweight="bold", color=INK, va="center")
    ax.text(0.4, 6.6, "Cada paso descarta artículos antes de que el siguiente gaste más. Se repite por lotes hasta llegar a la meta.", fontsize=12.5, color=MUTED, va="center")

    w, h, gap, x0, y0 = 2.7, 3.7, 0.4, 0.4, 2.2
    for i, (n, title, kind, body) in enumerate(STEPS):
        x = x0 + i * (w + gap)
        fill, edge, label = COST[kind]
        ax.add_patch(FancyBboxPatch((x, y0), w, h, boxstyle="round,pad=0.02,rounding_size=0.15", fc=fill, ec=edge, lw=2))
        ax.add_patch(plt.Circle((x + 0.38, y0 + h - 0.42), 0.24, fc=edge, ec="none"))
        ax.text(x + 0.38, y0 + h - 0.43, n, ha="center", va="center", fontsize=12, fontweight="bold", color="white")
        ax.text(x + 0.78, y0 + h - 0.43, title, ha="left", va="center", fontsize=14, fontweight="bold", color=INK)
        ax.text(x + 0.2, y0 + h - 1.05, "\n".join(textwrap.wrap(body, 23)), ha="left", va="top", fontsize=10.2, color=INK, linespacing=1.4)
        ax.text(x + 0.2, y0 + 0.28, label, ha="left", va="center", fontsize=9.6, fontweight="bold", color=edge)
        if i < len(STEPS) - 1:
            ax.add_patch(FancyArrowPatch((x + w + 0.03, y0 + h / 2), (x + w + gap - 0.03, y0 + h / 2), arrowstyle="-|>", mutation_scale=18, color=MUTED, lw=2))

    # bucle de repeticion
    xl, xr = x0 + w / 2, x0 + 5 * (w + gap) + w / 2
    yb = 1.75
    ax.plot([xr, xr], [y0, yb], color=MUTED, lw=2)
    ax.plot([xr, xl], [yb, yb], color=MUTED, lw=2)
    ax.add_patch(FancyArrowPatch((xl, yb), (xl, y0 - 0.03), arrowstyle="-|>", mutation_scale=18, color=MUTED, lw=2))
    ax.text((xl + xr) / 2, yb + 0.22, "Siguiente lote de ~40 artículos, hasta llegar a la meta", ha="center", va="center", fontsize=11.5, color=MUTED, style="italic",
            bbox=dict(fc=BG, ec="none", pad=3))

    # meta
    ax.add_patch(FancyBboxPatch((0.4, 0.2), 18.2, 1.0, boxstyle="round,pad=0.02,rounding_size=0.15", fc="#ffffff", ec=LINE, lw=1.5))
    ax.text(0.8, 0.7, "Meta de referencia", fontsize=12.5, fontweight="bold", color=INK, va="center")
    ax.text(3.6, 0.7, "26 curados hoy  →  50–60", fontsize=15, fontweight="bold", color="#1baf7a", va="center")
    ax.text(9.2, 0.7, "Al llegar, me detengo y reporto. Si el rendimiento cae mucho, aviso antes de gastar más.", fontsize=11.5, color=MUTED, va="center")

    out = ROOT / "curation" / "plan_diagrama.png"
    fig.savefig(out, facecolor=BG)
    print(out)


if __name__ == "__main__":
    main()
