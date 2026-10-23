# Validación de los modelos tabulares

- Gate final: **PASS**, 8 pruebas automáticas, cero fallos.
- Datos: 3116 filas / 1229 artículos; todos los folds oficiales conservados; ningún artículo repartido entre folds. Fallback importado: 0 artículos. Distribuciones de filas/artículos por fold/clase en `resultados/distribucion_folds_clases.csv`.
- Filtros: {"size_nm": 1, "pdi": 4, "zeta_mV": 0}; valores válidos: {"size_nm": 2749, "pdi": 1611, "zeta_mV": 1946}. Las filas y las identidades PMCID/sample permanecen alineadas con la fuente.
- Baselines: Media global OOF R²=-0.0031; media por clase OOF R²=0.1798; diferencia frente a 0,18=-0.0002. La comparación usa filas descriptor individuales, cinco folds oficiales por artículo, media de log10(tamaño) calculada solo con entrenamiento y filtros 1–5000 nm. El valor previo 0,18 es aproximado y no incluye sus predicciones ni su partición de origen; por ello la igualdad exacta no es comprobable. La magnitud reproduce el piso comunicado.
- Clasificación: mayorías y exactitud coinciden ([{"n_clases": 4, "proporcion_mayoritaria": 0.30779392338177014, "exactitud_dummy": 0.30779392338177014, "coinciden": true, "explicacion": "La misma clase es mayoritaria en los cinco entrenamientos."}, {"n_clases": 3, "proporcion_mayoritaria": 0.4120247568523431, "exactitud_dummy": 0.4120247568523431, "coinciden": true, "explicacion": "La misma clase es mayoritaria en los cinco entrenamientos."}]).
- Prueba de fuga: rechaza family, carrier_type, categoria_uso, título, sample, clase_modelo y nombres derivados fuera de la lista permitida. Una prueba sintética confirma que un test extremo no modifica la mediana de imputación aprendida con train.
- Reproducibilidad: los 8 clasificadores × 5 folds se entrenaron dos veces con semilla 0; predicciones exactamente iguales. Cada cache guarda la evidencia y el SHA-256 de datos/código/versión de sklearn.
- Ridge: búsqueda de alpha [.01, .1, 1, 10, 100] por GroupKFold interno de 4 grupos, scoring MAE log10; imputación/OHE/escalado dentro de la búsqueda. Ningún hiperparámetro se elige con el fold externo.
- Bootstrap: 1.000 remuestreos por artículo para todos los modelos; una prueba de replicación de filas dentro de artículos conserva los IC, confirmando que la unidad de remuestreo no es la fila. IC condicionales a OOF, no al reentrenamiento.
- Predicciones: 20 archivos completos y alineados con su población; las métricas publicadas se recalcularon independientemente desde sus y_real/y_pred. R² por clase y matrices de confusión están en CSV.
- Fuentes: los SHA-256 de los cuatro ext_*.csv, todos los archivos de v0.1 y tabla_modelo.py coinciden con la instantánea inicial. No se ejecutó git ni se abrieron los archivos excluidos por el brief.
- Figuras: PNG legibles de escalera, observado/predicho, coeficientes, permutaciones y matrices normalizadas. Permutación: 5 repeticiones sobre test por fold; variación entre folds, no interpretación causal.

No se hizo validación externa, auditoría manual de cada extracción ni entrenamiento de imágenes. Los checkpoints por fold/modelo permiten retomar sin declarar completa una etapa fallida.
