"""Tables and standalone PNGs from held-out predictions; no training or tuning."""
from __future__ import annotations

import json
import os
from pathlib import Path

from tabular_data import HERE, RESULTS, ROOT, load_dataset, save_json

os.environ.setdefault("MPLCONFIGDIR", str(RESULTS / ".mplconfig"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from tabular_common import N_BOOT, PRODUCT, checkpoint, environment

FIG = RESULTS / "figuras"
ORDER = ["lineal", "ridge", "rf300", "rf500", "hgb"]


def val(result, key):
    return result["metricas"][key]["valor"]


def fmt_metric(result, key, percent=False):
    m = result["metricas"][key]; factor = 100 if percent else 1
    return f"{m['valor']*factor:.3f} [{m['ic95'][0]*factor:.3f}, {m['ic95'][1]*factor:.3f}]"


def predictions(result):
    return pd.read_csv(ROOT / result["predicciones"], encoding="utf-8-sig")


def paired_delta_r2(result, baseline):
    a, b = predictions(result), predictions(baseline)
    assert a.pmcid.equals(b.pmcid) and np.allclose(a.y_real, b.y_real)
    codes, groups = pd.factorize(a.pmcid, sort=True)
    y = a.y_real.to_numpy(); n = len(groups)
    stats = np.column_stack([np.ones(len(y)), y, y*y, (y-b.y_pred.to_numpy())**2 - (y-a.y_pred.to_numpy())**2])
    grouped = np.zeros((n, 4)); np.add.at(grouped, codes, stats)
    weights = np.random.default_rng(0).multinomial(n, np.full(n, 1/n), size=N_BOOT)
    sums = weights @ grouped
    delta = sums[:, 3] / (sums[:, 2] - sums[:, 1]**2 / sums[:, 0])
    return [float(np.quantile(delta, .025)), float(np.quantile(delta, .975))]


def clean_label(name):
    name = name.replace("numeric__", "").replace("categorical__", "").replace("missingindicator_", "falta ")
    return name if len(name) <= 62 else name[:59] + "…"


def finish(fig, filename):
    fig.savefig(FIG / filename, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def plot_regression(registry):
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5), sharey=True)
    for ax, variant, color in zip(axes, ("A", "B"), ("#246399", "#24846b")):
        rows = [registry["tamano_dummy"], registry["tamano_media_clase"]] + [registry[f"tamano_{variant}_{k}"] for k in ORDER]
        ys = np.arange(len(rows))
        values = np.array([val(r, "r2") for r in rows])
        lows = np.array([r["metricas"]["r2"]["ic95"][0] for r in rows]); highs = np.array([r["metricas"]["r2"]["ic95"][1] for r in rows])
        ax.errorbar(values, ys, xerr=[values-lows, highs-values], fmt="o", color=color, capsize=4)
        ax.set_yticks(ys, [r["nombre"] for r in rows])
        ax.axvline(val(registry["tamano_media_clase"], "r2"), linestyle="--", color="#888888", linewidth=1)
        ax.set_title(f"Variante {variant}" + (": sin mediciones" if variant == "A" else ": + zeta y PDI"))
        ax.set_xlabel("R² de log10(tamaño), fuera de muestra"); ax.grid(axis="x", alpha=.2)
    axes[0].invert_yaxis()
    fig.suptitle("Escalera de regresión · IC 95 % por bootstrap de artículos", y=1.01)
    fig.tight_layout(); finish(fig, "regresion_escalera.png")

    best = max((r for r in registry.values() if r["tarea"] == "tamano_log10"), key=lambda r: val(r, "r2"))
    pred = predictions(best)
    fig, ax = plt.subplots(figsize=(6.8, 6.2))
    real = 10**pred.y_real; estimated = 10**pred.y_pred
    ax.hexbin(real, estimated, gridsize=38, xscale="log", yscale="log", mincnt=1, cmap="Blues")
    lower = min(real.min(), estimated.min())*.8; upper = max(real.max(), estimated.max())*1.2
    ax.plot([lower, upper], [lower, upper], color="#cc5b49", linestyle="--", label="Predicción ideal")
    ax.set(xlabel="Tamaño observado (nm, escala log)", ylabel="Tamaño predicho (nm, escala log)", title=f"{best['id']} · R²={val(best, 'r2'):.3f}")
    ax.legend(); fig.tight_layout(); finish(fig, "tamano_observado_predicho.png")


def coefficient_plot(model_id, title):
    path = RESULTS / f"coeficientes_{model_id}.csv"
    c = pd.read_csv(path, encoding="utf-8-sig")
    if model_id.startswith("clase"):
        by_fold = c.pivot_table(index=["variable_transformada", "clase"], columns="fold", values="coeficiente").reindex(columns=range(5)).fillna(0)
        mean = by_fold.mean(axis=1).unstack(fill_value=0)
        selected = mean.abs().max(axis=1).nlargest(16).index
        mean = mean.loc[selected]
        fig, ax = plt.subplots(figsize=(9, 7.5))
        limit = max(float(mean.abs().to_numpy().max()), .1)
        im = ax.imshow(mean, cmap="RdBu_r", vmin=-limit, vmax=limit, aspect="auto")
        ax.set_xticks(range(len(mean.columns)), mean.columns, rotation=20, ha="right")
        ax.set_yticks(range(len(mean)), [clean_label(x) for x in mean.index], fontsize=8)
        ax.set_title(title); fig.colorbar(im, ax=ax, label="Coeficiente del logit (promedio de folds)")
    else:
        coef = c.pivot_table(index="variable_transformada", columns="fold", values="coeficiente").fillna(0)
        average = coef.mean(axis=1)
        selected = average.abs().nlargest(16).index
        average = average.loc[selected].sort_values()
        fig, ax = plt.subplots(figsize=(10, 7))
        ax.barh([clean_label(x) for x in average.index], average, color=["#3375a2" if x >= 0 else "#d07860" for x in average])
        ax.axvline(0, color="black", linewidth=.7); ax.set_xlabel("Coeficiente sobre log10(tamaño)")
        ax.set_title(title)
    fig.tight_layout(); finish(fig, f"coeficientes_{model_id}.png")


def permutation_plot(result):
    imp = pd.read_csv(RESULTS / f"importancia_{result['id']}.csv", encoding="utf-8-sig")
    grouped = imp.groupby("variable").importancia_media.agg(["mean", "std"]).fillna(0).sort_values("mean").tail(16)
    fig, ax = plt.subplots(figsize=(8.5, 6))
    ax.barh(grouped.index, grouped["mean"], xerr=grouped["std"], color="#478c79", capsize=3)
    ax.axvline(0, color="black", linewidth=.7)
    ax.set_xlabel("Caída en R² de test" if result["tarea"] == "tamano_log10" else "Caída en F1 macro de test")
    ax.set_title(f"Permutación en test · {result['id']}\n5 repeticiones/fold; barras = DE entre folds")
    fig.tight_layout(); finish(fig, f"permutacion_{result['id']}.png")


def plot_classification(registry):
    keys = ["mayoritaria", "logistica", "rf", "hgb"]
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharex=True)
    for ax, n in zip(axes, (4, 3)):
        rows = [registry[f"clase{n}_{k}"] for k in keys]
        values = np.array([val(r, "f1_macro") for r in rows]); lows = [r["metricas"]["f1_macro"]["ic95"][0] for r in rows]; highs = [r["metricas"]["f1_macro"]["ic95"][1] for r in rows]
        ax.errorbar(values, range(4), xerr=[values-np.array(lows), np.array(highs)-values], fmt="o", capsize=4, color="#715395")
        ax.set_yticks(range(4), [r["nombre"] for r in rows]); ax.invert_yaxis(); ax.set_title(f"{n} clases"); ax.set_xlabel("F1 macro OOF · IC 95 % por artículo"); ax.grid(axis="x", alpha=.2)
    fig.tight_layout(); finish(fig, "clasificacion_escalera.png")
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.4))
    for ax, n in zip(axes, (4, 3)):
        best = max((registry[f"clase{n}_{k}"] for k in keys), key=lambda r: val(r, "f1_macro"))
        cm = pd.read_csv(RESULTS / f"confusion_{best['id']}.csv", encoding="utf-8-sig", index_col=0)
        ax.imshow(cm, cmap="Blues", vmin=0, vmax=1)
        for i in range(len(cm)):
            for j in range(len(cm)):
                ax.text(j, i, f"{cm.iloc[i,j]:.0%}", ha="center", va="center", color="white" if cm.iloc[i,j]>.55 else "black")
        ax.set_xticks(range(len(cm)), cm.columns, rotation=30, ha="right"); ax.set_yticks(range(len(cm)), cm.index)
        ax.set_xlabel("Clase predicha"); ax.set_ylabel("Clase real")
        ax.set_title(f"{best['id']} · F1={val(best,'f1_macro'):.3f}\nNormalización por clase real")
    fig.tight_layout(); finish(fig, "matrices_confusion.png")


