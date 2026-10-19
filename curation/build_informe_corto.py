"""Genera curation/INFORME_CORTO.html (autocontenido): metodologia (diagrama), resultados de la ampliacion a 63 articulos y siguientes pasos."""
from __future__ import annotations

import base64

from src.common import ROOT

CUR = ROOT / "curation"


def b64(p):
    return base64.b64encode(p.read_bytes()).decode()


def box(x, y, w, h, title, sub, kind):
    fill, edge = {"code": ("#eef2f8", "#2a62c9"), "haiku": ("#fff1e8", "#eb6834"), "sonnet": ("#fde3d3", "#b4501f"), "ok": ("#e7f6ef", "#1baf7a"), "plain": ("#ffffff", "#9aa3b2")}[kind]
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" fill="{fill}" stroke="{edge}" stroke-width="2"/>'
            f'<text x="{x + 14}" y="{y + 28}" font-size="14" font-weight="600" fill="#14181f">{title}</text>'
            f'<text x="{x + 14}" y="{y + 50}" font-size="12.5" fill="#4a5260">{sub}</text>')


def arrow(x1, x2, y, label):
    return (f'<path d="M{x1},{y} L{x2 - 4},{y}" stroke="#7b8494" stroke-width="2.2" fill="none" marker-end="url(#ar)"/>'
            f'<text x="{(x1 + x2) / 2}" y="{y - 8}" text-anchor="middle" font-size="12" fill="#4a5260">{label}</text>')


def svg() -> str:
    p = ['<svg viewBox="0 0 1000 452" role="img" aria-label="Ruta de lectura de la ampliación: filtro por código, y dos rutas con Haiku y Sonnet que terminan en 63 artículos" xmlns="http://www.w3.org/2000/svg" font-family="IBM Plex Sans, Segoe UI, system-ui, sans-serif">',
         '<defs><marker id="ar" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7b8494"/></marker></defs>',
         '<rect width="1000" height="452" fill="#fcfcfb"/>']
    # fila 1: filtro por codigo
    p.append(box(20, 24, 200, 70, "766 candidatos", "ya descargados y sin AAV", "plain"))
    p.append(arrow(222, 288, 59, "código"))
    p.append(box(290, 24, 400, 70, "Filtro barato · 0 tokens", "tabla con tamaño y zeta · medio junto a DLS y zeta", "code"))
    p.append(arrow(692, 758, 59, "elige"))
    p.append(box(760, 24, 220, 70, "Nivel A: 143 artículos", "83 % aprobó en el piloto", "code"))
    # ronda 1
    p.append('<text x="20" y="130" font-size="13" font-weight="600" fill="#b4501f">RONDA 1 · Haiku primero (44 artículos)</text>')
    p.append(box(20, 142, 190, 70, "Haiku · extracto", "frases clave, figuras, tablas", "haiku"))
    p.append(arrow(212, 298, 177, "33 pasan o casi"))
    p.append(box(300, 142, 190, 70, "Sonnet · completo", "33 artículos", "sonnet"))
    p.append(arrow(492, 578, 177, "12 en duda"))
    p.append(box(580, 142, 190, 70, "Sonnet arbitra", "cita literal obligatoria", "sonnet"))
    p.append(arrow(772, 828, 177, ""))
    p.append(box(830, 142, 150, 70, "21 entran", "48 % de 44", "ok"))
    # ronda 2
    p.append('<text x="20" y="246" font-size="13" font-weight="600" fill="#b4501f">RONDA 2 · Sonnet primero (31 artículos)</text>')
    p.append(box(20, 258, 190, 70, "Sonnet · completo", "31 artículos", "sonnet"))
    p.append(arrow(212, 298, 293, "18 aprobados"))
    p.append(box(300, 258, 190, 70, "Haiku · extracto", "segunda lectura barata", "haiku"))
    p.append(arrow(492, 578, 293, "5 en duda"))
    p.append(box(580, 258, 190, 70, "Sonnet arbitra", "cita literal obligatoria", "sonnet"))
    p.append(arrow(772, 828, 293, ""))
    p.append(box(830, 258, 150, 70, "16 entran", "52 % de 31", "ok"))
    # cierre
    p.append('<path d="M905,330 L905,362" stroke="#7b8494" stroke-width="2.2" fill="none" marker-end="url(#ar)"/>')
    p.append(box(20, 366, 740, 70, "Código y auditoría · en cada artículo", "citas literales · puerta · puntaje · misma muestra · licencia · Claude revisa (3 excluidos)", "code"))
    p.append(box(780, 366, 200, 70, "63 en total", "26 piloto + 21 + 16", "ok"))
    p.append('<path d="M762,401 L778,401" stroke="#7b8494" stroke-width="2.2" fill="none" marker-end="url(#ar)"/>')
    p.append("</svg>")
    return "".join(p)


