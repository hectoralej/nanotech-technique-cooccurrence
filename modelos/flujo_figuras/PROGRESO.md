# Progreso del flujo de revisión visual

## Acuerdo entre revisores (claude vs codex)

- {'figuras_comunes': 60, 'mismo_n_paneles': 0.933, 'mismo_destino': 0.983}

Figuras clasificadas: **2149** de 3079 (70%). Lotes con resultado: 73 de 104.

## Destino según la imagen

destino_vision
compuesta      1513
pareja          360
simple          146
excluir          66
superpuesto      64

## Imagen frente al pie (filas = imagen, columnas = pie)

destino_pie     compuesta  excluir  pareja  revisar_multiple  simple  superpuesto
destino_vision                                                                   
compuesta            1065       27     160               158      78           25
excluir                26        0       6                 2      24            8
pareja                 27        2     245                51      31            4
simple                  1        1       6                24     114            0
superpuesto             7        0       6                 0      13           38

Coinciden imagen y pie: 78.9%. Aceptadas automáticamente (coinciden, confianza ≥ 2): 1681. En la cola de revisión: 468.

## Por categoría (aceptadas / cola)

estado          aceptada_auto  cola_revision
destino_vision                              
compuesta                1209            304
excluir                     0             66
pareja                    296             64
simple                    138              8
superpuesto                38             26

Panel medio por figura: 4.59; figuras con 1 panel: 10.8%; con 2: 21.6%; con 3 o más: 67.5%.
