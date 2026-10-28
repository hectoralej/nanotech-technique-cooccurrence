# Historial previo — Atlas Nano2Predict

> **Estado vigente:** [INFORME_CIERRE.md](INFORME_CIERRE.md), cierre del 25 de octubre con `main` en `21bfd4f`. Las secciones anteriores a ese cierre conservan el historial; sus pendientes de figuras/NFFA/modelo ya se resolvieron.

**Corte del 24 de octubre de 2026 en `main`.** Este bloque es historial; el estado actual de la rama `web-carlos` está en la sección de abajo.

## Fuente y datos

El checkout se sincronizó con `origin/main` en `de48aa7`. Se ejecutó `python web/build_data.py` desde `producto/`. La selección contiene solo E1/E2: **1.707 artículos, 2.726 paneles, 3.116 descriptores y 4.015 espectros**. No se subieron cambios: el trabajo de esta sesión sigue local, sin commit ni push.

## Cambios que ya estaban incorporados en ese corte

- Categorías visibles `Nanomaterial` y `Nanoportador`.
- Panel del modelo con exactitud, exactitud balanceada, F1 macro, línea base y nota del JSON real.
- Página `modelos.html` con escalera tabular y métricas de imagen. Las tres líneas base están correctamente resaltadas.
- Página `construccion.html` con D1–D8 y enlaces a evidencias. El texto editorial de Bryan no estaba en `producto/web_contenido/`; queda pendiente sustituir el esqueleto cuando lo entregue.
- Créditos a Europe PMC, licencia/DOI por imagen y Kabré (CeNAT/CNCA) en el pie.
- Favicon agregado; evita el 404 que apareció en la primera ejecución de QA.
- Guion en 2:30 con un ejemplo coincidente y uno discrepante. Ambos se presentan como exploratorios.
- Las imágenes locales no se subieron a Git. `descargas.csv` registra las 44 figuras no disponibles de 30 PMCID.

## QA anterior automatizado en Chrome

Se ejecutó Chrome mediante Playwright en 1365×900 y 375×812. Se recorrieron la portada, una ficha con imágenes y predicción, el ejemplo con predicción distinta, una ficha sin imagen, la página de modelos y la de construcción.

- Cero errores de consola y cero respuestas fallidas/HTTP ≥400 al final del QA.
- Cero imágenes rotas en la ficha probada; los 2.669 paneles marcados `imagen_local=true` apuntan a archivos existentes.
- PMC12703698 muestra el marcador de imagen no descargada y conserva el enlace DOI.
- Categorías correctas y tres filas de línea base visibles.
- En viewport móvil, el documento mide 375 px, igual que el viewport: no hay desbordamiento horizontal. El espacio bajo el buscador se limita al rótulo y a la separación de cuadrícula; no se observó el hueco grande reportado.
- Capturas guardadas en `producto/web/capturas/`: portada laptop, dos fichas con imagen/predicción, una ficha sin imagen, móvil 375 px, modelos y construcción.
- `node --check` pasa para `app.js` y `modelos.js`; `python -m py_compile producto/web/build_data.py` pasa.

La revisión fue automatizada y visual sobre Chrome headless; no equivale a inspección humana en el equipo final ni a un ensayo de presentación.

## Pendientes que se registraron en ese corte

1. Recibir e integrar los textos editoriales de Bryan.
2. Hacer dos ensayos humanos cronometrados; ajustar el guion si supera 2:30.
3. Congelar la web después del ensayo y grabar la demo en 1920×1080.
4. Transferir el ZIP preparado a Héctor. No hay envío remoto realizado.
5. Pasar aparte `imagenes_v0.1.zip` (2.149 JPG, 273,7 MB) para que la copia del receptor pueda mostrar las figuras locales.

El ZIP actualizado está en `entrega/Atlas_traspaso_2026-10-24_QA.zip`. Contiene el código web, datos generados, JSON reales del modelo, métricas tabulares, informe y capturas; omite los JPG.
# Avance web final — 25 de octubre de 2026

## Hecho en `web-carlos`

