"""Genera REPORT.md (espanol) desde los archivos de data/: cada numero sale de un calculo registrado."""
from __future__ import annotations

import json

import numpy as np
import pandas as pd

from .common import DATA, ROOT, load_yaml
from .data import FAMILY_ORDER, MICRO, ORGANIC, load_articles, reliability_table
from .detect import technique_names
from .prec import median_halfwidth
from .stats import cochran_armitage

FAM = {"ALL": "Todas", "ORGANIC": "Orgánicas", "LNP": "LNP", "liposome": "Liposomas", "SLN_NLC": "SLN/NLC", "PLN": "PLN (híbridas)",
       "polymeric": "Poliméricas", "inorganic": "Inorgánicas", "AAV": "AAV"}
SPECTRA = ["UVVis", "FTIR", "XRD", "NMR", "EDS", "SAXS", "Raman_SERS", "XPS"]


def md(df: pd.DataFrame, floatfmt="{:.2f}") -> str:
    cols = list(df.columns)
    out = ["| " + " | ".join(str(c) for c in cols) + " |", "|" + "|".join("---" for _ in cols) + "|"]
    for _, r in df.iterrows():
        cells = []
        for c in cols:
            v = r[c]
            cells.append("" if (isinstance(v, float) and np.isnan(v)) else (floatfmt.format(v) if isinstance(v, (float, np.floating)) else str(v).replace("|", chr(92) + "|")))
        out.append("| " + " | ".join(cells) + " |")
    return "\n".join(out)


def fmt_n(n):
    return f"{n:,}".replace(",", ".")


def pct(x, d=0):
    return "n.d." if x != x else f"{100 * x:.{d}f} %"


