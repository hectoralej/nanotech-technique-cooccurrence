# Auditoría de las imágenes originales (v0.1) · 23 de octubre

Trabajo en paralelo a la sesión de Codex (segmentación en `modelos/imagenes_v02/`): esta auditoría vive en `modelos/auditoria_imagenes/` y **no toca** nada de la de Codex, ni `producto/imagenes/`. Se hizo por 5 lotes de 430 imágenes con checkpoint (`progreso.json`).

## Calidad de las 2.149 imágenes
- Mediana **0,39 megapíxeles** (percentil 10: 0,2 MP; percentil 90: 0,7 MP): son figuras pequeñas (unos 600 × 600 px). Reducirlas a 224 × 224 para el modelo pierde mucho detalle de una figura que ya mezcla paneles.
- **7 imágenes** menores de 0,1 MP y **8** con más de 2.000 px de lado.
- **124 imágenes (5,8 %)** son más del 70 % blanco: casi puro texto, gráficas o diagramas, sin micrografía útil. La fracción de blanco mediana es 0,21.
- **41 imágenes (1,9 %)** tienen más del 30 % de píxeles en color: suelen ser gráficas, mapas o ilustraciones, no micrografías en escala de grises.
- Detalle por imagen: `imagenes_calidad.csv` (ancho, alto, megapíxeles, peso, fracción blanca, fracción en color, contraste, hash).

## ¿Hay figuras repetidas entre artículos (fuga entre particiones)?
**No.** Dos comprobaciones:
1. **Hash perceptual de 8×8** (distancia ≤ 6 en dos hashes): 8 pares entre artículos, todos de clases distintas. Al verlos son micrografías grises distintas que comparten el aspecto general: **falsos positivos** de un hash demasiado grueso.
2. **Vectores DINOv2 (más fiables):** de 2.100 imágenes, **0 pares con similitud coseno ≥ 0,95**; el máximo ronda 0,94 (209 pares ≥ 0,90). Revisados visualmente, los 5 pares más parecidos son **figuras distintas** de nanopartículas (TEM de agregados, paneles con histogramas), no copias ni recortes de la misma figura.
Conclusión: no hay evidencia de que una misma figura esté en entrenamiento y en prueba. Esto responde al punto 1 y al 10 de `modelos/REVISION_CRITICA.md` para las imágenes. (No descarta reutilización de datos con figuras redibujadas.)

## Lo que dicen las 10 mejores coincidencias sobre el problema de las imágenes
Casi todas las figuras más parecidas son **compuestas**: micrografía + histograma de tamaños + curva de DLS + espectro EDS/Raman en un solo archivo. Es el mismo problema que muestran las hojas de Codex y confirma la hipótesis del profesor: el modelo aprende de una mezcla, no de la micrografía.

## Qué se desprende
1. **Resolución:** al recortar paneles (trabajo de Codex), cada recorte será aún más pequeño; conviene subirlos de escala con cuidado o usar 224 sin deformar.
2. **Filtro barato ya disponible:** las ~6 % de imágenes casi blancas y las de mucho color pueden marcarse como sospechosas en la tabla del modelo y probar su efecto (experimento para después).
3. **Sin necesidad de deduplicar** las imágenes en la v0.1.

Scripts: `auditar_imagenes.py` (calidad, por lotes y reanudable), `duplicados.py` (hash) y `duplicados_embeddings.py` (DINOv2). Muestras visuales en `muestras/`.