CSS = """
:root{--bg:#f6f7f9;--surface:#ffffff;--ink:#14181f;--ink2:#4a5260;--muted:#6b7485;--line:#dfe3ea;--accent:#2a62c9;--warn:#b4501f;--warn-soft:#fbeee6;--plate:#fcfcfb}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#0f1218;--surface:#171b23;--ink:#eef1f6;--ink2:#b4bccb;--muted:#8791a3;--line:#2a313d;--accent:#7aa6f0;--warn:#f0a070;--warn-soft:#2d2018;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#0f1218;--surface:#171b23;--ink:#eef1f6;--ink2:#b4bccb;--muted:#8791a3;--line:#2a313d;--accent:#7aa6f0;--warn:#f0a070;--warn-soft:#2d2018;color-scheme:dark}
body{background:var(--bg);color:var(--ink);font-family:"IBM Plex Sans",system-ui,-apple-system,"Segoe UI",sans-serif;font-size:16px;line-height:1.55}
.wrap{max-width:980px;margin-inline:auto;padding-inline:20px;padding-block:28px 56px;display:flex;flex-direction:column;gap:34px}
h1{font-size:clamp(1.5rem,3.4vw,2.05rem);line-height:1.2;margin:0;text-wrap:balance;font-weight:600}
h2{font-size:1.1rem;margin:0 0 12px;font-weight:600}
p{margin:0}.lede{color:var(--ink2);margin-top:10px;max-width:70ch}
.kicker{font:500 .78rem/1 "IBM Plex Mono",ui-monospace,monospace;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin-bottom:12px}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,200px),1fr));gap:12px}
.tile{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:14px 16px}
.tile b{display:block;font-size:1.7rem;font-weight:600;line-height:1.1;font-variant-numeric:tabular-nums}
.tile span{color:var(--ink2);font-size:.9rem}
.plate{background:var(--plate);border:1px solid var(--line);border-radius:10px;padding:8px;overflow-x:auto}
.plate svg{display:block;width:100%;height:auto;min-width:720px}.plate img{display:block;width:100%;height:auto}
figure{margin:0}figcaption{color:var(--ink2);font-size:.92rem;margin-top:8px;max-width:80ch}
.two{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,430px),1fr));gap:20px}
ul.f{margin:0;padding-left:1.1rem;display:grid;gap:8px}ul.f li{max-width:78ch}
ol.n{margin:0;padding:0;list-style:none;display:grid;counter-reset:n}
ol.n li{counter-increment:n;display:grid;grid-template-columns:2rem minmax(0,1fr);gap:4px 12px;padding:10px 0;border-top:1px solid var(--line)}
ol.n li:first-child{border-top:none}
ol.n li::before{content:counter(n);font:600 .9rem "IBM Plex Mono",monospace;color:var(--accent)}
.who{color:var(--muted);font-size:.85rem}
.caution{background:var(--warn-soft);border:1px solid var(--line);border-radius:10px;padding:14px 18px}
.caution h2{color:var(--warn)}.caution ul{margin:0;padding-left:1.1rem;display:grid;gap:6px}
.note{font-size:.88rem;color:var(--muted)}
"""


