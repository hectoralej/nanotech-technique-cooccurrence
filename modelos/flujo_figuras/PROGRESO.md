# Progreso del flujo de revisión visual

## Acuerdo entre revisores (claude vs codex)

- {'figuras_comunes': 210, 'mismo_n_paneles': 0.924, 'mismo_destino': 0.981}

Figuras clasificadas: **4219** de 5539 (76%). Lotes con resultado: 159 de 203.

## Destino según la imagen

destino_vision
compuesta      2713
pareja          709
simple          406
superpuesto     238
excluir         153

## Imagen frente al pie (filas = imagen, columnas = pie)

destino_pie     compuesta  excluir  pareja  revisar_multiple  simple  superpuesto
destino_vision                                                                   
compuesta            1718       37     359               169     146          284
excluir                60        2      22                24      34           11
pareja                 45        4     480                60      65           55
simple                  3        1      10                29     358            5
superpuesto            18        0       7                 0      63          150

Coinciden imagen y pie: 70.3%. Aceptadas automáticamente (coinciden, confianza ≥ 2): 2933. En la cola de revisión: 1286.

## Por categoría (aceptadas / cola)

estado          aceptada_auto  cola_revision
destino_vision                              
compuesta                1856            857
excluir                     2            151
pareja                    538            171
simple                    387             19
superpuesto               150             88

Panel medio por figura: 4.46; figuras con 1 panel: 16.0%; con 2: 20.7%; con 3 o más: 63.3%.
