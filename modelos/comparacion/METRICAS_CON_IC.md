# Métricas de la clase de portador con intervalos de confianza

2100 figuras de 1641 artículos, 4 clases, 5 particiones por artículo; predicciones fuera de muestra. IC 95 % por bootstrap de artículos (1.000 remuestreos; no incluye la incertidumbre de reentrenar ni la de haber probado varias variantes). Script: `modelos/comparacion/metricas_finales_con_ic.py`.

| Modelo | F1 macro [IC 95 %] | Exactitud [IC 95 %] | Exactitud balanceada [IC 95 %] |
|---|---|---|---|
| Clase mayoritaria (línea base) | 0.156 [0.149, 0.162] | 0.454 [0.426, 0.478] | 0.250 [0.250, 0.250] |
| Imagen: modelo del Atlas (SVM con probabilidades) | 0.442 [0.416, 0.467] | 0.526 [0.502, 0.549] | 0.432 [0.410, 0.456] |
| Imagen: SVM, regla de decisión directa (ResNet50 + DINOv2) | 0.475 [0.451, 0.499] | 0.495 [0.473, 0.519] | 0.489 [0.463, 0.515] |
| Solo medidas (logística) | 0.526 [0.500, 0.553] | 0.570 [0.545, 0.597] | 0.534 [0.507, 0.561] |
| Fusión: imagen (PCA 32) + medidas (logística) | 0.561 [0.535, 0.585] | 0.596 [0.571, 0.620] | 0.574 [0.548, 0.598] |

**Diferencias pareadas en F1 macro** (mismos remuestreos):

| Comparación | Diferencia [IC 95 %] |
|---|---|
| Fusión: imagen (PCA 32) + medidas (logística) − Solo medidas (logística) | +0.035 [+0.014, +0.056] |
| Fusión: imagen (PCA 32) + medidas (logística) − Imagen: modelo del Atlas (SVM con probabilidades) | +0.119 [+0.088, +0.151] |
| Solo medidas (logística) − Imagen: modelo del Atlas (SVM con probabilidades) | +0.084 [+0.049, +0.119] |
| Imagen: SVM, regla de decisión directa (ResNet50 + DINOv2) − Imagen: modelo del Atlas (SVM con probabilidades) | +0.033 [+0.012, +0.053] |

## Cuál cifra usar
- **Modelo de imagen que muestra el Atlas:** la fila «modelo del Atlas». Sus predicciones salen de un SVM con probabilidades (`predicciones.json`); es la cifra que debe coincidir con `producto/modelo/metricas.json`.
- **Misma entrada con otra regla de decisión (SVM directo):** da un F1 más alto porque la regla directa respeta el balanceo de clases; es una **variante exploratoria**, no el modelo publicado. No se cita como cifra principal.
- Todo es exploratorio: se probaron varias variantes sobre las mismas particiones y la mejor es algo optimista. El ajuste fino (cuaderno 03) producirá la cifra de imagen final, que sustituye a estas.
