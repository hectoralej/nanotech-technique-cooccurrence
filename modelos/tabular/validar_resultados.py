"""Executable gates: source immutability, OOF alignment, leakage and reproducibility."""
from __future__ import annotations

import json
import unittest

import numpy as np
import pandas as pd
from PIL import Image
from sklearn.linear_model import Ridge

from tabular_data import CUR, DATASET, HERE, RESULTS, load_dataset, protected_hashes, read_csv, save_json
from tabular_common import CLASS_FEATURES, PRODUCT, assert_classification_features, bootstrap_by_article, checkpoint, input_fingerprint, metric_values, pipeline_for


class Validaciones(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_dataset()
        cls.audit = json.loads((RESULTS / "validacion_datos.json").read_text(encoding="utf-8"))
        cls.models = {r["id"]: r for r in json.loads((PRODUCT / "metricas_tabular.json").read_text(encoding="utf-8"))["modelos"]}

    def test_fuentes_protegidas_identicas(self):
        self.assertEqual(self.audit["protected_inputs"], protected_hashes())

    def test_datos_folds_y_filtros(self):
        raw = read_csv(CUR / "ext_descriptores.csv")
        self.assertEqual(len(self.data), len(raw))
        self.assertTrue(self.data.fold.notna().all())
        self.assertTrue(self.data.fold.between(0, 4).all())
        self.assertTrue(self.data.groupby("pmcid").fold.nunique().eq(1).all())
        official = read_csv(CUR / "v0.1" / "tabla_modelo.csv").drop_duplicates("pmcid").set_index("pmcid").fold.astype(int)
        subset = self.data[self.data.pmcid.isin(official.index)]
        np.testing.assert_array_equal(subset.fold, subset.pmcid.map(official))
        for col, predicate in (("size_nm", lambda s: s.between(1, 5000)), ("pdi", lambda s: s.le(1.5)), ("zeta_mV", lambda s: s.abs().le(150))):
            source = pd.to_numeric(raw[col], errors="coerce")
            expected = source.where(predicate(source))
            np.testing.assert_allclose(self.data[col], expected, equal_nan=True)

    def test_columnas_prohibidas_y_derivadas(self):
        assert_classification_features(CLASS_FEATURES)
        for field in ("family", "carrier_type", "categoria_uso", "title", "sample", "clase_modelo", "carrier_type_codificado", "clase_derivada"):
            with self.assertRaises(AssertionError, msg=field):
                assert_classification_features([*CLASS_FEATURES, field])

    def test_imputacion_no_aprende_del_test(self):
        train = pd.DataFrame({"zeta_mV": [1., 3., np.nan], "pdi": [.1, .3, .2], "medium": ["agua", "agua", "not_declared"]})
        fitted = pipeline_for(Ridge(alpha=1), train).fit(train, [1., 2., 1.5])
        imputer = fitted.named_steps["preprocess"].named_transformers_["numeric"].named_steps["imputer"]
        self.assertEqual(imputer.statistics_[0], 2.)
        fitted.predict(pd.DataFrame({"zeta_mV": [100000., np.nan], "pdi": [10000., np.nan], "medium": ["nuevo", "nuevo"]}))
        self.assertEqual(imputer.statistics_[0], 2.)

    def test_bootstrap_es_por_articulo(self):
        y = np.linspace(1, 3, 12); p = y + np.sin(y)*.2; pm = np.array([f"PMC{i}" for i in range(12)])
        original = bootstrap_by_article(y, p, pm, "regresion")
        repeated = bootstrap_by_article(np.repeat(y, 3), np.repeat(p, 3), np.repeat(pm, 3), "regresion")
        for key in original:
            np.testing.assert_allclose(original[key], repeated[key], rtol=1e-10, atol=1e-10)

    def test_predicciones_metricas_y_grupos(self):
        self.assertEqual(len(self.models), 20)
        for model_id, result in self.models.items():
            with self.subTest(modelo=model_id):
                regression = result["tarea"] == "tamano_log10"
                if regression:
                    data = self.data[self.data.size_nm.notna()].copy()
                else:
                    data = self.data[self.data.clase_modelo.ne("") & self.data[["size_nm", "zeta_mV", "pdi"]].notna().any(axis=1)].copy()
                    if result["tarea"] == "clase_3":
                        data = data[data.clase_modelo.ne("nanomaterial")]
                    assert_classification_features(result["entradas"])
                pred = read_csv(RESULTS / f"predicciones_{model_id}.csv")
                self.assertEqual(len(data), len(pred))
                np.testing.assert_array_equal(pred.pmcid, data.pmcid)
                np.testing.assert_array_equal(pred["sample"], data["sample"])
                np.testing.assert_array_equal(pred.fold.astype(int), data.fold)
                y = np.log10(data.size_nm.to_numpy(float)) if regression else data.clase_modelo.to_numpy()
                yp = pred.y_pred.to_numpy(float) if regression else pred.y_pred.to_numpy()
                if regression:
                    np.testing.assert_allclose(pred.y_real.astype(float), y)
                    self.assertTrue(np.isfinite(yp).all())
                else:
                    np.testing.assert_array_equal(pred.y_real, y)
                    self.assertTrue(set(yp) <= set(y))
                metrics = metric_values(y, yp, "regresion" if regression else "clasificacion", sorted(set(y)) if not regression else None)
                for key, value in metrics.items():
                    self.assertAlmostEqual(value, result["metricas"][key]["valor"], places=10)
                    self.assertEqual(len(result["metricas"][key]["ic95"]), 2)
                    self.assertTrue(np.isfinite(result["metricas"][key]["ic95"]).all())
                self.assertEqual(len(result["por_fold"]), 5)
                for fold in result["por_fold"]:
                    test = data[data.fold == fold["fold"]]; train = data[data.fold != fold["fold"]]
                    self.assertFalse(set(test.pmcid) & set(train.pmcid))
                    self.assertEqual(fold["n_test"], len(test))
                    cached = json.loads((RESULTS / "cache" / model_id / f"fold_{fold['fold']}.json").read_text(encoding="utf-8"))
                    self.assertEqual(cached["fingerprint"], input_fingerprint())
                    if not regression:
                        self.assertTrue(fold["repeticion_entrenamiento_predicciones_identicas"])
                    if model_id.endswith("ridge"):
                        self.assertIn(fold["alpha"], [.01, .1, 1., 10., 100.])

    def test_baselines(self):
        self.assertLess(abs(self.models["tamano_dummy"]["metricas"]["r2"]["valor"]), .02)
        self.assertLess(abs(self.models["tamano_media_clase"]["metricas"]["r2"]["valor"] - .18), .03)
        checks = json.loads((RESULTS / "validacion_3.json").read_text(encoding="utf-8"))
        self.assertTrue(all(x["coinciden"] for x in checks["experimentos"]))

    def test_figuras_validas(self):
        paths = list((RESULTS / "figuras").glob("*.png"))
        self.assertGreaterEqual(len(paths), 10)
        for path in paths:
            with Image.open(path) as im:
                self.assertGreater(im.width, 500)
                self.assertGreater(im.height, 300)
                im.verify()


def main():
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(Validaciones)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    state = {"estado": "PASS" if result.wasSuccessful() else "FAIL", "tests": result.testsRun, "fallos": len(result.failures), "errores": len(result.errors)}
    save_json(RESULTS / "validacion_final.json", state)
    if result.wasSuccessful():
        audit = Validaciones.audit
        baseline = json.loads((RESULTS / "validacion_2.json").read_text(encoding="utf-8"))
        cls = json.loads((RESULTS / "validacion_3.json").read_text(encoding="utf-8"))
        text = f"""# Validación de los modelos tabulares

- Gate final: **PASS**, {result.testsRun} pruebas automáticas, cero fallos.
- Datos: {audit['filas']} filas / {audit['articulos']} artículos; todos los folds oficiales conservados; ningún artículo repartido entre folds. Fallback importado: {len(audit['articulos_fallback'])} artículos. Distribuciones de filas/artículos por fold/clase en `resultados/distribucion_folds_clases.csv`.
- Filtros: {json.dumps(audit['valores_fuera_de_rango_vaciados'])}; valores válidos: {json.dumps(audit['datos_validos'])}. Las filas y las identidades PMCID/sample permanecen alineadas con la fuente.
- Baselines: {baseline['explicacion']}
- Clasificación: mayorías y exactitud coinciden ({json.dumps(cls['experimentos'], ensure_ascii=False)}).
- Prueba de fuga: rechaza family, carrier_type, categoria_uso, título, sample, clase_modelo y nombres derivados fuera de la lista permitida. Una prueba sintética confirma que un test extremo no modifica la mediana de imputación aprendida con train.
- Reproducibilidad: los 8 clasificadores × 5 folds se entrenaron dos veces con semilla 0; predicciones exactamente iguales. Cada cache guarda la evidencia y el SHA-256 de datos/código/versión de sklearn.
- Ridge: búsqueda de alpha [.01, .1, 1, 10, 100] por GroupKFold interno de 4 grupos, scoring MAE log10; imputación/OHE/escalado dentro de la búsqueda. Ningún hiperparámetro se elige con el fold externo.
- Bootstrap: 1.000 remuestreos por artículo para todos los modelos; una prueba de replicación de filas dentro de artículos conserva los IC, confirmando que la unidad de remuestreo no es la fila. IC condicionales a OOF, no al reentrenamiento.
- Predicciones: 20 archivos completos y alineados con su población; las métricas publicadas se recalcularon independientemente desde sus y_real/y_pred. R² por clase y matrices de confusión están en CSV.
- Fuentes: los SHA-256 de los cuatro ext_*.csv, todos los archivos de v0.1 y tabla_modelo.py coinciden con la instantánea inicial. No se ejecutó git ni se abrieron los archivos excluidos por el brief.
- Figuras: PNG legibles de escalera, observado/predicho, coeficientes, permutaciones y matrices normalizadas. Permutación: 5 repeticiones sobre test por fold; variación entre folds, no interpretación causal.

No se hizo validación externa, auditoría manual de cada extracción ni entrenamiento de imágenes. Los checkpoints por fold/modelo permiten retomar sin declarar completa una etapa fallida.
"""
        (HERE / "VALIDACION_TABULAR.md").write_text(text, encoding="utf-8")
        checkpoint("entrega_validada", state)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
