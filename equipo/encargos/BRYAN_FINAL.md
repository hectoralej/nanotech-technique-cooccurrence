# Bryan: presentación, guion y textos de la web, cierre. Qué falta, dónde está todo y cómo entregarlo

Prompt para pegar en tu sesión, con este archivo como contexto. **Actualiza y reemplaza lo que contradiga a `BRYAN_PRESENTACION_FINAL.md`** (sigue vigente en lo que no se cambia aquí; léelo primero). Reglas de siempre: toda cifra sale de un archivo del repositorio y se cita; no inventes cifras; no toques `curation\`, `modelos\`, `producto\modelo\` ni `producto\web\` (es de Carlos). **El repositorio es PÚBLICO** (comprobado con `gh`): no subas credenciales ni imágenes sin licencia reutilizable; las imágenes de artículos solo con crédito (artículo, DOI y licencia).

## 0. Todo está ya en GitHub (rama `main`); haz `git pull origin main`
Los colaboradores con permiso de escritura son `juanabarcaurena-creator` y `BryanRZ02-org`; usa la cuenta con la que estás autorizado. Qué encuentras ahora (no pidas zips aparte):
| Qué | Dónde |
|---|---|
| **Figuras** (es/en; PNG 300 ppp, SVG, PDF): flujo de datos (`fig_hero_flujo_*`, fondo oscuro) y 3 de modelos (`fig_modelos_1/2/3_*`, fondo blanco) | `figuras/modelos/` |
| Figuras originales con cajas (2 por destino), rejilla de recortes por clase y `creditos.csv` | `entrega/ejemplos_presentacion/` |
| Diagrama del flujo de calidad (es/en) | `figuras/flujo_calidad_figuras_{es,en}.{png,svg}` |
| Resultados del modelo y del experimento NFFA | `modelos/comparacion/` (`ANALISIS_04_RECORTES.md`, `ANALISIS_FUSION_04.md`, `ANALISIS_06_NFFA.md`) |
| Modelo final: ficha, contrato, verificación | `modelos/modelo_final/` (el ONNX está en Releases, tag `modelo-v1.0`) |

## 1. Qué figuras usar en la presentación (mínimo 2 o 3; Héctor lo exige)
| Figura | Dónde va | Qué dice |
|---|---|---|
| **`fig_hero_flujo`** (flujo de datos) | Sección nueva «De la figura al recorte» (Bloque 2 del guion) y como imagen de apoyo en la portada del vídeo | De 5.539 figuras a 8.108 paneles y 4.670 recortes; qué entra al modelo y qué no |
| **`fig_modelos_2`** (figura completa → recortes) | Bloque 4 «Modelos» | La ventaja de los recortes, con el control de «mismo número de vistas» y el IC de la fusión que incluye 0 |
| **`fig_modelos_3`** (NFFA) | Bloque 4 «Modelos», como «lo que probamos y no funcionó» | Resultado negativo honesto (B − A incluye 0; mezclar etiquetas daña) |
| `fig_modelos_1` (opcional) | Solo si falta una escalera estática; ya tienes la escalera interactiva | Medidas → imagen → fusión (v0.1) |
Cómo mostrarlas: las de fondo blanco van sobre una tarjeta clara también en el modo oscuro (que no se vea un recuadro raro); la de flujo va en una tarjeta oscura. Visor con clic para ampliar y Esc para cerrar; siempre con su pie (fuente y n) copiado de la imagen, y texto alternativo. En el vídeo, mantén cada figura al menos 8 s en pantalla.

## 2. Pendiente de la ronda anterior (si no lo has hecho)
Sección nueva «De la figura al recorte» (tipos de figura con ejemplos y cajas, de la figura a los recortes en 3 pasos, qué recortes entran y cuáles no, muestra sin retoques con su nota honesta); tabla de decisiones en 4 grupos con las decisiones nuevas **como propuestas** (D25–D33, las confirma Héctor, y agrégalas a `equipo/DECISIONES.md`); bajar de peso la muestra de 20 artículos a una frase en Limitaciones; recursos visuales sin librerías externas (barras por destino, línea de proceso, contadores con `prefers-reduced-motion`); visor de imágenes. **No cites «IoU 0,88 contra Codex»** (no tiene informe); sí «IoU 0,89 contra las cajas humanas, 22 figuras» y «auditoría a ciegas 47/48».

## 3. Cifras del modelo: ya pueden entrar (todas de los archivos citados)
- **Tabla v0.1** (figura completa): déjala como línea base.
- **Con recortes (preliminar), por artículo:** `ANALISIS_04_RECORTES.md` (n = 1.112) y `ANALISIS_FUSION_04.md` (n = 786). **No mezcles columnas entre muestras distintas** (n = 2.100 figuras/1.641 artículos; 1.112; 786; 1.114) y pon el n junto a cada cifra. Salvedades obligatorias: la ventaja de los recortes se debe en buena parte a más vistas por artículo (con el mismo número de vistas baja a +0,006 en ResNet50 y +0,008 en DINOv2); el IC de «fusión 04 − fusión 03» incluye 0.
- **Modelo final:** DINOv2 ViT-S/14, ensamble de 3 semillas, entrenado con 4.670 recortes; **desempeño de referencia por validación cruzada por artículo: exactitud 0,561 y F1 macro 0,521** (1.114 artículos), frente a **0,442** de exactitud de la clase mayoritaria. El modelo final se entrenó con todos los datos: no se puede evaluar; esa es la única estimación honesta. Exploratorio; probabilidades sin calibrar.
- **Experimento NFFA:** `ANALISIS_06_NFFA.md` (A, B, C; diferencias con IC) y su lectura. Resultado: **no mejora**; el control con etiquetas mezcladas empeora.
- **Demo «sube tu micrografía»:** ya funciona en el navegador con ONNX (la hizo Carlos, verificada con 20/20 entradas). Actualiza `EVALUACION_APP_VS_WEB.md` y el guion: ya **no** es «trabajo futuro»; descríbela con sus advertencias (solo micrografías de partículas; sin calibrar; la clase es la del artículo).

## 4. Textos para la web de Carlos (entrega tuya)
Actualiza y deja en `producto/web_contenido/` (los integra Carlos con `git pull`): `como_se_construyo.md` (con el flujo de figuras y recortes, 5.539 → 1.702 figuras con paneles → 8.108 paneles → 4.670 recortes; reglas de elegibilidad; auditoría a ciegas 47/48; IoU 0,89) y `modelos_y_limitaciones.md` (cifras de la sección 3, cada una con su n y su fuente). Mantén el registro D1–D8.

## 5. Guion del vídeo (español e inglés) y cifras
Actualiza `video/GUION.md` y `video/GUION_EN.md`: presupuesto de 10:00 máximo (objetivo 9:50) con problema 1:00 · cómo se construyó 1:30 · **de la figura al recorte 1:30** · Atlas 2:30 (narra Carlos) · modelos y decisiones 2:00 (con las figuras de la sección 1) · limitaciones y cierre 1:20. Descriptores: «3.116 filas, **2.538 utilizables** tras la auditoría v03». Mantén las reglas de «no decir». Revisa que ninguna cifra contradiga los archivos citados.

## 6. Entrega
1. Rama **`presentacion-bryan`**: `git switch -c presentacion-bryan`, commit de `producto/presentacion/`, `video/` y `producto/web_contenido/`, y `git push -u origin presentacion-bryan`. Avisa a Héctor para el merge. Si el push falla por credenciales: `gh auth login`; si no sale, entrega un zip.
2. Verificación: abre la presentación con servidor local (`python -m http.server 8000` desde `producto/`), consola sin errores, 1920×1080 y 375 px, modo claro/oscuro y modo presentar; cada imagen con su crédito.
3. `PROGRESO.md` con qué se hizo, qué quedó pendiente y qué espera a Héctor. No publiques nada; el alojamiento lo decide Héctor.

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

**Para Bryan, especialmente:** las figuras que debes usar están en A.1 (`figuras/modelos/…`); copia a `producto/presentacion/assets/figuras/` solo los archivos que uses (los `.png` y, si quieres texto nítido, los `.svg`) y no cambies su contenido; el texto de apoyo y los pies salen de la propia imagen. Las imágenes de ejemplo de A.2 siempre con su crédito de `creditos.csv`.
