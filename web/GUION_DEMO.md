# Guion de demo del Atlas Nano2Predict

**Duración máxima:** 2 min 30 s. No acelerar la narración: si excede el tiempo, quitar contenido y repetir el ensayo.

| Tiempo | Acción | Narración sugerida |
|---|---|---|
| 0:00–0:10 | Portada y resumen visual. | «Este Atlas conecta artículos sobre nanoportadores con sus datos de caracterización y las figuras de origen.» |
| 0:10–0:25 | Abrir «Figuras y paneles»: mostrar una figura compuesta con las cajas de colores y expandir sus recortes al lado. | «Las cajas ubican los paneles en la figura completa; los recortes mantienen su vínculo con el artículo, la clase y el DOI.» |
| 0:25–0:45 | Volver al explorador, filtrar por portador y microscopía; seleccionar una ficha con imágenes disponibles. | «Puedo filtrar por portador y microscopía, y revisar el registro asociado sin perder la ruta a su fuente.» |
| 0:45–1:05 | Abrir una cita de descriptor; revisar licencia y DOI. | «Cada dato conserva una cita textual. La ficha muestra por separado la licencia registrada y el enlace al artículo.» |
| 1:05–1:25 | Mostrar una ficha con predicción, y otra que discrepa con la etiqueta de la base. | «La predicción es por artículo y no describe necesariamente el objeto de una imagen individual. Cuando difiere de la base, la interfaz lo marca como discrepancia, no como error.» |
| 1:25–1:45 | Página «Modelos y límites»: figuras de modelos, recortes, NFFA y tarjeta final. | «Los recortes ayudan en parte por aportar más vistas. Preentrenar con NFFA no mejoró. El ensamble final se apoya en validación por artículo: exactitud 0,561 y F1 macro 0,521.» |
| 1:45–2:05 | Demo ONNX verificada: elegir una micrografía y ejecutar el ensamble de tres semillas. | «Se ejecuta localmente y compara con una base mayoritaria de exactitud 0,442. Solo admite micrografías de partículas; sus probabilidades son exploratorias y no están calibradas.» |
| 2:05–2:30 | «Cómo se construyó»: diagrama, abrir paso de paneles y citar el criterio de recortes. | «El diagrama y las fuentes dejan trazable el proceso. Para el análisis morfológico se conservan micrografías de partículas elegibles y se excluyen espectros, insets y paneles biológicos.» |

## Reglas antes de grabar

- Usar los conteos reproducidos desde los archivos del repositorio. La base E1/E2 tiene 1.707 artículos; el índice visual tiene 5.539 figuras y 8.108 paneles, de los cuales 4.670 cumplen la regla de elegibilidad para morfología.
- Mantener separadas la predicción de imagen y la etiqueta del Atlas. La referencia histórica v0.1 tiene F1 macro 0,442; la demo final tiene F1 macro 0,521 y exactitud 0,561 por validación cruzada. La exactitud 0,442 de la clase mayoritaria es otra métrica y otra referencia.
- En el control con el mismo número de vistas, la diferencia de exactitud es +0,006 (ResNet50) y +0,008 (DINOv2); el IC de fusión 04 − fusión 03 incluye el 0. El modelo final usa todas las imágenes de entrenamiento y su desempeño se estima con la validación cruzada de referencia.
- Si el paquete ONNX no está disponible o la diferencia media de la prueba supera 0,03, no ejecutar la clasificación en la demo. Se puede mostrar la página «en preparación».
- No se hace la opción en inglés. Los subtítulos en inglés van en el vídeo.
- Antes de grabar, revisar consola, imágenes y vista móvil en un navegador limpio. Dos ensayos completos deben cronometrarse con Héctor presente.
- Congelar solo después de que Héctor lo confirme. La fecha indicada por él es domingo 25 de octubre, 5:45 p. m., hora de Costa Rica; no se congela automáticamente por llegar la fecha.
