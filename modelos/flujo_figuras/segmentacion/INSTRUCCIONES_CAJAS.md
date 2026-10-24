# Instrucciones: cajas de paneles en figuras compuestas

Tarea: para cada figura de la lista, marcar la **caja de cada panel** con coordenadas normalizadas (0–1) sobre la figura completa. Se te da una copia de la figura con una **cuadrícula roja cada 0,1**; el número de cada línea está rotulado: **arriba** los valores de x (izquierda→derecha) y **a la izquierda** los de y (arriba→abajo). Interpola entre líneas (p. ej. a mitad de camino entre 0,3 y 0,4 → 0,35).

## Reglas
- Una caja por panel, en orden de lectura (filas de arriba abajo; dentro de cada fila de izquierda a derecha). El número de cajas debe ser **exactamente** el número esperado de paneles que se te da.
- La caja debe incluir todo el panel: la imagen o gráfica, sus ejes y números, la barra de escala y la letra del panel **si está pegada**; no incluyas paneles vecinos. Los recuadros ampliados (inset) dentro de un panel quedan dentro de su caja.
- `tipo`: `micro` (micrografía TEM/SEM/AFM…), `espectro` (curva o patrón de un método: FTIR, XRD, UV-vis, EDS…), `otro` (histograma, barras, esquema, foto, patrón de difracción de electrones, mapa elemental de color, tabla).
- Redondea a 3 decimales. Prefiere cajas algo holgadas (≈ 1 % de margen) a cajas que corten el panel.
- No uses el pie de figura ni busques el artículo.

## Formato de salida (un archivo JSON por tanda)
```
{"<fig_id>": [{"tipo": "micro", "caja": [x0, y0, x1, y1]}, ...], "<otro fig_id>": [...]}
```
`caja = [x0, y0, x1, y1]` con x0 < x1 y y0 < y1, todos en 0–1.

## Entrega
Escribe el archivo de salida que se te indique y responde en una línea: figuras hechas, y cuáles dudaste.
