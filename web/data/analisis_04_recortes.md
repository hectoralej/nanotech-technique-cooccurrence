# Cuaderno 04 (recortes) frente al 03 (figura completa), por artículo

Unidad: artículo (promedio de las probabilidades de sus recortes o figuras). IC 95 % por bootstrap de artículos (2.000 remuestreos). 5 particiones por artículo; última época.

## resnet50 (1112 artículos comunes)

| | Exactitud | Exactitud balanceada | F1 macro |
|---|---:|---:|---:|
| Recortes (04), todas las vistas | 0.522 | 0.467 | 0.472 |
| Recortes (04), mismas vistas que el 03 (media de 200 sorteos) | 0.485 | – | 0.447 |
| Figura completa (03) | 0.479 | 0.424 | 0.416 |

Diferencia recortes − 03: exactitud +0.042 [IC +0.009, +0.076]; F1 macro +0.056 [IC +0.020, +0.091]. Vistas por artículo: 03 = 1.32, 04 = 4.18.

## dinov2_vits14 (1112 artículos comunes)

| | Exactitud | Exactitud balanceada | F1 macro |
|---|---:|---:|---:|
| Recortes (04), todas las vistas | 0.551 | 0.500 | 0.509 |
| Recortes (04), mismas vistas que el 03 (media de 200 sorteos) | 0.508 | – | 0.471 |
| Figura completa (03) | 0.500 | 0.454 | 0.458 |

Diferencia recortes − 03: exactitud +0.051 [IC +0.017, +0.082]; F1 macro +0.052 [IC +0.013, +0.086]. Vistas por artículo: 03 = 1.32, 04 = 4.18.

## Promedio de ResNet50 y DINOv2

Recortes: exactitud 0.558, F1 0.515. Figura completa (03): exactitud 0.520, F1 0.472. Diferencia: exactitud +0.038 [+0.005, +0.070], F1 +0.042 [+0.007, +0.079].

Línea base (clase mayoritaria por artículo): exactitud 0.442.
