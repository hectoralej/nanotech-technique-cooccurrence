"""Tipología de figuras a partir del pie (texto), sin mirar la imagen.

Para cada figura lógica del inventario (pmcid + figura) decide cuántos paneles tiene, de qué clase es cada uno
(micrografía, espectro/curva espectral, descriptores DLS/zeta, contenido no útil) y la tipología:
  micro_unica · espectro_unico · espectro_superpuesto · pareja_micro_espectro · pareja_micro · pareja_espectro ·
  micro_multiple_sin_etiquetas · compuesta_micro · compuesta_espectro · compuesta_mixta · compuesta_con_otros ·
  una_util_con_otros · solo_descriptores · sin_micro_ni_espectro
y el destino de depurado: simple | pareja | compuesta | superpuesto | excluir.

Solo lee modelos/imagenes_v02/inventario_figuras.csv, recortes_v02.csv y curation/ (lectura). No modifica nada fuera de esta carpeta.
Uso: python modelos/tipologia_figuras/clasificar_figuras.py
"""
import json
import re
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
I = re.I

# ---------- léxico -----------------------------------------------------------------------------------------------
MICRO = re.compile(
    r"\b(?:cryo[\s-]?(?:TEM|SEM|EM)|HR[\s-]?TEM|FE[\s-]?SEM|FESEM|HRSEM|STEM|TEM|AFM|SPM|SEM)\b|"
    r"electron\s+microscop|electron\s+micrograph|atomic\s+force|micrograph|negative[\s-]?stain|cryo[\s-]?electron", I)
SEM_ESTAD = re.compile(r"(?:±|\bmean\b|\bSD\b|\bSE\b)[^.]{0,25}\bSEM\b|\bSEM\b\s*\)?\s*(?:,|;)?\s*(?:n\s*=|\*+p)|standard\s+error", I)
ESPECTRO = re.compile(
    r"\bFT[\s-]?IR\b|\bIR\s+spectr|infrared|\bXRD\b|x[\s-]?ray\s+diffract|diffractogram|diffraction\s+pattern|"
    r"\bUV[\s\-–]*vis|\bUV\b[^.]{0,12}spectr|absorption\s+spectr|absorbance\s+spectr|\bRaman\b|\bEDS\b|\bEDX\b|energy[\s-]dispersive|"
    r"\bXPS\b|\bNMR\b|\bDSC\b|\bTGA\b|thermogram|thermogravimetr|calorimetr|\bSAXS\b|\bSANS\b|fluorescence\s+(?:emission\s+)?spectr|"
    r"emission\s+spectr|photoluminescence|circular\s+dichroism|\bXANES\b|\bEXAFS\b|\bSPR\b|plasmon\s+resonance|\bspectr(?:um|a|oscop)", I)
DESCRIPTOR = re.compile(r"\bDLS\b|dynamic\s+light\s+scattering|size\s+distribution|hydrodynamic|zeta|particle\s+size|\bPDI\b", I)
NO_UTIL = re.compile(
    r"schem|illustrat|diagram|representation|photograph|\bphoto\b|digital\s+image|viabil|cytotox|\bMTT\b|\brelease\b|in\s+vivo|"
    r"in\s+vitro|\bmice\b|\bmouse\b|\brats?\b|tumou?r|histolog|western|flow\s+cytometr|confocal|\bCLSM\b|fluorescence\s+(?:micro|image)|"
    r"inhibit|\bzone\b|bacteri|antibacter|antioxid|antimicrob|stability|biodistribut|pharmacokin|uptake|calibration|"
    r"standard\s+curve|chromatogram|\bHPLC\b|temperature\s+rise|catalytic|degradation|kinetic|apoptosis|hemolysis|"
    r"swelling|rheolog|viscosity|\bgraph\b|\bplot\b|bar\s+chart|\bcells?\b|wound|\bELISA\b|sensor|detection\s+limit|bars?\s+represent", I)
