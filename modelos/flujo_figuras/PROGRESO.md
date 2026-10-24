# Progreso del flujo de revisión visual

## Acuerdo entre revisores (claude vs codex)

- {'figuras_comunes': 120, 'mismo_n_paneles': 0.908, 'mismo_destino': 0.983}

Figuras clasificadas: **2299** de 3079 (75%). Lotes con resultado: 78 de 104.

## Destino según la imagen

destino_vision
compuesta      1627
pareja          384
simple          156
excluir          68
superpuesto      64

## Imagen frente al pie (filas = imagen, columnas = pie)

destino_pie     compuesta  excluir  pareja  revisar_multiple  simple  superpuesto
destino_vision                                                                   
compuesta            1142       32     172               169      87           25
excluir                26        1       7                 2      24            8
pareja                 30        3     261                52      34            4
simple                  1        1       6                25     123            0
superpuesto             7        0       6                 0      13           38

Coinciden imagen y pie: 78.8%. Aceptadas automáticamente (coinciden, confianza ≥ 2): 1794. En la cola de revisión: 505.

## Por categoría (aceptadas / cola)

estado          aceptada_auto  cola_revision
destino_vision                              
compuesta                1294            333
excluir                     1             67
pareja                    313             71
simple                    148              8
superpuesto                38             26

Panel medio por figura: 4.65; figuras con 1 panel: 10.6%; con 2: 21.4%; con 3 o más: 68.0%.