def main() -> None:
    emb = b64(CUR / "grafico_embudo.png")
    rend = b64(CUR / "grafico_rendimiento_por_ronda.png")
    niv = b64(CUR / "grafico_niveles_por_familia.png")
    page = f"""<title>Curación de calidad</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@500&family=IBM+Plex+Sans:wght@400;600&display=swap">
<style>{CSS}</style>
<main class="wrap">
<header><div class="kicker">Fase 2 · corpus de nanoportadores · resultados provisionales</div>
<h1>El repositorio curado pasó de 26 a 63 artículos con micrografía, DLS y zeta confiables</h1>
<p class="lede">Se leyeron 75 artículos más con un filtro por código y agentes Haiku y Sonnet. Cada dato lleva una cita literal que el código encontró en el texto. Falta la revisión humana, así que las cifras son provisionales.</p></header>

<section class="tiles" aria-label="Cifras clave">
<div class="tile"><b>63</b><span>artículos en el repositorio (S 8 · A 48 · B 7)</span></div>
<div class="tile"><b>175</b><span>artículos leídos con modelos, de 766 candidatos</span></div>
<div class="tile"><b>≈ 110 mil</b><span>tokens por artículo nuevo en el repositorio, contra ≈ 250 mil en el piloto</span></div>
<div class="tile"><b>2</b><span>artículos de nanopartículas inorgánicas: el vacío más claro</span></div>
</section>

<section><h2>Cómo se hizo</h2>
<figure><div class="plate">{svg()}</div>
<figcaption>Lo que cambió entre las rondas: en la 1, Haiku leía primero y dejó fuera a 8 de los 23 artículos que Sonnet aprobó (recall 65 %). En la 2, Sonnet lee primero y Haiku solo confirma a los aprobados. Naranja claro: Haiku. Naranja oscuro: Sonnet. Azul: código.</figcaption></figure>
<ul class="f" style="margin-top:14px">
<li><b>Puerta obligatoria:</b> micrografía útil (TEM, variantes o SEM), DLS útil y zeta útil de una misma muestra. «Útil» exige valor numérico con el medio declarado.</li>
<li><b>Sin evidencia no hay dato:</b> si la cita literal de un campo no aparece en el artículo, el código lo anula (menos del 1 % de las citas).</li>
<li><b>Puntuación determinista (0–100):</b> niveles S ≥ 85, A 70–84, B 60–69, fijados en <code>SCORING.md</code> antes de ver resultados.</li>
</ul></section>

<section><h2>Resultados</h2>
<div class="two">
<figure><div class="plate"><img alt="Embudo de los 175 artículos extraídos" src="data:image/png;base64,{emb}"></div><figcaption>El DLS con medio declarado sigue siendo el filtro que más descarta: de 153 artículos con micrografía útil, solo 85 lo cumplen.</figcaption></figure>
<figure><div class="plate"><img alt="Rendimiento por grupo" src="data:image/png;base64,{rend}"></div><figcaption>Elegir antes con el filtro barato casi duplica el porcentaje que llega al repositorio. El piloto, elegido al azar, describe mejor a los 766 candidatos.</figcaption></figure>
</div>
<ul class="f" style="margin-top:16px">
<li><b>Familias:</b> SLN/NLC 15, LNP 14, PLN 13, polímeros 11, liposomas 8, inorgánicas 2.</li>
<li><b>Micrografía:</b> TEM 40 artículos, SEM 19 (30 %), cryo 4. La tinción negativa es la preparación más frecuente.</li>
<li><b>Auditoría:</b> excluí 3 artículos a mano (nanomateriales comerciales que no son nanoportadores y un valor de DLS de 1,1 nm sacado de una frase de tendencia) y agregué una regla por código: la micrografía, el DLS y el zeta deben ser de una misma muestra. Bryan y Carlos pueden revertir mis exclusiones.</li>
<li><b>Licencias:</b> 43 verdes y 20 en conflicto (Europe PMC dice CC BY, el XML o el editor dicen CC BY-NC o -ND). Los conflictos no cuentan como verdes. 0 DOI sin resolver.</li>
<li><b>Casi-aprobados:</b> 89 artículos en <code>near_miss.csv</code>, sobre todo por DLS o zeta sin medio declarado.</li>
</ul></section>

<section class="caution"><h2>Límites</h2><ul>
<li>No hay revisión humana todavía. Mi auditoría revisó los 63 uno por uno, pero no es independiente de los modelos.</li>
<li>Las rondas 1 y 2 no tienen dos lecturas completas independientes en todos los casos: unos pasaron por un extracto corto de Haiku y otros por una sola lectura de Sonnet. Los desacuerdos de la puerta sí se arbitraron.</li>
<li>No se descargó el material suplementario (57 % de los candidatos lo tiene): el repositorio probablemente está subestimado.</li>
<li>Solo se usaron artículos ya descargados. No se buscaron artículos nuevos.</li>
</ul></section>

<section><h2>Siguientes pasos</h2>
<ol class="n">
<li><div><b>Revisión humana</b> de <code>hoja_revision_humana.csv</code> (60 artículos) y de los 3 que excluí a mano. Certifica los umbrales (puerta ≥ 0,95; kappa ≥ 0,80; licencia 100 %).<div class="who">Bryan y Carlos</div></div></li>
<li><div><b>Resolver los 20 conflictos de licencia</b> antes de redistribuir figuras de esos artículos.<div class="who">Bryan y Carlos</div></div></li>
<li><div><b>Búsqueda dirigida de los vacíos:</b> inorgánicas (2 artículos) y SAXS (7 mediciones en 3 artículos). Con los artículos ya descargados no se pueden llenar.<div class="who">Decisión tuya: ¿la inicio?</div></div></li>
<li><div><b>Seguir ampliando</b> con los 591 candidatos sin leer, con el mismo método. El costo por artículo bajó a la mitad respecto al piloto.<div class="who">Decisión tuya: ¿hasta cuántos?</div></div></li>
</ol></section>

<p class="note">Archivos en <code>curation/</code>: <code>INFORME.md</code>, <code>articles_curated_nuevo.csv</code> (renombrar a <code>articles_curated.csv</code> al cerrar Excel), <code>measurements.csv</code>, <code>near_miss.csv</code>, <code>Repositorio_articulos.docx</code>, <code>manual_review.csv</code>, <code>ESTADO.md</code>.</p>
</main>"""
    (CUR / "INFORME_CORTO.html").write_text('<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1">\n' + page, encoding="utf-8")
    print("ok", (CUR / "INFORME_CORTO.html").stat().st_size // 1024, "KB")


if __name__ == "__main__":
    main()
