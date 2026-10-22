# Cambios de congelación v0.1

- Corrida antes del cambio y corrida final: 1.824 artículos (E1 1.130, E2 577, no 117), 2.726 paneles, 3.251 descriptores iniciales y 4.015 espectros.
- Se añadió una etapa acotada en `curation/extended.py`, dentro de `apply`, para consolidar filas de descriptor de un mismo artículo y muestra normalizada.
- Regla: normaliza mayúsculas/minúsculas, espacios, puntuación y etiqueta parentética final; conserva distinciones como F1/F2. Une solo si los valores numéricos compartidos no se contradicen y los medios declarados no son incompatibles. Completa únicamente campos vacíos; no transforma ni redondea números. Conserva la cita de la fila principal (la que tiene tamaño, si existe; si no, la primera) y prefiere medio declarado. Por indicación del usuario, un `source` distinto no bloquea la unión: se conserva el `source` principal y se registran ambos `source` y la cita secundaria en `filas_unidas.csv`.
- Resultado: 135 uniones; 3.116 descriptores (reducción de 135). Artículos, niveles, paneles y espectros no cambiaron. Las columnas y el orden de los cuatro CSV permanecen iguales.
- `filas_unidas.csv` registra una fila por unión por pares; `filas_antes=2` describe el par consolidado en ese paso. Si varias filas se consolidan en cadena, puede haber más de una entrada para la misma muestra.
- Pruebas sintéticas: 5/5 casos aprobados (complementariedad con source distinto; F1/F2 separados; conflicto de números separado; conflicto de medios separado; caso ambiguo conservado separado). `py_compile` pasó.
- No se editaron manualmente los CSV ni las salidas de extracción. La explicación de la corrida rápida está en `curation/work/ext/explicacion_corrida_rapida.md`.