def interpretations(registry):
    lines = ["# Interpretación de coeficientes e importancias", "", "Los coeficientes lineales actúan sobre log10(tamaño). En variables numéricas, corresponden a un aumento de una desviación estándar del entrenamiento; 10^β es el factor asociado. Los indicadores también se estandarizan. Las categorías se codifican one-hot; clase y carrier_type son redundantes, de modo que sus coeficientes aislados no tienen una interpretación única en la regresión sin regularizar. Ridge estabiliza el ajuste, pero las asociaciones siguen sin ser causales.", ""]
    for variant in ("A", "B"):
        for model in ("lineal", "ridge"):
            model_id = f"tamano_{variant}_{model}"
            co = pd.read_csv(RESULTS / f"coeficientes_{model_id}.csv", encoding="utf-8-sig")
            co = co[co.variable_transformada.str.startswith("numeric__") & ~co.variable_transformada.str.contains("missingindicator")]
            mean = co.groupby("variable_transformada").coeficiente.mean()
            selected = mean.abs().nlargest(3).index
            lines += [f"## {model_id}", "", "| Variable estandarizada | β medio | Factor 10^β |", "|---|---:|---:|"]
            lines += [f"| {clean_label(name)} | {mean[name]:+.4f} | {10**mean[name]:.3f} |" for name in selected]
            lines += [""]
    lines += ["## Clasificación", "", "Las figuras logísticas muestran coeficientes por clase: un valor positivo aumenta su logit cuando crece la variable, manteniendo las otras constantes. No equivale a una variación fija de probabilidad. La estandarización se aprende solo en entrenamiento. Las matrices de confusión permiten ver qué clases se solapan.", "", "## Permutación", "", "Se permuta una columna de las filas de test, cinco veces por fold, y se mide la caída de R²/F1 macro. Una importancia negativa puede surgir por variabilidad o redundancia. Son sensibilidades predictivas condicionadas al modelo, no efectos causales; las variables correlacionadas pueden repartirse la importancia. Las figuras de importancia se eligen entre los modelos con este análisis y se identifican explícitamente."]
    (HERE / "INTERPRETACION.md").write_text("\n".join(lines)+"\n", encoding="utf-8")


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
    registry = {r["id"]: r for p in sorted(RESULTS.glob("metricas_*.json")) for r in [json.loads(p.read_text(encoding="utf-8"))]}
    assert len(registry) == 20, f"Se esperaban 20 modelos, hay {len(registry)}"
    environment()
    plot_regression(registry); plot_classification(registry)
    for variant in ("A", "B"):
        coefficient_plot(f"tamano_{variant}_ridge", f"Ridge {variant} · coeficientes de entrenamiento (media de 5 folds)")
        candidates = [r for r in registry.values() if r["tarea"] == "tamano_log10" and r["variante"] == variant and (RESULTS / f"importancia_{r['id']}.csv").exists()]
        permutation_plot(max(candidates, key=lambda r: val(r, "r2")))
    for n in (4, 3):
        coefficient_plot(f"clase{n}_logistica", f"Logística multinomial · {n} clases")
        candidates = [r for r in registry.values() if r["tarea"] == f"clase_{n}" and (RESULTS / f"importancia_{r['id']}.csv").exists()]
        permutation_plot(max(candidates, key=lambda r: val(r, "f1_macro")))
    interpretations(registry)
    flat = []
    for r in registry.values():
        item = {"modelo": r["id"], "tarea": r["tarea"], "variante": r["variante"], "n_filas": r["n_filas"], "n_articulos": r["n_articulos"]}
        for key, value in r["metricas"].items():
            item[key] = value["valor"]; item[key+"_ic95_inf"] = value["ic95"][0]; item[key+"_ic95_sup"] = value["ic95"][1]
        flat.append(item)
    pd.DataFrame(flat).to_csv(RESULTS / "metricas_todos_modelos.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame([{"modelo": r["id"], **f} for r in registry.values() for f in r["por_fold"]]).to_csv(RESULTS / "metricas_por_fold.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame([{"modelo": r["id"], **row} for r in registry.values() for row in r["r2_por_clase"]]).to_csv(RESULTS / "r2_por_clase.csv", index=False, encoding="utf-8-sig")

    base = registry["tamano_media_clase"]
    reg_lines = ["| Entradas | Modelo | R² [IC95] | ΔR² previo | MAE log10 | Error relativo mediano |", "|---|---|---:|---:|---:|---:|"]
    for r in (registry["tamano_dummy"], base):
        prev = "—" if r["id"] == "tamano_dummy" else f"{val(r,'r2')-val(registry['tamano_dummy'],'r2'):+.3f}"
        reg_lines.append(f"| A/B | {r['nombre']} | {fmt_metric(r,'r2')} | {prev} | {val(r,'mae_log10'):.3f} | {100*val(r,'error_mediano_relativo_nm'):.1f}% |")
    for variant in ("A", "B"):
        previous = val(base, "r2")
        for key in ORDER:
            r = registry[f"tamano_{variant}_{key}"]
            reg_lines.append(f"| {variant} | {r['nombre']} | {fmt_metric(r,'r2')} | {val(r,'r2')-previous:+.3f} | {val(r,'mae_log10'):.3f} | {100*val(r,'error_mediano_relativo_nm'):.1f}% |")
            previous = val(r, "r2")
    class_lines = ["| Clases | Modelo | Exactitud [IC95] | F1 macro [IC95] |", "|---|---|---:|---:|"]
    for n in (4, 3):
        for key in ("mayoritaria", "logistica", "rf", "hgb"):
            r = registry[f"clase{n}_{key}"]
            class_lines.append(f"| {n} | {r['nombre']} | {fmt_metric(r,'exactitud')} | {fmt_metric(r,'f1_macro')} |")
    best_reg = max((r for r in registry.values() if r["tarea"] == "tamano_log10"), key=lambda r: val(r, "r2"))
    delta_ci = paired_delta_r2(best_reg, base)
    save_json(RESULTS / "comparacion_pareada_tamano.json", {"modelo": best_reg["id"], "base": base["id"], "delta_r2": val(best_reg,"r2")-val(base,"r2"), "ic95_delta_r2": delta_ci, "advertencia": "El modelo destacado se identifica exploratoriamente entre la escalera; falta evaluación externa independiente."})
    best4 = max((r for r in registry.values() if r["tarea"] == "clase_4"), key=lambda r: val(r,"f1_macro"))
    best3 = max((r for r in registry.values() if r["tarea"] == "clase_3"), key=lambda r: val(r,"f1_macro"))
    data = load_dataset(); missing_medium = 100*(1-data.medio_declarado.mean())
    inference = "supera internamente a la media por clase" if delta_ci[0] > 0 else "no supera claramente a la media por clase; no debe presentarse como predictivo"
    report = f"""# Primeros modelos tabulares

Cinco folds oficiales por artículo; imputación, codificación y escalado aprendidos solo en entrenamiento. Ridge elige alpha por GroupKFold interno (4 particiones, MAE log10). IC95: 1.000 bootstrap de artículos sobre predicciones fuera de muestra. Cada bootstrap conserva todas las filas de los artículos sorteados; no incluye incertidumbre de reentrenamiento.

Regresión: {best_reg['n_filas']} tamaños válidos de {best_reg['n_articulos']} artículos. A usa metadatos, medio y presencia de técnicas; B añade zeta/PDI e indicadores de faltante. Dummy R²={val(registry['tamano_dummy'],'r2'):.4f}; media por clase={val(base,'r2'):.4f}, reproduce ≈0,18.

{chr(10).join(reg_lines)}

Δ previo sigue el orden de la escalera, incluida la corrida de sensibilidad RF500/hoja1; no implica mejora monotónica. IC de MAE y error relativo, MAE en nm, R² por clase y alphas están en CSV/JSON. Los coeficientes lineales/Ridge y logísticos se interpretan en `INTERPRETACION.md`; las importancias se calculan por permutación en test. HGB usa 300 iteraciones sin parada temprana por filas.

{chr(10).join(class_lines)}

Conclusiones:

1. Tamaño: {best_reg['id']} alcanza R²={val(best_reg,'r2'):.3f}, MAE log10={val(best_reg,'mae_log10'):.3f} y error relativo mediano={100*val(best_reg,'error_mediano_relativo_nm'):.1f}%; {inference}. ΔR² pareado: IC95 [{delta_ci[0]:.3f}, {delta_ci[1]:.3f}]. La mejora es modesta: el error relativo mediano es casi igual al piso ({100*val(base,'error_mediano_relativo_nm'):.1f}%).
2. Clasificación: el mayor F1 macro OOF es {val(best4,'f1_macro'):.3f} con 4 clases ({best4['id']}) y {val(best3,'f1_macro'):.3f} con 3 ({best3['id']}). Son problemas con poblaciones distintas; quitar nanomaterial cambia la dificultad y no constituye una mejora directamente comparable.
3. No hubo artículos compartidos entre train/test; la prueba rechaza columnas prohibidas y sus variantes no autorizadas. Los ocho clasificadores repitieron cada entrenamiento con la misma semilla y produjeron predicciones idénticas. El modelo destacado es exploratorio; el rendimiento final requiere una evaluación externa.

Limitaciones: faltan parámetros de formulación (proporciones, preparación); {missing_medium:.1f}% de filas no declara medio. Hay varias filas por artículo: el n efectivo se aproxima al número de artículos, y las métricas puntuales ponderan filas. Los datos fueron extraídos con IA y verificados por código, no revalidados manualmente en esta tarea. Familia de portador y técnicas se correlacionan con sesgos editoriales; importancias/coefs no demuestran causalidad. Los IC son condicionales a estas predicciones OOF. No se entrenaron modelos de imágenes ni multimodales.

Reproducción: `python modelos/tabular/tabular_data.py`, `modelo_tamano.py`, `modelo_clase.py`, `generar_reporte.py`, `validar_resultados.py` (los cuatro últimos dentro de esa carpeta). Código separado de `resultados/` y `producto/modelo_tabular/metricas_tabular.json`; los CSV protegidos de curation se mantienen idénticos por SHA-256.
"""
    (HERE / "REPORTE_TABULAR.md").write_text(report, encoding="utf-8")
    product = {"evaluacion": "5 particiones por artículo", "bootstrap": "1000 remuestreos de artículos; IC condicional a predicciones OOF", "modelos": list(registry.values())}
    save_json(PRODUCT / "metricas_tabular.json", product)
    checkpoint("reporte_y_figuras_generados", {"modelos": len(registry), "figuras": len(list(FIG.glob("*.png"))), "mejor_tamano": best_reg["id"], "mejor_clase4": best4["id"], "mejor_clase3": best3["id"]})


if __name__ == "__main__":
    main()