PLURAL_MICRO = re.compile(r"\b(?:images|micrographs|micrographies|photomicrographs|morphologies|micrograms)\b|\bTEM/SEM\b", I)
PLURAL_ESP = re.compile(r"\b(?:spectra|patterns|curves|thermograms|profiles|diffractograms|spectrograms)\b", I)
SUPERPOSICION = re.compile(r"overlay|superimpos|stack(?:ed)?|different|various|varying|increasing|series|ratios?\b|concentrations?\b|"
                           r"before\s+and\s+after|and\s+after|comparative|comparison|compared|\bvs\.?\b|versus|together|combined|\bboth\b|"
                           r"same\s+(?:plot|graph)|temperatures?\b|\bpH\b|at\s+\d+\s*(?:min|h)\b|\bbatch(?:es)?\b", I)

# etiquetas de subpanel: (a) (A) A) a) A: A. ; rangos (a-d) (a–c) (a,b) (a and b) ; "panel A" ; i/ii/iii
RANGO = re.compile(r"\(\s*([A-Za-z])\s*(?:[-–—]|to|,|&|and)\s*([A-Za-z])(?:\s*(?:,|&|and)\s*([A-Za-z]))?(?:\s*(?:,|&|and)\s*([A-Za-z]))?\s*\)", I)
UNICA = re.compile(r"(?:\(\s*([A-Ha-h])\s*\))|(?:(?<![\w(])([A-H])\s*[\):](?=\s))|(?:(?<=[\s.;,])([A-H])\.(?=\s+[A-Z]))|(?:\b(?:panel|panels|fig(?:ure)?s?\.?)\s+([A-H])\b)")
ROMANOS = re.compile(r"\(\s*(i{1,3}|iv|v)\s*\)")


def expandir(a, b):
    a, b = a.lower(), b.lower()
    if ord(b) > ord(a) and ord(b) - ord(a) <= 8:
        return [chr(c) for c in range(ord(a), ord(b) + 1)]
    return [a, b]


def etiquetas(pie):
    """Devuelve [(posicion, [letras])] de cada marcador de subpanel."""
    marc = []
    ocupados = []
    for m in RANGO.finditer(pie):
        letras = []
        g = [x for x in m.groups() if x]
        sep = pie[m.start():m.end()]
        if re.search(r"[-–—]|\bto\b", sep, I) and len(g) == 2:
            letras = expandir(g[0], g[1])
        else:
            letras = [x.lower() for x in g]
        marc.append((m.start(), letras)); ocupados.append((m.start(), m.end()))
    for m in UNICA.finditer(pie):
        if any(a <= m.start() < b for a, b in ocupados):
            continue
        letra = next(x for x in m.groups() if x)
        marc.append((m.start(), [letra.lower()]))
    for m in ROMANOS.finditer(pie):
        marc.append((m.start(), ["r" + m.group(1)]))
    marc.sort()
    return marc


def grupo(texto):
    """Clase de un fragmento: micro / espectro / descriptor / otro / sin_dato (puede devolver varias)."""
    g = []
    t = SEM_ESTAD.sub(" ", texto)
    if MICRO.search(t):
        g.append("micro")
    if ESPECTRO.search(texto):
        g.append("espectro")
    if DESCRIPTOR.search(texto) and not g:
        g.append("descriptor")
    if NO_UTIL.search(texto) and not g:
        g.append("otro")
    return g or ["sin_dato"]


