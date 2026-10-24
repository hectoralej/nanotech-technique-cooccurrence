# Instrucciones para el revisor visual (Claude o Codex)

Tarea: mirar hojas de contacto de figuras de artículos de nanomateriales y contar, **solo con la imagen**, cuántos paneles tiene cada figura y de qué tipo. No uses el pie de figura ni busques el artículo: la clasificación debe ser independiente del texto. No inventes: si una hoja no deja ver, baja la confianza.

## Reglas generales
- No modifiques nada fuera de `modelos/flujo_figuras/resultados/<tu_nombre>/`. No uses git. No entrenes modelos.
- Trabaja **un lote a la vez** y **guarda el archivo del lote apenas lo termines** (checkpoint). Si la sesión se corta, se reanuda con `siguiente_lote.py`.
- Cada lote tiene 30 figuras en 5 hojas (6 por hoja, cuadrícula 3×2, número rojo en la esquina). El número rojo identifica la figura; no cuenta como panel.

## Paso a paso
1. `python modelos/flujo_figuras/siguiente_lote.py <tu_nombre>` → imprime los próximos lotes pendientes (por defecto 3). `<tu_nombre>` = `claude` o `codex`.
2. Abre `modelos/flujo_figuras/lotes/Lxxx.json` (lista de figuras y de hojas) y mira cada hoja (`miniaturas/Lxxx_hN.jpg`) con la herramienta de lectura de imágenes.
3. Escribe `modelos/flujo_figuras/resultados/<tu_nombre>/Lxxx.jsonl`: **una línea JSON por figura**, 30 líneas, en el orden del lote.
4. Cuando termines una tanda, corre `python modelos/flujo_figuras/consolidar.py` para validar el formato y ver el progreso. Corrige lo que marque.

## Campos (una línea por figura)
```
{"n": 1, "paneles": 9, "n_micro": 9, "n_espectro": 0, "n_otro": 0, "curvas_superpuestas": "na", "espectro_limpio": "na", "tecnicas": "TEM", "calidad": "buena", "confianza": 3, "nota": "9 TEM en cuadricula 3x3"}
```
- `paneles`: número de imágenes o gráficas **separadas** (por borde, hueco blanco o letra a, b, c…). Un recuadro ampliado (inset) dentro de un panel **no** cuenta aparte. Una gráfica con varias curvas es **1** panel.
- `n_micro`: paneles que son micrografías (TEM, SEM, AFM, cryo-EM, fotos de microscopía con partículas/estructura y a veces barra de escala).
- `n_espectro`: paneles que son curvas o patrones de un solo método (FTIR, XRD, UV-vis, Raman, EDS, XPS, DSC/TGA, SAXS, fluorescencia, NMR…). Curva con ejes numéricos.
- `n_otro`: histogramas de tamaño, barras de viabilidad/liberación, esquemas, fotos de frascos/animales, tablas, estructuras químicas, mapas de color, etc.
- `n_micro + n_espectro + n_otro` debe sumar `paneles`.
- `curvas_superpuestas`: `"si"` si algún panel espectral tiene **2 o más curvas dibujadas en los mismos ejes** (varias muestras, tiempos, concentraciones); `"no"` si cada panel espectral muestra una sola curva; `"na"` si no hay espectros.
- `espectro_limpio`: `"si"` si hay al menos un espectro de una sola curva legible; `"no"` si todos están superpuestos o ilegibles; `"na"` si no hay espectros.
- `tecnicas`: técnicas que **se leen** en la imagen (ejes, rótulos, barra de escala, 'TEM'), separadas por `+`; `""` si no se puede saber. No supongas.
- `calidad`: `"buena"` (legible), `"regular"`, `"mala"` (borrosa o diminuta).
- `confianza`: 3 = seguro del conteo; 2 = probable; 1 = dudoso (la hoja no deja contar con certeza).
- `nota`: máximo 12 palabras, solo si ayuda (p. ej. «mezcla 4 TEM y 1 gráfico de barras»).

## Casos frecuentes
- Cuadrícula de micrografías 2×2, 3×3 → compuesta (n_micro = nº de celdas).
- Una micrografía + su espectro EDS al lado → 2 paneles (n_micro 1, n_espectro 1).
- FTIR con 4 curvas apiladas en un solo gráfico → 1 panel, `curvas_superpuestas: "si"`.
- Cuatro FTIR cada uno con una curva → 4 paneles espectro, `curvas_superpuestas: "no"`.
- Diagrama del proceso + micrografía → `n_otro: 1`, `n_micro: 1`.
- Patrón de difracción de electrones (SAED/FFT, puntos o anillos sobre fondo negro), mapas elementales de color y curvas DLS/zeta → `n_otro` (no son micrografía ni espectro limpio).
- Imagen demasiado pequeña para contar → `confianza: 1`.

## Entrega de la tanda
Al terminar cada tanda responde solo con: lotes terminados, número de figuras con `confianza` 1, y cualquier problema (hoja ilegible, formato). Nada de resúmenes largos.
