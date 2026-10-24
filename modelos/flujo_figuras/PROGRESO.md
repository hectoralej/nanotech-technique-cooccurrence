# Progreso del flujo de revisión visual

## Acuerdo entre revisores (claude vs codex)

- {'figuras_comunes': 180, 'mismo_n_paneles': 0.917, 'mismo_destino': 0.978}

Figuras clasificadas: **2479** de 3079 (81%). Lotes con resultado: 84 de 121.

## Destino según la imagen

destino_vision
compuesta      1760
pareja          413
simple          174
excluir          68
superpuesto      64

## Imagen frente al pie (filas = imagen, columnas = pie)

destino_pie     compuesta  excluir  pareja  revisar_multiple  simple  superpuesto
destino_vision                                                                   
compuesta            1238       37     184               183      93           25
excluir                26        1       7                 2      24            8
pareja                 31        4     279                59      36            4
simple                  1        1       7                26     139            0
superpuesto             7        0       6                 0      13           38

Coinciden imagen y pie: 79.2%. Aceptadas automáticamente (coinciden, confianza ≥ 2): 1944. En la cola de revisión: 535.

## Por categoría (aceptadas / cola)

estado          aceptada_auto  cola_revision
destino_vision                              
compuesta                1403            357
excluir                     1             67
pareja                    337             76
simple                    165              9
superpuesto                38             26

Panel medio por figura: 4.69; figuras con 1 panel: 10.5%; con 2: 21.3%; con 3 o más: 68.1%.
