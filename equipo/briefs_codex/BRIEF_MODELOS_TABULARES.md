# Codex: primeros modelos tabulares (tamaño y clase de portador)

`RAIZ` = `C:\Users\Hector\Desktop\Quimioinformatica Proyecto\nanotech-technique-cooccurrence`. Parte de la etiqueta `v0.1`. Reglas de siempre: no abrir `curation\work\clave_modelo.csv` ni `curation\qc_codex\`; no tocar `curation\ext_*.csv`, `curation\v0.1\` ni `curation\work\llm\`; no usar git; no inventar; cada paso se cierra solo si pasa su validación. `scikit-learn` 1.9.1, `pandas` y `numpy` ya están instalados (Python 3.13: `%LOCALAPPDATA%\Programs\Python\Python313\python.exe`). Sin `torch`: no hace falta.

**Meta:** una línea base honesta con modelos livianos. Los modelos de imágenes (Kabré) se compararán después contra esto. Es el primer escalón de una herramienta multimodal.

## 0. Hallazgos previos (para que sepas qué esperar)
- 3.116 filas de descriptores (1.229 artículos). Tamaño: 2.750 filas; zeta: 1.946; PDI: 1.615; las tres a la vez: 1.205.
- El 75 % de las filas tiene `medium = not_declared`.
- Con solo la clase de portador, el R² de log10(tamaño) con validación por artículo es **0,18**: ese es el piso a superar.
- Clases en `tabla_modelo.csv`: `lipidico`, `polimerico`, `inorganico`, `nanomaterial` (+ vacía para `other`, `not_a_nanocarrier`, cubosoma, nanoemulsión).

## 1. Datos y partición
1. Crea `RAIZ\modelos\tabular\tabular_data.py` que construya `RAIZ\modelos\tabular\dataset_descriptores.csv` (`utf-8-sig`), **una fila por fila de `ext_descriptores.csv`**, con columnas: `pmcid, sample, size_nm, pdi, zeta_mV, medium, medio_declarado (0/1), clase_modelo, carrier_type, categoria_uso, year, n_paneles, tiene_TEM, tiene_SEM, tiene_cryoTEM, tiene_FTIR, tiene_XRD, tiene_UVVis, tiene_SAXS, tiene_EDS, tiene_Raman, fold`.
2. `clase_modelo` y `fold` salen de `curation\v0.1\tabla_modelo.csv` por `pmcid`. Si un artículo no está en esa tabla, calcula su `fold` con **la misma regla determinista** de `curation\tabla_modelo.py` (impórtala; no inventes otra) y su `clase_modelo` con el mismo mapeo.
3. Filtros: tamaño solo si 1 ≤ `size_nm` ≤ 5.000; PDI solo si ≤ 1,5; |zeta| ≤ 150. Los valores fuera de rango se tratan como vacíos (no se borran filas).
4. **Validación 1:** ninguna fila sin `fold`; ningún `pmcid` en dos folds; recuento de filas y artículos por fold y por clase.

## 2. Modelo 1: predecir el tamaño (regresión)
**Objetivo:** `log10(size_nm)`. Filas con tamaño válido.

**Variantes de entradas:**
- **A (sin mediciones):** `clase_modelo`, `carrier_type`, `medio_declarado`/`medium`, `year`, `tiene_*` de microscopía y espectros, `n_paneles`.
- **B:** A + `zeta_mV` y `pdi` (con indicador de «faltante» y mediana por fold de entrenamiento como imputación).

**Escalera de modelos** (se entrenan **en este orden** y se reporta cada peldaño; el objetivo es ver cuánto aporta cada nivel de complejidad):
1. `DummyRegressor` (media global) y media por `clase_modelo` (el piso).
2. **Regresión lineal múltiple** simple (`LinearRegression`, one-hot + estandarizar): primer modelo de verdad; se interpretan sus coeficientes.
3. `Ridge` (elige `alpha` con validación **interna por grupos**, rejilla `[0.01, 0.1, 1, 10, 100]`).
4. `RandomForestRegressor` (300 árboles, `min_samples_leaf=3`, `random_state=0`; segunda corrida con `min_samples_leaf=1` y 500 árboles para ver la sensibilidad).
5. `HistGradientBoostingRegressor` (`max_iter=300`, `learning_rate=0.05`, `random_state=0`).
Los hiperparámetros se eligen **solo con los datos de entrenamiento** de cada partición. En el informe, una tabla con un renglón por peldaño y la mejora sobre el anterior.

**Evaluación:** validación cruzada de 5 particiones con la columna `fold` (por artículo). Reporta R², MAE de log10 y error mediano relativo en nm. Intervalos de confianza del 95 % con **bootstrap por artículo** (1.000 remuestreos). R² también por clase. Importancia de variables: coeficientes de Ridge y **importancia por permutación** en los datos de prueba.

**Validación 2:** la media global da R² ≈ 0 (o ligeramente negativo); el modelo (b) reproduce ≈ 0,18; si alguno de tus números contradice esto, explica por qué antes de seguir.

## 3. Modelo 2: predecir la clase de portador (clasificación)
**Objetivo:** `clase_modelo` (4 clases) en filas con al menos una de `size_nm`, `zeta_mV`, `pdi`. Segunda versión: **sin** `nanomaterial` (3 clases), porque se solapa con `inorganico`.

**Entradas permitidas:** log10(tamaño), zeta, PDI (con indicadores de faltante), `medium`/`medio_declarado`, `year`, `tiene_*` de microscopía y espectros, `n_paneles`.

**PROHIBIDO como entrada (la respuesta disfrazada):** `family`, `carrier_type`, `categoria_uso`, el título, el texto de `sample`, `clase_modelo` y cualquier columna derivada de ellas. Escribe una prueba automática que falle si alguna de esas columnas está en la matriz de entrada.

**Escalera de modelos** (mismo orden y reporte por peldaño): (1) clase mayoritaria; (2) `LogisticRegression` multinomial con estandarización (primer modelo de verdad, con coeficientes); (3) `RandomForestClassifier` (300 árboles, `class_weight="balanced"`, `random_state=0`); (4) `HistGradientBoostingClassifier` (`max_iter=300`, `learning_rate=0.05`, `random_state=0`). Evaluación por `fold` (por artículo): exactitud, F1 macro, matriz de confusión normalizada, y IC 95 % por bootstrap de artículos. Importancia por permutación.

**Validación 3:** la línea base de la clase mayoritaria coincide con la proporción de la clase más grande; la prueba de columnas prohibidas pasa; repetir el entrenamiento con la misma semilla da las mismas métricas.

## 4. Si sobra tiempo (opcionales, mismo formato y validación)
- Signo del zeta (negativo/positivo): hoy el 68 % es negativo (79 % en lipídica, 52 % en polimérica).
- PDI < 0,3 (monodisperso): hoy el 62 % cumple.

## 4b. Después de esta tarea (no la hagas todavía)
Esta es la base de una escalera más larga: tras los modelos tabulares seguirán los modelos de imágenes en el clúster Kabré (embeddings, CNN con ajuste fino, transformer) y, al final, un modelo multimodal que combine imagen, descriptores y espectros. Deja el código modular (`tabular_data.py` reutilizable) y guarda las predicciones fuera de muestra de cada modelo en `modelos\tabular\resultados\predicciones_*.csv` (`pmcid, sample, y_real, y_pred, fold`) para poder comparar y combinar modelos después.

## 5. Entregables
- `modelos\tabular\`: `tabular_data.py`, `modelo_tamano.py`, `modelo_clase.py`, `dataset_descriptores.csv`, `resultados\` (tablas CSV y gráficas PNG de coeficientes/importancias).
- `producto\modelo_tabular\metricas_tabular.json`: un objeto por modelo con `tarea`, `entradas`, `n_filas`, `n_articulos`, `evaluacion` («5 particiones por artículo»), `metricas` (con IC 95 %) y `linea_base`.
- `modelos\tabular\REPORTE_TABULAR.md` (una página y media): tablas de resultados, 3 conclusiones, y una sección **Limitaciones** que diga: la base no tiene parámetros de formulación (proporciones, método de preparación), el 75 % de las filas no declara el medio, hay varias filas por artículo (n efectivo ≈ artículos), y los datos fueron extraídos con IA y verificados por código.
- Reporte corto en el chat con cifras y lo que no pudiste verificar. **No uses git**: Claude revisa y sube.

## 6. Qué no hacer
No cambies columnas ni valores de los CSV de `curation\`. No uses `family` ni `carrier_type` como entradas del modelo 2. No ajustes hiperparámetros con los datos de prueba de la partición. No presentes el modelo de tamaño como predictivo si el R² no supera claramente a la línea base: dilo.
