# Primeros modelos tabulares

Cinco folds oficiales por artículo; imputación, codificación y escalado aprendidos solo en entrenamiento. Ridge elige alpha por GroupKFold interno (4 particiones, MAE log10). IC95: 1.000 bootstrap de artículos sobre predicciones fuera de muestra. Cada bootstrap conserva todas las filas de los artículos sorteados; no incluye incertidumbre de reentrenamiento.

Regresión: 2749 tamaños válidos de 1080 artículos. A usa metadatos, medio y presencia de técnicas; B añade zeta/PDI e indicadores de faltante. Dummy R²=-0.0031; media por clase=0.1798, reproduce ≈0,18.

| Entradas | Modelo | R² [IC95] | ΔR² previo | MAE log10 | Error relativo mediano |
|---|---|---:|---:|---:|---:|
| A/B | Media global (Dummy) | -0.003 [-0.009, -0.001] | — | 0.323 | 45.0% |
| A/B | Media por clase | 0.180 [0.127, 0.226] | +0.183 | 0.287 | 43.6% |
| A | Lineal múltiple | 0.217 [0.158, 0.268] | +0.037 | 0.285 | 44.2% |
| A | Ridge (alpha interno) | 0.220 [0.169, 0.265] | +0.003 | 0.284 | 43.9% |
| A | RF 300 / hoja 3 | 0.138 [0.064, 0.204] | -0.082 | 0.299 | 46.9% |
| A | RF 500 / hoja 1 | 0.061 [-0.022, 0.138] | -0.076 | 0.313 | 48.8% |
| A | HistGradientBoosting | 0.112 [0.032, 0.185] | +0.051 | 0.304 | 48.3% |
| B | Lineal múltiple | 0.237 [0.181, 0.288] | +0.057 | 0.282 | 44.1% |
| B | Ridge (alpha interno) | 0.240 [0.189, 0.287] | +0.003 | 0.281 | 43.7% |
| B | RF 300 / hoja 3 | 0.198 [0.129, 0.263] | -0.042 | 0.285 | 42.6% |
| B | RF 500 / hoja 1 | 0.162 [0.085, 0.236] | -0.036 | 0.290 | 43.3% |
| B | HistGradientBoosting | 0.167 [0.090, 0.239] | +0.005 | 0.296 | 46.5% |

Δ previo sigue el orden de la escalera, incluida la corrida de sensibilidad RF500/hoja1; no implica mejora monotónica. IC de MAE y error relativo, MAE en nm, R² por clase y alphas están en CSV/JSON. Los coeficientes lineales/Ridge y logísticos se interpretan en `INTERPRETACION.md`; las importancias se calculan por permutación en test. HGB usa 300 iteraciones sin parada temprana por filas.

| Clases | Modelo | Exactitud [IC95] | F1 macro [IC95] |
|---|---|---:|---:|
| 4 | Clase mayoritaria | 0.308 [0.275, 0.340] | 0.118 [0.108, 0.127] |
| 4 | Logística multinomial | 0.540 [0.509, 0.574] | 0.513 [0.482, 0.544] |
| 4 | RandomForest balanceado | 0.509 [0.476, 0.539] | 0.488 [0.456, 0.516] |
| 4 | HistGradientBoosting | 0.496 [0.466, 0.525] | 0.473 [0.442, 0.502] |
| 3 | Clase mayoritaria | 0.412 [0.369, 0.454] | 0.195 [0.180, 0.208] |
| 3 | Logística multinomial | 0.576 [0.535, 0.613] | 0.576 [0.534, 0.612] |
| 3 | RandomForest balanceado | 0.571 [0.533, 0.606] | 0.569 [0.531, 0.604] |
| 3 | HistGradientBoosting | 0.546 [0.511, 0.579] | 0.540 [0.504, 0.572] |

Conclusiones:

1. Tamaño: tamano_B_ridge alcanza R²=0.240, MAE log10=0.281 y error relativo mediano=43.7%; supera internamente a la media por clase. ΔR² pareado: IC95 [0.025, 0.094]. La mejora es modesta: el error relativo mediano es casi igual al piso (43.6%).
2. Clasificación: el mayor F1 macro OOF es 0.513 con 4 clases (clase4_logistica) y 0.576 con 3 (clase3_logistica). Son problemas con poblaciones distintas; quitar nanomaterial cambia la dificultad y no constituye una mejora directamente comparable.
3. No hubo artículos compartidos entre train/test; la prueba rechaza columnas prohibidas y sus variantes no autorizadas. Los ocho clasificadores repitieron cada entrenamiento con la misma semilla y produjeron predicciones idénticas. El modelo destacado es exploratorio; el rendimiento final requiere una evaluación externa.

Limitaciones: faltan parámetros de formulación (proporciones, preparación); 74.6% de filas no declara medio. Hay varias filas por artículo: el n efectivo se aproxima al número de artículos, y las métricas puntuales ponderan filas. Los datos fueron extraídos con IA y verificados por código, no revalidados manualmente en esta tarea. Familia de portador y técnicas se correlacionan con sesgos editoriales; importancias/coefs no demuestran causalidad. Los IC son condicionales a estas predicciones OOF. No se entrenaron modelos de imágenes ni multimodales.

Reproducción: `python modelos/tabular/tabular_data.py`, `modelo_tamano.py`, `modelo_clase.py`, `generar_reporte.py`, `validar_resultados.py` (los cuatro últimos dentro de esa carpeta). Código separado de `resultados/` y `producto/modelo_tabular/metricas_tabular.json`; los CSV protegidos de curation se mantienen idénticos por SHA-256.
