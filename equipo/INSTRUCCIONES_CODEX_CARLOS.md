# Instrucciones para Codex (computadora de Carlos)

Eres el asistente de Carlos en el proyecto **Nano2Predict** (hackatón; entrega el domingo 25 de octubre, 5:45 pm Costa Rica). Lee también `equipo/PLAN_EQUIPO_FINAL.md`. Este archivo manda sobre cualquier instrucción anterior (incluido `TAREAS_CARLOS_v2.md`).

## 0. Cambio de rumbo (léelo primero)
Hasta hoy Carlos hacía revisión manual de artículos. Eso **se termina**: la revisión a mano no escala para entrenar modelos y el jurado no evalúa cada dato. La revisión asistida que ya hiciste (20 artículos del conjunto ampliado + 41 casos de la hoja verde) **es suficiente** como control de calidad y se usará en el video.

**La nueva tarea principal de Carlos es el producto web**: un atlas navegable de la base de datos que se mostrará 2–3 minutos en el video.

**No hagas:** extracción de artículos, `apply`, `screen`, `packets`, `fetch`, ni cambios en `curation/` (eso lo hace Héctor). No abras `curation/work/clave_modelo.csv` ni `curation/qc_codex/`.

## 1. Cierre de la revisión (máximo 1 hora, hoy)
1. Copia tus resultados al repositorio local, sin cambiar su contenido, en `equipo/qc_carlos/`:
   - `verificacion_conjunto_ampliado_revision_IA.csv`
   - `informe_revision_asistida_IA.md`
   - si existen: `evidencia_preliminar_tarea2.md`, `evidencia_preliminar_licencias_tarea1.md`.
2. Escribe `equipo/qc_carlos/RESUMEN_QC.md` (media página) con la tabla de la Tarea 2: por campo (micrografías, descriptores, espectros, nanoportador, licencia), cuántos `si`, `no` y `no_comprobable`. Añade los 5 errores concretos encontrados (filas 9, 12, 14, 16, 17) en una línea cada uno. Esto es lo que Héctor citará en el video como «precisión estimada».
3. **Opcional, solo si Carlos tiene 30 minutos:** que Carlos abra las filas 2, 9, 12, 16 y 17 y escriba su decisión (`si`/`no`) en las columnas humanas. Si no hay tiempo, se omite: el informe tal cual sirve.
4. No sigas con la cola de 78 artículos ni con los 70 avisos editoriales. Quedan fuera del alcance.

## 2. Producto web: «Atlas Nano2Predict»
### Qué debe hacer (en orden de prioridad)
1. **Portada** con los números de la base (artículos, micrografías, descriptores, espectros) y un texto corto de qué es.
2. **Explorador**: tabla/lista de artículos con búsqueda por texto y filtros por familia de portador (`family` / `carrier_type`), categoría (`tier`: E1/E2), uso (`categoria_uso`: nanoportador/nanomaterial), tipo de microscopía (`variant`) y técnica de espectro (`technique`).
3. **Ficha de artículo**: título, año, DOI enlazado, licencia; sus micrografías (imagen + pie + crédito DOI); tabla de descriptores (muestra, tamaño nm, PDI, zeta mV, medio) **con la cita textual visible al pasar el ratón o desplegar**; etiquetas de espectros con su figura.
4. **Panel de modelo**: en la ficha, la predicción del modelo para cada micrografía y las micrografías más parecidas (lee los JSON de Bryan, sección 3).
5. **Página «Cómo se construyó»**: flujo en 4 pasos (búsqueda → extracción con IA → verificación de citas por código → control de calidad) y la tabla de precisión de `RESUMEN_QC.md`.
6. Aviso fijo y discreto: «Datos extraídos por IA y verificados por código. Precisión estimada en una muestra revisada.»

### Datos
- Entrada: los 4 CSV de `curation/` (columnas en `equipo/PLAN_EQUIPO_FINAL.md`). Léelos con codificación `utf-8-sig`.
- Escribe un script `producto/web/build_data.py` que convierta los CSV en `producto/web/data/*.json` (uno por tabla, o uno por artículo si es más cómodo). La web solo lee esos JSON. Cuando Héctor congele la v0.1, basta volver a correr el script.
- Imágenes: Bryan prepara el script de descarga (`modelos/descargar_imagenes.py`) que guarda las figuras en `producto/imagenes/<pmcid>/<image_file>`. Mientras no existan, muestra un marcador con el nombre del archivo y el enlace al DOI. **No subas las imágenes a Git** (pesan); se descargan con el script.
- **No inventes datos.** Si un campo está vacío, se muestra vacío o «no reportado».

