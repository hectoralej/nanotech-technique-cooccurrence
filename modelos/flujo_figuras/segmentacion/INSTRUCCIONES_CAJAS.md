# Instrucciones: cajas de paneles en figuras compuestas (v2, 24-oct)

Tarea: para cada figura de la lista, marcar la **caja de cada panel** con coordenadas normalizadas (0–1) sobre la figura completa. Se te da una copia con una **cuadrícula roja cada 0,1**; el número de cada línea está rotulado: **arriba** los valores de x (izquierda→derecha) y **a la izquierda** los de y (arriba→abajo). Interpola entre líneas (a mitad de camino entre 0,3 y 0,4 → 0,35).

## Reglas de cajas
1. **Una caja por panel útil, en orden de lectura** (filas de arriba abajo; dentro de cada fila, de izquierda a derecha). La caja incluye la imagen o gráfica, sus ejes y números, la barra de escala y la letra del panel si está pegada. No incluyas paneles vecinos. Prefiere cajas algo holgadas (≈ 1 %) a cajas que corten el panel.
2. **`paneles_esperados` es una estimación** (sale de la clasificación visual). Dibuja los paneles que realmente hay según estas reglas. Si tu conteo de paneles útiles (micro + espectro) difiere del esperado, la figura pasa a revisión; no fuerces el número.
3. **Recuadros ampliados (inset)**: dibújalos como **caja hija**: `"padre": k, "rel": "inset"` donde `k` es el nº (1, 2, 3…) de la caja del panel que los contiene (la caja del padre **no** se recorta; sigue incluyendo el inset). Las cajas hijas no cuentan como paneles y pueden solaparse con su padre.
4. **Gráficos con ejes propios** (aunque compartan letra, p. ej. dos espectros apilados, cada uno con su eje y) → **una caja por gráfico**.
5. **Espectros en cascada** (curvas de muestras distintas, desplazadas verticalmente sin solaparse, eje x compartido) → **una caja por curva** (banda horizontal de esa curva con su rótulo), cada una con `tipo: "espectro"` y `"cascada": true`. **Curvas que se cruzan o se solapan sobre los mismos ejes → una sola caja** de espectro (es un espectro superpuesto, no se divide).
6. **Fluorescencia, confocal, histología (H&E), citometría y fotos de células o animales → `tipo: "otro"`**. Solo TEM, SEM, STEM, AFM, cryo-EM y microscopía óptica/DIC de partículas o muestras son `micro`.
7. `tipo`: `micro` (micrografías), `espectro` (curva o patrón de un método: FTIR, XRD, UV-vis, EDS, Raman…), `otro` (histograma, barras, esquema, foto, difracción de electrones, mapa elemental de color, tabla, DLS/zeta). Las **tiras de fotos sin letra** (frascos, flujo de trabajo) no se cajean.
8. No uses el pie de figura ni busques el artículo.

## Formato de salida (un archivo JSON por lote)
```
{"<fig_id>": [
   {"tipo": "micro", "caja": [x0, y0, x1, y1]},
   {"tipo": "espectro", "caja": [x0, y0, x1, y1], "cascada": true},
   {"tipo": "otro", "caja": [x0, y0, x1, y1], "padre": 2, "rel": "inset"}
 ], "<otro fig_id>": [...]}
```
`caja = [x0, y0, x1, y1]` con x0 < x1 y y0 < y1, todos en 0–1, 3 decimales. `padre` es el nº de la caja padre (1 = la primera de la lista de esa figura). Campos `cascada`, `padre` y `rel` solo cuando aplican.

## Qué valida el sistema (`consolidar_cajas.py`)
Cajas válidas (0–1, área ≥ 0,5 %); las cajas de nivel superior no se solapan más del 30 %; cada hija está dentro de su padre; el nº de paneles útiles de nivel superior (micro + espectro) coincide con el esperado (si no, la figura va a la cola de revisión con sus cajas, sin recortarse).

## Entrega
Escribe el archivo de salida que se te indique y responde en una línea: figuras hechas y cuáles dudaste.
