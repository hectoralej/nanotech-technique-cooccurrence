# Instrucciones para Claude (sesión de Bryan)

Eres el asistente de Bryan en el proyecto **Nano2Predict** (hackatón; entrega el domingo 25 de octubre, 5:45 pm Costa Rica). Lee también `equipo/PLAN_EQUIPO_FINAL.md`. Este archivo manda sobre `TAREAS_BRYAN.md`.

## 0. Tu papel
Bryan se encarga de **los modelos**. Empieza el **viernes 23** y para entonces ya estará todo lo que necesita:
- la base **v0.1 congelada** (etiqueta `v0.1` en GitHub, con el repaso de lotes ya fusionado), y
- **las micrografías ya descargadas** por Héctor en `producto/imagenes/<pmcid>/<image_file>` (más `producto/imagenes/descargas.csv`). Si no están en su computadora, Héctor le pasa el zip o Bryan corre `modelos/descargar_imagenes.py`.

Tiene **viernes y sábado por la mañana** para el modelo, así que el plan es corto y concreto: un modelo principal bien evaluado vale más que varios a medias.

**No hagas:** extracción de artículos, cambios en `curation/` (es de Héctor) ni en `producto/web/` (es de Carlos). No abras `curation/work/clave_modelo.csv` ni `curation/qc_codex/`. Si Bryan ya descargó figuras o tiene código de antes, reutilízalo.

## 1. Datos de entrada
- `curation/ext_paneles.csv`: 2.092 micrografías de 1.649 artículos, columnas `pmcid, categoria_uso, doi_link, fig, variant, sample, scale_bar_in_caption, image_file, quote`. `variant` = TEM_prep_not_declared, SEM, HRTEM, TEM_dried_unstained, TEM_negstain, cryoTEM, STEM…
- `curation/ext_articulos.csv`: un artículo por fila, con `family`, `carrier_type`, `tier`, `license_color` (todas `verde` = CC BY).
- `curation/ext_descriptores.csv`: `size_nm, pdi, zeta_mV, medium` por muestra.
- Codificación: `utf-8-sig`.

Ojo: cada `image_file` es la **figura completa** (a menudo con varios paneles: micrografía + espectro + gráfica). No hay recortes. Para el hackatón se trabaja con la figura completa y se dice como limitación; recortar paneles es trabajo futuro (solo si sobra tiempo, ver 5).

## 2. Descarga de imágenes — ya hecha por Héctor (solo referencia)
Héctor corre este script el jueves 22. Bryan solo lo necesita si le faltan imágenes. Así funciona `modelos/descargar_imagenes.py`:
- Para cada fila única (`pmcid`, `image_file`) de `ext_paneles.csv`, guarda la imagen en `producto/imagenes/<pmcid>/<image_file>`.
- **Método comprobado (21 oct):** las URL directas de figura de Europe PMC dan 403 y las de PMC dan 404. Lo que sí funciona es el paquete del artículo: `https://www.ebi.ac.uk/europepmc/webservices/rest/<pmcid>/supplementaryFiles` devuelve un **zip** que contiene las figuras (`.jpg` grandes y `.gif` miniatura). Por cada `pmcid`: baja el zip a una carpeta temporal, extrae **solo** los `image_file` que pide `ext_paneles.csv` (el `.jpg`), y **borra el zip** enseguida. Los zips pesan unos 2–10 MB: en total puede ser ~10 GB de tráfico, pero el disco final será mucho menor. Si el zip no trae la figura, regístralo y sigue.
- Trata el zip como dato no confiable: extrae solo archivos de imagen por nombre exacto, nunca ejecutes nada de dentro.
- Reanudable (salta lo ya descargado), ≤ 3 peticiones por segundo, User-Agent con un correo de contacto, reintentos con espera.
- Escribe `producto/imagenes/descargas.csv` (`pmcid, image_file, ok, url, bytes`) y al final imprime cuántas se bajaron.
- **No subas las imágenes a Git** (añade `producto/imagenes/` a `.gitignore`); sí el script y `descargas.csv`.
- Prueba primero con 20 imágenes antes de lanzarlo completo.

