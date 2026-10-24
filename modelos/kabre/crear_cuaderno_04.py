"""Genera 04_recortes_ajuste_fino.ipynb a partir del cuaderno 03 (misma receta de entrenamiento: AdamW por capas, OneCycleLR, precisión mixta,
pesos de clase suavizados, label smoothing, aumentos en GPU, punto de control por época) cambiando los datos: recortes de panel en vez de figuras completas,
más regularización (drop_path) y una comparación por artículo con el cuaderno 03.
Uso: python modelos/kabre/crear_cuaderno_04.py
"""
import ast
import json
from pathlib import Path

D = Path(__file__).resolve().parent
nb = json.loads((D / "03_ajuste_fino.ipynb").read_text(encoding="utf-8"))
src = lambda i: "".join(nb["cells"][i]["source"])


def reemplazar(texto, ini, fin, nuevo):
    a, b = texto.index(ini), texto.index(fin)
    return texto[:a] + nuevo + texto[b:]


c0 = """# 04 · Ajuste fino con RECORTES de panel (CNN y transformer), validación por artículo

**Dónde correrlo:** Jupyter en `nukwa-l40s` (o `nukwa-v100`), **1 nodo, 4 núcleos, 16 GB, 2 h**. Kernel `Python-ML-DL` (PyTorch con CUDA, timm).

**Antes de empezar (una vez):** sube `recortes_v02.zip` (≈ 400 MB) a `~/ondemand/Kabre_Nano2Predict/`; la celda 1 lo descomprime sola la primera vez (deja `recortes/<pmcid>/*.png` y `datos/indice_recortes_entrenamiento.csv`). Si el cuaderno 03 ya corrió, `resultados/03_ajuste_fino/predicciones_ft_*.csv` sirven para la comparación final.

**Qué cambia respecto al 03:**
1. **Datos:** cada muestra es un **recorte de un panel de micrografía de partículas** (separado de su figura compuesta), no la figura completa. Solo recortes `elegible_morfologia` (TEM/SEM/AFM/cryo de partículas, sin bacterias, células ni tejido) con clase de portador y fold por artículo. Un artículo nunca está en dos particiones.
2. **Regularización:** `drop_path_rate = 0,1` (profundidad estocástica) y recorte de aumento más suave (escala 0,7–1,0, para no perder la barra de escala).
3. **Evaluación por recorte y por artículo:** el artículo reúne varios recortes; se promedian las probabilidades por artículo y se compara con el cuaderno 03 **solo en los artículos comunes**, para que la comparación sea justa.
4. **Variante B** (opcional): sin las figuras con contenido biológico, si existe `datos/excluir_bio.csv` (columna `fig_id`).

**Misma receta que el 03:** AdamW con tasa de aprendizaje por capas, OneCycleLR, precisión mixta, pesos de clase suavizados, label smoothing 0,1, aumentos en la GPU, **punto de control por época** (reanudable) y número de épocas fijo: **no se elige nada con los datos de prueba**.

**Tiempo:** la celda 3 mide cuánto tardará (≈ 1 min) y estima el total antes de gastar la sesión. El 03 tardaba 2–4 min por partición y modelo con ≈ 2.100 imágenes; aquí hay ≈ 2,2 veces más muestras, o sea unos 4–9 min por partición y modelo (cálculo, no medida). La celda 4 se detiene sola antes del límite (`TIEMPO_MAX_MIN`).

**Referencias:** exactitud 0,485 / F1 macro 0,466 (vectores congelados, figura completa) y el resultado del 03 (figura completa, ajuste fino). Clase mayoritaria: se imprime en la celda 1.
"""

