"""Genera entrega/REPORTE_SIMPLE.md y entrega/resumen.html (pagina autonoma: hallazgos, 4 figuras y diagrama)."""
from __future__ import annotations

import base64
import html
import re
import shutil

import pandas as pd

from .common import DATA, ROOT
from .data import load_articles

OUT = ROOT / "entrega"
CORE = ["LNP", "liposome", "SLN_NLC", "PLN", "polymeric"]
NAMES = {"LNP": "LNP", "liposome": "Liposomas", "SLN_NLC": "SLN/NLC", "PLN": "PLN", "polymeric": "Poliméricas", "inorganic": "Inorgánicas"}
SPECTRA = ["UVVis", "FTIR", "XRD", "NMR", "EDS", "SAXS", "Raman_SERS", "XPS"]


def nfmt(n):
    return f"{n:,}".replace(",", ".")


def dec(x, d=2):
    return f"{x:.{d}f}".replace(".", ",")


def b64(path):
    return base64.b64encode(path.read_bytes()).decode()


def facts():
    prev = pd.read_csv(DATA / "prevalence.csv")
    pairs = pd.read_csv(DATA / "pairs.csv")
    em = pd.read_csv(DATA / "em_row.csv")
    strata = pd.read_csv(DATA / "ids" / "strata_counts.csv")
    ev = pd.read_csv(DATA / "evidence.csv", dtype={"pmcid": str})
    df = load_articles()
    pr = lambda st, t: 100 * float(prev[(prev.stratum == st) & (prev.technique == t)].prevalence.iloc[0])   # noqa: E731
    ph = lambda st, a, b: float(pairs[(pairs.stratum == st) & (pairs.A == a) & (pairs.B == b)].phi.iloc[0])   # noqa: E731
    rng = lambda t: (min(pr(s, t) for s in CORE), max(pr(s, t) for s in CORE))   # noqa: E731
    f = {"n": len(df), "dls": rng("DLS"), "zeta": rng("zeta"), "tem": rng("TEM")}
    f["inorg"] = {t: pr("inorganic", t) for t in ("UVVis", "TEM", "SEM", "DLS", "zeta")}
    f["phi"] = {"dls_zeta": ph("ORGANIC", "DLS", "zeta"), "ftir_xrd_o": ph("ORGANIC", "FTIR", "XRD"), "ftir_xrd_i": ph("inorganic", "FTIR", "XRD"),
                "eds_sem_i": ph("inorganic", "EDS", "SEM"), "eds_xrd_i": ph("inorganic", "EDS", "XRD")}
    # AAV
    aav = df[df.primary_family == "AAV"]
    e = aav[aav.EM]
    f["aav"] = dict(dls=pr("AAV", "DLS"), zeta=pr("AAV", "zeta"), qpcr=pr("AAV", "qPCR_ddPCR"), n_em_pct=100 * len(e) / len(aav),
                    tem_in_em=100 * e.TEM.mean(), cryo_in_em=100 * e.cryoEM.mean(),
                    qpcr_in_em=100 * (e.qPCR_ddPCR | e.AUC).mean(), dls_in_em=100 * e.DLS.mean())
    # qPCR fuera de AAV: expresion genica vs titulo (aprox. por palabras clave del fragmento de evidencia)
    expr = re.compile(r"expression|mRNA level|gene|primer|GAPDH|cDNA|transcript|knockdown|RT-", re.I)
    titer = re.compile(r"titer|titre|genome cop|vector genome|viral genome|vg/|capsid|AAV|packag", re.I)
    q = ev[ev.technique == "qPCR_ddPCR"].merge(df[["pmcid", "primary_family"]], on="pmcid")
    rest = q[q.primary_family != "AAV"]
    f["qpcr_rest"] = dict(expr=100 * rest.evidence.str.contains(expr).mean(), titer=100 * rest.evidence.str.contains(titer).mean(),
                          lo=min(pr(s, "qPCR_ddPCR") for s in CORE + ["inorganic"]), hi=max(pr(s, "qPCR_ddPCR") for s in CORE + ["inorganic"]), lnp=pr("LNP", "qPCR_ddPCR"))
    # pares imagen-espectro
    same, art, proj = {}, {}, {}
    for fam in CORE + ["inorganic"]:
        sub = df[df.primary_family == fam]
        em_ = sub[sub.EM]
        art[fam] = 100 * em_[SPECTRA].any(axis=1).mean()
        r = em[(em.stratum == fam) & (em.what == "micrograph+spectrum_same_figure")].iloc[0]
        same[fam] = 100 * r.P
        pop = int(strata[(strata.primary_family == fam) & strata.period.isin(["main_early", "main_late"])].N_population.sum())
        proj[fam] = round(pop * r.k / len(sub), -1)
    f["same"], f["art"], f["proj"] = same, art, proj
    em_in = df[(df.primary_family == "inorganic") & df.EM]
    f["inorg_no_stain"] = 100 * (em_in.TEM & ~em_in.cryoEM & ~em_in.sub__neg_stain & ~em_in.sub__pos_stain).mean()
    f["saxs_k"] = int(prev[(prev.stratum == "ALL") & (prev.technique == "SAXS")].k.iloc[0])
    return f


