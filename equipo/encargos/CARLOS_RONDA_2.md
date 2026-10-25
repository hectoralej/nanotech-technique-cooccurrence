# Carlos: ronda 2 del Atlas (correcciones visibles + resultados con recortes)

Prompt para pegar en tu sesión, con este archivo como contexto. Mismas reglas de siempre: toda cifra sale de un archivo del repositorio y se cita; no toques `curation\`, `modelos\` ni `producto\modelo\`; no publiques nada. La integración de los ZIP quedó bien (5.538/5.539 imágenes, 8.108/8.108 miniaturas): no la repitas.

## 1. Cuatro correcciones que se ven en la web (capturas del 24-oct)
1. **Cartel inferior** «Control de calidad asistido por IA (20 artículos)…» tapa el número de la «Línea base» en el panel del modelo. Muévelo o hazlo descartable (botón ×), sin que cubra cifras.
2. **«Micrografías parecidas»** muestra franjas diminutas y deformadas. Usa `object-fit: contain`, un tamaño mínimo legible y relación de aspecto original.
3. **Predicción por artículo, no por muestra.** En fichas con varias muestras (ej. DPPC_Ctrl y DPPC_HA) aparece la misma predicción. Rotúlala «Predicción por artículo (clase del portador)» y, cuando difiera de la clase de la base, márcalo como «discrepa», no como error.
4. **Panel del modelo desactualizado.** Hoy dice «figura completa · DINOv2 + ResNet50 congelados → SVM» (exactitud 52,62 %). Conserva ese bloque como «Línea base de la v0.1» y añade debajo una sección **«Resultados preliminares con recortes de panel»** con las cifras de la sección 2.

## 2. Resultados con recortes (lee estos archivos; no copies cifras de memoria)
Fuentes: `modelos/comparacion/ANALISIS_04_RECORTES.md/.json` y `ANALISIS_FUSION_04.md/.json`. Muestra en una tabla: imagen con figura completa (03), imagen con recortes (04), medidas (descriptores), fusión 03 y fusión 04; exactitud, exactitud balanceada y F1 macro por artículo, la línea base mayoritaria y los IC 95 % de las diferencias.
Texto obligatorio junto a la tabla (puedes parafrasear, sin quitar ninguna idea): **resultados preliminares; evaluación por artículo con 5 particiones; la ventaja de los recortes se debe en buena parte a que aportan más vistas por artículo (con el mismo número de vistas la diferencia baja a ≈ +0,006 de exactitud); el IC de fusión 04 − fusión 03 incluye el 0.**
Si el JSON de alguna cifra no existe en el checkout, no la pongas y dilo en `PROGRESO.md`.

## 3. Cifras que NO debes mostrar
- «IoU 0,88 contra Codex (31 figuras)»: no está respaldada por un informe. Si ya aparece en la web, el guion o los textos, quítala. Sí se puede citar IoU 0,89 contra las cajas humanas (22 figuras), que consta en `equipo/ESTADO_FIGURAS_24OCT_NOCHE.md`.

## 4. Guion, ensayos y congelado
- Añade al guion de 2:30 la vista **«Figuras y paneles»** (10–15 s: una figura compuesta con sus cajas y los recortes al lado). Si el total supera 2:30, quita algo del resto, no aceleres.
- Dos ensayos cronometrados con Héctor presente. Congela solo cuando Héctor lo confirme. La opción en inglés **no** se hace: los subtítulos en inglés van en el vídeo.
- Si `git push` sigue sin credenciales, entrégale a Héctor la carpeta `producto/web/` (sin `img/`) en un ZIP; él la integra.

## 5. Entrega
Actualiza `producto/web/PROGRESO.md` (qué se hizo, qué quedó) y las 3 capturas nuevas. Verifica otra vez en Chrome limpio a 1440 px y 375 px: 0 errores de consola, 0 imágenes rotas, sin desbordamiento horizontal.
