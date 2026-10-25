# Carlos: web (Atlas), cierre. Qué falta, dónde está todo y cómo entregarlo

Prompt para pegar en tu sesión, con este archivo como contexto. **Actualiza y reemplaza lo que contradiga a `CARLOS_WEB_RONDA_3.md`** (sigue vigente en lo que no se cambia aquí). Reglas de siempre: toda cifra sale de un archivo del repositorio y se cita; no toques `curation\`, `modelos\` ni `producto\modelo\`; no inventes cifras. **El repositorio es PÚBLICO** (comprobado con `gh`): no subas credenciales, imágenes sin licencia reutilizable ni datos que no deban verse; las imágenes de artículos solo con crédito (DOI y licencia).

## 0. Todo está ya en GitHub (rama `main`); haz `git pull origin main`
Los colaboradores con permiso de escritura son `juanabarcaurena-creator` y `BryanRZ02-org`; usa la cuenta con la que estás autorizado. Si `git push` falla por credenciales: ejecuta `gh auth login` (o inicia sesión en Git Credential Manager) y vuelve a intentar; si no sale, entrega el zip (sección 6).
Qué encuentras ahora en el repositorio (no pidas zips aparte):
| Qué | Dónde |
|---|---|
| 3 figuras de modelos + 1 figura de flujo de datos (es/en; PNG, SVG, PDF) | `figuras/modelos/` (`fig_hero_flujo_*`, `fig_modelos_1/2/3_*`) |
| Ejemplos de figuras con cajas (2 por destino) y rejilla de recortes por clase, con `creditos.csv` | `entrega/ejemplos_presentacion/` |
| Experimento NFFA (informe y datos) | `modelos/comparacion/ANALISIS_06_NFFA.md` y `modelos/comparacion/entrada_kabre/06_nffa/` |
| Modelo final: ficha, contrato, verificación, 20 entradas de prueba | `modelos/modelo_final/` |
| **Modelo ONNX (67 MB)** | **GitHub Releases, tag `modelo-v1.0`** (`ensamble3_int8.onnx`, `semilla0_int8.onnx`, `SHA256_onnx.txt`). Ya lo tienes en tu copia local; si lo vuelves a bajar, compara el SHA-256. No va en Git. |

## 1. Estado de lo que ya hiciste (verificado por Héctor en el navegador)
Hecho y bien: filtros de «Nivel de evidencia», chips de técnicas (UV-vis ya sin duplicados), etiquetas legibles de microscopía, vista rápida con gráficos, galería de recortes, visor, diagrama descargable, 6 pasos de trazabilidad, panel de modelos con recortes y fusión, demo ONNX operativa (20/20 entradas, diferencia media 0,0051). No lo rehagas.

## 2. Correcciones que faltan (en este orden)
1. **Técnicas:** quedan ~47 técnicas con un solo registro y sinónimos sin unificar (`cryo-EM`/`cryo-TEM`; `H&E`/`HE`/`histologia H&E`; `Potencial zeta`/`zeta`; `DSC-TGA`/`TGA/DSC`/`TGA/DTA`/`TGA`+`DSC`; `HAADF-STEM`/`STEM`; `fluorescencia`/`confocal`/`CLSM`) y etiquetas que no son técnicas (DAPI, FITC, PI, DIC, BF, DiOC6, `N2`, `citometria`, `distribucion de tamano`). Haz un mapa de sinónimos en `build_data.py` y **agrupa por familias** (Microscopía electrónica y de sonda · Espectroscopías · Térmicas · Dispersión de luz/rayos X · Fluorescencia y óptica · Otras). Muestra las 10 técnicas principales, el resto en «Otras» desplegable, y guarda cómo se normalizó en `LEEME.md`.
2. **Cifras que no coinciden:** el gráfico dice 1.974 «Sin técnica» y el filtro 2.886. Explica la diferencia (por ejemplo, solo figuras visibles) o unifícalo.
3. **Lenguaje:** «Clase de portador · tres/cuatro **grupos**» y «D7 · **Grupos** de portador» deben decir **clases**.
4. **Página «Modelos y límites»:**
   - Pon arriba **mis figuras** de `figuras/modelos/` (versión `_es`): `fig_modelos_1` (de las medidas a la imagen y la fusión, v0.1), `fig_modelos_2` (figura completa → recortes) y `fig_modelos_3` (NFFA). Con clic para ampliar y botón de descarga SVG/PNG. Las tablas quedan debajo, plegables.
   - Arregla el formato: «−0 (IC −0,01–−0)» → «0,00 (−0,01 a 0,00)»; las diferencias de recortes están como porcentajes («4,23 %»): son **puntos de exactitud/F1** (escribe «+0,042» o «+4,2 puntos»); «≈ +0,006» → «+0,006 (ResNet50) y +0,008 (DINOv2)»; las celdas «IC por artículo» en las columnas de vistas, déjalas vacías o con «n/a».
   - **Sección NFFA** (ya tienes los datos): título «Experimento: preentrenar con NFFA-EUROPE no mejoró», con la tabla de `ANALISIS_06_NFFA.md` (A, B, C; diferencias con IC) y su texto de lectura y límites. No agregues cifras que no estén en esos archivos.
   - **Modelo final:** una tarjeta con lo de `modelos/modelo_final/02_onnx/modelo_card.json` (qué es, entrenamiento, desempeño de referencia por validación cruzada: exactitud 0,561 y F1 macro 0,521 frente a 0,442 de la clase mayoritaria; el modelo final se entrenó con todos los datos y no se puede evaluar).
5. **«Cómo se construyó»:**
   - Inserta la **figura de flujo** `figuras/modelos/fig_hero_flujo_es.png` (fondo oscuro; ponla en una tarjeta oscura o con borde) al inicio de la sección, con descarga.
   - El paso 6 debe decir «**auditoría a ciegas de figuras: 47/48** y **cajas contra cajas humanas: IoU 0,89 (22 figuras)**»; la muestra de 20 artículos asistida por IA pasa a **Limitaciones/D8**, no a un paso del proceso.
   - Añade «**Tipos de figura**» con los 5 destinos (simple, pareja, compuesta, superpuesto, excluir): una figura de ejemplo con cajas para cada uno (`entrega/ejemplos_presentacion/ejemplo_<destino>_<n>.jpg`), qué es y qué se hace con ella, y su crédito (`creditos.csv`). Mantén el mismo texto y cifras que la presentación de Bryan.
6. **Imagen rota** en la primera página de «Figuras y paneles» (un `<img>` con `src` vacío). Que las miniaturas ausentes muestren el marcador, no una imagen rota.
7. **Textos de Bryan** (`producto/web_contenido/como_se_construyo.md`, `modelos_y_limitaciones.md`): Bryan los actualiza (ver su encargo). Cuando lleguen por `git pull`, sustituye el esqueleto sin cambiar el registro D1–D8.

## 3. Demo del modelo (ya operativa): comprobaciones finales
- Que la ficha mostrada sea la del modelo final (ensamble de 3 semillas) y no otra; que junto a cada resultado aparezcan la validación cruzada (0,561 / 0,521) y la línea base 0,442, más las advertencias (exploratorio, sin calibrar, solo micrografías de partículas, la clase es la del artículo).
- Documenta en `LEEME.md` cómo obtener el ONNX: **descargar de la release `modelo-v1.0`**, comprobar el SHA-256 de `modelos/modelo_final/SHA256_onnx.txt` y copiarlo a `producto/modelo_onnx/02_onnx/`. El runtime (`web/vendor/onnxruntime-web/`) sigue fuera de Git; di cómo reconstruirlo (versión fijada 1.30.0 y su integridad).
- Prueba una micrografía **que no sea de entrenamiento** (por ejemplo una figura recortada de otro artículo) y anota el tiempo de carga e inferencia en Chrome.

## 4. Interfaz
Si te queda tiempo después de lo anterior: un modo de comparación lado a lado en la galería (recorte, figura original con su caja, clase del artículo); atajos de teclado documentados; y un último repaso de contraste/foco en modo claro y oscuro.

## 5. Ensayos y congelado
Guion de demo de 2:30 con la vista «Figuras y paneles» y 20 s de la demo del modelo (`GUION_DEMO.md`). Dos ensayos cronometrados con Héctor presente. **Congela solo cuando Héctor lo confirme** (entrega: domingo 25 de octubre, 5:45 pm, Costa Rica).

## 6. Entrega
1. Rama **`web-carlos`**: `git switch -c web-carlos` (o la que tengas), commit de `producto/web/` **sin** `web/img/`, `web/vendor/` ni `modelo_onnx/` (están ignorados) y `git push -u origin web-carlos`. Avisa a Héctor para el merge.
2. Si no puedes hacer push: un zip de `producto/web/` (sin `img/`) como antes.
3. Actualiza `PROGRESO.md` (qué se hizo, qué quedó, qué espera a otros) y las capturas. QA final en navegador limpio a 1440 y 375 px: 0 errores de consola, 0 imágenes rotas, sin desbordamiento; con servidor local (no doble clic).
