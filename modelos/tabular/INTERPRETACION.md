# Interpretación de coeficientes e importancias

Los coeficientes lineales actúan sobre log10(tamaño). En variables numéricas, corresponden a un aumento de una desviación estándar del entrenamiento; 10^β es el factor asociado. Los indicadores también se estandarizan. Las categorías se codifican one-hot; clase y carrier_type son redundantes, de modo que sus coeficientes aislados no tienen una interpretación única en la regresión sin regularizar. Ridge estabiliza el ajuste, pero las asociaciones siguen sin ser causales.

## tamano_A_lineal

| Variable estandarizada | β medio | Factor 10^β |
|---|---:|---:|
| tiene_SEM | +0.0667 | 1.166 |
| tiene_UVVis | -0.0393 | 0.914 |
| tiene_SAXS | +0.0370 | 1.089 |

## tamano_A_ridge

| Variable estandarizada | β medio | Factor 10^β |
|---|---:|---:|
| tiene_SEM | +0.0563 | 1.138 |
| tiene_UVVis | -0.0509 | 0.889 |
| tiene_cryoTEM | -0.0268 | 0.940 |

## tamano_B_lineal

| Variable estandarizada | β medio | Factor 10^β |
|---|---:|---:|
| tiene_SEM | +0.0664 | 1.165 |
| pdi | +0.0472 | 1.115 |
| tiene_SAXS | +0.0407 | 1.098 |

## tamano_B_ridge

| Variable estandarizada | β medio | Factor 10^β |
|---|---:|---:|
| tiene_SEM | +0.0576 | 1.142 |
| tiene_UVVis | -0.0479 | 0.896 |
| pdi | +0.0456 | 1.111 |

## Clasificación

Las figuras logísticas muestran coeficientes por clase: un valor positivo aumenta su logit cuando crece la variable, manteniendo las otras constantes. No equivale a una variación fija de probabilidad. La estandarización se aprende solo en entrenamiento. Las matrices de confusión permiten ver qué clases se solapan.

## Permutación

Se permuta una columna de las filas de test, cinco veces por fold, y se mide la caída de R²/F1 macro. Una importancia negativa puede surgir por variabilidad o redundancia. Son sensibilidades predictivas condicionadas al modelo, no efectos causales; las variables correlacionadas pueden repartirse la importancia. Las figuras de importancia se eligen entre los modelos con este análisis y se identifican explícitamente.
