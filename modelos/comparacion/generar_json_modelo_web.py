"""Genera los tres JSON del panel del modelo del Atlas (producto/modelo/) con predicciones REALES fuera de muestra.

Modelo: vectores DINOv2 + ResNet50 (calculados en Kabre, cuaderno 02) -> PCA(64) -> SVM rbf (probabilidades de Platt), 5 particiones por articulo
(columna fold de curation/v0.1/tabla_modelo.csv). Cada prediccion viene de la particion en la que esa imagen fue de prueba.
Vecinos: 5 imagenes mas parecidas por similitud coseno (DINOv2), excluyendo imagenes del mismo articulo.

Uso: python modelos/comparacion/generar_json_modelo_web.py [carpeta_resultados_kabre]
"""
import json
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.metrics import accuracy_score, balanced_accuracy_score, confusion_matrix, f1_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import normalize
from sklearn.svm import SVC

warnings.filterwarnings("ignore")
RAIZ = Path(__file__).resolve().parents[2]
R = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / "Desktop" / "Kabre_Nano2Predict" / "Resultados"
SALIDA = RAIZ / "producto" / "modelo"
SALIDA.mkdir(parents=True, exist_ok=True)

idx = pd.read_csv(R / "indice_embeddings.csv")
din, res = normalize(np.load(R / "emb_dinov2_vits14.npy")), normalize(np.load(R / "emb_resnet50.npy"))
X = np.hstack([res, din])
assert len(idx) == len(X)
y = idx.clase_modelo.values
folds = idx.fold.astype(int).values
clases = sorted(set(y))

pred = np.empty(len(idx), dtype=object)
conf = np.zeros(len(idx))
for k in sorted(set(folds)):
    tr, te = folds != k, folds == k
    m = make_pipeline(PCA(64, random_state=0), SVC(C=1, kernel="rbf", class_weight="balanced", probability=True, random_state=0))
    m.fit(X[tr], y[tr])
    p = m.predict_proba(X[te])
    pred[te] = m.classes_[p.argmax(1)]
    conf[te] = p.max(1)

base = pd.Series(y).value_counts(normalize=True).max()
cm = confusion_matrix(y, pred, labels=clases)
metricas = {
    "prueba": False,
    "tarea": "clase de portador a partir de la micrografía (figura completa)",
    "backbone": "DINOv2 ViT-S/14 + ResNet50 congelados (vectores) → PCA 64 → SVM rbf",
    "evaluacion": "5 particiones por artículo (columna fold); cada predicción es fuera de muestra",
    "n_imagenes": int(len(idx)), "n_articulos": int(idx.pmcid.nunique()),
    "clases": clases,
    "accuracy": round(float(accuracy_score(y, pred)), 4),
    "accuracy_balanceada": round(float(balanced_accuracy_score(y, pred)), 4),
    "f1_macro": round(float(f1_score(y, pred, average="macro")), 4),
    "linea_base": round(float(base), 4),
    "matriz_confusion": cm.tolist(),
    "nota": "Resultado exploratorio: se probaron varias variantes sobre las mismas particiones; la cifra puede ser algo optimista. La clase mayoritaria da exactitud 0,454 pero F1 macro ~0,16.",
}
(SALIDA / "metricas.json").write_text(json.dumps(metricas, ensure_ascii=False, indent=2), encoding="utf-8")

preds = [{"pmcid": a, "image_file": b, "prediccion": c, "confianza": round(float(d), 4), "real": r}
         for a, b, c, d, r in zip(idx.pmcid, idx.image_file, pred, conf, y)]
(SALIDA / "predicciones.json").write_text(json.dumps(preds, ensure_ascii=False), encoding="utf-8")

S = din @ din.T
pm = idx.pmcid.values
vec = {}
for i in range(len(idx)):
    s = S[i].copy()
    s[pm == pm[i]] = -1                                   # nunca vecinos del mismo artículo
    top = np.argpartition(-s, 5)[:5]
    top = top[np.argsort(-s[top])]
    vec[f"{idx.pmcid[i]}/{idx.image_file[i]}"] = [{"pmcid": idx.pmcid[j], "image_file": idx.image_file[j], "similitud": round(float(s[j]), 4)} for j in top]
(SALIDA / "similares.json").write_text(json.dumps(vec, ensure_ascii=False), encoding="utf-8")

print("exactitud", metricas["accuracy"], "| balanceada", metricas["accuracy_balanceada"], "| F1 macro", metricas["f1_macro"], "| base", metricas["linea_base"])
for p in sorted(SALIDA.iterdir()):
    print(" ", p.name, f"{p.stat().st_size/1e6:.2f} MB")