def points(f):
    a, q, i = f["aav"], f["qpcr_rest"], f["inorg"]
    smin, smax = min(f["same"][k] for k in NAMES), max(f["same"][k] for k in NAMES)
    amin, amax = min(f["art"][k] for k in NAMES), max(f["art"][k] for k in NAMES)
    r = lambda t: f"{t[0]:.0f}–{t[1]:.0f}"   # noqa: E731
    return [
        ("DLS, zeta y TEM dominan en lípidos y polímeros.",
         f"Según la familia: DLS {r(f['dls'])} %, zeta {r(f['zeta'])} %, TEM {r(f['tem'])} %. En inorgánicas mandan UV-Vis ({i['UVVis']:.0f} %), TEM ({i['TEM']:.0f} %) y SEM ({i['SEM']:.0f} %); DLS y zeta bajan a ~{i['DLS']:.0f} %."),
        ("Las técnicas secundarias van en bloque: UV-Vis, SEM, FTIR y XRD.",
         f"Se reportan juntas: FTIR–XRD (phi {dec(f['phi']['ftir_xrd_o'])} en orgánicas, {dec(f['phi']['ftir_xrd_i'])} en inorgánicas), y en inorgánicas EDS con SEM ({dec(f['phi']['eds_sem_i'])}) y con XRD ({dec(f['phi']['eds_xrd_i'])}). "
         f"DLS y zeta son la pareja más fuerte ({dec(f['phi']['dls_zeta'])}). El resto casi no se correlaciona."),
        ("AAV es la excepción.",
         f"DLS {a['dls']:.0f} % y zeta {a['zeta']:.0f} %, pero qPCR/ddPCR {a['qpcr']:.0f} %. Solo {a['n_em_pct']:.0f} % de los artículos de AAV traen microscopía (TEM {a['tem_in_em']:.0f} %, cryo-EM {a['cryo_in_em']:.0f} % de esos), "
         f"y {a['qpcr_in_em']:.0f} % de ellos trae también qPCR/ddPCR o ultracentrifugación; solo {a['dls_in_em']:.0f} % trae DLS."),
        ("El qPCR fuera de AAV es otra cosa.",
         f"Aparece en {q['lo']:.0f}–{q['hi']:.0f} % de los artículos (LNP {q['lnp']:.0f} %), pero aprox. {q['expr']:.0f} % de los fragmentos hablan de expresión génica (RT-qPCR) y solo {q['titer']:.0f} % de título de vector "
         "(clasificación por palabras clave). Es una lectura biológica del efecto, no una caracterización del nanoportador."),
        ("Pares imagen–espectro: abundantes por artículo, escasos por figura.",
         f"Entre los artículos con micrografía, {amin:.0f}–{amax:.0f} % traen también un espectro, pero solo {smin:.0f}–{smax:.0f} % lo muestran en la misma figura "
         f"(inorgánicas {f['same']['inorganic']:.0f} %, liposomas {f['same']['liposome']:.0f} %, poliméricas {f['same']['polymeric']:.0f} %)."),
    ]