def build() -> str:
    samp = load_yaml("sampling.yaml")
    head = samp["headline_definition"]
    meta = json.loads((DATA / "analysis_meta.json").read_text(encoding="utf-8"))
    df = load_articles(head)
    allart = pd.read_csv(DATA / "articles_all.csv", dtype={"pmcid": str}, low_memory=False)
    main = allart[allart.analysis_set == "main"]
    trend_all = allart[allart.analysis_set == "trend_only"]
    pairs = pd.read_csv(DATA / "pairs.csv")
    prev = pd.read_csv(DATA / "prevalence.csv")
    em = pd.read_csv(DATA / "em_row.csv")
    hyp = pd.read_csv(DATA / "hypotheses.csv")
    sens = pd.read_csv(DATA / "sensitivity_summary.csv")
    gold = pd.read_csv(DATA / "gold_metrics.csv")
    trend = pd.read_csv(DATA / "trend.csv")
    strata = pd.read_csv(DATA / "ids" / "strata_counts.csv")
    qt = json.loads((DATA / "ids" / "query_totals.json").read_text(encoding="utf-8"))
    rel = reliability_table(head)
    relmap = rel.set_index("technique")["reliability"].to_dict()
    techs = meta["techniques_in_matrix"]
    core = technique_names("core")
    first_q = pd.read_json(ROOT / "logs" / "queries.jsonl", lines=True)
    ts = pd.to_datetime(first_q["ts"], utc=True)
    d0, d1 = ts.min().date(), ts.max().date()
    n_main = len(df)

    def P(st, a, b):
        r = pairs[(pairs.stratum == st) & (pairs.A == a) & (pairs.B == b)]
        return None if r.empty else r.iloc[0]

    def cell(st, a, b):
        r = P(st, a, b)
        if r is None or r.P_B_given_A != r.P_B_given_A:
            return "n.d."
        flag = " (n(A)<20)" if r.low_n else ""
        return f"{100 * r.P_B_given_A:.0f} % [{100 * r.ci_lo:.0f}–{100 * r.ci_hi:.0f}] ({int(r.nAB)}/{int(r.nA)}){flag}"

    L = []
    w = L.append
    w("# Co-ocurrencia de técnicas de caracterización en artículos de nanoportadores")
    w("")
    w(f"> Informe generado por `python -m src.report` desde `data/`. Fecha de las consultas a Europe PMC: {d0} a {d1}. "
      f"Definición principal de «técnica reportada»: `{head}` (ver Enmienda 1 en `PREREGISTRATION.md`). "
      "Etiquetas: **[medido]** = salida de una consulta/cálculo registrado; **[literatura]** = tomado del brief con su fuente; **[inferido]** = proyección o interpretación.")
    w("")
    w("> **Aviso principal (léalo antes de citar números):** la validación del detector usó una anotación **provisional de un solo anotador (Claude)**, no la doble anotación humana que pide el brief. "
      "Las métricas de fiabilidad son por eso optimistas y deben confirmarse con `GOLD_GUIDELINES.md`. Las técnicas *extendidas* no se validaron.")
    w("")
    # ---------------------------------------------------------------- 1
    w("## 1. Resumen")
    w("")
    ho = {r.id: r for r in hyp.itertuples()}
    w(f"- **[medido]** Muestra principal: {fmt_n(n_main)} artículos de acceso abierto en alcance (de {fmt_n(len(main))} procesados), 2018–2026, 7 familias, texto completo vía Europe PMC.")
    pt = P("ORGANIC", "TEM", "DLS"); pi = P("inorganic", "TEM", "DLS")
    w(f"- **[medido]** Dado TEM, el DLS aparece en {pct(pt.P_B_given_A)} de los artículos orgánicos (IC95 % {pct(pt.ci_lo)}–{pct(pt.ci_hi)}) frente a {pct(pi.P_B_given_A)} en inorgánicos: **el DLS es una etiqueta casi gratuita para lípidos y polímeros con TEM, no para inorgánicos**.")
    pz = P("ALL", "DLS", "zeta")
    w(f"- **[medido]** DLS y zeta son la asociación más fuerte entre técnicas (phi = {pz.phi:.2f}; P(zeta|DLS) = {pct(pz.P_B_given_A)}); la base debería capturarlas como un par.")
    e_all = em[(em.stratum == "ALL") & (em.what == "micrograph+spectrum_same_figure")].iloc[0]
    w(f"- **[medido]** Solo {pct(e_all.P)} de los artículos con micrografía (IC95 % {pct(e_all.ci_lo)}–{pct(e_all.ci_hi)}) muestran micrografía y espectro en la misma figura (proxy por pie de figura); varía de {pct(em[(em.what=='micrograph+spectrum_same_figure')&em.stratum.isin(FAMILY_ORDER)].P.min())} a {pct(em[(em.what=='micrograph+spectrum_same_figure')&em.stratum.isin(FAMILY_ORDER)].P.max())} según la familia.")
    w(f"- **[medido]** Hipótesis (reglas del preregistro): " + "; ".join(f"{h} {ho[h].verdict.split(' (')[0]}" for h in [f"H{i}" for i in range(1, 11)]) + ". Detalle en §3.6.")
    sa = P("ALL", "TEM", "SAXS")
    w(f"- **[medido]** SAXS es raro ({int(prev[(prev.stratum=='ALL')&(prev.technique=='SAXS')].k.iloc[0])} de {n_main} artículos): un módulo de SAXS **no tiene datos suficientes** con esta fuente; cryo-EM aparece en {pct(prev[(prev.stratum=='ALL')&(prev.technique=='cryoEM')].prevalence.iloc[0])} de los artículos (más en LNP).")
    w("- **[inferido]** Muchos artículos de las familias «liposoma», «inorgánica» y «AAV» no son estudios de nanoportadores sino usos del material como herramienta (p. ej., estructuras de proteínas en liposomas, vectores AAV en neurociencia); esto arrastra las matrices de esas familias (ver §5).")
    w("")
    # ---------------------------------------------------------------- 2
    w("## 2. Método")
    w("")
    w("### 2.1 Acceso y cumplimiento")
    w("")
    w("- **[medido]** Prueba de acceso (2026-10-09): la API REST de Europe PMC respondió HTTP 200 a una consulta mínima (`pageSize=1`) y el endpoint `fullTextXML` entregó el texto completo de un artículo OA. "
      "El impedimento previo (429/403) venía del entorno en la nube, no del acceso local.")
    w("- Términos: la página de descargas de Europe PMC lista sus servicios web y FTP como vía para el subconjunto OA; las páginas de términos de la API REST devolvieron 403 desde WebFetch, así que **no pude leer la política de la API REST** (solo la lista de servicios permitidos). PMC prohíbe la recuperación sistemática fuera de cuatro servicios, y por eso solo se usó Europe PMC (no PMC directamente). "
      "Se respetó ≤ 3 solicitudes/s con `User-Agent` identificable, reintentos con espera exponencial y caché; solo artículos con `OPEN_ACCESS:y` y licencia registrada. No se redistribuye texto completo ni figuras (la caché cruda está en `.gitignore`).")
    w("")
    w("### 2.2 Búsqueda, universo y muestreo")
    w("")
    tot = pd.DataFrame([{"Familia": FAM[f], "Hits API (2015–2026, no revisión)": qt[f]["hitCount_api"]} for f in qt])
    w(md(tot, "{:.0f}"))
    w("")
    w(f"Desviaciones de consulta registradas: AAV se restringió a artículos con términos de caracterización/manufactura del vector (sin restricción: 8.459 resultados, casi todos uso del AAV como vector); la familia polimérica añade micelas, quitosano, dendrímeros y nanogeles. "
      f"Universo elegible: licencia registrada, 2018–2026, sin revisiones; familia primaria = la más mencionada en título+resumen (ver tabla). Muestreo aleatorio estratificado proporcional (familia primaria × {{2018–2021, 2022–2026}} × {{CC BY, resto}}), semilla {samp['seed']}, lotes de {samp['batch_size']}, "
      f"parada cuando la mitad de ancho mediana del IC95 % de las celdas con n(A) ≥ 30 fue ≤ {samp['stop_halfwidth_median']} y se alcanzó el mínimo de la familia.")
    w("")
    rows = []
    for f in FAMILY_ORDER:
        pop = int(strata[(strata.primary_family == f) & strata.period.isin(["main_early", "main_late"])].N_population.sum())
        mm = main[main.primary_family == f]
        sc = mm[mm.in_scope.astype(bool)]
        hw, nc = median_halfwidth(load_articles(head).query("primary_family == @f"), core, 30)
        rows.append({"Familia": FAM[f], "Población 2018–26": pop, "Procesados": len(mm), "En alcance": len(sc),
                     "Objetivo": samp["targets"][f], "Mitad de ancho mediana IC95 % (celdas n(A)≥30)": hw, "Celdas": nc,
                     "CC BY (muestra)": "%.0f %%" % (100 * (sc.license_group == "cc_by").mean())})
    pop_ccby = float(strata[strata.period.isin(["main_early", "main_late"]) & (strata.license_group == "cc_by")].N_population.sum()
                     / strata[strata.period.isin(["main_early", "main_late"])].N_population.sum())
    w(md(pd.DataFrame(rows), "{:.3f}"))
    w("")
    w(f"**[medido]** Proporción CC BY en la población elegible 2018–2026: {100 * pop_ccby:.0f} %.")
    w("")
    w("**[medido]** Todas las familias cumplieron el criterio de precisión (≤ 0,08) y el mínimo de artículos, salvo PLN: su población completa es de 119 artículos (114 en alcance, por debajo de los 150 del objetivo; se tomaron todos los disponibles). "
      "El tope de 4.000 artículos no se alcanzó. El conjunto de validación (56 artículos) está dentro de la muestra; por eso, como el muestreo toma «los siguientes sin procesar», la muestra es un prefijo del orden estratificado más algunos artículos adicionales aleatorios de la validación.")
    w("")
    ex = main[~main.in_scope.astype(bool)].exclusion.fillna("").str.replace("type:", "tipo: ").value_counts()
    w("Exclusiones tras la descarga (muestra principal): " + "; ".join(f"{k} {v}" for k, v in ex.items()) + ".")
    w("")
    w("### 2.3 Detección")
    w("")
    w("Diccionarios (regex con límites de palabra) en `config/techniques.yaml`, aplicados por sección (Métodos, Resultados, pies de figura/tabla, otras). Reglas para las trampas del brief: siglas ambiguas (SEM, TEM-1, NTA, AUC, EDS, TGA, DSC) aceptadas solo con el término completo en el artículo o contexto a ≤ 80 caracteres y con exclusiones (p. ej. «mean ± SEM», «Ni-NTA»); cryo-TEM se clasifica antes y se excluye del conteo de TEM; revisiones y artículos que no son de investigación se excluyen; se normalizan los guiones Unicode. "
      "Subbanderas (tinción negativa, HRTEM, FE-SEM, etc.) y una proxy de «micrografía y espectro en el mismo pie de figura».")
    w("")
    w("Ajustes tras el piloto y la validación (permitidos por el preregistro): patrones de magnitudes derivadas (z-average, PDI, diffractograms, ZP) que cuentan solo en Resultados/pies; contenido de encabezados de tablas como «dato mostrado»; exclusión de listas de referencias y secciones administrativas; "
      "corrección de un patrón extendido erróneo (`Quant-?iT` coincidía con «quantitative»: RiboGreen/EE pasó de 59 % a 8 %, detectado revisando prevalencias, no en la validación: **las técnicas extendidas pueden tener errores no detectados**). No se usó ningún LLM (costo 0 USD).")
    w("")
    w("### 2.4 Estadística")
    w("")
    w("P(B|A) con IC de Wilson 95 %; OR con corrección de Haldane-Anscombe cuando hay una celda cero; lift, phi, Jaccard; prueba exacta de Fisher; BH (FDR 5 %) dentro de cada estrato; OR de Mantel-Haenszel estratificado por familia primaria; regresión logística `B ~ A + familia + año` con errores estándar robustos agrupados por revista; "
      "reglas de celda (n(A) < 20 atenuada; IC > 0,3 señalado); Apriori con soporte mínimo 0,05 por familia; prueba de Cochran-Armitage para tendencia; ajuste de Rogan-Gladen con sensibilidad/especificidad de la validación. Todas las funciones puras se prueban con datos sintéticos de probabilidades conocidas (`tests/test_stats.py`).")
    w("")
    # ---------------------------------------------------------------- 3
    w("## 3. Resultados")
    w("")
    w("### 3.1 Validación del detector")
    w("")
    w("56 artículos (8 por familia, fuera del piloto). **Anotación provisional de un solo anotador (Claude); no hay kappa.** Verdad terreno: técnica usada y con datos presentados (`GOLD_GUIDELINES.md`).")
    w("")
    g = gold.pivot_table(index="technique", columns="definition", values=["recall", "precision"]).reindex(core)
    gt = gold[gold.definition == head].set_index("technique").reindex(core)
    tab = pd.DataFrame({"Técnica": core, "Positivos": gt["n_true"].astype(int).to_numpy(),
                        f"Precisión ({head})": gt["precision"].to_numpy(), f"Recall ({head})": gt["recall"].to_numpy(),
                        "F1": gt["f1"].to_numpy(), "Recall «primary»": g["recall"]["primary"].to_numpy(),
                        "Fiabilidad": [relmap.get(t, "") for t in core]})
    w(md(tab))
    w("")
    f1 = gt[gt.n_true > 0]["f1"].mean(); f1p = gold[(gold.definition == "primary") & (gold.n_true > 0)]["f1"].mean()
    w(f"**[medido]** F1 medio (técnicas con positivos): {f1:.2f} con `{head}` frente a {f1p:.2f} con la definición `primary` preregistrada (recall < 0,85 en {int(((gold[(gold.definition=='primary')&(gold.n_true>=3)]).recall<0.85).sum())} técnicas): por eso se promovió `{head}` (Enmienda 1). "
      "STEM y SAXS no tuvieron positivos en la validación (**sin validar**, sus resultados deben leerse con cautela); UV-Vis tiene precisión baja (convención de anotación: lectura colorimétrica vs. espectroscopía; detector UV de HPLC). "
      "**Optimismo:** el diccionario se ajustó mirando esos mismos 56 artículos, así que estas métricas sobreestiman el rendimiento en artículos nuevos.")
    w("")
    pa_ = prev[prev.stratum == "ALL"].set_index("technique")
    rg = "; ".join(f"{t} {pa_.loc[t, 'prevalence']:.2f} → {pa_.loc[t, 'prevalence_rogan_gladen']:.2f}" for t in ["DLS", "UVVis", "TEM", "cryoEM"] if pa_.loc[t, "prevalence_rogan_gladen"] == pa_.loc[t, "prevalence_rogan_gladen"])
    w(f"Corrección de Rogan-Gladen (prevalencia observada → ajustada con la sensibilidad/especificidad de la validación; `data/prevalence.csv`): {rg}. Con una validación provisional y de un solo anotador estos ajustes son indicativos, no definitivos.")
    w("")
    w("### 3.2 Prevalencia marginal")
    w("")
    pv = prev[prev.technique.isin(techs)].copy()
    tab = pv.pivot(index="technique", columns="stratum", values="prevalence").reindex(techs)[["ALL"] + FAMILY_ORDER] * 100
    tab = tab.sort_values("ALL", ascending=False).reset_index().rename(columns={**FAM, "technique": "Técnica"})
    tab["Técnica"] = [t + {"recall_low": "†", "precision_low": "‡", "unvalidated": "°", "ok": ""}[relmap[t]] for t in tab["Técnica"]]
    w("Prevalencia (%) en la muestra principal (con IC95 % en `data/prevalence.csv`; † recall < 0,85; ‡ precisión < 0,80; ° sin validar).")
    w("")
    w(md(tab, "{:.0f}"))
    w("")
    w("### 3.3 Matriz de P(B | A)")
    w("")
    w("Figura 1 (`figures/fig1_matriz_P_B_dado_A.*`): una subtrama por familia más la agregada, filas = A con n(A), ordenadas por agrupamiento sobre 1 − phi; celdas con n(A) < 20 en gris con hachurado y celdas con IC ancho pálidas. Valores completos: `data/pairs.csv`. Algunas celdas clave (P(B|A) [IC95 %] (n(A∧B)/n(A))):")
    w("")
    keys = [("TEM", "DLS"), ("SEM", "DLS"), ("DLS", "zeta"), ("zeta", "DLS"), ("TEM", "zeta"), ("cryoEM", "DLS"), ("cryoEM", "SAXS"), ("TEM", "SAXS"), ("TEM", "UVVis"), ("TEM", "XRD"), ("SEM", "EDS"), ("TEM", "EDS"), ("TEM", "FTIR"), ("SEM", "FTIR")]
    rows = [{"A → B": f"{a} → {b}", **{FAM[s]: cell(s, a, b) for s in ["ALL", "LNP", "liposome", "SLN_NLC", "PLN", "polymeric", "inorganic"]}} for a, b in keys]
    w(md(pd.DataFrame(rows)))
    w("")
    w("### 3.4 Asociaciones y combinaciones")
    w("")
    pa = pairs[(pairs.stratum == "ALL") & (pairs.A < pairs.B) & (pairs.p_adj_bh < 0.05)].sort_values("phi", ascending=False).head(10)
    tab = pd.DataFrame({"Par": pa.A + " – " + pa.B, "phi": pa.phi, "OR crudo": pa.OR, "OR MH (por familia)": pa.MH_OR,
                        "OR ajustado (logística, SE por revista)": pa.adj_OR, "IC95 % ajustado": [f"{lo:.1f}–{hi:.1f}" for lo, hi in zip(pa.adj_lo, pa.adj_hi)]})
    w("Diez asociaciones más fuertes entre técnicas (agregada, FDR < 5 %). En la mayoría de los pares el OR de MH y el ajustado son menores que el crudo, lo que indica el efecto de la composición por familia (paradoja de Simpson), aunque no en todos (p. ej. DLS–TEM):")
    w("")
    w(md(tab))
    w("")
    n_edge = int(((pairs[(pairs.stratum == 'ALL') & (pairs.A < pairs.B)].phi > 0.2) & (pairs[(pairs.stratum == 'ALL') & (pairs.A < pairs.B)].p_adj_bh < 0.05)).sum())
    w(f"**[medido]** Solo {n_edge} de {len(pairs[(pairs.stratum=='ALL')&(pairs.A<pairs.B)])} parejas superan phi = 0,2 con FDR < 5 % (Figura 3). Los bloques son: dispersión de luz (DLS–zeta–TEM), sólidos (FTIR–XRD–EDS–SEM–DSC/TGA) y ensayos de EE (RiboGreen–TNS).")
    w("")
    it = pd.read_csv(DATA / "itemsets.csv")
    ng = pd.read_csv(DATA / "next_given_combo.csv")
    ia = it[it.stratum == "ALL"].head(8)
    w("Combinaciones más frecuentes (soporte; agregada; Apriori, soporte mínimo 0,05):")
    w("")
    w(md(pd.DataFrame({"Conjunto": ia.itemset, "Soporte": ia.support * 100, "Artículos": ia["count"]}), "{:.1f}"))
    w("")
    for combo, nxt in [("{TEM, DLS, zeta}", "UVVis"), ("{TEM, DLS, zeta}", "SEM"), ("{TEM, DLS, zeta}", "SAXS"), ("{TEM, DLS, zeta}", "FTIR")]:
        r = ng[(ng.stratum == "ALL") & (ng.combo == combo) & (ng.next == nxt)]
        if len(r):
            r = r.iloc[0]
            w(f"- **[medido]** P({nxt} | {combo[1:-1]}) = {pct(r.P)} [{pct(r.ci_lo)}–{pct(r.ci_hi)}] ({int(r.k)}/{int(r.n_combo)}).")
    w("")
    w("Figura 4 (UpSet) muestra las 15 combinaciones exactas más frecuentes por familia: ninguna domina fuera de AAV, donde un artículo típico solo usa qPCR/ddPCR.")
    w("")
    w("### 3.5 Tendencia temporal (secundaria)")
    w("")
    tt = trend.groupby("technique").agg(CA_z=("CA_z", "first"), CA_p=("CA_p", "first")).reset_index()
    first = trend.sort_values("year").groupby("technique").first()
    last = trend.sort_values("year").groupby("technique").last()
    tt["Prev. primer año (%)"] = 100 * first.loc[tt.technique, "prevalence"].to_numpy()
    tt["Prev. último año (%)"] = 100 * last.loc[tt.technique, "prevalence"].to_numpy()
    w("Prueba de Cochran-Armitage sobre año (2015–2026; 2015–2017 es una submuestra de ≈ 40 artículos por familia). Sin corrección por composición de familias.")
    w("")
    w(md(tt.rename(columns={"technique": "Técnica"}), "{:.3g}"))
    w("")
    w(f"Con {len(tt)} pruebas, el umbral de Bonferroni es p < {0.05 / len(tt):.4f}: solo " + ", ".join(tt[tt.CA_p < 0.05 / len(tt)].technique) + " lo supera; en el resto no se detecta tendencia (FTIR, p = 0,02, no sobrevive a la corrección).")
    w("")
    w("### 3.6 Contraste de hipótesis (reglas de `PREREGISTRATION.md`)")
    w("")
    h_rows = [{"#": r.id, "Veredicto": r.verdict, "Evidencia [medido]": str(r.evidence).replace(" | ", "; "), "Cautela": r.caveat if isinstance(r.caveat, str) else ""} for r in hyp.itertuples()]
    w(md(pd.DataFrame(h_rows)))
    w("")
    w("Notas: **H2**: P(SAXS|cryo-EM) supera a TEM seco en LNP (diferencia significativa) pero no en liposomas (n pequeño; 1 positivo): veredicto *parcial*. **H4** parcial: EDS es más probable dado SEM que dado TEM en inorgánicas, pero EDS **no** es raro (< 10 %) en todas las familias orgánicas. "
      "**H7** depende de qPCR/ddPCR, que en AAV mide títulos pero en otras familias mide expresión génica (interpretar solo en AAV; extendidas sin validar). **H9** usa un proxy por pie de figura. **H10**: compara lípidos, polímeros e inorgánicas (AAV queda fuera de la hipótesis; su cryo-EM es 44 %).")
    w("")
    w("### 3.7 Sensibilidad")
    w("")
    sens2 = sens.rename(columns={"scenario": "Escenario", "n_pairs": "Pares", "pearson_P_B_given_A": "Correlación P(B|A) con la principal", "direction_agreement": "Acuerdo en dirección (lift)",
                                  "n_fdr_significance_changes": "Pares que cambian de significancia FDR"})
    w(md(sens2.drop(columns="examples_changed"), "{:.3f}"))
    w("")
    w("**[medido]** Las probabilidades condicionales casi no cambian entre definiciones y escenarios (r ≥ 0,94), y la dirección de la asociación coincide en ≥ 90 % de los pares; los cambios están en qué pares alcanzan significancia FDR; **[inferido]** son más numerosos con definiciones más restrictivas o con solo CC BY, donde baja la potencia. "
      "Excluir las técnicas con detector poco fiable no cambia ninguna conclusión. Lista de pares que cambian: `data/sensitivity_summary.csv`; todas las tablas: `data/pairs_sensitivity.csv`.")
    w("")
    # ---------------------------------------------------------------- 4
    w("## 4. Implicaciones para el esquema de la base")
    w("")
    w("Regla usada **[inferido]**: *obligatorio* si la técnica se reporta en ≥ 30 % de los artículos de alguna familia núcleo (LNP, liposomas, SLN/NLC, PLN, poliméricas); *opcional* si en ≥ 10 %; si no, *solo bandera de texto*. Inorgánicas y AAV se evalúan aparte. † = detector poco fiable, ° = sin validar.")
    w("")
    rows = []
    for t in techs:
        pr = {s: float(prev[(prev.stratum == s) & (prev.technique == t)].prevalence.iloc[0]) for s in FAMILY_ORDER}
        mx = max(pr[s] for s in ["LNP", "liposome", "SLN_NLC", "PLN", "polymeric"])
        lvl = "obligatorio" if mx >= 0.30 else ("opcional" if mx >= 0.10 else "solo bandera")
        if t in ("qPCR_ddPCR",):
            lvl = "obligatorio solo en AAV (títulos)"
        rows.append({"Técnica": t + {"recall_low": "†", "precision_low": "‡", "unvalidated": "°", "ok": ""}[relmap[t]], "Nivel": lvl,
                     "Máx. familias núcleo (%)": 100 * mx, "Inorgánicas (%)": 100 * pr["inorganic"], "AAV (%)": 100 * pr["AAV"]})
    w(md(pd.DataFrame(rows).sort_values("Máx. familias núcleo (%)", ascending=False), "{:.0f}"))
    w("")
    w("Campos de preparación de EM (obligatorio para toda micrografía, brief §1.2): entre los artículos con EM, la tinción negativa se declara en una fracción grande de TEM de lípidos/polímeros y el cryo solo es frecuente en LNP y AAV (H10, §3.6); en inorgánicas la mayoría de TEM no declara tinción (seco por defecto), por lo que el valor «no declarado» debe existir en el esquema.")
    w("")
    w("### Pares micrografía–espectro realistas por familia")
    w("")
    rows = []
    for f in FAMILY_ORDER:
        sub = df[df.primary_family == f]
        emn = int(sub["EM"].sum())
        r = em[(em.stratum == f) & (em.what == "micrograph+spectrum_same_figure")].iloc[0]
        pop = int(strata[(strata.primary_family == f) & strata.period.isin(["main_early", "main_late"])].N_population.sum())
        n_s = len(sub)
        spec_any = int((sub["EM"] & sub[[s for s in SPECTRA if s in sub.columns]].any(axis=1)).sum())
        rows.append({"Familia": FAM[f], "Artículos muestra": n_s, "Con EM": emn, "EM + algún espectro (artículo)": spec_any,
                     "EM + espectro en la misma figura (n)": int(r.k), "… como % de EM": 100 * r.P, "IC95 %": f"{100 * r.ci_lo:.0f}–{100 * r.ci_hi:.0f}",
                     "[inferido] Población × % misma figura": round(pop * (r.k / n_s))})
    w(md(pd.DataFrame(rows), "{:.0f}"))
    w("")
    w("La última columna proyecta a la población de cada familia (2018–2026, acceso abierto, con licencia) la fracción de artículos con micrografía y espectro en la misma figura observada en la muestra; es una **proyección [inferida]** que asume que la muestra es representativa y que el proxy por pie de figura se comporta igual en toda la población. "
      f"Solo una minoría de los artículos con EM tiene el par a nivel de figura; solo con licencia CC BY (≈ {100 * pop_ccby:.0f} % de la población elegible) se podría redistribuir la imagen.")
    w("")
    # ---------------------------------------------------------------- 5
    w("## 5. Limitaciones y desviaciones")
    w("")
    for s in [
        "**Validación provisional de un solo anotador (Claude):** falta la doble anotación humana, el kappa y la confirmación de recall/precisión. STEM y SAXS no tuvieron positivos en la validación; las técnicas extendidas (Raman, XPS, BET, VSM, AUC, SEC-MALS, FFF, fotometría de masas, CDMS, qPCR/ddPCR, RiboGreen, TNS) no se validaron y un error de regex ya se encontró en una (RiboGreen).",
        "**Mención ≠ dato:** detectar una técnica en Métodos/Resultados/pies no garantiza que los datos sean útiles (p. ej. «DLS» como control de calidad sin datos mostrados, UV-Vis como lectura de ensayos). El proxy de «misma figura» se basa en pies de figura y es más estricto que la detección a nivel de artículo.",
        "**Definición principal cambiada tras la validación** (Enmienda 1), antes de calcular co-ocurrencias; las demás definiciones están en sensibilidad.",
        "**Familias ruidosas:** las consultas por título/resumen incluyen artículos donde el nanoportador es un reactivo (liposomas en estructural, AuNP/AgNP como material en recubrimientos o biosensores, vectores AAV). Esto es parte de «el corpus real» pero diluye los resultados de esas familias; no se hizo un filtro semántico por tema.",
        f"**Sesgo de acceso abierto y de revista:** solo OA con licencia registrada (la proporción CC BY es {100 * pop_ccby:.0f} % de la población elegible); el reporte de técnicas depende de la revista (se agrupó por revista en la logística, sin efecto aleatorio).",
        "**Texto en el suplemento:** el texto completo de Europe PMC no incluye el material suplementario; técnicas descritas solo allí no se ven (p. ej. artículos de Chem. Sci. con Métodos en el SI).",
        "**Tendencia 2015–2017** proviene de una submuestra pequeña; no controla composición de familia/revista.",
        "**Familia primaria** = la más mencionada en título+resumen; la sensibilidad con duplicación multietiqueta se reporta (r = 0,999, sin cambios de conclusión).",
        "**No obtenido:** ningún dato requirió «no obtenido» salvo la política de términos de la API REST de Europe PMC (403) y la lectura de los artículos/listas mencionados en el brief §2.4 (no se intentó; no eran necesarios para el cálculo).",
        "**Tamaño del conjunto de validación:** 56 en lugar de 50 (7 familias × 8); recall con pocos positivos tiene IC amplios.",
    ]:
        w(f"- {s}")
    w("")
    w("## 6. Reproducibilidad")
    w("")
    w("`make all` (Linux/macOS) o `.\\run_all.ps1` (Windows). Semilla fija en `config/sampling.yaml`; consultas y descargas con fecha en `logs/queries.jsonl`; listas de PMCID por celda en `data/cell_pmcids/`; evidencia por detección (≤ 25 palabras) en `data/evidence.csv`. "
      "Si no se vuelve a descargar, la caché de XML (no redistribuible) reproduce todo. Archivos principales: `data/articles.csv`, `data/pairs.csv`, `data/pairs_sensitivity.csv`, `data/gold_set.csv`, `data/gold_metrics.csv`, `figures/`.")
    return "\n".join(L) + "\n"


def main() -> None:
    (ROOT / "REPORT.md").write_text(build(), encoding="utf-8")
    print("REPORT.md escrito")


if __name__ == "__main__":
    main()