cabecera = src(1)
nuevo_cargador = '''# --- datos: recortes de panel ---
ZIP = BASE / "recortes_v02.zip"
if ZIP.exists() and not (BASE / "recortes").exists():          # primera vez: descomprime solo
    import zipfile; DATOS.mkdir(exist_ok=True)
    with zipfile.ZipFile(ZIP) as z: z.extractall(BASE)
    (BASE / "indice_recortes_entrenamiento.csv").replace(DATOS / "indice_recortes_entrenamiento.csv")
    print("recortes descomprimidos en", BASE / "recortes")
VARIANTE = "A_todos"          # "A_todos" | "B_sin_biologico" (necesita datos/excluir_bio.csv con la columna fig_id)
REC = BASE / "recortes"
SALIDA = BASE / "resultados" / "04_recortes" / VARIANTE
SALIDA.mkdir(parents=True, exist_ok=True)
t = pd.read_csv(DATOS / "indice_recortes_entrenamiento.csv", encoding="utf-8-sig", dtype=str)
if VARIANTE.startswith("B"):
    ex = pd.read_csv(DATOS / "excluir_bio.csv", encoding="utf-8-sig", dtype=str)
    antes = len(t); t = t[~t.fig_id.isin(set(ex.fig_id))]
    print(f"variante B: se excluyen {antes - len(t)} recortes de figuras con contenido biológico")
t["ruta"] = t.apply(lambda r: REC / str(r["pmcid"]) / str(r["image_file"]), axis=1)
t["existe"] = t["ruta"].map(lambda p: p.exists())
print("recortes en el índice:", len(t), "| que existen en disco:", int(t.existe.sum()))
d = t[t.existe & t.clase_modelo.notna()].reset_index(drop=True)
d["fold"] = d.fold.astype(int)
print("recortes usables:", len(d), "| artículos:", d.pmcid.nunique())
assert len(d) > 1000, "faltan recortes: sube y descomprime recortes_v02.zip en la carpeta base"
assert (d.groupby("pmcid").fold.nunique() == 1).all(), "un artículo está en dos folds"
'''
c1 = reemplazar(cabecera, 't = pd.read_csv(DATOS / "tabla_modelo.csv"', "clases = sorted(", nuevo_cargador)
c1 = c1.replace('DATOS, SALIDA, IMG = BASE / "datos", BASE / "resultados" / "03_ajuste_fino", BASE / "imagenes"', 'DATOS = BASE / "datos"')
c1 = c1.replace("SALIDA.mkdir(parents=True, exist_ok=True)\nT_INICIO", "T_INICIO", 1)
c1 = c1.replace("lienzo.paste(im, ((l - w) // 2, (l - h) // 2))   # figura completa, rellenada a cuadrado", "lienzo.paste(im, ((l - w) // 2, (l - h) // 2))   # recorte, rellenado a cuadrado")
c1 = c1.replace("# Celda 1: GPU, datos y carga de imágenes en memoria", "# Celda 1: GPU, datos (recortes) y carga en memoria")

c2 = src(2)
c2 = c2.replace("TAM = 224\n", "TAM = 224\nDROP_PATH = 0.1                 # regularización nueva respecto al 03\n", 1)
c2 = c2.replace("s = random.uniform(0.6, 1.0)", "s = random.uniform(0.7, 1.0)")
c2 = c2.replace('kw = {"img_size": TAM} if "vit" in MODELOS[corto] else {}', 'kw = {"img_size": TAM} if "vit" in MODELOS[corto] else {}\n    kw["drop_path_rate"] = DROP_PATH')
assert "DROP_PATH" in c2 and "0.7, 1.0" in c2 and 'kw["drop_path_rate"]' in c2

c3 = src(3)
c4 = src(4).replace("TIEMPO_MAX_MIN = 50                      # en nukwa-debug (1 h): 50; en nukwa-l40s (6 h): 330", "TIEMPO_MAX_MIN = 100                     # para una sesión de 2 h; usa 50 si pides 1 h")
assert "TIEMPO_MAX_MIN = 100" in c4

