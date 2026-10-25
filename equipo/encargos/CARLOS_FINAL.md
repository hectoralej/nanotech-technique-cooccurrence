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

## Anexo A · Inventario exacto de archivos (rutas desde la raíz del repositorio) y cómo obtenerlos
Repositorio: <https://github.com/hectoralej/nanotech-technique-cooccurrence> (rama `main`). Para tenerlo todo: `git clone https://github.com/hectoralej/nanotech-technique-cooccurrence.git` (la primera vez) o `git pull origin main` (si ya lo tienes). Todas las rutas de abajo son **relativas a la raíz del repositorio**.

### A.1 Figuras de los modelos y del flujo de datos (carpeta `figuras/modelos/`)
Cada figura existe en **español (`_es`) e inglés (`_en`)**. PNG para pantalla (la de flujo a 220 ppp; las de modelos a 300 ppp), SVG editable (con texto real) y PDF (solo las de modelos).
| Archivo | Tamaño |
|---|---|
| `figuras/modelos/fig_hero_flujo_en.png` | 0.31 MB |
| `figuras/modelos/fig_hero_flujo_en.svg` | 0.02 MB |
| `figuras/modelos/fig_hero_flujo_es.png` | 0.31 MB |
| `figuras/modelos/fig_hero_flujo_es.svg` | 0.02 MB |
| `figuras/modelos/fig_modelos_1_en.pdf` | 0.04 MB |
| `figuras/modelos/fig_modelos_1_en.png` | 0.32 MB |
| `figuras/modelos/fig_modelos_1_en.svg` | 0.03 MB |
| `figuras/modelos/fig_modelos_1_es.pdf` | 0.04 MB |
| `figuras/modelos/fig_modelos_1_es.png` | 0.31 MB |
| `figuras/modelos/fig_modelos_1_es.svg` | 0.03 MB |
| `figuras/modelos/fig_modelos_2_en.pdf` | 0.04 MB |
| `figuras/modelos/fig_modelos_2_en.png` | 0.29 MB |
| `figuras/modelos/fig_modelos_2_en.svg` | 0.03 MB |
| `figuras/modelos/fig_modelos_2_es.pdf` | 0.04 MB |
| `figuras/modelos/fig_modelos_2_es.png` | 0.29 MB |
| `figuras/modelos/fig_modelos_2_es.svg` | 0.03 MB |
| `figuras/modelos/fig_modelos_3_en.pdf` | 0.04 MB |
| `figuras/modelos/fig_modelos_3_en.png` | 0.24 MB |
| `figuras/modelos/fig_modelos_3_en.svg` | 0.02 MB |
| `figuras/modelos/fig_modelos_3_es.pdf` | 0.04 MB |
| `figuras/modelos/fig_modelos_3_es.png` | 0.26 MB |
| `figuras/modelos/fig_modelos_3_es.svg` | 0.02 MB |

Qué es cada una:
- `fig_hero_flujo_*` (fondo **oscuro**, 16:9): flujo de datos 5.539 figuras → 1.702 con paneles → 8.108 paneles → 4.670 recortes para el modelo → clase del artículo.
- `fig_modelos_1_*` (fondo blanco): **de las medidas a la imagen y la fusión** (v0.1, figura completa): tamaño (R²) y clase de portador (F1 macro) con IC 95 %.
- `fig_modelos_2_*` (fondo blanco): **de la figura completa a los recortes**, por artículo, con el control de «mismo número de vistas».
- `fig_modelos_3_*` (fondo blanco): **experimento NFFA** (A línea base, B NFFA, C control) por semilla y diferencias con IC.
Se regeneran con `python figuras/generar_figuras_modelos.py` y `python figuras/generar_figura_flujo_datos.py` (la segunda lee los CSV de `modelos/flujo_figuras/`).

