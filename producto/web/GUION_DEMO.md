# Guion de demo del Atlas Nano2Predict

**Duración prevista:** 2 min 20 s. Ajustar los conteos de filtros tras la revisión visual final.

| Tiempo | Acción | Narración sugerida |
|---|---|---|
| 0:00–0:10 | Mostrar portada y cifras. | «Este Atlas organiza evidencia publicada sobre nanoportadores, sus micrografías y las técnicas usadas para caracterizarlos.» |
| 0:10–0:30 | Ir al explorador; elegir **Liposoma** y `cryoTEM`. | «Puedo combinar el tipo de portador con una técnica y reducir la lista a artículos que documentan ambos.» |
| 0:30–1:10 | Abrir una ficha con imagen local y descriptores; desplegar una cita; pulsar “Copiar cita/DOI”. | «La ficha conserva el DOI, muestra la micrografía y sus metadatos, y permite volver a la cita textual que respalda cada medición.» |
| 1:10–1:40 | En un artículo de ejemplo con predicción real, mostrar la clase de la base separada de la predicción y sus vecinos. | «La etiqueta observada en la base y la predicción del modelo se distinguen. Los vecinos muestran qué micrografías se parecen más.» |
| 1:40–2:00 | Filtrar por `XRD` y elegir un artículo `Nanomaterial`. | «También se puede explorar por técnica espectral y revisar qué material se caracterizó.» |
| 2:00–2:20 | Ir a «Cómo se construyó». | «Cada dato mantiene una ruta de trazabilidad y un control de calidad asistido por IA y verificado por código.» |

## Condiciones para grabar

- Usar las cifras vigentes: 1.707 artículos, 2.726 paneles, 3.116 descriptores y 4.015 espectros.
- Usar predicciones y métricas finales de Bryan. Los JSON locales actuales llevan `prueba: true`: la interfaz los marca como prueba y no se deben presentar como resultados reales.
- Cuando se sustituyan los fixtures por los archivos finales, ejecutar `python web/build_data.py` desde `producto/` para regenerar el indicador de disponibilidad del modelo.
- Si Bryan no entregó los archivos reales, omitir el segmento del modelo o posponer la grabación; no narrar como reales los datos de prueba.
- Antes de grabar, comprobar filtros, citas, imágenes, consola y vista móvil en Chrome. No afirmar que esta revisión quedó hecha por el solo hecho de seguir el guion.
- Cronometrar dos ensayos completos; cambiar el guion si excede 2:30.
