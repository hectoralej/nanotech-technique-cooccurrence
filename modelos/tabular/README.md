# Modelos tabulares

Código: `tabular_data.py` construye una fila por descriptor; `modelo_tamano.py` y `modelo_clase.py` ejecutan las escaleras; `tabular_common.py` contiene evaluación, imputación y bootstrap; `generar_reporte.py` genera figuras/tablas; `validar_resultados.py` aplica las pruebas de cierre.

Desde la raíz del proyecto: `python modelos/tabular/ejecutar_todo.py`.
Requiere Python 3.13, numpy, pandas, scikit-learn, matplotlib, Pillow y threadpoolctl. Las versiones exactas se guardan en `resultados/entorno.json`. No necesita red ni imágenes.

Outputs: `dataset_descriptores.csv`; `resultados/` (predicciones OOF, métricas, coeficientes, importancias, matrices, figuras PNG, pruebas y cache); `producto/modelo_tabular/metricas_tabular.json`; `REPORTE_TABULAR.md`, `INTERPRETACION.md`, `VALIDACION_TABULAR.md`. `CHECKPOINTS.md` y `progreso.json` muestran el estado persistente por fold/modelo.

Las predicciones de regresión guardan y_real/y_pred en log10(nm); se incluye MAE en nm y error relativo mediano en las métricas. Las de clasificación guardan las etiquetas textuales. Identidad y orden de filas se conservan aunque PMCID/sample se repitan.

Se conservan los folds oficiales. Ridge usa validación interna GroupKFold de entrenamiento; el resto de hiperparámetros está fijado por el brief. Clasificación usa una lista cerrada de entradas que excluye etiquetas y sus sustitutos. Hay 12 regresores (2 baselines compartidos + 5 modelos por variante A/B) y 8 clasificadores (4 por experimento de 4/3 clases). Cada entrenamiento de clasificación se repite con la misma semilla antes de validarse.

Los caches se reutilizan solo si coinciden dataset, código de entrenamiento y versión de sklearn. No se guardan modelos RF voluminosos; cada cache contiene predicciones, validación del fold, coeficientes/importancias y parámetros elegidos. Los datos de `curation` se leen sin modificarlos y sus hashes se verifican al final.

La ejecución es monohilo: el entorno de Windows bloquea las tuberías internas que joblib intenta crear para la paralelización. Esto no altera los parámetros de los estimadores ni la semilla. Los checkpoints retienen el fallo inicial y la posterior ejecución correcta.
