# Codex: figuras para el video

`RAIZ` = `C:\Users\Hector\Desktop\Quimioinformatica Proyecto\nanotech-technique-cooccurrence`. Parte de la etiqueta `v0.1`. Reglas de siempre: no abrir `curation\work\clave_modelo.csv` ni `curation\qc_codex\`; no tocar `curation\`; no usar git; no inventar; cada figura se cierra solo si pasa su validación. `matplotlib` 3.11.2, `pandas` y `numpy` ya están instalados (Python 3.13: `%LOCALAPPDATA%\Programs\Python\Python313\python.exe`).

**Meta:** una carpeta de figuras limpias que se vean como parte del mismo producto que la web de Carlos. Salida en `RAIZ\figuras\figuras_para_el_video\`; los scripts, en `RAIZ\figuras\scripts\`. Bryan hace las gráficas del modelo de imágenes y Carlos la web: **no repitas eso**.

## 1. Estilo común (hazlo primero)
- Crea `figuras\scripts\estilo.py` con la paleta, tipografías, tamaños y funciones comunes. Lee `producto\web\styles.css` y toma de ahí los colores y la tipografía (si la fuente de la web no está instalada, usa una sans-serif legible y una monoespaciada para números).
- **Un color fijo por clase de portador, igual en todas las figuras:** `lipidico`, `polimerico`, `inorganico`, `nanomaterial` (+ gris para «otro»). Usa una paleta apta para daltonismo (por ejemplo Okabe–Ito).
- Lienzo **1920×1080 px** (`figsize=(19.2, 10.8)`, `dpi=100`), fondo claro, márgenes amplios. Salida **PNG y SVG** por figura.
- Texto legible a pantalla de video: títulos ≥ 36 pt, etiquetas ≥ 20 pt, números ≥ 18 pt.
- Todo en español. **El título dice la conclusión** («El 62 % de las micrografías son TEM»), no el nombre del gráfico. Subtítulo con el n exacto. Pie: «Fuente: Nano2Predict v0.1 · extraído con IA y verificado por código».
- Sin gráficos de pastel, sin 3D, sin rejillas densas, sin leyendas lejanas: etiquetas directas.

## 2. Las figuras
Fuentes: `curation\ext_articulos.csv`, `ext_paneles.csv`, `ext_descriptores.csv`, `ext_espectros.csv` (`utf-8-sig`), `curation\v0.1\tabla_modelo.csv` (clase) y `curation\v0.1\RESUMEN_NUMEROS.json`. Solo artículos `tier` E1/E2 (1.707) salvo la figura 1.

1. **Cobertura de la base:** 1.824 artículos leídos → 1.707 con evidencia (E1 1.130, E2 577) → 2.726 micrografías, 3.116 descriptores, 4.015 espectros.
2. **Artículos por año** (barras apiladas por clase).
3. **Artículos por tipo de portador** (barras horizontales ordenadas, con conteo).
4. **Micrografías por tipo de microscopía** (TEM, SEM, cryo-TEM, STEM, HRTEM…), con la clase en color.
5. **Espectros por técnica y clase** (matriz de calor técnica × clase, con conteos).
6. **Distribución del tamaño por clase** (eje log; cajas con puntos; mediana anotada; n por clase).
7. **Zeta frente a tamaño** (dispersión, eje x log, color por clase; marca los 5 valores extremos de `curation\v0.1\valores_extremos.csv` o exclúyelos con una nota).
8. **Cómo se construyó la base:** diagrama de flujo en 4 pasos (búsqueda en Europe PMC → extracción con IA → verificación de cada cita y número por código → control de calidad) usando **solo cifras verificadas** de `RESUMEN_NUMEROS.json`.
9. **Precisión estimada** (de `equipo\qc_carlos\RESUMEN_QC.md`): barras de «sí» sobre lo comprobable en 20 artículos para micrografías, descriptores y espectros. Rotula claramente «muestra de 20 artículos, revisión asistida por IA»; no la presentes como validación humana.

## 3. Validación (obligatoria por figura)
1. Cada número del gráfico coincide con un recuento hecho por el script desde los CSV (imprime la tabla de datos de cada figura en `figuras\figuras_para_el_video\datos\figura_N.csv`).
2. Los totales de las figuras 1–5 coinciden con `RESUMEN_NUMEROS.json` o la diferencia está explicada en el pie.
3. Sin texto superpuesto ni cortado; legible al 50 % de zoom.
4. Mismos colores por clase en todas las figuras (compara visualmente la 2, la 4 y la 6).
5. Cada script puede ejecutarse solo (`python figuras\scripts\figura_N.py`) y regenera su PNG y SVG idénticos.

## 4. Entregables
- `figuras\figuras_para_el_video\figura_1.png/.svg` … `figura_9.png/.svg` y `datos\`.
- `figuras\figuras_para_el_video\INDICE.md`: por figura, el mensaje en una línea, el n, y de dónde salen los datos.
- `figuras\scripts\` con `estilo.py` y un script por figura.
- Reporte corto en el chat: qué figuras quedaron, cuáles fallaron la validación y por qué. **No uses git**: Claude revisa y sube.
