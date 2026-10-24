# Rendimiento del modelo de clase según el tipo de figura (por el pie)

Validación por artículo. IC 95 % por bootstrap de artículos. `n` = imágenes. Los grupos se asignan solo con el texto del pie (estimación, no verdad humana).

## ResNet50 congelado (n = 2100, exactitud global 43.9%)

| Grupo | n | % del total | Exactitud | IC 95 % |
|---|---:|---:|---:|---|
| compuesta | 1139 | 54.2% | 44.8% | 41.8%–47.9% |
| micro_multiple_sin_etiquetas | 223 | 10.6% | 42.2% | 35.7%–48.7% |
| pareja | 421 | 20.0% | 43.2% | 38.5%–47.8% |
| simple | 232 | 11.0% | 45.7% | 38.7%–52.2% |
| sin_micro_ni_espectro | 46 | 2.2% | 37.0% | 22.2%–50.0% |
| sin_pie_en_inventario | 34 | 1.6% | 32.4% | 18.2%–47.1% |
| superpuesto | 5 | 0.2% | 40.0% | 0.0%–80.0% |

Por contenido (qué dice el pie que hay en la figura):

| Contenido | n | % del total | Exactitud | IC 95 % |
|---|---:|---:|---:|---|
| micrografias_y_espectros | 450 | 21.4% | 49.1% | 44.3%–54.1% |
| ni_micro_ni_espectro | 46 | 2.2% | 37.0% | 22.9%–51.1% |
| sin_pie_en_inventario | 34 | 1.6% | 32.4% | 18.2%–48.5% |
| solo_espectros | 36 | 1.7% | 47.2% | 32.3%–64.7% |
| solo_micrografias | 1534 | 73.0% | 42.8% | 40.4%–45.2% |

## DINOv2 congelado (n = 2100, exactitud global 41.6%)

| Grupo | n | % del total | Exactitud | IC 95 % |
|---|---:|---:|---:|---|
| compuesta | 1139 | 54.2% | 44.2% | 41.3%–47.0% |
| micro_multiple_sin_etiquetas | 223 | 10.6% | 34.5% | 28.0%–41.1% |
| pareja | 421 | 20.0% | 42.0% | 37.5%–46.9% |
| simple | 232 | 11.0% | 37.1% | 30.7%–43.2% |
| sin_micro_ni_espectro | 46 | 2.2% | 39.1% | 25.0%–54.3% |
| sin_pie_en_inventario | 34 | 1.6% | 32.4% | 15.2%–50.0% |
| superpuesto | 5 | 0.2% | 20.0% | 0.0%–60.0% |

Por contenido (qué dice el pie que hay en la figura):

| Contenido | n | % del total | Exactitud | IC 95 % |
|---|---:|---:|---:|---|
| micrografias_y_espectros | 450 | 21.4% | 40.9% | 36.4%–45.3% |
| ni_micro_ni_espectro | 46 | 2.2% | 39.1% | 26.0%–53.3% |
| sin_pie_en_inventario | 34 | 1.6% | 32.4% | 17.6%–50.0% |
| solo_espectros | 36 | 1.7% | 22.2% | 8.1%–37.8% |
| solo_micrografias | 1534 | 73.0% | 42.6% | 40.0%–45.1% |

## ResNet50 ajuste fino (n = 2100, exactitud global 45.9%)

| Grupo | n | % del total | Exactitud | IC 95 % |
|---|---:|---:|---:|---|
| compuesta | 1139 | 54.2% | 47.8% | 44.8%–50.9% |
| micro_multiple_sin_etiquetas | 223 | 10.6% | 42.2% | 35.3%–49.5% |
| pareja | 421 | 20.0% | 46.8% | 42.1%–51.8% |
| simple | 232 | 11.0% | 43.5% | 37.0%–50.4% |
| sin_micro_ni_espectro | 46 | 2.2% | 32.6% | 19.6%–46.8% |
| sin_pie_en_inventario | 34 | 1.6% | 29.4% | 12.1%–45.5% |
| superpuesto | 5 | 0.2% | 20.0% | 0.0%–60.0% |

Por contenido (qué dice el pie que hay en la figura):

| Contenido | n | % del total | Exactitud | IC 95 % |
|---|---:|---:|---:|---|
| micrografias_y_espectros | 450 | 21.4% | 52.9% | 48.1%–57.7% |
| ni_micro_ni_espectro | 46 | 2.2% | 32.6% | 19.1%–46.7% |
| sin_pie_en_inventario | 34 | 1.6% | 29.4% | 14.6%–44.8% |
| solo_espectros | 36 | 1.7% | 38.9% | 21.6%–54.3% |
| solo_micrografias | 1534 | 73.0% | 44.7% | 42.1%–47.2% |

## DINOv2 ajuste fino (n = 2100, exactitud global 48.2%)

| Grupo | n | % del total | Exactitud | IC 95 % |
|---|---:|---:|---:|---|
| compuesta | 1139 | 54.2% | 50.2% | 47.3%–53.0% |
| micro_multiple_sin_etiquetas | 223 | 10.6% | 44.8% | 38.1%–51.3% |
| pareja | 421 | 20.0% | 46.8% | 41.5%–52.0% |
| simple | 232 | 11.0% | 48.3% | 41.8%–55.0% |
| sin_micro_ni_espectro | 46 | 2.2% | 32.6% | 20.0%–45.7% |
| sin_pie_en_inventario | 34 | 1.6% | 41.2% | 24.2%–57.2% |
| superpuesto | 5 | 0.2% | 60.0% | 20.0%–100.0% |

Por contenido (qué dice el pie que hay en la figura):

| Contenido | n | % del total | Exactitud | IC 95 % |
|---|---:|---:|---:|---|
| micrografias_y_espectros | 450 | 21.4% | 51.3% | 46.4%–55.9% |
| ni_micro_ni_espectro | 46 | 2.2% | 32.6% | 19.1%–45.9% |
| sin_pie_en_inventario | 34 | 1.6% | 41.2% | 24.2%–58.8% |
| solo_espectros | 36 | 1.7% | 38.9% | 22.9%–55.3% |
| solo_micrografias | 1534 | 73.0% | 48.2% | 45.6%–50.9% |
