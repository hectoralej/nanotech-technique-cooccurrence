# Progreso del flujo de revisión visual

## Acuerdo entre revisores (claude vs codex)

- {'figuras_comunes': 60, 'mismo_n_paneles': 0.933, 'mismo_destino': 0.983}

Figuras clasificadas: **1470** de 3079 (48%). Lotes con resultado: 49 de 104.

## Destino según la imagen

destino_vision
compuesta    1067
pareja        279
simple        119
excluir         5

## Imagen frente al pie (filas = imagen, columnas = pie)

destino_pie     compuesta  excluir  pareja  revisar_multiple  simple  superpuesto
destino_vision                                                                   
compuesta             784       26     113                92      47            5
excluir                 4        0       1                 0       0            0
pareja                 23        2     183                47      24            0
simple                  1        1       5                23      89            0

Coinciden imagen y pie: 82.9%. Aceptadas automáticamente (coinciden, confianza ≥ 2): 1206. En la cola de revisión: 264.

## Por categoría (aceptadas / cola)

estado          aceptada_auto  cola_revision
destino_vision                              
compuesta                 864            203
excluir                     0              5
pareja                    230             49
simple                    112              7

Panel medio por figura: 4.46; figuras con 1 panel: 8.1%; con 2: 22.8%; con 3 o más: 69.1%.
