# Atlas Nano2Predict — revisión de cierre para Héctor

**25 de octubre de 2026.** Trabajo en `web-carlos`, sincronizado con `main` en `21bfd4f` mediante el merge local `2c72ec4`. Este informe sustituye el corte anterior en el que faltaban las figuras y NFFA.

## Entrega y navegación

- Paquete: `entrega/atlas_web.zip`, carpeta `web/`, sin `web/img/`. Incluye el runtime local y su licencia; el ONNX sigue en la carpeta hermana `producto/modelo_onnx/`, fuera del ZIP y de Git.
- [Guía para instalar y abrir el Atlas](LEEME.md), [progreso completo](PROGRESO.md), [mapa de técnicas](TECNICAS.md), [guion de 2:30](GUION_DEMO.md).
- [Portada](index.html), [figuras y paneles](figuras.html), [galería](galeria.html), [construcción](construccion.html), [modelos y límites](modelos.html), [demo ONNX](demo.html).
- Vista previa en esta computadora mientras el servidor esté activo: <http://127.0.0.1:8010/web/>. Para otra computadora, seguir LEEME y servir `producto/` con Python; los enlaces locales no constituyen una publicación en la nube.

## Qué quedó completo

1. **Técnicas.** Alias normalizados conservando el texto original de cada figura. Seis familias, incluida «Microscopía electrónica y de sonda» con AFM. Diez técnicas principales visibles; las otras 28 etiquetas dentro de «Otras técnicas», desplegable. Los marcadores que no definen un método quedan fuera del filtro.
2. **Sin técnica.** Los números anteriores usaban universos distintos: 1.974 entre 3.873 aceptadas visibles y 2.886 entre 5.539 fuente. Tras depurar marcadores son 1.975 visibles y 2.892 fuente. Gráfico y chips muestran el mismo alcance inicial y explican la diferencia.
3. **Lenguaje y cifras.** «Clases» en las tareas de tres/cuatro clases y D7. Cero e intervalos sin «−0». Diferencias como +0,042, sin porcentaje relativo; +0,006 ResNet50 y +0,008 DINOv2. Celdas de vistas en filas de diferencia: n/a.
4. **Modelos.** Tres figuras españolas originales arriba, visor y descargas PNG/SVG/PDF. Tablas plegables debajo. Las muestras permanecen identificadas: recortes n=1.112, fusión n=786, NFFA/modelo final n=1.114.
5. **NFFA.** Informe y datos reales incorporados desde `modelos/comparacion/`: brazos A/B/C, diferencias e IC. La lectura indica que NFFA no mejoró; el control de etiquetas mezcladas empeoró. Se conservan los límites de una sola receta y etapa inicial.
6. **Modelo final.** Tarjeta derivada de `modelos/modelo_final/02_onnx/modelo_card.json`: ensamble DINOv2 de tres semillas, entrenamiento con todos los recortes y referencia por validación cruzada de exactitud 0,561 / F1 macro 0,521, frente a 0,442 de exactitud mayoritaria. No se presenta el entrenamiento como evaluación independiente.
7. **Construcción.** Hero oscuro del flujo, cinco destinos con ejemplos y cajas, DOI y licencia CC BY. Paso 6: auditoría ciega 47/48 y cajas frente a humano IoU 0,89 en 22 figuras. La muestra asistida de 20 artículos se explica en D8/Limitaciones.
8. **Imágenes y demo.** El visor crea su imagen al abrirse; no queda un `img` con fuente vacía. La demo ejecuta `ensamble3_int8.onnx`; ambos ONNX locales coinciden con `SHA256_onnx.txt`. Runtime Web 1.30.0 verificado contra la integridad SHA-512 de npm y reconstruible con `instalar_runtime.py`.

## Qué se verificó y con qué alcance

- Chrome con pestaña de prueba nueva a **1440×1000 y 375×812**: portada, modelos, construcción, figuras, galería y demo. En los recorridos inspeccionados: **0 errores de consola, 0 imágenes rotas, 0 imágenes con fuente vacía y 0 desbordamientos horizontales del documento**. Las tablas anchas se desplazan dentro de su contenedor.
- Visor de modelos abre/cierra y devuelve el foco; NFFA despliega sus tablas; el filtro «Sin técnica» devuelve **1.975**; «Otras» abre sus etiquetas. DOI/licencia presentes en los cinco ejemplos.
- Las referencias HTML locales existen. Sintaxis JavaScript y generación de datos correctas; no se editaron CSV canónicos ni métricas científicas.
- Equivalencia ONNX: **20/20 entradas**, diferencia absoluta media **0,0051**, máxima **0,0219**. Contrato y CSV de `main` tienen el mismo contenido que el ZIP original; las 20 PNG son idénticas. La diferencia de fin de línea en JSON/CSV no altera los datos.
- Prueba funcional con `PMC10727426`, Fig 1, panel 1 ([DOI](https://doi.org/10.1371/journal.pone.0296032), CC BY). Se comprobó que el artículo no forma parte de los **1.114 artículos / 4.670 recortes etiquetados de entrenamiento**. Carga **1.453 ms**, inferencia **1.745 ms** en esta ejecución. Salida mostrada: inorgánico 42 %, lipídico 6,3 %, nanomaterial 17,6 %, polimérico 34,1 %. Al faltar clase de referencia en el índice de entrenamiento, esta prueba confirma funcionamiento; no mide acierto ni constituye validación externa.
- [Registro de QA](capturas/QA_CIERRE.json) y [captura de modelos en escritorio](capturas/modelos-final-1440.png), [modelos móvil](capturas/modelos-final-375.png), [construcción móvil](capturas/construccion-final-375.png), [tipos de figura](capturas/tipos-figura-final-1440.png), [demo con recorte fuera del entrenamiento](capturas/demo-fuera-entrenamiento-1440.png).

## Qué queda y por qué

- **Textos de Bryan:** se incorporaron la introducción y la lectura compatibles con las fuentes actuales. Los archivos recibidos aún contienen afirmaciones históricas («no hay recortes», ajuste fino/auditoría pendientes). Esas frases no sustituyen los resultados actuales. Próximo paso: Bryan revisa el texto editorial final y confirma su coherencia con la presentación.
- **Dos ensayos con Héctor y grabación:** requieren al presentador. El guion está preparado; falta cronometrar ambos ensayos, ajustar si excede 2:30 y recibir confirmación de congelado.
- **Imágenes al transferir:** el ZIP solicitado omite miniaturas y originales. El receptor aporta las carpetas hermanas de imágenes, `web/img/` y el modelo descargado de la release. LEEME detalla la reconstrucción.
- **Opcionales de interfaz:** no se añadió comparación lado a lado ni un nuevo modo oscuro global. Se revisaron foco, contraste y tarjeta oscura del hero en el diseño existente.
- **Publicación:** el Atlas no se desplegó en un hosting. El estado exacto de commit/push se entrega junto al ZIP en `entrega/estado_git.txt`; Héctor decide el merge y la publicación.

## Continuidad

El checkpoint de sesión está en `C:/Users/abarc/Documents/Codex/2026-10-20/re/CHECKPOINT_ATLAS_CIERRE.md`, con checkpoints de Modelos y Construcción al lado. Permite retomar los pendientes sin repetir la integración.