- La nueva vista `figuras.html` consulta las figuras clasificadas, los paneles, sus cajas normalizadas, técnica, contenido, clase, elegibilidad, insets y cascada. Los filtros corren localmente y la paginación renderiza 12 figuras por página. La cola queda apagada por defecto; puede activarse con una casilla visible.
- `build_data.py` genera los JSON desde las fuentes canónicas; no usa copias de `.build_input/`. Además valida que `paneles.csv` e `indice_recortes.csv` tengan las mismas claves. Si `producto/web/img/paneles_web.csv` existe, exige que coincida con el índice y solo enlaza miniaturas que realmente están en disco.
- La imagen original se dibuja con cajas SVG en coordenadas normalizadas. Solo se enlaza en la web cuando el archivo existe localmente y `license_epmc` indica CC BY/CC0 sin NC o ND. Cada ficha muestra artículo, DOI y licencia registrada. Las imágenes no disponibles muestran un marcador sin petición a una ruta inexistente.
- Los espectros clasificados como `superpuesto` quedan señalados explícitamente como no utilizables para entrenamiento.
- El detalle del explorador ya lee `descriptores_v03.json`: muestra solo `usable_v03=True`, conserva columnas originales y `*_final`, y señala las filas `revisar_v03`. El conteo de portada corresponde a filas v03 utilizables.
- Se agregaron `LEEME.md`, navegación y estilos adaptables a 375 px.
- La base de modelos no se modificó. Se verificaron antes y después los SHA-256 de `metricas.json`, `predicciones.json` y `similares.json`; los hashes coinciden.

## Conteos reproducidos desde los CSV del checkout

- Figuras clasificadas: **5.539**; aceptadas: **4.027**; en cola: **1.512**. La vista inicial muestra **3.873**. Omite los **297** registros con destino `excluir` (154 aceptados y 143 en cola); al activar la cola se agregan 1.369 filas. El filtro de destino ofrece `simple`, `pareja`, `compuesta` y `superpuesto`.
- Índice de paneles: **8.108** filas; cada caja pasa la validación de coordenadas 0–1 y ancho/alto positivo. Conteo calculado directamente: **4.670** recortes micrográficos de partículas elegibles para morfología con clase de portador.
- Descriptores v03: **3.116** filas fuente; **2.538** utilizables; **148** marcadas para revisión en el conjunto fuente, de las que **90** también son utilizables y aparecen marcadas en la ficha.
- Imágenes originales con archivo local y licencia reutilizable: **2.114** de 5.539 figuras; al regenerar, el resto queda como marcador.

## Estado anterior a la llegada de los ZIP (corte previo)

- No se encontró `web_paneles_miniaturas.zip`, `paneles_web.csv` ni `producto/web/img/paneles/`. Por eso hay **0/8.108** miniaturas disponibles. El código y la instrucción para integrar el ZIP están listos, pero no se pueden verificar sus miniaturas ni su alineación visual hasta que Héctor entregue el paquete.
- No se publicaron los archivos ni se activó Netlify, Cloudflare Pages o GitHub Pages; la instrucción exige que Héctor decida cualquier publicación externa. La guía explica el paquete estático sin afirmar que esos despliegues estén probados.
- La cifra de comparación IoU con Codex del encargo carece de tabla o informe respaldatorio en este checkout y no se usa como resultado. La cifra Haiku–humano de 0,89 y la auditoría 47/48 aparecen en el checkpoint `equipo/ESTADO_FIGURAS_24OCT_NOCHE.md`; el reporte es anterior al cierre de la clasificación, por lo que para el total actual se cita `modelos/flujo_figuras/PROGRESO.md` (5.539/5.539).
- No se hicieron los dos ensayos cronometrados ni se grabó la demo: requieren al presentador humano y el paquete de miniaturas para que el ensayo refleje la entrega completa. No se declara congelado el Atlas.

## QA realizado antes de recibir los ZIP

- `python producto/web/build_data.py` terminó y generó los JSON.
- `node --check producto/web/figuras.js` y `node --check producto/web/app.js` pasaron.
- Validación independiente de JSON: 5.539 figuras, 8.108 paneles, 2.538 descriptores utilizables, coordenadas válidas, licencia antes de cargar imágenes y miniaturas existentes antes de enlazarlas.
- QA en Chrome headless con perfil limpio: 1440×1000 y 375×812; la vista abrió con 3.873 resultados, el filtro por PMCID devuelve 2 figuras y activar la cola produce 5.242 resultados visibles. Se encontraron 0 imágenes rotas, 0 errores de consola, 0 solicitudes fallidas y 0 respuestas HTTP ≥400.
- En móvil, el ancho del documento y del cuerpo es 375 px, igual al viewport. En el detalle del explorador se comprobaron 2 filas v03 marcadas para revisión humana.
- Se guardaron tres capturas nuevas en `producto/web/capturas/`: vista de figuras en desktop, vista móvil 375 px y detalle con descriptores v03.

