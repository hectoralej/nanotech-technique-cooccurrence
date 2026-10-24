# Guion de demo del Atlas Nano2Predict

**Duración máxima:** 2 min 30 s. Ajustar los conteos de filtros tras la revisión visual final.

| Tiempo | Acción | Narración sugerida |
|---|---|---|
| 0:00–0:10 | Mostrar portada y cifras. | «Este Atlas organiza evidencia publicada sobre nanoportadores, sus micrografías y las técnicas usadas para caracterizarlos.» |
| 0:10–0:30 | Ir al explorador; elegir **Liposoma** y `cryoTEM`. | «Puedo combinar el tipo de portador con una técnica y reducir la lista a artículos que documentan ambos.» |
| 0:30–1:05 | Abrir una ficha con imagen local y descriptores; desplegar una cita; pulsar “Copiar cita/DOI”. | «La ficha conserva el DOI, muestra la micrografía y sus metadatos, y permite volver a la cita textual que respalda cada medición.» |
| 1:05–1:45 | Mostrar predicción y etiqueta registrada, separadas, para PMC11397097; luego repetir con PMC12657925, donde difieren. | «Aquí coinciden la etiqueta de la base y la predicción; en este otro ejemplo difieren. La etiqueta registrada y la predicción se muestran por separado: es un resultado exploratorio, no una validación definitiva.» |
| 1:45–2:05 | Filtrar por `XRD` y elegir un artículo `Nanomaterial`. | «También se puede explorar por técnica espectral y revisar qué material se caracterizó.» |
| 2:05–2:30 | Abrir «Modelos y límites» y después «Cómo se construyó». | «Se muestran las líneas base y las limitaciones del modelo. Las decisiones y sus fuentes quedan enlazadas para poder revisar el proceso.» |

## Condiciones para grabar

- Usar las cifras vigentes: 1.707 artículos, 2.726 paneles, 3.116 descriptores y 4.015 espectros.
- Los JSON actuales contienen predicciones reales fuera de muestra y `prueba: false`. Métricas del modelo de imagen: exactitud 52,62 %, exactitud balanceada 43,24 %, F1 macro 44,2 % y línea base de exactitud 45,38 %. La nota del modelo advierte que se probaron variantes sobre las mismas particiones y la cifra podría ser algo optimista.
- Ejemplos seleccionados desde las predicciones fuera de muestra: PMC11397097 (nanomaterial / nanomaterial) y PMC12657925 (lipídico / nanomaterial). Confirma ambos en la web antes de grabar y mantén la etiqueta de la base separada de la predicción.
- No describir los ejemplos como prueba de validez del modelo ni afirmar «el modelo acierta». El resultado es exploratorio; la línea base, F1 macro, exactitud balanceada y nota deben quedar visibles.
- Antes de grabar, comprobar filtros, citas, imágenes, consola y vista móvil en Chrome. No afirmar que esta revisión quedó hecha por el solo hecho de seguir el guion.
- Cronometrar dos ensayos completos; cambiar el guion si excede 2:30.
- Grabar con la web congelada, 1920×1080, tras completar la revisión visual de laptop y móvil.