### A.2 Ejemplos de figuras con cajas y recortes (carpeta `entrega/ejemplos_presentacion/`)
| Archivo | Tamaño |
|---|---|
| `entrega/ejemplos_presentacion/creditos.csv` | 0.01 MB |
| `entrega/ejemplos_presentacion/ejemplo_compuesta_1.jpg` | 0.09 MB |
| `entrega/ejemplos_presentacion/ejemplo_compuesta_2.jpg` | 0.11 MB |
| `entrega/ejemplos_presentacion/ejemplo_excluir_1.jpg` | 0.18 MB |
| `entrega/ejemplos_presentacion/ejemplo_excluir_2.jpg` | 0.13 MB |
| `entrega/ejemplos_presentacion/ejemplo_pareja_1.jpg` | 0.07 MB |
| `entrega/ejemplos_presentacion/ejemplo_pareja_2.jpg` | 0.07 MB |
| `entrega/ejemplos_presentacion/ejemplo_simple_1.jpg` | 0.06 MB |
| `entrega/ejemplos_presentacion/ejemplo_simple_2.jpg` | 0.03 MB |
| `entrega/ejemplos_presentacion/ejemplo_superpuesto_1.jpg` | 0.05 MB |
| `entrega/ejemplos_presentacion/ejemplo_superpuesto_2.jpg` | 0.09 MB |
| `entrega/ejemplos_presentacion/LEEME.txt` | 0.00 MB |
| `entrega/ejemplos_presentacion/recortes_por_clase.jpg` | 0.15 MB |

`creditos.csv` trae, para cada imagen, el artículo (`fig_id`), el título, el **DOI** y la **licencia**: úsalo para el crédito obligatorio en pantalla. Las cajas: verde = micrografía, azul = espectro, naranja = otro.

### A.3 Modelo final (carpeta `modelos/modelo_final/` + GitHub Release)
Archivos pequeños dentro de Git:
| Archivo | Tamaño |
|---|---|
| `modelos/modelo_final/01_entrenamiento/diagnostico_kabre.json` | 0.00 MB |
| `modelos/modelo_final/01_entrenamiento/metricas_entrenamiento.json` | 0.00 MB |
| `modelos/modelo_final/02_onnx/clases.json` | 0.00 MB |
| `modelos/modelo_final/02_onnx/modelo_card.json` | 0.00 MB |
| `modelos/modelo_final/02_onnx/preprocesado.json` | 0.00 MB |
| `modelos/modelo_final/03_verificacion/resumen_verificacion.json` | 0.00 MB |
| `modelos/modelo_final/03_verificacion/verificacion_onnx.csv` | 0.00 MB |
| `modelos/modelo_final/LEEME.md` | 0.00 MB |
| `modelos/modelo_final/LEEME_WEB.txt` | 0.00 MB |
| `modelos/modelo_final/SHA256_onnx.txt` | 0.00 MB |
y `modelos/modelo_final/03_verificacion/entradas/` con **20 PNG** de prueba (`entrada_00_inorganico.png` … `entrada_19_polimerico.png`).

**Los modelos ONNX NO están en Git** (son 67 MB y 22 MB): están en la **Release `modelo-v1.0`**: <https://github.com/hectoralej/nanotech-technique-cooccurrence/releases/tag/modelo-v1.0>
| Asset | Tamaño | SHA-256 |
|---|---|---|
| `ensamble3_int8.onnx` (**el que usa la demo**: ensamble de 3 semillas) | 67.151.951 bytes | `faed3852850e0b882111a1995b76a6fead15448975981f2f4372bf5ea263d623` |
| `semilla0_int8.onnx` (versión ligera, una semilla) | 22.385.726 bytes | `c2e84c423b6f1b952df99fc8abb81872739c5de533c23a1d1af04ecee77be9b4` |
| `SHA256_onnx.txt` | 173 bytes | |

