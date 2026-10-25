# Imágenes y espectros v0.2 · ajuste 1

Inventario completo: 1707 artículos E1/E2, 6524 figuras lógicas y 10205 referencias gráficas. Las alternativas GIF/JPG se conservan como referencias para la descarga, pero cada figura se recorta una sola vez usando el JPG grande disponible. Claude gestiona las descargas; este flujo solo usa archivos locales.

| Lote | Artículos | Recortes | Muestra visual | Estado |
|---|---:|---:|---:|---|
| 01 | 100 | 348 | 5/5 | aprobado |
| 02 | 100 | 394 | 5/5 | aprobado |
| 03 | 100 | 186 | 4/5 | aprobado |
| 04 | 100 | 226 | 5/5 | aprobado |
| 05 | 100 | 213 | 4/5 | aprobado |
| 06 | 100 | 193 | 4/5 | aprobado |
| 07 | 100 | 224 | 4/5 | aprobado |
| 08 | 100 | 212 | 2/5 | pendiente/no aprobado |
| 09 | 100 | 185 | 4/5 | aprobado |
| 10 | 100 | 208 | 3/5 | aprobado |
| 11 | 100 | 220 | 2/5 | pendiente/no aprobado |
| 12 | 100 | 251 | 4/5 | aprobado |
| 13 | 100 | 202 | 4/5 | aprobado |
| 14 | 100 | 185 | 5/5 | aprobado |
| 15 | 100 | 211 | 5/5 | aprobado |
| 16 | 100 | 219 | 4/5 | aprobado |
| 17 | 100 | 271 | 4/5 | aprobado |
| 18 | 7 | 13 | 3/5 | pendiente/no aprobado |

Las muestras son autoevaluaciones del asistente, no etiquetas humanas. Hay 1474 artículos con recorte en lotes aprobados. Primeros 400: 389 con recorte y 11 pendientes de imagen; meta no cumplida. Ver `pendientes_primeros_400.csv`. Los lotes 8 y 11 fallaron el muestreo. El 18 tiene 3/5 útiles, pero cero gráficas elegibles: queda `PENDIENTE_MEZCLA`, excluido aunque alcance 3/5. No se redujo la exigencia.

Las tablas para modelos contienen solo los lotes con validación técnica y muestra aprobadas: 1102 micrografías probables y 65 gráficas con técnica espectral asignada de forma inequívoca al panel. Las demás gráficas se conservan en `graficas_sin_tecnica_asignada.csv`. Las clases siguen siendo provisionales hasta revisión humana o clasificación del clúster.

Se procesaron 2374 imágenes de figura; 1609 (67.78%) quedaron con estado `compuesta_sin_separar`. Este estado significa que la segmentación conservó la figura completa, no prueba que todas ellas sean composiciones. El total disponible actualmente es 2149 imágenes originales y 248 archivos del destino nuevo; esa cifra incluye alternativas que se deduplican antes de recortar. Se utilizaron 225 figuras que no estaban en la carpeta antigua, beneficiando a 112 artículos; no se cuentan como ganancia los duplicados con el mismo nombre base.

## Método y límites

Se analiza la figura con dimensión máxima 1.400 px, manteniendo su proporción. La máscara no blanca usa mínimo RGB <245; dilatación 3×3, componentes conexas, unión de cajas a ≤5 px y anexión de texto/escala a ≤22 px. Los componentes principales ocupan ≥3% del área. Se combinan con franjas de tinta ≤1,2% y ancho ≥2 px. Todas las cajas finales se expresan en píxeles del original `(x0,y0,x1,y1)`, con extremo derecho/inferior exclusivo. Los recortes no solapan; ante ambigüedad se conserva la figura completa. Figuras mixtas o con subpaneles explícitos sin separar se marcan dudosas.

Se descartan fracción de tinta <2%, <120 píxeles de tinta en la imagen de análisis, proporción >8:1 y regiones de poca tinta/variación de gris compatibles con texto aislado. Descartes observados: 1312 componentes pequeños no asociados antes de formar recortes, y 0 candidatos por filtros de recorte; motivos: {'componente_menor_3pct_o_poca_tinta_no_asociado_a_panel': 1312}. Se registran las cajas y motivos en `descartes_ajuste1.csv`. La prueba específica del antiguo recorte “drying” activa poca tinta y proporción extrema aunque ese candidato ya no se genera con el método nuevo.

Ilustración probable: >78% de la tinta concentrada en 12 colores RGB cuantizados (16 niveles/canal), saturación media de la tinta >0,12 y sin ejes ortogonales detectables. Los demás tipos usan entropía de gris, tinta, saturación y ejes; no son probabilidades calibradas. Un dibujo y una gráfica pueden compartir estadística: la hoja humana permite corregirlos.

`tecnicas_en_pie` contiene solo nombres canónicos extraídos del pie limpio. `tecnica_asignada` queda vacía salvo coincidencia del número de recortes con etiquetas de subpanel consecutivas y mención explícita de técnica en ese subpanel. Se aceptan etiquetas de prefijo; ante sufijos ambiguos como “DLS (A), SEM (B)” se abstiene. No se infiere DLS de “distribución de tamaño”; SEM estadístico se excluye. Cada figura conserva el fold oficial del artículo. La validación compara todos los recortes con su caja en el original orientado mediante EXIF y su hash de píxeles, y reproduce la segmentación.

Discrepancia comprobada visualmente: en PMC10605403, figura 3, el pie intercambia las técnicas de los subpaneles respecto de la imagen. Se retiraron todas las asignaciones de esa figura mediante una abstención por hash del pie, documentada en `reglas_tecnica_ajuste1.json`; no se corrigió ni reinterpretó el artículo. El caso no cuenta como positivo en la muestra del lote 17. Esta observación limita la expresión «inequívoca»: la regla textual no garantiza que el pie publicado sea correcto.

## Evidencia y entrega

`muestras/ajuste1/` guarda las hojas y los veredictos por elemento. `validacion_ajuste1_lote_NN.json`, `CHECKPOINTS.md` y `progreso.json` documentan cada cierre. `conteos_por_lote_clase.csv` y `recortes_por_lote_clase.csv` contienen los conteos detallados. El inventario completo no depende del control visual; 6602 referencias aún no tienen imagen local (pueden ser alternativas del mismo gráfico). No se atribuyen diferencias de calidad a revistas/editoriales sin una revisión específica.

`producto/imagenes_recortes/ETIQUETADO.html` presenta 300 casos fijos, con original al lado, teclas 1–4, anterior, guardado local y exportación `etiquetas_humanas.csv`. Las predicciones están ocultas inicialmente para reducir sesgo. Las etiquetas humanas comienzan vacías. Los originales de referencia se copian sin editar a una carpeta derivada para que la hoja no cambie durante descargas posteriores. Las funciones y 600 rutas se comprobaron en un DOM simulado; el navegador de la aplicación bloqueó `file://`, por lo que su apariencia en navegador no se pudo verificar. No se entrenó ningún modelo ni se ejecutó git.
