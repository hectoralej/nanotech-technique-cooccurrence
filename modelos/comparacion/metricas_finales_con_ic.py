"""Métricas de la clase de portador con IC 95 % (bootstrap de artículos) para las variantes de imagen, medidas y fusión.

Mismas 2.100 figuras y mismos folds por artículo (indice_embeddings.csv / tabla_modelo.csv). Cada predicción es fuera de muestra.
Uso: python modelos/comparacion/metricas_finales_con_ic.py [carpeta_resultados_kabre]
Escribe modelos/comparacion/METRICAS_CON_IC.md y .json
"""
import json
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler, normalize
from sklearn.svm import SVC

warnings.filterwarnings("ignore")
RAIZ = Path(__file__).resolve().parents[2]
R = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / "Desktop" / "Kabre_Nano2Predict" / "Resultados"
idx = pd.read_csv(R / "indice_embeddings.csv")
din, res = normalize(np.load(R / "emb_dinov2_vits14.npy")), normalize(np.load(R / "emb_resnet50.npy"))
Ximg = np.hstack([res, din])
t = pd.read_csv(RAIZ / "curation/v0.1/tabla_modelo.csv", encoding="utf-8-sig")
d = idx.merge(t, on=["pmcid", "image_file"], how="left", suffixes=("", "_t"))
y = d.clase_modelo.values
folds = d.fold.astype(int).values
tab = pd.DataFrame({"log_tam": np.log10(d.size_nm_mediana.where(d.size_nm_mediana > 0)), "zeta": d.zeta_mV_mediana, "pdi": d.pdi_mediana, "n_desc": d.n_descriptores, "year": d.year,
                    "tem": (d.microscopia == "TEM").astype(int), "sem": (d.microscopia == "SEM").astype(int), "cryo": (d.microscopia == "cryoTEM").astype(int),
                    **{c: d[c] for c in d.columns if c.startswith("tiene_")}})
for c in ("log_tam", "zeta", "pdi"):
    tab[c + "_falta"] = tab[c].isna().astype(int)
Xt = tab.values.astype(float)
n_img = Ximg.shape[1]


def oof(make, X):
    p = np.empty(len(d), dtype=object)
    for k in sorted(set(folds)):
        m = make(); m.fit(X[folds != k], y[folds != k]); p[folds == k] = m.predict(X[folds == k])
    return p


svm = lambda: make_pipeline(PCA(64, random_state=0), SVC(C=1, kernel="rbf", class_weight="balanced"))
logi = lambda: make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), LogisticRegression(max_iter=3000, C=1, class_weight="balanced", random_state=0))
fus = lambda: make_pipeline(ColumnTransformer([("i", make_pipeline(StandardScaler(), PCA(32, random_state=0)), list(range(n_img))),
                                               ("t", make_pipeline(SimpleImputer(strategy="median"), StandardScaler()), list(range(n_img, n_img + Xt.shape[1])))]),
                            LogisticRegression(max_iter=3000, C=0.3, class_weight="balanced", random_state=0))
atlas = pd.DataFrame(json.load(open(RAIZ / "producto/modelo/predicciones.json", encoding="utf-8")))
atlas = idx[["pmcid", "image_file"]].merge(atlas, on=["pmcid", "image_file"], how="left")
assert atlas.prediccion.notna().all()

P = {
    "Clase mayoritaria (línea base)": np.array([pd.Series(y).value_counts().idxmax()] * len(y), dtype=object),
    "Imagen: modelo del Atlas (SVM con probabilidades)": atlas.prediccion.values,
    "Imagen: SVM, regla de decisión directa (ResNet50 + DINOv2)": oof(svm, Ximg),
    "Solo medidas (logística)": oof(logi, Xt),
    "Fusión: imagen (PCA 32) + medidas (logística)": oof(fus, np.hstack([Ximg, Xt])),
}
pm = d.pmcid.values
arts = pd.unique(pm)
pos = {a: np.where(pm == a)[0] for a in arts}
rng = np.random.default_rng(0)
B = 1000
res_b = {k: {"acc": [], "bal": [], "f1": []} for k in P}
for _ in range(B):
    ii = np.concatenate([pos[a] for a in rng.choice(arts, len(arts))])
    for k, p in P.items():
        res_b[k]["acc"].append(accuracy_score(y[ii], p[ii])); res_b[k]["bal"].append(balanced_accuracy_score(y[ii], p[ii])); res_b[k]["f1"].append(f1_score(y[ii], p[ii], average="macro"))
