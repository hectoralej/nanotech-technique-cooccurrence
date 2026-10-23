# Análisis rápido de los vectores de imagen (23 oct, local)

Vectores: ResNet50 (2048) y DINOv2 ViT-S/14 (384) de 2.100 figuras (1.641 artículos), calculados en Kabré (cuaderno 02). Clase de portador en 4 categorías; validación por artículo. Scripts: `analisis_rapido_embeddings.py` y `analisis_rapido_estabilidad.py` (los vectores `.npy`, 20 MB, están en `Kabre_Nano2Predict\Resultados`, fuera de Git).

| Modelo (mismas 2.100 figuras) | Exactitud | Exactitud balanceada | F1 macro |
|---|---:|---:|---:|
| Clase mayoritaria / azar | 0,454 | 0,250 | ~0,16 |
| Imagen: DINOv2 + logística (cuaderno 02) | 0,416 | 0,410 | 0,394 |
| Imagen: DINOv2 + PCA64 + SVM rbf | 0,485 | 0,482 | 0,466 |
| Imagen: ResNet50 + DINOv2 + PCA64 + SVM rbf | 0,495 | 0,489 | 0,474 |
| Solo medidas (logística; descriptores, espectros, microscopía) | 0,579 | 0,545 | 0,537 |
| **Fusión: imagen (PCA) + medidas** | **0,596** | **0,569** | **0,559** |

Estabilidad (5 particiones distintas por artículo, F1 macro, media ± desviación): imagen DINOv2+SVM 0,461 ± 0,004; imagen ambos+SVM 0,468 ± 0,005; medidas 0,519 ± 0,004; fusión 0,546 ± 0,005. La fusión supera a las medidas por ~2,7 puntos de F1 en las 5 particiones.

Comprobaciones: el vecino más cercano de una imagen es del mismo artículo solo en el 2,7 % de los casos (no hay fuga por reparto). Acierto por microscopía (DINOv2+logística): SEM 34 %, TEM 44 %, cryo-TEM 55 %; no depende del tamaño de la figura.

Advertencia: probé muchas variantes sobre las mismas particiones; la mejor de ellas es algo optimista. Para el resultado final hay que fijar el modelo de antemano y evaluarlo con validación anidada.