LEVELS = [
    ("Capturar siempre", "DLS, zeta, TEM, SEM, UV-Vis y el estado de preparación de la muestra de microscopía electrónica (con la opción «no declarado»)."),
    ("Capturar como opcional", "FTIR, XRD, DSC/TGA, RMN y cryo-EM (relevante en LNP y AAV)."),
    ("Solo una bandera de texto", "EDS (salvo inorgánicas), AFM, NTA, SAXS, XPS, Raman. SAXS aparece en muy pocos artículos: no vale un módulo."),
    ("Separar dos campos de PCR", "«qPCR de título» (útil en AAV) y «RT-qPCR de expresión» (resto). Son cosas distintas."),
    ("Para AAV", "El par útil es micrografía + título o lleno/vacío (qPCR, ultracentrifugación), no micrografía + DLS."),
]
CAUTIONS = [
    "La validación del detector la hice yo, sola y con un conjunto pequeño (56 artículos). Falta que dos personas del equipo lo revisen.",
    "Tu observación de que un modelo puede aprender solo de micrografías de vectores virales no se puede comprobar con estos datos. Solo vemos que, en AAV, la imagen viene con títulos y no con tamaño o zeta. Adenovirus no está en la muestra.",
    "Una parte de los artículos de liposomas, inorgánicas y AAV usa el material como herramienta y no estudia el nanoportador. «Misma figura» y la separación expresión/título del qPCR son aproximaciones por texto.",
]
FILES = [
    ("entrega/resumen.html", "esta página"),
    ("entrega/REPORTE_SIMPLE.md", "el mismo reporte en texto"),
    ("entrega/diagrama_procedimiento.svg", "el diagrama de 7 pasos"),
    ("entrega/decision_*.png", "las figuras de decisión"),
    ("REPORT.md", "informe completo: método, 10 hipótesis, limitaciones"),
    ("figures/", "las 7 figuras completas; 1, 2, 5 y 6 son interactivas (.html)"),
    ("data/pairs.csv, data/articles.csv", "todos los números y los artículos clasificados"),
]
FIGS = [
    ("decision_1_que_capturar.png", "Qué capturar", "Cuanto más oscura la celda, más artículos reportan la técnica. De aquí salen los niveles de captura."),
    ("decision_5_que_se_correlaciona.png", "Qué se correlaciona", "Cada línea une técnicas que aparecen juntas más de lo esperado. DLS, zeta y TEM forman un bloque; FTIR, XRD, EDS, SEM y DSC/TGA, otro."),
    ("decision_4_AAV_excepcion.png", "AAV frente al resto", "AAV casi no usa DLS ni zeta y se apoya en qPCR/ddPCR."),
    ("decision_3_pares_imagen_espectro.png", "Pares imagen–espectro", "Azul: emparejar por artículo. Naranja: por figura. Decide con qué familia empezar."),
]


