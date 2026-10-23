import warnings
warnings.filterwarnings("ignore")
import json
import numpy as np
import pandas as pd
from pathlib import Path
from PIL import Image
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler, normalize
from sklearn.pipeline import make_pipeline
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score

R = Path(r"C:\Users\Hector\Desktop\Kabre_Nano2Predict\Resultados")
RAIZ = Path(r"C:\Users\Hector\Desktop\Quimioinformatica Proyecto\nanotech-technique-cooccurrence")
idx = pd.read_csv(R / "indice_embeddings.csv")
E = {"resnet50": np.load(R / "emb_resnet50.npy"), "dinov2": np.load(R / "emb_dinov2_vits14.npy")}
t = pd.read_csv(RAIZ / "curation/v0.1/tabla_modelo.csv", encoding="utf-8-sig")
d = idx.merge(t, on=["pmcid", "image_file"], how="left", suffixes=("", "_t"))
assert len(d) == len(idx) == E["resnet50"].shape[0]
y = d.clase_modelo.values
folds = d.fold.astype(int).values
classes = sorted(set(y))
base = pd.Series(y).value_counts(normalize=True).max()
print(f"n={len(d)} articulos={d.pmcid.nunique()} linea_base_acc={base:.3f} azar_balanceado=0.250")


def cv(make, X, name):
    pred = np.empty(len(d), dtype=object)
    for k in sorted(set(folds)):
        tr, te = folds != k, folds == k
        m = make()
        m.fit(X[tr], y[tr])
        pred[te] = m.predict(X[te])
    r = dict(acc=accuracy_score(y, pred), bal=balanced_accuracy_score(y, pred), f1=f1_score(y, pred, average="macro"))
    print(f"{name:52s} acc {r['acc']:.3f} | acc.balanceada {r['bal']:.3f} | F1 macro {r['f1']:.3f}")
    return pred, r


def LR(C, cw="balanced"):
    return lambda: make_pipeline(StandardScaler(), LogisticRegression(max_iter=3000, C=C, class_weight=cw, random_state=0))


print("\n== 1. Clasificadores sobre vectores de imagen ==")
res = {}
for nombre, X in (("resnet50", E["resnet50"]), ("dinov2", E["dinov2"]), ("ambos", np.hstack([normalize(E["resnet50"]), normalize(E["dinov2"])]))):
    Xn = normalize(X)
    for C in (0.01, 0.1, 1):
        cv(LR(C), Xn, f"{nombre} logistica C={C} balanceada")
    cv(LR(0.1, None), Xn, f"{nombre} logistica C=0.1 sin pesos")
    cv(lambda: KNeighborsClassifier(n_neighbors=15, metric="cosine", weights="distance"), Xn, f"{nombre} kNN k=15 coseno")
    cv(lambda: make_pipeline(PCA(64, random_state=0), SVC(C=1, kernel="rbf", class_weight="balanced")), Xn, f"{nombre} PCA64 + SVM rbf")
    cv(lambda: make_pipeline(PCA(64, random_state=0), HistGradientBoostingClassifier(max_iter=150, learning_rate=0.05, random_state=0)), Xn, f"{nombre} PCA64 + HistGB")

print("\n== 2. Solo medidas (mismas 2100 imagenes, rasgos del articulo) ==")
tab = pd.DataFrame({
    "log_tam": np.log10(d.size_nm_mediana.where(d.size_nm_mediana > 0)),
    "zeta": d.zeta_mV_mediana, "pdi": d.pdi_mediana, "n_desc": d.n_descriptores, "n_img": d.groupby("pmcid").image_file.transform("count"),
    "year": d.year, "tem": (d.microscopia == "TEM").astype(int), "sem": (d.microscopia == "SEM").astype(int), "cryo": (d.microscopia == "cryoTEM").astype(int),
    **{c: d[c] for c in d.columns if c.startswith("tiene_")}})
for c in ("log_tam", "zeta", "pdi"):
    tab[c + "_falta"] = tab[c].isna().astype(int)
Xt = tab.values.astype(float)
mk_t = lambda: make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), LogisticRegression(max_iter=3000, C=1, class_weight="balanced", random_state=0))
cv(mk_t, Xt, "tabular logistica (medidas+espectros+microscopia)")
cv(lambda: make_pipeline(SimpleImputer(strategy="median"), HistGradientBoostingClassifier(max_iter=200, learning_rate=0.05, random_state=0)), Xt, "tabular HistGB")

print("\n== 3. Fusion: imagen (PCA) + medidas ==")
for nombre in ("dinov2", "resnet50"):
    Xn = normalize(E[nombre])
    for nc in (32, 64):
        def mk(nc=nc):
            from sklearn.compose import ColumnTransformer
            return make_pipeline(ColumnTransformer([("img", make_pipeline(StandardScaler(), PCA(nc, random_state=0)), list(range(Xn.shape[1]))),
                                                    ("tab", make_pipeline(SimpleImputer(strategy="median"), StandardScaler()), list(range(Xn.shape[1], Xn.shape[1] + Xt.shape[1])))]),
                                 LogisticRegression(max_iter=3000, C=0.3, class_weight="balanced", random_state=0))
        cv(mk, np.hstack([Xn, Xt]), f"fusion {nombre} PCA{nc} + medidas (logistica)")

print("\n== 4. Rendimiento por tipo de imagen (dinov2 + logistica C=0.1) ==")
pred, _ = cv(LR(0.1), normalize(E["dinov2"]), "dinov2 base")
dims = []
for _, r in d.iterrows():
    try:
        with Image.open(RAIZ / r.ruta_imagen) as im:
            dims.append(im.size)
    except Exception:
        dims.append((np.nan, np.nan))
d["w"], d["h"] = zip(*dims)
d["pix"] = d.w * d.h
d["aspecto"] = d.w / d.h
d["ok"] = (pred == y)
d["tam_grp"] = pd.qcut(d.pix, 3, labels=["pequena", "mediana", "grande"])
print("acierto por tamano de figura:\n", d.groupby("tam_grp").ok.agg(["mean", "size"]).round(3).to_string())
print("acierto por microscopia:\n", d.groupby("microscopia").ok.agg(["mean", "size"]).round(3).to_string())
d["asp_grp"] = pd.cut(d.aspecto, [0, 0.8, 1.25, 10], labels=["vertical", "cuadrada", "horizontal"])
print("acierto por aspecto:\n", d.groupby("asp_grp").ok.agg(["mean", "size"]).round(3).to_string())
print("\nfiguras por articulo (mediana):", d.groupby("pmcid").image_file.count().median(), "| pix mediana:", int(d.pix.median()))

print("\n== 5. Comprobacion de fuga: el vecino mas cercano de cada imagen, ¿es del mismo articulo? ==")
Xn = normalize(E["dinov2"])
S = Xn @ Xn.T
np.fill_diagonal(S, -1)
nn = S.argmax(1)
print("vecino mas cercano del mismo articulo: %.1f%%" % (100 * (d.pmcid.values[nn] == d.pmcid.values).mean()), "| (si el reparto no fuera por articulo, esto inflaria el resultado)")