**Cómo descargarlo y colocarlo** (desde la raíz del repositorio; el repositorio es público, no hace falta iniciar sesión):
```powershell
# 1) crear la carpeta que espera el generador de la web y copiar lo pequeño desde Git
New-Item -ItemType Directory -Force producto\modelo_onnx\02_onnx, producto\modelo_onnx\03_verificacion | Out-Null
Copy-Item modelos\modelo_final\02_onnx\* producto\modelo_onnx\02_onnx\ -Force
Copy-Item modelos\modelo_final\03_verificacion\* producto\modelo_onnx\03_verificacion\ -Recurse -Force
# 2) descargar el ONNX de la release (con gh, o con el navegador desde la URL de la release)
gh release download modelo-v1.0 --repo hectoralej/nanotech-technique-cooccurrence --dir producto\modelo_onnx\02_onnx --pattern "*.onnx" --clobber
# 3) comprobar la huella (debe coincidir con la tabla de arriba y con SHA256_onnx.txt)
Get-FileHash producto\modelo_onnx\02_onnx\ensamble3_int8.onnx -Algorithm SHA256
```
Resultado esperado en tu disco: `producto/modelo_onnx/02_onnx/` con `ensamble3_int8.onnx`, `semilla0_int8.onnx`, `clases.json`, `preprocesado.json` y `modelo_card.json`; y `producto/modelo_onnx/03_verificacion/` con `verificacion_onnx.csv`, `resumen_verificacion.json` y `entradas/*.png`. Esa carpeta (`producto/modelo_onnx/`) está en el `.gitignore` de la web: **no se sube a Git**.

**Contrato del modelo** (también en `modelos/modelo_final/02_onnx/preprocesado.json`): entrada `imagen` float32 `[N,3,256,256]`, valores 0–255, RGB (NCHW); recorte rellenado a cuadrado con blanco, centrado, reducido a 256×256 con suavizado alto; sin normalizar (el modelo reduce a 224 y normaliza por dentro). Salida `probabilidades` `[N,4]` = media de las 3 redes, en el orden de `clases.json` (inorgánico, lipídico, nanomaterial, polimérico). Verificación: ONNX fp32 contra PyTorch, diferencia máxima 3e-6; int8, diferencia media 0,008 y misma clase en el 98,5 % de 200 recortes; en la demo de Carlos, 20/20 entradas con diferencia media 0,0051.
**Desempeño de referencia** (la única estimación honesta; el modelo final se entrenó con todos los datos): validación cruzada por artículo, 1.114 artículos, ensamble de 3 semillas: **exactitud 0,561 y F1 macro 0,521**, frente a **0,442** de exactitud de la clase mayoritaria. Fuente: `modelos/comparacion/ANALISIS_06_NFFA.md` y `modelos/comparacion/entrada_kabre/06_nffa/metricas_06.json`.

### A.3b Otras fuentes de cifras (todas en `modelos/comparacion/` salvo la última)
`ANALISIS_04_RECORTES.md/.json` (recortes frente a figura completa, n = 1.112), `ANALISIS_FUSION_04.md/.json` (fusión con medidas, n = 786), `ANALISIS_06_NFFA.md` (experimento NFFA, n = 1.114), `METRICAS_CON_IC.md` y `METRICAS_AJUSTE_FINO_CON_IC.md` (v0.1, n = 2.100 figuras de 1.641 artículos) y `modelos/tabular/REPORTE_TABULAR.md` (modelos de tamaño y de clase con medidas). **No mezcles cifras de muestras distintas en una misma tabla.**

### A.4 Otros archivos que te pueden hacer falta
`modelos/flujo_figuras/figuras_vision.csv` (5.539 figuras clasificadas), `modelos/flujo_figuras/segmentacion/cajas/indice_recortes.csv` y `paneles.csv` (8.108 paneles con cajas), `modelos/flujo_figuras/PROGRESO.md` (conteos), `modelos/descriptores_v02/descriptores_v03.csv` y `DESCRIPTORES_V03.md` (descriptores y su auditoría), `equipo/DECISIONES.md` (decisiones D1–D24), `equipo/ESTADO_FIGURAS_24OCT_NOCHE.md` (auditoría 47/48 e IoU 0,89). Las imágenes originales y los recortes **no están en Git** (pesan cientos de MB): `producto/imagenes_v02/` y `producto/web/img/` se reciben por zip de Héctor y están en el `.gitignore`.

**Para Carlos, especialmente:** el modelo de la demo es `producto/modelo_onnx/02_onnx/ensamble3_int8.onnx`; si ya lo tienes en tu copia local, comprueba que su SHA-256 coincide con el de la tabla A.3. Si no, sigue los 3 pasos de A.3. Las figuras de A.1 las copias a `producto/web/` (por ejemplo `producto/web/recursos/`) al usarlas en las páginas.