## Siguientes pasos en ese corte

1. Héctor comparte `web_paneles_miniaturas.zip` y confirma si las miniaturas se entregan solo dentro del paquete de despliegue o se agregan a Git.
2. Extraer el ZIP en `producto/web/img/`, regenerar JSON y revisar varias figuras en desktop y 375 px, incluido el alineamiento de cajas, DOI, licencia y miniaturas.
3. Cuando existan las miniaturas, repetir inspección de consola, alineamiento de cajas e imágenes en un navegador limpio a 1440 px y 375 px.
4. Hacer los ensayos y grabación con el presentador; mantener la publicación en espera de la decisión de Héctor.
5. Entregar la rama `web-carlos` para que Héctor revise y una a `main`.

**Estado de GitHub:** el cambio está comprometido en la rama local `web-carlos`. El intento `git push -u origin web-carlos` no pudo obtener credenciales desde Git Credential Manager, así que no se creó `origin/web-carlos`. El conector de GitHub reporta permiso `push`, pero ese acceso aún no está disponible para el cliente Git local. El merge y cualquier publicación siguen pendientes.

## Actualización con paquetes de imágenes — 25 de octubre de 2026

Se recibieron y validaron los ZIP `web_figuras_v02_reducidas.zip` y `web_paneles_miniaturas.zip`. Se comprobó integridad CRC y que no hubiera rutas absolutas ni `..` antes de extraerlos. Las imágenes se mantuvieron fuera de Git: `producto/imagenes_v02/` ya está ignorada y se añadió `producto/web/img/` al `.gitignore` por el tamaño del paquete.

- `web_paneles_miniaturas.zip`: el manifiesto contiene 8.108 claves únicas y coincide exactamente con `indice_recortes.csv`; las 18 columnas comparables también coinciden y las 8.108 miniaturas existen localmente. El generador registró 8.108 recortes disponibles, tras filtrar artículos por licencia.
- `web_figuras_v02_reducidas.zip`: contiene 3.424 archivos (3.346 JPG y 78 WebP) de las 3.425 rutas `producto/imagenes_v02/` requeridas por `figuras_vision.csv`. Falta `PMC10390827/Beilstein_J_Nanotechnol-14-804-g008.jpg`; su registro está en `cola_revision` y `destino_vision=excluir`, así que no se muestra en la vista actual. El DOI y `image_available=false` constan en los JSON; no se presenta como marcador visible mientras permanezca excluida. Los archivos locales totales resueltos para figuras son 5.538/5.539.
- `python web/build_data.py` se volvió a ejecutar desde `producto/`: 1.707 artículos, 5.539 figuras, 8.108 recortes y 2.538 descriptores v03 utilizables. Las cifras anteriores se reproducen.
- No se alteraron los CSV canónicos, `curation/`, `modelos/` ni `producto/modelo/`. La rama no se publica; el despliegue estático requiere decidir con Héctor si estos paquetes de imágenes se incluyen en una entrega aparte.
- Los artefactos de integración (JSON regenerados, guía, progreso y capturas) están en el árbol de trabajo local; no se creó otro commit ni se intentó publicar esta actualización. Los binarios de imagen permanecen ignorados por Git.

## QA tras integrar los ZIP

- Atlas abierto en Chrome headless con contexto limpio a 1440×1000 y 375×812. La página muestra los conteos regenerados y la nota de disponibilidad: 5.538/5.539 imágenes originales y 8.108/8.108 miniaturas.
- En los primeros 12 resultados se cargaron 41 imágenes (figuras originales y recortes) tras desplegar el primer grupo de paneles: 0 rotas. También hubo 0 errores de consola, 0 solicitudes fallidas y 0 respuestas HTTP ≥400.
- A 375 px, `scrollWidth=375` y `clientWidth=375`; no hay desbordamiento horizontal. La atribución DOI/licencia aparece en las fichas inspeccionadas; las cajas SVG se ven alineadas sobre las imágenes en desktop y móvil.
- Validación de decodificación con Pillow: 13.603 JPG (2.149 imágenes `producto/imagenes/`, 3.346 `imagenes_v02/` y 8.108 miniaturas) y 78 WebP, sin archivos inválidos. Se comprobó CRC de ambos ZIP antes de extraerlos.
- La búsqueda `PMC10002596` devuelve 2 figuras y expone el DOI correcto `https://doi.org/10.3390/ijms24054480` junto a la licencia; la ficha muestra la imagen original con cajas y los recortes.
- La auditoría independiente de solo lectura confirmó los conteos, el manifiesto, los campos comparables y la ruta ausente; no encontró discrepancias adicionales.
- Capturas actuales guardadas en `producto/web/capturas/figuras-desktop-zip.png`, `figuras-movil-375-zip.png` y `figuras-paneles-detalle-zip.png`.

