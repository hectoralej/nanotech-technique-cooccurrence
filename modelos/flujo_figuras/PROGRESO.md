# Progreso del flujo de revisión visual

## Acuerdo entre revisores (claude vs codex)

- {'figuras_comunes': 180, 'mismo_n_paneles': 0.917, 'mismo_destino': 0.978}

Figuras clasificadas: **2479** de 5539 (45%). Lotes con resultado: 96 de 203.

## Destino según la imagen

destino_vision
compuesta      1753
pareja          403
simple          174
excluir         112
superpuesto      37

## Imagen frente al pie (filas = imagen, columnas = pie)

destino_pie     compuesta  excluir  pareja  revisar_multiple  simple  superpuesto
destino_vision                                                                   
compuesta            1226       37     189               167      98           36
excluir                43        1      16                18      26            8
pareja                 31        4     269                59      35            5
simple                  1        1       7                26     139            0
superpuesto             2        0       2                 0       7           26

Coinciden imagen y pie: 77.2%. Aceptadas automáticamente (coinciden, confianza ≥ 2): 1889. En la cola de revisión: 590.

## Por categoría (aceptadas / cola)

estado          aceptada_auto  cola_revision
destino_vision                              
compuesta                1370            383
excluir                     1            111
pareja                    327             76
simple                    165              9
superpuesto                26             11

Panel medio por figura: 4.87; figuras con 1 panel: 9.4%; con 2: 21.0%; con 3 o más: 69.5%.