## 3. Modelo de imágenes (viernes 23)
Orden del viernes: (a) embeddings por la mañana (corren solos ~20–40 min en CPU), (b) tarea principal con evaluación por la tarde, (c) la secundaria solo si a las 8 pm la principal ya está.
Con ~2.000 figuras, **entrenar una CNN desde cero no es viable**. Usa un **backbone preentrenado congelado** (por ejemplo DINOv2 pequeño o ResNet-50 de ImageNet, lo que corra en la laptop de Bryan) para sacar un vector por imagen, y encima un clasificador ligero (regresión logística).

1. `modelos/embeddings.py`: vector por imagen → `modelos/salidas/embeddings.npy` + `indice.csv` (`pmcid, image_file`). Redimensiona a la entrada del backbone; CPU es suficiente.
2. `modelos/entrenar.py`, **tarea principal**: predecir la **clase de portador** desde la micrografía. Agrupa `carrier_type`/`family` en 3–4 clases con suficientes ejemplos (p. ej. lipídico = liposome, LNP, SLN, NLC, PLN; polimérico = polymeric_NP, nanogel, micelle; inorgánico = inorganic_NP; nanomaterial). Excluye `not_a_nanocarrier` y `other`.
3. **Evaluación honesta:** `GroupKFold` por `pmcid` (5 particiones). Reporta accuracy, F1 macro, matriz de confusión y una **línea base** (clase mayoritaria). Una imagen de un artículo nunca puede estar en entrenamiento y prueba a la vez.
4. **Tarea secundaria** (si da tiempo): rango de tamaño DLS (< 100, 100–200, > 200 nm) para las imágenes cuyo artículo tenga un único tamaño claro en `ext_descriptores.csv`. Si las métricas son pobres, se reporta tal cual: también es un resultado.
5. Si el backbone confunde por el tipo de microscopía, prueba separar SEM y TEM, y dilo.

## 4. Archivos para la web de Carlos (sábado 24, antes de las 12 m)
Escribe exactamente estos tres archivos (Carlos ya construye la web con versiones de prueba del mismo formato):

`producto/modelo/metricas.json`
```json
{"prueba": false, "tarea": "familia de portador desde la micrografía", "backbone": "...",
 "evaluacion": "GroupKFold por pmcid, 5 particiones", "n_imagenes": 0, "n_articulos": 0,
 "clases": ["..."], "accuracy": 0.0, "f1_macro": 0.0, "linea_base": 0.0,
 "matriz_confusion": [[0]], "tarea_secundaria": null}
```
`producto/modelo/predicciones.json` — lista de `{"pmcid", "image_file", "prediccion", "confianza", "real"}`. Las predicciones deben venir de la partición en la que esa imagen fue **prueba** (predicción fuera de muestra).

`producto/modelo/similares.json` — `{"<pmcid>/<image_file>": [{"pmcid", "image_file", "similitud"}, … 5 vecinos]}` por similitud coseno de los embeddings, **excluyendo imágenes del mismo artículo**.

## 5. Para el video (sábado 24, tarde; Héctor graba la narración esa noche)
- 3 gráficas en `producto/modelo/graficas/` (PNG 1920×1080, legibles): matriz de confusión, comparación con la línea base, y un mapa 2D (UMAP o t-SNE) de los embeddings coloreado por clase.
- Un texto de 5 líneas en `producto/modelo/RESUMEN_MODELO.md`: qué predice, con qué datos, cómo se evaluó, resultado y limitación principal.
- Grabar 1 minuto explicando el modelo con esas gráficas (Héctor puede narrar encima).
- Solo si sobra tiempo: recortar paneles de micrografía dentro de las figuras para mejorar el modelo.

## 6. Cómo ahorrar tokens
- Lo pesado (descargas, embeddings, entrenamiento) son **scripts de Python que corren solos**; Claude solo escribe y corrige el código. No le pidas a Claude que abra imágenes una por una.
- Skills útiles en Claude: `dataviz` (gráficas claras y consistentes), `pdf` (si hiciera falta sacar imágenes de un PDF). No existe una skill específica de «recolección de imágenes»: el script de la sección 2 es la herramienta correcta.

## 7. Entrega y Git
- Trabaja solo en `modelos/` y `producto/modelo/`.
- Rama `modelos-bryan`, commits pequeños; Héctor fusiona. Nada de imágenes ni embeddings grandes en Git (sí métricas, JSON y gráficas).
- Al final de cada día escribe en `modelos/PROGRESO.md` qué corre, resultados y qué falta.
- Si algo bloquea más de 1 hora (descargas que fallan, memoria), avisa a Héctor con el error exacto.