## Pendientes

1. Conseguir la imagen ausente `PMC10390827/Beilstein_J_Nanotechnol-14-804-g008.jpg`, o mantener documentada la ausencia. El registro está excluido y no aparece en la vista; mostrarlo requeriría una decisión sobre su inclusión, sin cambiar silenciosamente el CSV canónico.
2. Confirmar con Héctor si los paquetes locales de imágenes se incluirán en una entrega estática separada. `producto/imagenes_v02/` y `producto/web/img/` están excluidas de Git y no se subieron.
3. No se publicó el Atlas. El push desde Git local a `web-carlos` sigue sin credenciales; el commit previo existe solo en el checkout local. Quedan pendientes sincronizar la rama y revisión/merge de Héctor.
4. La opción de idioma inglés indicada como “si da tiempo” no se implementó; el Atlas permanece en español.
5. Siguen pendientes los dos ensayos cronometrados con presentador y la grabación final; son tareas humanas.

## Ronda 3 — 25 de octubre de 2026

### Cambios incorporados localmente

- Normalicé los nombres de técnicas para los filtros de figuras y añadí el filtro por cualquier/todas las técnicas, el conteo de figuras sin técnica y sus enlaces desde los gráficos. El filtro usa la técnica de la figura; no infiere técnicas a partir de paneles cuando el dato no existe.
- Añadí etiquetas legibles para códigos de preparación de microscopía y una galería de recortes paginada, con carga diferida y ficha de artículo, DOI y licencia.
- Añadí el visor ampliado con controles de teclado y opción de mostrar u ocultar cajas, gráficos interactivos y la explicación de D1–D8 con enlaces a fuentes. La página de construcción conserva explícita la regla de inclusión de recortes.
- Mantuve separadas las predicciones exploratorias por imagen de la clase asignada al artículo. La línea base v0.1 de figura completa se conserva; los análisis de recortes y fusión se presentan como preliminares con sus fuentes e intervalos. No cambié las cifras finales del modelo.
- La sección NFFA ahora tiene título neutral. Este checkout no trae `modelos/comparacion/ANALISIS_06_NFFA.md` ni `entrada_kabre/06_nffa/`; por eso no se atribuye un resultado ni se muestran cifras de ese experimento.
- Preparé la interfaz de demo local ONNX, pero sus controles siguen desactivados: faltan el modelo, el runtime local, los archivos de preprocesado/clases y el paquete de verificación. No se carga nada desde CDN y no se generan predicciones simuladas.
- Actualicé el guion de demo, esta bitácora y `LEEME.md`. El README aclara que `entrega/atlas_web.zip` omite `web/img/` y los originales ubicados fuera de `web/`; por tanto, el ZIP es para revisar el código/datos y necesita esos recursos por separado para mostrar imágenes y miniaturas.

### QA realizado

- Regeneré los JSON con `python producto/web/build_data.py`: 1.707 artículos, 5.539 figuras (4.027 aceptadas, 1.512 en cola), 8.108 paneles y 2.886 figuras sin técnica asignada. El estado de demo queda `available=false`.
- Revisé en Chrome las páginas de inicio, figuras, construcción, modelos, galería y demo en escritorio y a 375×812 px. No observé desbordamiento horizontal ni imágenes rotas en los recursos que cargaron. La galería cargó 24 miniaturas en su primera página y pasó correctamente de los recortes 1–24 a 25–48.
- Probé búsqueda por `PMC10002596` (devuelve 2 figuras y resalta coincidencias), el filtro desde una barra del gráfico (actualiza a `destination=simple`), el visor, el control de cajas y el cierre del visor. La página de modelos muestra el aviso de ausencia de fuentes NFFA; la demo informa que no ejecuta un modelo y desactiva cargar/inferir/comparar.
- Los archivos locales de `web/img/` se excluyen intencionalmente del ZIP solicitado. La revisión del sitio local con esos recursos no sustituye la verificación de imágenes al instalar el ZIP en otro checkout.

