# Flujo local de imágenes · ajuste 1

El ejecutable actual es `ajuste1.py`, con Python 3.13, Pillow, numpy, pandas y scipy. Solo lee JATS/imágenes locales; no tiene descargas ni redes neuronales. `procesar_lotes.py` se retiró para impedir volver al descargador anterior. Claude mantiene `descargar_v02.py` y su registro `descargas_v02_requests.csv`.

1. `py -3.13 modelos/imagenes_v02/ajuste1.py inventario` completa F1 para los 1.707 E1/E2, independientemente del control visual. Guarda `orden_articulos.csv`, `pies_ajuste1.json` e `inventario_figuras.csv`. Conserva referencias GIF/JPG; para recortar elige JPG antes que GIF y deduplica por figura/archivo disponible.
2. `py -3.13 modelos/imagenes_v02/ajuste1.py lote --lote N` procesa 100 artículos en orden E1→E2. Cada artículo se guarda inmediatamente en `resultados_ajuste1/`. El hash de configuración y las firmas de archivo permiten reanudar sin repetir los artículos cuyos archivos no cambiaron.

Sin `--lote`, `py -3.13 modelos/imagenes_v02/ajuste1.py lote` decide qué retomar desde `progreso.json`: primero un lote extraído pendiente de inspección, después el siguiente sin procesar y, al terminar la primera pasada, el primer lote que recibió imágenes nuevas. Respeta la pausa de calidad. No inventa un cierre visual ni continúa automáticamente tras una muestra sin revisar.
3. `py -3.13 modelos/imagenes_v02/ajuste1.py validar --lote N` compara cajas, imágenes y hashes de píxeles con las figuras originales, reproduce la segmentación y comprueba folds. Un lote recién extraído queda pendiente hasta esta validación y su inspección visual.
4. Mostrar `muestras/ajuste1/muestra_lote_NN.png` e inspeccionar las cinco filas. Registrar los veredictos explícitos en `revision_ajuste1.py` y ejecutarlo con el número del lote. Los veredictos son autoevaluaciones del asistente, no etiquetas humanas. Una figura de una sola modalidad conservada entera puede ser válida como fallback; esto no se reporta como separación individual conseguida. Una figura mixta mal clasificada o un panel cortado/incompleto no cuenta como acierto.
5. `py -3.13 modelos/imagenes_v02/informe_ajuste1.py` reconstruye tablas solo de lotes aprobados y actualiza el informe, cifras por lote/clase y disponibilidad de imágenes. El siguiente lote se bloquea si falta el veredicto anterior, si los lotes 1–2 no pasaron, o si se acumularon dos muestras consecutivas <3/5. Una muestra sin la mezcla mínima puede registrar sus cinco veredictos, pero permanece `PENDIENTE_MEZCLA`, nunca aprobada, aunque alcance 3/5. Es el caso del lote 18 (siete artículos, ninguna gráfica elegible).

Si Claude incorpora imágenes nuevas, ejecutar otra vez el lote afectado: solo se repiten los artículos con firmas distintas. Sus tablas/muestras se regeneran y su cierre anterior queda invalidado hasta repetir validación e inspección. No borrar las versiones anteriores; los recortes nuevos están en `producto/imagenes_recortes/ajuste1/` y los anteriores se conservan para auditoría.

`config_ajuste1.json` documenta los umbrales. Las cajas `(x0,y0,x1,y1)` usan píxeles del original, con extremos derecho/inferior exclusivos. `compuesta_sin_separar` indica que el método conservó la figura completa; también puede ser una figura simple. Los tipos y las puntuaciones son heurísticos y no probabilidades calibradas. En figuras mixtas, un bloque >42% sin técnica inequívoca queda dudoso. Se conservan por separado técnica de figura y de panel.

La revisión del detector de ejes del ajuste 1 solo recalculó estadísticas y tipos: no cambió cajas ni píxeles. `MIGRACION_EJES.json` y `historial_ajuste1_antes_ejes_delgados/` conservan el antes/después. Los nombres de algunos archivos contienen el hash de su generación inicial; el hash vigente es el campo `config_hash` del CSV.

## Hoja humana

`py -3.13 modelos/imagenes_v02/crear_etiquetado.py` genera `producto/imagenes_recortes/ETIQUETADO.html`. La muestra fija de 300 casos queda congelada en `muestra_etiquetado_300.json`; al actualizar predicciones se conservan orden y archivos para no perder etiquetas humanas guardadas. Las imágenes usan rutas relativas y las predicciones empiezan ocultas. Abrir con doble clic manteniendo la estructura de carpetas. Teclas 1–4 etiquetan; ← vuelve; el botón exporta `etiquetas_humanas.csv` con `archivo_recorte,etiqueta,hora`.

`node modelos/imagenes_v02/validar_etiquetado.cjs` verifica en un DOM simulado teclas, anterior, restauración localStorage, exportación y existencia de las 600 rutas. La simulación no escribe etiquetas en la hoja real. El navegador de la aplicación bloquea `file://`; esa comprobación visual del HTML no pudo realizarse y no se eludió la restricción.

`validar_reglas_ajuste1.py` conserva comprobaciones concretas de los errores anteriores y un fixture sintético de colores planos usado solo como prueba. No añade imágenes ni etiquetas artificiales a los datos científicos.