ci = lambda v: (float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5)))
out = {"n_imagenes": int(len(d)), "n_articulos": int(len(arts)), "evaluacion": "5 particiones por articulo; IC 95 % por bootstrap de articulos (1.000); predicciones fuera de muestra", "modelos": {}, "diferencias_pareadas_f1": {}}
filas = []
for k, p in P.items():
    f1, acc, bal = f1_score(y, p, average="macro"), accuracy_score(y, p), balanced_accuracy_score(y, p)
    out["modelos"][k] = {"f1_macro": round(f1, 4), "f1_ic95": [round(x, 4) for x in ci(res_b[k]["f1"])], "accuracy": round(acc, 4), "accuracy_ic95": [round(x, 4) for x in ci(res_b[k]["acc"])],
                         "accuracy_balanceada": round(bal, 4), "balanceada_ic95": [round(x, 4) for x in ci(res_b[k]["bal"])]}
    filas.append(f"| {k} | {f1:.3f} [{ci(res_b[k]['f1'])[0]:.3f}, {ci(res_b[k]['f1'])[1]:.3f}] | {acc:.3f} [{ci(res_b[k]['acc'])[0]:.3f}, {ci(res_b[k]['acc'])[1]:.3f}] | {bal:.3f} [{ci(res_b[k]['bal'])[0]:.3f}, {ci(res_b[k]['bal'])[1]:.3f}] |")
dif = []
for a, b in (("Fusión: imagen (PCA 32) + medidas (logística)", "Solo medidas (logística)"), ("Fusión: imagen (PCA 32) + medidas (logística)", "Imagen: modelo del Atlas (SVM con probabilidades)"),
             ("Solo medidas (logística)", "Imagen: modelo del Atlas (SVM con probabilidades)"), ("Imagen: SVM, regla de decisión directa (ResNet50 + DINOv2)", "Imagen: modelo del Atlas (SVM con probabilidades)")):
    dd = np.array(res_b[a]["f1"]) - np.array(res_b[b]["f1"])
    pt = f1_score(y, P[a], average="macro") - f1_score(y, P[b], average="macro")
    out["diferencias_pareadas_f1"][f"{a} - {b}"] = {"diferencia": round(pt, 4), "ic95": [round(x, 4) for x in ci(dd)]}
    dif.append(f"| {a} − {b} | {pt:+.3f} [{ci(dd)[0]:+.3f}, {ci(dd)[1]:+.3f}] |")
(RAIZ / "modelos/comparacion/METRICAS_CON_IC.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
md = f"""# Métricas de la clase de portador con intervalos de confianza

{len(d)} figuras de {len(arts)} artículos, 4 clases, 5 particiones por artículo; predicciones fuera de muestra. IC 95 % por bootstrap de artículos (1.000 remuestreos; no incluye la incertidumbre de reentrenar ni la de haber probado varias variantes). Script: `modelos/comparacion/metricas_finales_con_ic.py`.

| Modelo | F1 macro [IC 95 %] | Exactitud [IC 95 %] | Exactitud balanceada [IC 95 %] |
|---|---|---|---|
""" + "\n".join(filas) + """

**Diferencias pareadas en F1 macro** (mismos remuestreos):

| Comparación | Diferencia [IC 95 %] |
|---|---|
""" + "\n".join(dif) + """

## Cuál cifra usar
- **Modelo de imagen que muestra el Atlas:** la fila «modelo del Atlas». Sus predicciones salen de un SVM con probabilidades (`predicciones.json`); es la cifra que debe coincidir con `producto/modelo/metricas.json`.
- **Misma entrada con otra regla de decisión (SVM directo):** da un F1 más alto porque la regla directa respeta el balanceo de clases; es una **variante exploratoria**, no el modelo publicado. No se cita como cifra principal.
- Todo es exploratorio: se probaron varias variantes sobre las mismas particiones y la mejor es algo optimista. El ajuste fino (cuaderno 03) producirá la cifra de imagen final, que sustituye a estas.
"""
(RAIZ / "modelos/comparacion/METRICAS_CON_IC.md").write_text(md, encoding="utf-8")
print(md)
