# Ronda 2: modelos tabulares y menciones de formulación

28 banderas léxicas, 1.707 artículos (1.691 métodos; 16 texto completo sin referencias). Ninguna bandera está por debajo de 10 artículos. Revisión asistida por IA de 30 pares positivos aleatorios: 21 correctos y 9 dudosos para atribuirlos a formulación (70 %); las 30 citas son literales y ≤200 caracteres. No es una estimación de precisión humana de toda la extracción. `met_*`, `mat_*` y `ctx_*` significan mención, no receta confirmada.

## Tamaño: R² [IC95]

Media por clase compartida: 0.180 [0.127, 0.226]. A conserva las entradas y predicciones R1; A+F añade 28 banderas, B+F también zeta/PDI. Se mantienen 2.749 filas/1.080 artículos y los mismos folds; Ridge usa GroupKFold interno. Random Forest: 300 árboles, hoja mínima 3; HGB 300 iteraciones, LR=0,05; sin tuning externo.

| Modelo | A (R1) | A+F | B+F |
|---|---:|---:|---:|
| lineal | 0.217 [0.158, 0.268] | 0.239 [0.181, 0.295] | 0.257 [0.190, 0.316] |
| ridge | 0.220 [0.169, 0.265] | 0.244 [0.193, 0.294] | 0.264 [0.200, 0.322] |
| rf300 | 0.138 [0.064, 0.204] | 0.255 [0.197, 0.309] | 0.285 [0.226, 0.344] |
| hgb | 0.112 [0.032, 0.185] | 0.203 [0.135, 0.272] | 0.256 [0.184, 0.323] |

## Qué aporta la formulación

La comparación primaria pareada Ridge A+F−A da ΔR²=+0.0241, IC95 [-0.0024, 0.0504]; no demuestra una mejora clara. Los cuatro modelos tienen comparaciones pareadas A+F−A y B+F−B en `resultados/mejoras_pareadas.csv`. Los IC usan 1.000 bootstrap por artículo sobre OOF, sin reentrenar. Importancias de las banderas: permutación en test, tres repeticiones por fold; CSV y PNG disponibles. La ganancia de una mención no demuestra un mecanismo de formulación.

## Clasificación y tareas nuevas

Para clase: medidas, medio/año/técnicas y únicamente métodos/contexto. Ninguna bandera de material entra a los clasificadores. Zeta: negativo/positivo, excluye zeta=0 y usa tamaño/PDI; PDI: umbral estricto <0,3, usa tamaño/zeta. Ninguna tarea recibe su medida objetivo. Cada clasificador/fold se entrena dos veces y debe producir idénticas probabilidades. Las probabilidades OOF por clase se guardan en todas las predicciones.

| Tarea | Modelo | Exactitud [IC95] | F1 macro [IC95] |
|---|---|---:|---:|
| clase4 | mayoritaria | 0.308 [0.275, 0.340] | 0.118 [0.108, 0.127] |
| clase4 | logistica | 0.662 [0.633, 0.693] | 0.644 [0.613, 0.674] |
| clase4 | rf | 0.633 [0.601, 0.664] | 0.610 [0.579, 0.639] |
| clase4 | hgb | 0.622 [0.590, 0.651] | 0.600 [0.568, 0.630] |
| clase3 | mayoritaria | 0.412 [0.369, 0.454] | 0.195 [0.180, 0.208] |
| clase3 | logistica | 0.693 [0.656, 0.729] | 0.694 [0.656, 0.729] |
| clase3 | rf | 0.687 [0.648, 0.721] | 0.685 [0.644, 0.719] |
| clase3 | hgb | 0.660 [0.622, 0.694] | 0.657 [0.619, 0.691] |
| zeta | mayoritaria | 0.689 [0.654, 0.725] | 0.408 [0.395, 0.420] |
| zeta | logistica | 0.735 [0.703, 0.770] | 0.622 [0.578, 0.665] |
| zeta | rf | 0.728 [0.695, 0.760] | 0.639 [0.598, 0.678] |
| zeta | hgb | 0.718 [0.686, 0.749] | 0.629 [0.589, 0.667] |
| pdi | mayoritaria | 0.628 [0.587, 0.668] | 0.386 [0.370, 0.400] |
| pdi | logistica | 0.606 [0.567, 0.643] | 0.528 [0.489, 0.565] |
| pdi | rf | 0.641 [0.606, 0.674] | 0.602 [0.565, 0.635] |
| pdi | hgb | 0.632 [0.600, 0.665] | 0.580 [0.547, 0.614] |

Para C se añade `clase4_mediciones_logistica`: solo log10(tamaño), zeta, PDI e indicadores de faltante. Evita llamar «solo mediciones» a un clasificador que también utiliza texto, año o técnicas.

## Limitaciones

Oro puede ser recubrimiento SEM; sílice puede ser TLC; sonicación o evaporación pueden preparar muestras para caracterización. El 70 % revisado apoya tratar las banderas como proxies textuales ruidosos. No hay proporciones ni condiciones de preparación verificadas; 74,6 % de filas no declara medio. Los artículos tienen varias filas y las métricas ponderan filas; los IC agrupan por artículo. Selección de banderas por prevalencia global sin usar objetivos; una selección estrictamente anidada sería una sensibilidad futura. Sin evaluación externa ni ajuste del clúster.

## Reproducción

`extraer_formulacion.py` usa Python con lxml y utilidades locales; la ejecución de esta ronda empleó el Python 3.12 incluido con la app (requests puro de Python 3.13). Entrenamiento: Python 3.13, `python modelos/tabular_v2/run_models.py`; informe/gates: `python modelos/tabular_v2/informe_v2.py`. Se importa tabular_common de R1 para preprocesamiento, coeficientes, métricas y bootstrap; ningún archivo de R1 se copia como código ni modifica. Las predicciones A se reutilizan verificando su identidad de filas/targets/folds.