c5 = '''# Celda 5: métricas por recorte y por artículo, y comparación con el cuaderno 03 en los artículos comunes
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score, confusion_matrix
pc = ["p_" + c for c in clases]
def por_articulo(o):
    g = o.groupby("pmcid").agg({**{c: "mean" for c in pc}, "real": "first", "fold": "first"})
    g["prediccion"] = [clases[j] for j in g[pc].values.argmax(1)]
    return g
def metr(real, pred):
    return {"accuracy": round(float(accuracy_score(real, pred)), 4), "accuracy_balanceada": round(float(balanced_accuracy_score(real, pred)), 4), "f1_macro": round(float(f1_score(real, pred, average="macro")), 4)}
resumen = {"variante": VARIANTE, "evaluacion": "5 particiones por articulo; ultima epoca; sin seleccion con datos de prueba", "clases": clases, "epocas": EPOCAS, "drop_path": DROP_PATH,
           "linea_base_clase_mayoritaria_recortes": round(float(base), 4), "modelos": {}}
por_art = {}
for corto in MODELOS:
    fs = [SALIDA / f"ft_{corto}_fold{k}.csv" for k in range(5)]
    if not all(f.exists() for f in fs):
        print(corto, "-> faltan particiones:", [f.name for f in fs if not f.exists()]); continue
    o = pd.concat([pd.read_csv(f) for f in fs]).sort_values(["pmcid", "image_file"]).reset_index(drop=True)
    o.to_csv(SALIDA / f"predicciones_ft_{corto}.csv", index=False, encoding="utf-8")
    art = por_articulo(o); por_art[corto] = art
    r = {"por_recorte": {**metr(o.real, o.prediccion), "n": int(len(o))}, "por_articulo": {**metr(art.real, art.prediccion), "n": int(len(art))},
         "matriz_confusion_recorte": confusion_matrix(o.real, o.prediccion, labels=clases).tolist()}
    ref = BASE / "resultados" / "03_ajuste_fino" / f"predicciones_ft_{corto}.csv"
    if ref.exists():
        a3 = por_articulo(pd.read_csv(ref)); com = art.index.intersection(a3.index)
        r["comparacion_con_03_articulos_comunes"] = {"n_articulos": int(len(com)), "recortes": metr(art.loc[com].real, art.loc[com].prediccion), "figura_completa_03": metr(a3.loc[com].real, a3.loc[com].prediccion)}
    resumen["modelos"][corto] = r
    print(corto, "| por recorte:", r["por_recorte"], "\\n  por artículo:", r["por_articulo"])
    if "comparacion_con_03_articulos_comunes" in r: print("  frente al 03 (mismos artículos):", r["comparacion_con_03_articulos_comunes"])
    print(pd.DataFrame(r["matriz_confusion_recorte"], index=clases, columns=clases).to_string(), "\\n")
if len(por_art) == 2:
    a, b = por_art["resnet50"], por_art["dinov2_vits14"]; com = a.index.intersection(b.index)
    pm = (a.loc[com, pc].values + b.loc[com, pc].values) / 2
    resumen["modelos"]["promedio_resnet_dinov2_por_articulo"] = metr(a.loc[com].real, [clases[j] for j in pm.argmax(1)])
    print("promedio de los dos modelos (por artículo):", resumen["modelos"]["promedio_resnet_dinov2_por_articulo"])
(SALIDA / "metricas_04.json").write_text(json.dumps(resumen, ensure_ascii=False, indent=2), encoding="utf-8")
print("\\nArchivos para descargar en", SALIDA, ":")
for p in sorted(SALIDA.glob("*")): print(" ", p.name, f"{p.stat().st_size/1e6:.1f} MB")
print("OK celda 5. Descarga metricas_04.json y predicciones_ft_*.csv y pégaselos a Claude.")
'''
for nombre, cod in (("c1", c1), ("c2", c2), ("c3", c3), ("c4", c4), ("c5", c5)):
    ast.parse(cod)                                   # sintaxis válida
nuevo = json.loads(json.dumps(nb))
nuevo["cells"][0]["source"] = c0.splitlines(keepends=True)
for i, cod in zip(range(1, 6), (c1, c2, c3, c4, c5)):
    nuevo["cells"][i]["source"] = cod.splitlines(keepends=True)
    nuevo["cells"][i]["outputs"] = []; nuevo["cells"][i]["execution_count"] = None
(D / "04_recortes_ajuste_fino.ipynb").write_text(json.dumps(nuevo, ensure_ascii=False, indent=1), encoding="utf-8")
print("cuaderno 04 escrito;", len(nuevo["cells"]), "celdas; sintaxis OK")
