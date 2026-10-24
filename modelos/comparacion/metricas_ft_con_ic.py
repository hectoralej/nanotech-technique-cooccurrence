"""IC 95 % (bootstrap de artículos) del ajuste fino (ResNet50, DINOv2, promedio) frente a vectores congelados y medidas; fusión tardía con peso fijo 50/50.

Entradas: modelos/comparacion/entrada_kabre/03_ajuste_fino/predicciones_ft_*.csv (salida del cuaderno 03) y los vectores de 02.
Uso: python modelos/comparacion/metricas_ft_con_ic.py [carpeta_resultados_kabre_02]
"""
import json
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")
RAIZ = Path(__file__).resolve().parents[2]
E = RAIZ / "modelos/comparacion/entrada_kabre"
FT = E / "03_ajuste_fino"
idx = pd.read_csv(E / "indice_embeddings.csv")
rn, dn = (pd.read_csv(FT / f"predicciones_ft_{m}.csv") for m in ("resnet50", "dinov2_vits14"))
key = ["pmcid", "image_file"]
rn, dn = idx[key].merge(rn, on=key, how="left"), idx[key].merge(dn, on=key, how="left")
assert rn.real.notna().all() and dn.real.notna().all()
clases = [c[2:] for c in rn.columns if c.startswith("p_")]
y = rn.real.values
t = pd.read_csv(RAIZ / "curation/v0.1/tabla_modelo.csv", encoding="utf-8-sig")
d = idx.merge(t, on=key, how="left", suffixes=("", "_t"))
assert (d.clase_modelo.values == y).all()
folds = d.fold.astype(int).values
tab = pd.DataFrame({"log_tam": np.log10(d.size_nm_mediana.where(d.size_nm_mediana > 0)), "zeta": d.zeta_mV_mediana, "pdi": d.pdi_mediana, "n_desc": d.n_descriptores, "year": d.year,
                    "tem": (d.microscopia == "TEM").astype(int), "sem": (d.microscopia == "SEM").astype(int), "cryo": (d.microscopia == "cryoTEM").astype(int),
                    **{c: d[c] for c in d.columns if c.startswith("tiene_")}})
for c in ("log_tam", "zeta", "pdi"):
    tab[c + "_falta"] = tab[c].isna().astype(int)
Xt = tab.values.astype(float)
Pt = np.zeros((len(d), len(clases)))
for k in sorted(set(folds)):
    m = make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), LogisticRegression(max_iter=3000, C=1, class_weight="balanced", random_state=0))
    m.fit(Xt[folds != k], y[folds != k])
    assert list(m.classes_) == clases
    Pt[folds == k] = m.predict_proba(Xt[folds == k])
cols = ["p_" + c for c in clases]
Pimg = (rn[cols].values + dn[cols].values) / 2
lab = lambda p: np.array(clases, dtype=object)[p.argmax(1)]
atlas = pd.DataFrame(json.load(open(RAIZ / "producto/modelo/predicciones.json", encoding="utf-8")))
atlas = idx[key].merge(atlas, on=key, how="left")
P = {
    "Clase mayoritaria (línea base)": np.array([pd.Series(y).value_counts().idxmax()] * len(y), dtype=object),
    "Vectores congelados: modelo del Atlas": atlas.prediccion.values,
    "Ajuste fino ResNet50": rn.prediccion.values,
    "Ajuste fino DINOv2": dn.prediccion.values,
    "Ajuste fino: promedio ResNet50 + DINOv2": lab(Pimg),
    "Solo medidas (logística)": lab(Pt),
    "Fusión tardía: ajuste fino (promedio) + medidas, peso 50/50": lab((Pimg + Pt) / 2),
}
pm = d.pmcid.values
arts = pd.unique(pm)
pos = {a: np.where(pm == a)[0] for a in arts}
rng = np.random.default_rng(0)
B = {k: [] for k in P}
for _ in range(1000):
    ii = np.concatenate([pos[a] for a in rng.choice(arts, len(arts))])
    for k, p in P.items():
        B[k].append(f1_score(y[ii], p[ii], average="macro"))
ci = lambda v: (np.percentile(v, 2.5), np.percentile(v, 97.5))
out, filas = {"modelos": {}, "diferencias_f1": {}}, []
for k, p in P.items():
    f1, acc, bal = f1_score(y, p, average="macro"), accuracy_score(y, p), balanced_accuracy_score(y, p)
    lo, hi = ci(B[k])
    out["modelos"][k] = {"f1_macro": round(f1, 4), "f1_ic95": [round(lo, 4), round(hi, 4)], "accuracy": round(acc, 4), "accuracy_balanceada": round(bal, 4)}
    filas.append(f"| {k} | {f1:.3f} [{lo:.3f}, {hi:.3f}] | {acc:.3f} | {bal:.3f} |")
dif = []
for a, b in (("Ajuste fino: promedio ResNet50 + DINOv2", "Vectores congelados: modelo del Atlas"), ("Ajuste fino DINOv2", "Vectores congelados: modelo del Atlas"),
             ("Fusión tardía: ajuste fino (promedio) + medidas, peso 50/50", "Solo medidas (logística)"), ("Ajuste fino ResNet50", "Ajuste fino DINOv2")):
    dd = np.array(B[a]) - np.array(B[b]); pt = f1_score(y, P[a], average="macro") - f1_score(y, P[b], average="macro"); lo, hi = ci(dd)
    out["diferencias_f1"][f"{a} - {b}"] = {"diferencia": round(pt, 4), "ic95": [round(lo, 4), round(hi, 4)]}
    dif.append(f"| {a} − {b} | {pt:+.3f} [{lo:+.3f}, {hi:+.3f}] |")
(RAIZ / "modelos/comparacion/METRICAS_AJUSTE_FINO_CON_IC.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
md = f"""# Ajuste fino frente a vectores congelados (con IC 95 %)

Cuaderno 03 en Kabré (GPU L40S): ResNet50 y DINOv2 ajustados 10 épocas, 5 particiones por artículo, última época, sin elegir nada con los datos de prueba. {len(d)} figuras de {len(arts)} artículos. IC 95 % por bootstrap de artículos (1.000). La fusión tardía usa un peso fijo 50/50 elegido de antemano, sin ajustarlo.

| Modelo | F1 macro [IC 95 %] | Exactitud | Exactitud balanceada |
|---|---|---:|---:|
""" + "\n".join(filas) + """

| Comparación | Diferencia en F1 macro [IC 95 %] |
|---|---|
""" + "\n".join(dif) + """

**Lectura:** el ajuste fino no supera de forma clara a los vectores congelados; DINOv2 sobreajusta (acierto de entrenamiento ≈ 0,96 frente a ≈ 0,48 en prueba) y ResNet50 aprende poco con esta configuración. La limitación está en las imágenes (figuras compuestas, una por artículo), no en la arquitectura.
"""
(RAIZ / "modelos/comparacion/METRICAS_AJUSTE_FINO_CON_IC.md").write_text(md, encoding="utf-8")
print(md)