def analizar(pie):
    pie = re.sub(r"\s+", " ", str(pie))
    marc = etiquetas(pie)
    letras = []
    for _, l in marc:
        for x in l:
            if x not in letras:
                letras.append(x)
    general = grupo(pie)
    paneles = []                                        # una clase por panel
    if len(letras) >= 2:
        # fragmentos desde cada marcador hasta el siguiente; marcadores contiguos comparten el fragmento siguiente
        pos = [p for p, _ in marc] + [len(pie)]
        introduccion = pie[:pos[0]]
        gi = [x for x in grupo(introduccion) if x != "sin_dato"]
        gg = [x for x in general if x != "sin_dato"]
        cola = re.sub(r"[\s.,;:)\-–]", "", RANGO.sub("", UNICA.sub("", pie[pos[-2]:])))
        posterior = len(cola) >= 4 or len(introduccion.strip()) < 15       # «(a) TEM … (b) SEM …» frente a «TEM … (a) y SEM … (b)»
        fragmentos = []
        if posterior:
            for k, (p, l) in enumerate(marc):
                fragmentos.append((l, pie[p:pos[k + 1]]))
        else:
            ant = 0
            for k, (p, l) in enumerate(marc):
                fragmentos.append((l, pie[ant:p])); ant = p
        por_letra = {}                                    # una clase por letra distinta (las letras repetidas son referencias, no paneles)
        pendientes = []
        for l, frag in fragmentos:
            frag_sin_marca = RANGO.sub("", UNICA.sub("", frag)).strip(" ,;.:-–")
            pendientes += l
            if len(frag_sin_marca) < 3:
                continue                                 # marcador pegado al siguiente
            g = [x for x in grupo(frag_sin_marca) if x != "sin_dato"] or (gi if posterior else []) or (gg if len(gg) == 1 else []) or ["sin_dato"]
            for x in pendientes:
                if por_letra.get(x, "sin_dato") == "sin_dato":
                    por_letra[x] = "+".join(g)
            pendientes = []
        for x in pendientes:
            por_letra.setdefault(x, "+".join(gg) if len(gg) == 1 else "sin_dato")
        paneles = [por_letra[x] for x in letras]
        metodo = "etiquetas"
    else:
        sin_marca = [x for x in general if x != "sin_dato"]
        if not sin_marca:
            paneles = ["sin_dato"]
        else:
            paneles = list(sin_marca)
        metodo = "texto"
    # un panel "micro+espectro" (p. ej. "SEM image and EDS spectrum" en un mismo fragmento) cuenta como 2 contenidos
    contenidos = [c for p in paneles for c in p.split("+")]
    n_micro, n_esp = contenidos.count("micro"), contenidos.count("espectro")
    n_desc, n_otro = contenidos.count("descriptor"), contenidos.count("otro")
    plural_m = bool(PLURAL_MICRO.search(pie)) and "micro" in general
    plural_e = bool(PLURAL_ESP.search(pie)) and "espectro" in general
    sup = bool(SUPERPOSICION.search(pie))
    # lista de muestras sin etiquetas: «de A, B y C» / «of A, B, and C»
    primera = re.split(r"\.\s+(?=[A-Z(])", pie, maxsplit=1)[0]
    nsep = len(re.findall(r",|\band\b|&|\bvs\.?\b|\bversus\b", re.sub(r"\([^)]*\)", "", primera), I))
    lista = nsep >= 2 or (nsep >= 1 and plural_e)
    return dict(n_etiquetas=len(letras), etiquetas="".join(x for x in letras if len(x) == 1) or ("|".join(letras)),
                paneles="|".join(paneles), metodo_conteo=metodo, n_micro=n_micro, n_espectro=n_esp, n_descriptor=n_desc, n_otro=n_otro,
                plural_micro=int(plural_m), plural_espectro=int(plural_e), indicio_superposicion=int(sup and len(letras) < 2), lista_muestras=int(lista and len(letras) < 2))


def tipologia(r):
    nu, ntot = r["n_micro"] + r["n_espectro"], r["n_micro"] + r["n_espectro"] + r["n_descriptor"] + r["n_otro"]
    sin_etiq = r["n_etiquetas"] < 2
    if nu == 0:
        return "solo_descriptores" if r["n_descriptor"] else "sin_micro_ni_espectro"
    if r["n_otro"] or r["n_descriptor"]:
        return "una_util_con_otros" if nu == 1 else "compuesta_con_otros"
    if nu == 1 and ntot == 1:
        if r["n_micro"]:
            return "micro_multiple_sin_etiquetas" if (sin_etiq and r["plural_micro"]) else "micro_unica"
        # espectro
        if sin_etiq and (r["lista_muestras"] or (r["plural_espectro"] and r["indicio_superposicion"])):
            return "espectro_superpuesto"
        return "espectro_unico"
    if nu == 2:
        if r["n_micro"] == 1 and r["n_espectro"] == 1:
            return "pareja_micro_espectro"
        return "pareja_micro" if r["n_micro"] == 2 else "pareja_espectro"
    if r["n_espectro"] == 0:
        return "compuesta_micro"
    if r["n_micro"] == 0:
        return "compuesta_espectro"
    return "compuesta_mixta"


