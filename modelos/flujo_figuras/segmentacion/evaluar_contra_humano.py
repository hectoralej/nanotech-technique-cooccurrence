import json, sys
import numpy as np, pandas as pd
sys.stdout.reconfigure(encoding="utf-8")
D = "modelos/flujo_figuras/segmentacion/"
h = json.load(open(D + "anotador/cajas_humano_Hector.json", encoding="utf-8-sig")); h.pop("_meta")
hk = json.load(open(D + "cajas/resultados/claude/C001.json", encoding="utf-8-sig"))


def iou(a, b):
    ix = max(0, min(a[2], b[2]) - max(a[0], b[0])); iy = max(0, min(a[3], b[3]) - max(a[1], b[1])); i = ix * iy
    u = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - i
    return i / u if u > 0 else 0


for excl in ([], ["PMC10005067|Figure 5"], ["PMC10005067|Figure 5", "PMC10002596|Figure 9"]):
    v, t = [], []
    for fid, pr in h.items():
        if fid not in hk or fid in excl:
            continue
        po = hk[fid]; libres = list(range(len(po)))
        for a in pr:
            if not libres:
                break
            j = max(libres, key=lambda k: iou(a["caja"], po[k]["caja"])); libres.remove(j)
            v.append(iou(a["caja"], po[j]["caja"])); t.append(a["tipo"] == po[j]["tipo"])
    print("excluyendo", excl or "nada", "| paneles", len(v), "| IoU medio", round(float(np.mean(v)), 2), "| >=0.7:", f"{np.mean(np.array(v) >= 0.7):.0%}", "| tipo igual:", f"{np.mean(t):.0%}")
plan = pd.read_csv(D + "cajas/plan_cajas.csv", dtype=str, encoding="utf-8-sig").set_index("fig_id")
ok = 0
for fid, p in h.items():
    hu = sum(x["tipo"] in ("micro", "espectro") for x in p); cu = int(plan.loc[fid, "n_micro"]) + int(plan.loc[fid, "n_espectro"]); ok += hu == cu
print("figuras con igual nº de paneles útiles (micro+espectro):", ok, "/ 22")
tm = pd.read_csv("curation/v0.1/tabla_modelo.csv", dtype=str, encoding="utf-8-sig")
print("variant:", tm.variant.value_counts().head(12).to_dict())
print("microscopia:", tm.microscopia.value_counts().head(10).to_dict())