def write_md(f):
    L = ["# Qué técnicas capturar y qué pares imagen–espectro son realistas", "",
         f"Base: {nfmt(f['n'])} artículos de acceso abierto (2018–2026), 7 familias de nanoportadores, texto completo de Europe PMC.", "", "## Hallazgos", ""]
    L += [f"{i}. **{t}** {d}" for i, (t, d) in enumerate(points(f), 1)]
    L += ["", "## Qué decidir", ""] + [f"- **{a}:** {b}" for a, b in LEVELS]
    L += [f"- En inorgánicas, {f['inorg_no_stain']:.0f} % de los artículos con microscopía electrónica muestran TEM sin declarar tinción ni cryo."]
    L += ["", "## Pares micrografía + espectro en la misma figura (estimación para la literatura abierta 2018–2026)", "",
          "| Familia | En la misma figura | Artículos estimados |", "|---|---|---|"]
    for k in ["inorganic", "polymeric", "liposome", "LNP", "SLN_NLC", "PLN"]:
        L += [f"| {NAMES[k]} | {f['same'][k]:.0f} % | ≈ {nfmt(int(f['proj'][k]))} |"]
    L += ["", "## Antes de confiar", ""] + [f"- {c}" for c in CAUTIONS]
    L += ["", "## Figuras", ""] + [f"- `entrega/{a}`: {b}. {c}" for a, b, c in FIGS]
    L += ["", "Diagrama del procedimiento: `entrega/diagrama_procedimiento.svg`. Informe completo: `REPORT.md`.", ""]
    (OUT / "REPORTE_SIMPLE.md").write_text("\n".join(L), encoding="utf-8")


CSS = """
:root{--bg:#f6f7f9;--surface:#ffffff;--ink:#14181f;--ink2:#4a5260;--muted:#7b8494;--line:#dfe3ea;--accent:#2a62c9;--warn:#b4501f;--warn-soft:#fbeee6;--plate:#fcfcfb}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#0f1218;--surface:#171b23;--ink:#eef1f6;--ink2:#b4bccb;--muted:#8791a3;--line:#2a313d;--accent:#7aa6f0;--warn:#f0a070;--warn-soft:#2d2018;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#0f1218;--surface:#171b23;--ink:#eef1f6;--ink2:#b4bccb;--muted:#8791a3;--line:#2a313d;--accent:#7aa6f0;--warn:#f0a070;--warn-soft:#2d2018;color-scheme:dark}
body{background:var(--bg);color:var(--ink);font-family:"IBM Plex Sans",system-ui,-apple-system,"Segoe UI",sans-serif;font-size:16px;line-height:1.55}
.wrap{max-width:980px;margin-inline:auto;padding-inline:20px;padding-block:28px 56px;display:flex;flex-direction:column;gap:36px}
h1{font-size:clamp(1.55rem,3.4vw,2.1rem);line-height:1.2;margin:0;text-wrap:balance;font-weight:600}
h2{font-size:1.1rem;margin:0 0 12px;font-weight:600;text-wrap:balance}
p{margin:0}
.lede{color:var(--ink2);margin-top:10px;max-width:68ch}
.kicker{font:500 .78rem/1 "IBM Plex Mono",ui-monospace,monospace;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin-bottom:12px}
.pts{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,420px),1fr));gap:14px}
.pt{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:16px 18px;min-width:0}
.pt b{display:block;margin-bottom:6px;font-weight:600}
.pt span{color:var(--ink2);font-size:.95rem}
.lv{display:grid}
.lv div{display:grid;grid-template-columns:minmax(0,13rem) minmax(0,1fr);gap:6px 18px;padding:10px 0;border-top:1px solid var(--line)}
.lv div:first-child{border-top:none}
.lv b{font-weight:600}
@media (max-width:560px){.lv div{grid-template-columns:1fr}}
.figs{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,440px),1fr));gap:26px 22px}
.fig{display:flex;flex-direction:column;gap:10px;min-width:0}
.plate{background:var(--plate);border:1px solid var(--line);border-radius:10px;padding:8px;overflow-x:auto}
.plate img{display:block;width:100%;height:auto}
.plate svg{display:block;width:100%;height:auto;min-width:640px}
.fig p{color:var(--ink2);font-size:.92rem}
table{border-collapse:collapse;width:100%;font-variant-numeric:tabular-nums;font-size:.95rem}
th,td{text-align:left;padding:8px 10px;border-bottom:1px solid var(--line)}
th{font-weight:600;color:var(--ink2);font-size:.85rem}
td:nth-child(n+2),th:nth-child(n+2){text-align:right}
.tw{overflow-x:auto}
.note{font-size:.88rem;color:var(--muted);margin-top:8px}
.caution{background:var(--warn-soft);border:1px solid var(--line);border-radius:10px;padding:14px 18px}
.caution h2{color:var(--warn)}
.caution ul{margin:0;padding-left:1.1rem;display:grid;gap:6px}
.files{list-style:none;padding:0;margin:0}
.files li{display:grid;grid-template-columns:minmax(0,17rem) minmax(0,1fr);gap:4px 16px;padding:7px 0;border-top:1px solid var(--line)}
.files code{font:500 .85rem "IBM Plex Mono",ui-monospace,monospace;color:var(--accent);overflow-wrap:anywhere}
@media (max-width:560px){.files li{grid-template-columns:1fr}}
"""


