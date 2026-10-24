# Codex: ajuste 1 de la depuración de imágenes (continuación de `CODEX_IMAGENES_ESPECTROS.md`)

Mismas reglas de siempre (no tocar `curation\`, `producto\web\`, `producto\imagenes\`; no git; no inventar; no redes neuronales; validar antes de cerrar) y mismo protocolo de lotes y checkpoints. **Tu pausa por el control visual fue correcta**: eso es exactamente lo que queríamos. Claude revisó las dos hojas de muestra y tu informe. Este archivo dice qué ajustar.

## 1. Qué vimos en tus muestras
**Funcionó:** recortes C–D de una figura TEM (PMC11421787), FTIR (PMC11152947) y zeta (PMC10799878) quedaron completos y bien etiquetados; el corte A–B de PMC10135330 es útil aunque parcial.
**Falló, y por qué:**
1. **Figuras sin separar** (PMC12071938, PMC12940844, PMC9647953): se conservó la figura entera aunque mezcla micrografías, histogramas y mapas; el umbral de franjas blancas no ve paneles pegados o con rejillas finas.
2. **Recortes que no son lo que dice la etiqueta:** la ilustración (dibujo) de PMC10172346 se marcó `grafica_probable · TEM|SAXS`; los histogramas de PMC11672701 heredaron la técnica TEM de la figura.
3. **Recorte casi vacío:** en PMC11945751 salió solo el texto «drying».
4. **Texto de pie corrupto** en la técnica de PMC9647953 («0.26 · N · a c d e g i m n p r s t v»): hay que limpiar o descartar ese campo.
5. Los **`.gif` del inventario (445 de 1.235)** son miniaturas: el zip trae también el `.jpg` grande con el mismo nombre. **Claude ya descarga las imágenes** (ver sección 4).

## 2. Cambios que debes hacer (en este orden)
**A. Segmentación por componentes conexas, además de las franjas.** Con `scipy.ndimage` (instalado): máscara de «no blanco» (umbral configurable), dilatación suave, etiquetado de componentes y cajas envolventes; fusiona cajas que se solapen o que estén muy cerca (la etiqueta «A», la barra de escala y el panel deben quedar juntos); descarta cajas con menos del 3 % del área de la figura o con menos de un mínimo de píxeles «de tinta». Si la figura da 1 sola caja, o las cajas se solapan casi todas, **conserva la figura entera** y márcala `compuesta_sin_separar`. Guarda la **caja (x0,y0,x1,y1)** de cada recorte en `recortes_v02.csv` (para reproducir y revisar).
**B. Filtros de calidad por recorte:** descarta recortes cuya fracción de tinta sea < 2 % (texto suelto, casi vacíos), de proporción extrema (> 8:1), o que sean casi puro texto (muy poca variación de gris). Anota el motivo en un archivo de descartes.
**C. Ilustraciones:** un recorte con pocos colores planos y bordes limpios (dibujo) se marca `ilustracion_probable`, **no** `micrografia_probable` ni `grafica_probable` (estadística de colores únicos y saturación; documéntala).
**D. Técnica:** asignar `tecnica_asignada` a un recorte solo si el número de recortes de la figura coincide con el de etiquetas de subpanel del pie **y** la etiqueta de ese panel nombra la técnica; si no, déjala vacía (la técnica de la figura queda en `tecnicas_en_pie`, no heredada). Limpia el texto de pie (ruido tipográfico) antes de guardar.
**E. Figuras `mixta` del inventario:** si no se separa con seguridad, `mixto_o_dudoso`.
**F. Hoja de etiquetado humano** (nuevo, importante). Genera `RAIZ\producto\imagenes_recortes\ETIQUETADO.html`: una página **autocontenida** (HTML + JavaScript, sin servidor ni librerías externas; abre con doble clic) que muestra de uno en uno **300 recortes al azar con semilla fija** (mezcla de `micrografia_probable`, `grafica_probable`, `ilustracion_probable` y `mixto_o_dudoso`), con la figura original al lado y botones/teclas **1 = micrografía, 2 = gráfica o espectro, 3 = ilustración, 4 = mixto o no sirve, ← = anterior**; guarda el avance en el navegador y tiene un botón «Descargar CSV» que baja `etiquetas_humanas.csv` (`archivo_recorte, etiqueta, hora`). Las rutas a las imágenes deben ser relativas a la carpeta del HTML. Con 300 etiquetas humanas Claude entrena un clasificador de tipo de panel en el clúster; **tú no entrenas nada**.

## 3. Reanudar y validar
1. **Rehace con semilla fija las muestras de los lotes 1 y 2** con el nuevo método y exige ≥ 3/5 bien extraídas en cada uno **antes de seguir**. Como siempre: hoja de contacto de 5 recortes con la figura original al lado, mostrada en la sesión, con tu veredicto por cada uno.
2. Continúa por lotes de 100 artículos. **El inventario (fase 1) no depende del control visual**: complétalo ya para los 1.707 artículos sin esperar.
3. Si dos lotes seguidos bajan otra vez de 3/5, vuelve a parar y propón cambios.
4. Reporta en `INFORME_IMAGENES_V02.md` el porcentaje de figuras que quedaron como `compuesta_sin_separar` y los motivos de descarte.

## 4. Descargas: ya no te toca
Tu descarga con `urllib` dio **468 timeouts de 595** (328 «read operation timed out», 117 «timed out», 21 de apretón SSL): es un problema de red del entorno, no de las figuras. **Claude ejecuta la descarga** con `modelos\imagenes_v02\descargar_v02.py` (zip de Europe PMC con `requests`; mapea `.gif`→`.jpg`). Deja las imágenes en `RAIZ\producto\imagenes_v02\<pmcid>\` y su registro en `modelos\imagenes_v02\descargas_v02_requests.csv`. **Tú usa esas imágenes** y no vuelvas a descargar. Cuando completes el inventario de otros lotes, avísalo y se descargan.

## 5. Plazos
- **Hoy (viernes noche):** A–E hechos y muestras 1–2 revalidadas; inventario completo de 1.707 artículos.
- **Sábado 12 m:** `ETIQUETADO.html` listo y recortes de al menos los 400 primeros artículos con control visual aprobado.
- **Sábado 3 pm:** lo que no esté validado no entra a los modelos del clúster.