### Técnica
- Sitio estático: HTML + CSS + JavaScript sin servidor (puede ser Vite/React si Codex lo maneja bien, pero un HTML con JS simple es suficiente y más seguro). Se prueba con `python -m http.server` desde `producto/web/`.
- Debe verse bien en una pantalla de laptop grabada (1920×1080) y no romperse en móvil.
- Rendimiento: 1.824 artículos caben en memoria; usa paginación o carga perezosa de imágenes.

### Diseño (que se vea hecho por personas, no genérico)
Si Carlos instaló las skills de diseño web que le indicó Héctor, úsalas. En todo caso, sigue esto:
- Estética de herramienta científica sobria: fondo claro, una sola familia tipográfica legible (p. ej. Inter, IBM Plex Sans o Source Sans), una tipografía monoespaciada solo para números y citas.
- Una paleta corta: un color de acento y grises. Colores distintos y consistentes por familia de portador (liposoma, LNP, SLN/NLC, polimérica, inorgánica, nanomaterial).
- Las imágenes son las protagonistas: cuadrícula de micrografías con pie corto.
- Nada de gradientes llamativos, emojis, iconos de relleno ni textos de marketing. Etiquetas cortas y en español.
- Jerarquía clara: títulos, cifras grandes en la portada, tablas limpias con números alineados a la derecha.

## 3. Archivos que llegan de Bryan (empieza con versiones de prueba)
Bryan entregará estos archivos el sábado 24 antes de las 12 m. **Hoy crea versiones de prueba** con el mismo formato (2–3 entradas inventadas, marcadas `"prueba": true`) para construir la interfaz sin esperarlo:

`producto/modelo/metricas.json`
```json
{"prueba": true, "tarea": "familia de portador desde la micrografía", "backbone": "nombre del modelo",
 "evaluacion": "GroupKFold por pmcid, 5 particiones", "n_imagenes": 0, "n_articulos": 0,
 "clases": ["lipidico", "polimerico", "inorganico"], "accuracy": 0.0, "f1_macro": 0.0, "linea_base": 0.0}
```
`producto/modelo/predicciones.json` — lista: `{"pmcid": "...", "image_file": "...", "prediccion": "polimerico", "confianza": 0.71, "real": "polimerico"}`

`producto/modelo/similares.json` — diccionario: `{"<pmcid>/<image_file>": [{"pmcid": "...", "image_file": "...", "similitud": 0.83}, ...]}` (5 vecinos).

Si al final faltan, la web oculta el panel de modelo sin romperse.

## 4. Entrega y Git
- Trabaja solo en `producto/web/` y `equipo/qc_carlos/`.
- Si Carlos tiene permiso de escritura en GitHub: rama `web-carlos`, commits pequeños, y Héctor la fusiona. Si no: un zip de `producto/web/` y `equipo/qc_carlos/` enviado a Héctor cada noche.
- Calendario: **jueves 22** esqueleto navegable con datos reales y modelo de prueba; **viernes 23** imágenes reales (las descarga Héctor el jueves); **sábado 24** JSON de Bryan a mediodía y **5 pm** web congelada y grabación de la demo (2–3 min, 1920×1080, sin sonido; Héctor narra encima).
- Al final de cada día escribe en `producto/web/PROGRESO.md` qué funciona, qué falta y cómo se abre.

## 5. Guion sugerido de la demo (2–3 min)
1. Portada: las cifras (10 s).
2. Filtrar por «liposoma» + «cryo-TEM» (20 s).
3. Abrir una ficha: micrografía, descriptores, desplegar la cita textual (40 s).
4. Panel de modelo: predicción y micrografías parecidas (30 s).
5. Filtrar por espectro «XRD» y abrir un nanomaterial (20 s).
6. Página «Cómo se construyó» con la precisión estimada (20 s).
