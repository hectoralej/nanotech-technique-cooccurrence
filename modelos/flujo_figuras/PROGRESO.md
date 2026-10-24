# Progreso del flujo de revisión visual

## Acuerdo entre revisores (claude vs codex)

- {'figuras_comunes': 300, 'mismo_n_paneles': 0.903, 'mismo_destino': 0.973}

Figuras clasificadas: **4459** de 5539 (81%). Lotes con resultado: 176 de 222.

## Destino según la imagen

destino_vision
compuesta      2834
pareja          747
simple          442
superpuesto     279
excluir         157

## Imagen frente al pie (filas = imagen, columnas = pie)

destino_pie     compuesta  excluir  pareja  revisar_multiple  simple  superpuesto
destino_vision                                                                   
compuesta            1783       36     378               169     153          315
excluir                63        3      22                24      34           11
pareja                 41        4     506                60      71           65
simple                  3        1      10                29     388           11
superpuesto            21        0       7                 0      73          178

Coinciden imagen y pie: 69.9%. Aceptadas automáticamente (coinciden, confianza ≥ 2): 3250. En la cola de revisión: 1209.

## Por categoría (aceptadas / cola)

estado          aceptada_arbitrada  aceptada_auto  cola_revision
destino_vision                                                  
compuesta                       31           1917            886
excluir                         84              2             71
pareja                          20            562            165
simple                           7            415             20
superpuesto                     34            178             67

Panel medio por figura: 4.42; figuras con 1 panel: 16.8%; con 2: 20.6%; con 3 o más: 62.5%.