def write_html(f):
    pts = "".join(f'<div class="pt"><b>{html.escape(t)}</b><span>{html.escape(d)}</span></div>' for t, d in points(f))
    lv = "".join(f"<div><b>{html.escape(a)}</b><span>{html.escape(b)}</span></div>" for a, b in LEVELS)
    rows = "".join(f"<tr><td>{NAMES[k]}</td><td>{f['same'][k]:.0f} %</td><td>≈ {nfmt(int(f['proj'][k]))}</td></tr>" for k in ["inorganic", "polymeric", "liposome", "LNP", "SLN_NLC", "PLN"])
    figs = "".join(f'<section class="fig"><h2>{html.escape(t)}</h2><div class="plate"><img alt="{html.escape(t)}" src="data:image/png;base64,{b64(OUT / a)}"></div><p>{html.escape(c)}</p></section>' for a, t, c in FIGS)
    svg = (OUT / "diagrama_procedimiento.svg").read_text(encoding="utf-8")
    cautions = "".join(f"<li>{html.escape(c)}</li>" for c in CAUTIONS)
    files = "".join(f"<li><code>{html.escape(a)}</code><span>{html.escape(b)}</span></li>" for a, b in FILES)
    page = f"""<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Mapa de técnicas</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@500&family=IBM+Plex+Sans:wght@400;600&display=swap">
<style>{CSS}</style>
<main class="wrap">
<header><div class="kicker">Nanoportadores · técnicas de caracterización</div>
<h1>Qué técnicas capturar y qué pares imagen–espectro son realistas</h1>
<p class="lede">Resultado de leer {nfmt(f['n'])} artículos de acceso abierto (2018–2026) de 7 familias de nanoportadores y medir qué técnicas aparecen juntas.</p></header>
<section><h2>Hallazgos</h2><div class="pts">{pts}</div></section>
<section><h2>Figuras clave</h2><div class="figs">{figs}</div></section>
<section><h2>Qué decidir</h2><div class="lv">{lv}</div>
<p class="note">En inorgánicas, {f['inorg_no_stain']:.0f} % de los artículos con microscopía electrónica muestran TEM sin declarar tinción ni cryo.</p></section>
<section><h2>Pares micrografía + espectro en la misma figura</h2><div class="tw"><table><thead><tr><th>Familia</th><th>En la misma figura</th><th>Artículos estimados</th></tr></thead><tbody>{rows}</tbody></table></div>
<p class="note">La última columna proyecta la muestra a toda la literatura abierta 2018–2026 de cada familia. Es una estimación.</p></section>
<section><h2>Cómo se hizo</h2><div class="plate">{svg}</div></section>
<section class="caution"><h2>Antes de confiar</h2><ul>{cautions}</ul></section>
<section><h2>Dónde está cada cosa</h2><ul class="files">{files}</ul></section>
</main>"""
    (OUT / "resumen.html").write_text(page, encoding="utf-8")


def main():
    shutil.copyfile(ROOT / "figures" / "fig3_red_de_tecnicas.png", OUT / "decision_5_que_se_correlaciona.png")
    f = facts()
    write_md(f)
    write_html(f)
    print("ok", (OUT / "resumen.html").stat().st_size // 1024, "KB")


if __name__ == "__main__":
    main()
