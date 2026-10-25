# Carlos: web (Atlas), versión casi final: correcciones, visuales y preparación de la demo del modelo

Prompt para pegar en tu sesión, con este archivo como contexto. **Reemplaza a `CARLOS_RONDA_2.md`** (sus 4 correcciones están aquí). Es una tarea larga: analiza primero, luego cambia, luego verifica en navegador limpio. Reglas de siempre: toda cifra sale de un archivo del repositorio y se cita; no toques `curation\`, `modelos\` ni `producto\modelo\`; rama `web-carlos`; no publiques nada; sin credenciales en archivos.

**Qué está muy bien (no lo rompas):** «Figuras y paneles» (destino simple/pareja/compuesta/superpuesto, técnica, clase del portador, cajas sobre la figura), el explorador, la validación de licencia antes de mostrar imágenes, los conteos reproducibles. A Héctor le encanta la parte de figuras clasificadas.

**Qué NO se hace aún:** poner las cifras del modelo final; llegan después. Sí se prepara el espacio (secciones 4 y 5).

---

## 1. Correcciones de datos y filtros (errores reales detectados al revisar los JSON)
1. **«Grupo» (E1/E2) no se entiende.** Es el campo `tier`: **E1** = micrografía + medidas + espectro; **E2** = micrografía + medidas **o** espectro (1.130 y 577 artículos; decisión D4 en `equipo/DECISIONES.md`). Renómbralo «**Nivel de evidencia**», muestra las opciones como «E1 · micrografía + medidas + espectro (1.130)» y «E2 · micrografía + medidas o espectro (577)», con una ayuda corta (icono «?»).
2. **Técnicas duplicadas en «Figuras y paneles».** El campo `tecnicas` de `figuras.json` trae combinaciones libres separadas por `+` (`UV-vis+FTIR`, `FTIR+XRD` y `XRD+FTIR` por separado, `SEM+EDS` y `EDS+SEM`…): el desplegable repite «UV-vis» decenas de veces. Arréglalo en `build_data.py`: separa por `+`, **normaliza** (UVVis = UV-vis; cryoTEM = cryo-TEM; mayúsculas), ordena y deduplica, y ofrece **chips de selección múltiple** («cualquiera de» / «todas»), con conteos por técnica individual. Usa los **mismos nombres** en el explorador (hoy dice «UVVis») y en figuras.
3. **Figuras sin técnica:** 2.886 de 5.539 (52 %) tienen `tecnicas` vacío. Añade la opción «Sin técnica asignada» y una nota que lo explique; no lo ocultes. En los **paneles recortados** el campo `tecnica` está vacío en 8.010 de 8.108: no ofrezcas filtro de técnica a nivel de panel (usa el tipo micro/espectro/otro y el contenido).
4. **Microscopía con códigos crudos** (`TEM_prep_not_declared`, `TEM_negstain`, `TEM_dried_unstained`…): muestra etiquetas legibles («TEM, preparación no declarada», «TEM con tinción negativa»…) con ayuda, sin cambiar los valores de los datos.
5. Confirma de nuevo que no se usa la cifra **«IoU 0,88 contra Codex»** en ningún sitio (no tiene informe). Sí se puede citar IoU 0,89 contra las cajas humanas (22 figuras), de `equipo/ESTADO_FIGURAS_24OCT_NOCHE.md`.

## 2. Correcciones visibles pendientes (de la ronda 2)
1. El **cartel oscuro inferior** («Control de calidad asistido por IA (20 artículos)…») tapa cifras (la línea base). Hazlo descartable (×) y que no cubra contenido; en móvil, que no tape controles.
2. **«Micrografías parecidas»:** miniaturas diminutas y deformadas. Usa `object-fit: contain`, tamaño mínimo legible y proporción original.
3. **Predicción por artículo, no por muestra:** en fichas con varias muestras sale la misma predicción. Rotúlala «Predicción por artículo (clase del portador)» y marca como «discrepa» (no «error») cuando difiera de la clase de la base.
4. **Panel del modelo desactualizado:** conserva el bloque actual como «**Línea base de la v0.1 (figura completa)**», y añade debajo «**Resultados preliminares con recortes de panel**» leyendo `modelos/comparacion/ANALISIS_04_RECORTES.json` y `ANALISIS_FUSION_04.json` (tabla con exactitud, exactitud balanceada, F1 macro por artículo, línea base y los IC de las diferencias). Texto fijo: *preliminar; por artículo; la ventaja de los recortes se debe en buena parte a que aportan más vistas por artículo (con el mismo número de vistas la diferencia baja a ≈ +0,006 de exactitud); el IC de fusión 04 − fusión 03 incluye el 0.* Añade también «**Experimento negativo: preentrenar con NFFA-EUROPE no mejoró**» con la tabla de `modelos/comparacion/ANALISIS_06_NFFA.md` (datos en `entrada_kabre/06_nffa/`): es un resultado honesto y útil para el jurado. Si falta una cifra en el JSON, no la pongas y dilo en `PROGRESO.md`.

## 3. «Cómo se construyó»: diagrama y criterio de figuras
1. Inserta el **diagrama actualizado del flujo** (`figuras/flujo_calidad_figuras_es.png` y `_en.png`; también `.svg`): imagen grande, con clic para ampliar y descarga.
2. Debajo, un **paso a paso interactivo** (6 pasos clicables: búsqueda → extracción → verificación de citas → clasificación de figuras → recorte de paneles → control de calidad), cada uno con su cifra y la ruta del archivo de donde sale.
3. Añade el bloque «**Qué recortes se usan para el modelo y cuáles no**» con la regla (solo micrografía de partículas de nivel superior; no insets, espectros, fluorescencia/histología ni biología) y la muestra honesta de `Para_Bryan\recortes_por_clase.jpg` o su equivalente generado desde la web. Mantén la coherencia con la presentación de Bryan (mismo texto y cifras).

## 4. Visuales e interfaz (hoy es simple)
- **Resumen visual** en la portada y en «Figuras y paneles», en SVG/CSS sin librerías externas: barras apiladas por destino (simple/pareja/compuesta/superpuesto/excluir), donut de clase del portador, barras de técnicas individuales y un histograma de paneles por figura, calculados desde `figuras.json` en el navegador. Cada barra, al hacer clic, filtra la lista.
- **Visor de imagen** (lightbox) con teclado (flechas, Esc), y un interruptor «mostrar/ocultar cajas» con leyenda de colores (verde micrografía, azul espectro, naranja otro; insets con línea punteada).
- **Galería de recortes** por clase del portador (página o pestaña nueva), con paginación y carga diferida, mostrando a qué figura pertenece cada recorte, el artículo, DOI y licencia.
- Estados vacíos y de carga claros; búsqueda con resaltado; contraste y foco visible (accesibilidad); móvil a 375 px sin desbordamiento; `prefers-reduced-motion` respetado.
- Mantén el rótulo «prototipo» y la nota «el modelo es exploratorio».

## 5. Demo «sube una micrografía» en el navegador (preparar ahora, activar cuando llegue el modelo)
Héctor entrega pronto `05_para_web.zip` (ONNX int8, ≈ 90 MB, fuera de Git) con `clases.json`, `preprocesado.json`, `modelo_card.json`, 20 imágenes de prueba y `verificacion_onnx.csv`. Prepara `producto/web/demo.html` + `demo.js`:
1. Carga **`onnxruntime-web`** (WASM, licencia MIT; **copia local** de los archivos en `producto/web/vendor/` con su licencia, versión fijada; sin CDN) y el modelo desde `producto/modelo_onnx/ensamble3_int8.onnx`. Si el archivo no existe, la página lo dice y queda desactivada (nada de errores en consola).
2. **Contrato del modelo:** entrada `imagen` float32 `[N,3,256,256]`, valores **0–255**, RGB (NCHW), sin normalizar. Preprocesado en JS: dibujar el recorte **centrado sobre un lienzo cuadrado blanco** (lado = max(ancho, alto)), reducir a **256×256** con `imageSmoothingQuality = 'high'`, leer `getImageData`, pasar a NCHW float32. El modelo reduce a 224 y normaliza por dentro. Salida `probabilidades` `[N,4]` en el orden de `clases.json` (media de 3 redes).
3. **Prueba de equivalencia:** botón «Comprobar con las 20 imágenes de prueba» que carga cada PNG de `03_verificacion/entradas/`, corre el modelo y compara con `onnx_int8_*` de `verificacion_onnx.csv`; muestra la diferencia máxima. Si la diferencia media supera 0,03, muestra una alerta (el preprocesado de JS no coincide).
4. Interfaz: arrastrar y soltar o elegir un archivo (la imagen **no se sube a ningún servidor**: se procesa en el navegador; dilo), barras con las probabilidades de las 4 clases, y 4 ejemplos pregrabados para probar sin subir nada.
5. **Advertencias visibles siempre:** «Resultados exploratorios. Las probabilidades no están calibradas. Solo tiene sentido con micrografías de partículas (TEM/SEM/AFM/cryo): con espectros, gráficas, células o tejido la salida no significa nada. La clase que predice es la del artículo de origen, no la del objeto fotografiado.» Muestra además el desempeño de referencia de `modelo_card.json` (validación cruzada por artículo) cuando exista.
6. No pongas el modelo en Git (≈ 22–65 MB): ignora `producto/modelo_onnx/` y documenta en `LEEME.md` cómo copiarlo. Mide y anota el tiempo de carga y de inferencia en Chrome.
Mientras no llegue el modelo, prueba la página con un ONNX de juguete o con un simulacro, y deja la página marcada «en preparación» en el menú.

## 6. Guion de la demo (2:30), ensayos y congelado
- Reescribe `GUION_DEMO.md` incluyendo la vista «Figuras y paneles» (10–15 s: una figura compuesta con sus cajas y los recortes al lado) y, si la demo del modelo funciona, 20 s con una micrografía. Si se pasa de 2:30, quita algo, no aceleres.
- Dos ensayos cronometrados con Héctor presente. **Congela solo cuando Héctor lo confirme** (entrega: domingo 25 de octubre, 5:45 pm, Costa Rica). La opción en inglés **no** se hace; los subtítulos en inglés van en el vídeo.

## 7. Verificación y entrega
1. Navegador limpio a 1440 px y 375 px: 0 errores de consola, 0 imágenes rotas, 0 solicitudes fallidas, sin desbordamiento horizontal; prueba con servidor (`python -m http.server`), **no** con doble clic (el `fetch` falla en `file://`: añádelo con letra grande al `LEEME.md`, porque a Héctor le salió vacía por eso).
2. Comprueba los conteos contra los CSV (5.539 figuras; 8.108 paneles; 4.670 recortes elegibles; 2.538 descriptores utilizables).
3. Actualiza `LEEME.md` y `PROGRESO.md` (qué se hizo, qué quedó, qué cifras esperan a Héctor) y las capturas nuevas.
4. Entrega a Héctor un zip de `producto/web/` (sin `img/`, sin `vendor/` pesado si no cabe; indícalo). Si `git push` sigue sin credenciales, ese zip es la entrega.