### Pendiente o bloqueado por insumos externos

1. Recibir de Bryan los textos editoriales y sustituir el esqueleto factual sin cambiar el registro D1–D8.
2. Recibir el informe y los datos fuente NFFA antes de mostrar el resultado de ese experimento.
3. Recibir y validar el paquete local ONNX, runtime y 20 imágenes de verificación; solo entonces activar y probar la demo.
4. Hacer los dos ensayos cronometrados con Héctor/presentador, ajustar el guion si hace falta y congelar/grabar únicamente tras la aprobación de Héctor.
5. Héctor debe revisar la rama y decidir sincronización/merge y publicación. No se hizo push ni publicación.

### Entrega local

- ZIP actualizado: `entrega/atlas_web.zip`, con los archivos de `producto/web/` salvo `producto/web/img/`, `.build_input/` y `__pycache__/`; incluye `LEEME.md` y este `PROGRESO.md`.
- Estado Git al preparar la entrega: rama `web-carlos`; HEAD `523062f` (`Add figure and panel explorer to Atlas`), seguido de `9a21e57` y `6a5ef9b`. La ronda 3 tiene cambios locales sin commit. No se intentó push.

## Modelo final de demo recibido — 25 de octubre de 2026

- Se verificó CRC de `05_para_web.zip` y se extrajeron solo `02_onnx/` y `03_verificacion/` dentro de `producto/modelo_onnx/`. Quedaron los modelos `ensamble3_int8.onnx` (67.151.951 bytes) y `semilla0_int8.onnx`, clases, preprocesado, ficha, CSV y las 20 PNG de entrada.
- Añadí localmente ONNX Runtime Web 1.30.0 (variante WASM; archivos JS/WASM y licencia MIT), fijado por versión e integridad SHA-512 del tarball. El generador ahora detecta las rutas anidadas, el runtime y las 20 imágenes; `demo-status.json` informa `available=true` y `runtime_version=1.30.0`.
- La demo usa `ensamble3_int8.onnx`. El preprocesado implementa RGB float32 NCHW `[1,3,256,256]`, rango 0–255, lienzo blanco cuadrado, recorte centrado con coordenadas subpíxel y reducción con suavizado alto. La salida usa el orden de `clases.json`.
- Comparación ejecutada en Chrome con las 20 filas completas de `verificacion_onnx.csv`, alineadas con `onnx_int8_*`: diferencia absoluta media **0,0051**, máxima **0,0219**; pasa el requisito de media `< 0,03`. La interfaz muestra el máximo y el promedio.
- Se probó una inferencia real con `entrada_00_inorganico.png`; las cuatro probabilidades se renderizaron en el orden acordado con nombres legibles. Las cifras de referencia aparecen tanto en el aviso como junto a cada resultado: validación cruzada por artículo, exactitud **0,561**, F1 macro **0,521**; línea base mayoritaria, exactitud **0,442**. La advertencia exploratoria, de probabilidades sin calibrar, uso exclusivo con micrografías de partículas y etiqueta del artículo permanece visible.
- QA final de la demo en Chrome: escritorio a 1440×1000 y móvil a 375×812; sin desbordamiento horizontal ni imágenes fallidas observadas, y sin errores/advertencias en la consola durante carga, prueba e inferencia. La carga del modelo y la inferencia quedan locales al navegador.
- `producto/modelo_onnx/` y `producto/web/vendor/onnxruntime-web/` están ignorados por Git; no se añadió ni subió el modelo o el runtime. El archivo `entrega/atlas_web.zip` de la sección anterior no incluye estos recursos locales. Para compartir esta demo ejecutable, deben acompañarse el paquete de modelo/runtime o entregarse en una carpeta de producto que los contenga.

### Estado final de la demo

**Operativa localmente y verificada con 20/20 entradas.** No se hizo push, no se cambió la línea base v0.1 ni se publicaron cifras distintas a las indicadas arriba. Permanecen los pendientes editoriales de Bryan, el informe fuente NFFA y los ensayos/aprobación de Héctor para congelar o publicar el Atlas.

## Ajustes finales solicitados — 25 de octubre de 2026