DESTINO = {"micro_unica": "simple", "espectro_unico": "simple", "espectro_superpuesto": "superpuesto", "pareja_micro_espectro": "pareja",
           "pareja_micro": "pareja", "pareja_espectro": "pareja", "micro_multiple_sin_etiquetas": "revisar_multiple",
           "compuesta_micro": "compuesta", "compuesta_espectro": "compuesta", "compuesta_mixta": "compuesta", "compuesta_con_otros": "compuesta",
           "una_util_con_otros": "compuesta", "solo_descriptores": "excluir", "sin_micro_ni_espectro": "excluir"}


def clave(f):
    m = re.search(r"(\d+)\s*([A-Za-z]?)", str(f))
    s = "S" if re.search(r"\bS(?:upp|\d)|supplement", str(f), I) else ""
    return f"{s}{m.group(1)}{m.group(2).lower()}" if m else str(f).lower()


def main():
    inv = pd.read_csv(RAIZ / "modelos/imagenes_v02/inventario_figuras.csv", dtype=str, encoding="utf-8-sig")
    fig = inv.drop_duplicates(["pmcid", "figura"]).copy()
    fig["clave_fig"] = fig.figura.map(clave)
    filas = [analizar(p) for p in fig.pie]
    t = pd.concat([fig.reset_index(drop=True), pd.DataFrame(filas)], axis=1)
    t["tipologia"] = t.apply(tipologia, axis=1)
    t["destino"] = t.tipologia.map(DESTINO)
    t["n_paneles_pie"] = t.n_micro + t.n_espectro + t.n_descriptor + t.n_otro
    # contraste con la segmentación visual de Codex
    rec = pd.read_csv(RAIZ / "modelos/imagenes_v02/recortes_v02.csv", dtype=str, encoding="utf-8-sig")
    rec["clave_fig"] = rec.figura.map(clave)
    vis = rec.groupby(["pmcid", "clave_fig"]).agg(n_recortes_visual=("n_recortes_figura", lambda s: int(s.iloc[0])),
                                                     estado_visual=("estado_segmentacion", "first")).reset_index()
    t = t.merge(vis, on=["pmcid", "clave_fig"], how="left")
    # consistencia: el número de recortes coincide con el número de paneles del pie
    t["consistente_visual"] = ((t.n_recortes_visual == t.n_paneles_pie) | ((t.n_paneles_pie == 1) & (t.n_recortes_visual == 1))).where(t.n_recortes_visual.notna())
    cols = ["pmcid", "figura", "clave_fig", "clase_modelo", "fold", "tier", "tipologia", "destino", "n_paneles_pie", "n_etiquetas", "etiquetas", "paneles", "metodo_conteo",
            "n_micro", "n_espectro", "n_descriptor", "n_otro", "plural_micro", "plural_espectro", "indicio_superposicion", "lista_muestras",
            "n_recortes_visual", "estado_visual", "consistente_visual", "tecnicas_en_pie", "archivo_grafico", "pie"]
    t = t[cols]
    t.to_csv(OUT / "tipologia_figuras.csv", index=False, encoding="utf-8-sig")
    for d, nom in [("simple", "figuras_simples"), ("pareja", "figuras_pareja"), ("compuesta", "figuras_compuestas"), ("superpuesto", "espectros_superpuestos"),
                   ("revisar_multiple", "figuras_multiples_sin_etiquetas")]:
        t[t.destino == d].to_csv(OUT / f"{nom}.csv", index=False, encoding="utf-8-sig")
    resumen = {"figuras": int(len(t)), "por_tipologia": t.tipologia.value_counts().to_dict(), "por_destino": t.destino.value_counts().to_dict(),
               "consistencia_visual": {"con_visual": int(t.n_recortes_visual.notna().sum()), "consistentes": int((t.consistente_visual == True).sum())}}
    (OUT / "resumen_tipologia.json").write_text(json.dumps(resumen, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(resumen, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
