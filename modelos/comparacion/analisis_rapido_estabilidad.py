import warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.svm import SVC
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler, normalize
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score

R = Path(r"C:\Users\Hector\Desktop\Kabre_Nano2Predict\Resultados")
RAIZ = Path(r"C:\Users\Hector\Desktop\Quimioinformatica Proyecto\nanotech-technique-cooccurrence")
idx = pd.read_csv(R / "indice_embeddings.csv")
E = {"resnet50": normalize(np.load(R / "emb_resnet50.npy")), "dinov2": normalize(np.load(R / "emb_dinov2_vits14.npy"))}
t = pd.read_csv(RAIZ / "curation/v0.1/tabla_modelo.csv", encoding="utf-8-sig")
d = idx.merge(t, on=["pmcid", "image_file"], how="left", suffixes=("", "_t"))
y = d.clase_modelo.values
tab = pd.DataFrame({"log_tam": np.log10(d.size_nm_mediana.where(d.size_nm_mediana > 0)), "zeta": d.zeta_mV_mediana, "pdi": d.pdi_mediana, "n_desc": d.n_descriptores,
                    "year": d.year, "tem": (d.microscopia == "TEM").astype(int), "sem": (d.microscopia == "SEM").astype(int), "cryo": (d.microscopia == "cryoTEM").astype(int),
                    **{c: d[c] for c in d.columns if c.startswith("tiene_")}})
for c in ("log_tam", "zeta", "pdi"):
    tab[c + "_falta"] = tab[c].isna().astype(int)
Xt = tab.values.astype(float)


def semilla_folds(seed):
    pm = d.pmcid.unique()
    rng = np.random.default_rng(seed)
    rng.shuffle(pm)
    m = {p: i % 5 for i, p in enumerate(pm)}
    return d.pmcid.map(m).values


def evalua(make, X, folds):
    pred = np.empty(len(d), dtype=object)
    for k in range(5):
        m = make(); m.fit(X[folds != k], y[folds != k]); pred[folds == k] = m.predict(X[folds == k])
    return balanced_accuracy_score(y, pred), f1_score(y, pred, average="macro"), accuracy_score(y, pred)


svm = lambda: make_pipeline(PCA(64, random_state=0), SVC(C=1, kernel="rbf", class_weight="balanced"))
mk_t = lambda: make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), LogisticRegression(max_iter=3000, C=1, class_weight="balanced", random_state=0))
def mk_f():
    n = E["dinov2"].shape[1]
    return make_pipeline(ColumnTransformer([("i", make_pipeline(StandardScaler(), PCA(32, random_state=0)), list(range(n))),
                                            ("t", make_pipeline(SimpleImputer(strategy="median"), StandardScaler()), list(range(n, n + Xt.shape[1])))]),
                         LogisticRegression(max_iter=3000, C=0.3, class_weight="balanced", random_state=0))

filas = []
for seed in (1, 2, 3, 4, 5):
    f = semilla_folds(seed)
    filas.append({"semilla": seed,
                  "img_dinov2_SVM_F1": evalua(svm, E["dinov2"], f)[1],
                  "img_ambos_SVM_F1": evalua(svm, np.hstack([E["resnet50"], E["dinov2"]]), f)[1],
                  "medidas_logistica_F1": evalua(mk_t, Xt, f)[1],
                  "fusion_dinov2+medidas_F1": evalua(mk_f, np.hstack([E["dinov2"], Xt]), f)[1]})
r = pd.DataFrame(filas).set_index("semilla")
print(r.round(3).to_string())
print("\nmedia ± desviacion (5 particiones distintas por articulo):")
for c in r.columns:
    print(f"  {c:28s} {r[c].mean():.3f} ± {r[c].std():.3f}")