- Se creó `TECNICAS.md` con los sinónimos y las seis familias. El CSV fuente conserva las etiquetas originales; `build_data.py` genera etiquetas normalizadas, familias y conteos auditables. El gráfico presenta diez técnicas principales, «Otras técnicas» y «Sin técnica». El filtro usa las mismas etiquetas y el mismo alcance inicial que el gráfico.
- La diferencia anterior de «Sin técnica» era de universo: **1.974** entre las **3.873** figuras aceptadas y visibles, frente a **2.886** entre las **5.539** figuras fuente. Al retirar marcadores que no son métodos (DAPI, FITC, PI, DIC, BF, DiOC6, N2 y citometría, entre otros), esos conteos pasan a **1.975** y **2.892**. Se explican junto al filtro y en el gráfico.
- Se reemplazó «grupos» por «clases» en la evaluación tabular y D7. El paso 6 de construcción muestra la auditoría ciega **47/48** y el IoU **0,89** de cajas frente al anotador humano; la muestra de **20 artículos** se explica en Limitaciones de modelos.
- Las diferencias de recortes y fusión se muestran como fracciones absolutas con signo (por ejemplo **+0,042**, equivalente a **+4,2 puntos porcentuales**), y los intervalos ya no generan «−0». El texto distingue el control de igual número de vistas: **+0,006 (ResNet50)** y **+0,008 (DINOv2)**.
- La imagen vacía del visor ampliado se crea solo al abrirlo. La primera página ya no contiene un `<img>` sin `src`.
- La demo ONNX permanece activa localmente. Se repitió la comparación de **20/20** PNG: diferencia absoluta media **0,0051**, máxima **0,0219**, ambas por debajo del umbral de media **0,03**. La página muestra exactitud **0,561**, F1 macro **0,521** y línea base mayoritaria **0,442** junto a la advertencia metodológica.
- Quedan por integrar **tres figuras en español** de `Para_Carlos/figuras_modelos` y el informe/datos **NFFA** (`ANALISIS_06_NFFA.md` y `entrada_kabre/06_nffa`). Esas rutas no estaban en el checkout, `origin/main` ni en las carpetas locales accesibles al preparar este corte; se solicitó la ruta exacta al usuario. La sección NFFA presenta la conclusión cualitativa comunicada por el usuario (sin mejora; control con etiquetas mezcladas peor), identifica la fuente pendiente y no atribuye cifras no verificadas.
- La entrega `entrega/atlas_web.zip` se reconstruyó con `web/vendor/onnxruntime-web/` y su licencia; omite `web/img/` y el modelo ONNX que reside fuera de `web/`. Para reproducir la demo en otro checkout hay que aportar `producto/modelo_onnx/` desde `05_para_web.zip`, las carpetas de imágenes y regenerar los JSON.

## Cierre tras CARLOS_FINAL — 25 de octubre de 2026

Se incorporó `main` en `21bfd4f` mediante merge `2c72ec4` preservando todos los cambios locales. Ya están integradas las tres figuras españolas, el hero oscuro, los cinco ejemplos con DOI/licencia, NFFA real A/B/C con IC y la ficha final del ensamble. Técnicas: diez principales y 28 etiquetas en Otras desplegable; AFM pasa a Microscopía electrónica y de sonda. No se modificaron CSV ni métricas fuente.

QA en Chrome a 1440×1000 y 375×812 en seis páginas: sin errores de consola, imágenes rotas, fuentes vacías ni desbordamiento del documento observados. El visor, las tablas plegables y Sin técnica (1.975) funcionan. Datos de equivalencia: media 0,0051, máximo 0,0219 sobre 20 entradas; contrato/CSV/PNG conservan contenido. Prueba funcional fuera de los artículos de entrenamiento: PMC10727426, Fig 1, panel 1; carga 1.453 ms e inferencia 1.745 ms, sin clase de referencia para medir acierto. Registro y capturas en `capturas/QA_CIERRE.json`.

Ambos ONNX coinciden con `modelos/modelo_final/SHA256_onnx.txt`. Runtime 1.30.0 coincide con el tarball npm verificado por SHA-512; `instalar_runtime.py` permite reconstruirlo sin subir vendor a Git. LEEME incluye release, huellas, estructura y mapa de técnicas; GUION_DEMO diferencia referencias históricas y modelo final.

Pendientes reales: revisión editorial final de Bryan (su fuente conserva frases históricas), dos ensayos humanos y confirmación de congelado/grabación. Opcionales no añadidos: comparación lado a lado y modo oscuro global. El ZIP omite img y modelo hermano; incluye vendor/licencia. El informe completo para el traspaso es `INFORME_CIERRE.md`. Resultado de Git/transferencia en `entrega/estado_git.txt`.
