# Ajuste fino frente a vectores congelados (con IC 95 %)

Cuaderno 03 en Kabré (GPU L40S): ResNet50 y DINOv2 ajustados 10 épocas, 5 particiones por artículo, última época, sin elegir nada con los datos de prueba. 2100 figuras de 1641 artículos. IC 95 % por bootstrap de artículos (1.000). La fusión tardía usa un peso fijo 50/50 elegido de antemano, sin ajustarlo.

| Modelo | F1 macro [IC 95 %] | Exactitud | Exactitud balanceada |
|---|---|---:|---:|
| Clase mayoritaria (línea base) | 0.156 [0.149, 0.162] | 0.454 | 0.250 |
| Vectores congelados: modelo del Atlas | 0.442 [0.416, 0.467] | 0.526 | 0.432 |
| Ajuste fino ResNet50 | 0.406 [0.384, 0.428] | 0.459 | 0.413 |
| Ajuste fino DINOv2 | 0.443 [0.418, 0.468] | 0.482 | 0.444 |
| Ajuste fino: promedio ResNet50 + DINOv2 | 0.460 [0.437, 0.484] | 0.504 | 0.458 |
| Solo medidas (logística) | 0.526 [0.500, 0.553] | 0.570 | 0.534 |
| Fusión tardía: ajuste fino (promedio) + medidas, peso 50/50 | 0.580 [0.554, 0.603] | 0.629 | 0.582 |

| Comparación | Diferencia en F1 macro [IC 95 %] |
|---|---|
| Ajuste fino: promedio ResNet50 + DINOv2 − Vectores congelados: modelo del Atlas | +0.018 [-0.008, +0.045] |
| Ajuste fino DINOv2 − Vectores congelados: modelo del Atlas | +0.001 [-0.025, +0.028] |
| Fusión tardía: ajuste fino (promedio) + medidas, peso 50/50 − Solo medidas (logística) | +0.054 [+0.032, +0.077] |
| Ajuste fino ResNet50 − Ajuste fino DINOv2 | -0.037 [-0.065, -0.011] |

**Lectura:** el ajuste fino no supera de forma clara a los vectores congelados; DINOv2 sobreajusta (acierto de entrenamiento ≈ 0,96 frente a ≈ 0,48 en prueba) y ResNet50 aprende poco con esta configuración. La limitación está en las imágenes (figuras compuestas, una por artículo), no en la arquitectura.
