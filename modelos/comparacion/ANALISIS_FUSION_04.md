# Fusión por artículo: medidas + imagen (recortes frente a figura completa)

786 artículos con medidas, figura completa y recortes. Particiones por artículo; fusión tardía 50/50; IC 95 % por bootstrap de artículos. Clase mayoritaria: exactitud 0.363.

| Modelo | Exactitud | Exactitud balanceada | F1 macro |
|---|---:|---:|---:|
| Solo medidas (logística) | 0.471 | 0.423 | 0.406 |
| Imagen, figura completa (03) | 0.499 | 0.471 | 0.475 |
| Imagen, recortes (04) | 0.541 | 0.511 | 0.519 |
| Fusión medidas + imagen 03 | 0.547 | 0.499 | 0.504 |
| Fusión medidas + imagen 04 | 0.576 | 0.529 | 0.535 |

**Diferencias pareadas** (mismos remuestreos):

| Comparación | Δ exactitud [IC 95 %] | Δ F1 macro [IC 95 %] |
|---|---|---|
| imagen_04 - imagen_03 | +0.042 [+0.003, +0.081] | +0.044 [+0.002, +0.086] |
| fusion_04 - fusion_03 | +0.029 [-0.005, +0.064] | +0.031 [-0.010, +0.071] |
| fusion_04 - medidas | +0.106 [+0.066, +0.144] | +0.129 [+0.082, +0.172] |
| fusion_03 - medidas | +0.076 [+0.034, +0.116] | +0.099 [+0.052, +0.143] |
| medidas - imagen_04 | -0.070 [-0.120, -0.018] | -0.114 [-0.163, -0.059] |