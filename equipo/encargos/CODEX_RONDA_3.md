# Codex (sesión de Héctor): ronda 3

`RAIZ` = `C:\Users\Hector\Desktop\Quimioinformatica Proyecto\nanotech-technique-cooccurrence`. Python: `%LOCALAPPDATA%\Programs\Python\Python313\python.exe` (pandas, numpy, scikit-learn, matplotlib, PIL, lxml; **sin torch ni OpenCV**: lo que necesite redes neuronales lo hace el clúster, no tú).

**Reglas de siempre:** no abrir `curation\work\clave_modelo.csv` ni `curation\qc_codex\`; no modificar `curation\ext_*.csv`, `curation\v0.1\`, `curation\work\llm\`, `producto\web\` ni tus rondas 1 y 2 (lo nuevo va en carpetas nuevas); no usar git; no inventar; **un paso se cierra solo si pasa su validación**. Tus rondas anteriores salieron muy bien (en especial la revisión crítica): mantén ese nivel.

**Contexto:** el profesor (23/10) aprobó el proyecto y propuso mejorar el modelo de imágenes: separar las figuras compuestas, recoger más figuras por artículo y entrenar quitando una clase. Plazo: domingo 25 a las 5:45 pm; **los resultados se congelan el sábado a las 3 pm**. Orden de prioridad: **R1 → R2 → R3 → R4**. Entrega un checkpoint por tarea en `RAIZ\modelos\CHECKPOINTS_RONDA3.md`.

---

## R1. Corregir las figuras del video (prioridad 1; entrega hoy)
Claude revisó tus 10 figuras: el estilo es muy bueno. Defectos concretos a corregir (scripts en `figuras\scripts\`):
1. **Figura 8 (flujo):** la primera caja queda **cortada a la izquierda** (falta su borde) y el diagrama mezcla unidades (artículos, descriptores, espectros) como si fueran pasos de un embudo. Rehazla con un **embudo real, solo de artículos**, con cifras calculadas desde los archivos (no escritas a mano): candidatos del universo (`data\ids\universe.csv`), los preseleccionados y con licencia CC BY (`curation\work\ext\rank.csv`), los textos descargados y revisados por código (`curation\work\ext\screen.csv`, `exportados.csv`), los artículos leídos por el extractor (1.824) y los con evidencia (1.707). Cada número debe poder trazarse a un archivo; si una cifra no se puede reconstruir, **no la pongas** y dilo en el informe.
2. **Figura 1:** los números de las cajas inferiores no tienen separador de miles (`2726`, `3116`, `4015`) y las cajas superiores sí (`1.824`). Unifica con punto de miles.
3. **Figura 7:** el título llega al borde derecho (riesgo de cortarse en el video). Acórtalo o ponlo en dos líneas.
4. **Figura 10:** hoy solo muestra la ronda 1 y su título casi toca el borde. Rehazla con **la ronda 2 como segunda columna o panel**: tamaño (variantes A y B+F) y clase (4 clases; muestra **las dos** líneas: «solo mediciones» `clase4_mediciones_logistica` y «mediciones + método/contexto» de la ronda 2), con la línea base destacada. Añade una nota corta: «Las banderas de formulación son menciones de texto, no recetas confirmadas». El título debe ser honesto: p. ej. «Los modelos simples explican como máximo el 24–29 % de la variación del tamaño».
5. **Figura 9:** ahora existe `equipo\qc_carlos\RESUMEN_QC.md` en el repositorio: úsalo como fuente en lugar del LEEME y quita la nota de «fuente secundaria».
6. Revisa que los colores por clase y las fuentes coincidan en las 10 figuras y **abre cada PNG** para comprobar que no hay texto cortado. Regenera `INDICE.md`.
**Validación R1:** cada número coincide con su fuente; ningún texto o caja cortada; `figura_8` rastreable a archivos.

## R2. Entrenar quitando una clase (prioridad 2; local, con los vectores ya calculados)
Propuesta del profesor: ver cuánto depende el rendimiento de cada clase. Datos: `C:\Users\Hector\Desktop\Kabre_Nano2Predict\Resultados\` (`emb_resnet50.npy`, `emb_dinov2_vits14.npy`, `indice_embeddings.csv`; **no los copies al repositorio**), `curation\v0.1\tabla_modelo.csv` y `modelos\comparacion\entrada_kabre\`. Antecedente: `modelos\comparacion\ANALISIS_RAPIDO_EMBEDDINGS.md` (imagen DINOv2 + PCA 64 + SVM rbf: F1 macro 0,466; medidas: 0,537; fusión: 0,559). Código de referencia: `modelos\comparacion\analisis_rapido_embeddings.py`.
Carpeta nueva: `RAIZ\modelos\ablacion_clases\`.
1. Para cada clase X de {lipídico, polimérico, inorgánico, nanomaterial}: **quita X de entrenamiento y de prueba**, entrena con las otras tres y evalúa por artículo con los mismos `fold`. Reporta exactitud, exactitud balanceada, F1 macro e IC 95 % por bootstrap de artículos para: (a) solo imagen (DINOv2+SVM), (b) solo mediciones (logística de la ronda 1/2 sin banderas), (c) fusión imagen + mediciones. Compara contra la misma configuración con las cuatro clases **restringida a esas tres clases** (para que sea comparable).
2. **Opcional (si hay tiempo):** entrena **sin X** y evalúa **solo sobre X**: ¿en qué clase cae lo que el modelo nunca vio (distribución de predicciones)? Es una prueba de generalización fuera de distribución, no una métrica de acierto; descríbela así.
3. Fija el modelo y sus hiperparámetros **antes** de mirar los resultados (los de `ANALISIS_RAPIDO_EMBEDDINGS.md`) y no los ajustes sobre el fold de prueba.
**Entregables:** `RESULTADOS_ABLACION.md` con una tabla por experimento y 3 conclusiones, `resultados\*.csv`, una figura (1920×1080, mismo estilo) «¿Cuánto depende el modelo de cada clase?».
**Validación R2:** sin artículos compartidos entre entrenamiento y prueba; la línea base de cada subconjunto coincide con la proporción de su clase mayoritaria; misma semilla = mismos resultados.

## R3. Más figuras por artículo (prioridad 3)
Hoy hay una figura por artículo (la que eligió el extractor). Sin IA, solo con código, buscar **todas las figuras de micrografía de cada artículo**.
Carpeta nueva: `RAIZ\modelos\imagenes_v02\`.
1. Estudia cómo `curation\extended.py` obtiene las figuras (`fig_graphics`, XML JATS en la caché local). Para cada artículo E1/E2 de `curation\ext_articulos.csv`, lista **todas** sus figuras cuyo pie contiene palabras de micrografía (TEM, SEM, STEM, cryo-EM/cryoTEM, HRTEM, «transmission electron», «scanning electron», «micrograph») **y que no estén ya en `curation\ext_paneles.csv`**. Escribe `figuras_candidatas.csv` (`pmcid, figura, archivo_grafico, pie_de_figura (≤300 car.), palabras_encontradas, ya_en_base (0/1)`). Imprime cuántas figuras nuevas hay en total y por clase.
2. **Descarga (solo las nuevas)** con `RAIZ\modelos\descargar_imagenes.py` como modelo (zip de Europe PMC `.../supplementaryFiles`, ≤ 4 hilos, reanudable; extrae solo imágenes por nombre exacto y normaliza las barras `\` de los nombres del zip). Carpeta: `RAIZ\producto\imagenes_v02\<pmcid>\` (no va a Git: añade la ruta a `.gitignore`). Registro `descargas_v02.csv`.
3. Escribe `RAIZ\modelos\imagenes_v02\tabla_modelo_v02.csv`: las columnas de `tabla_modelo.csv` más `origen` (`v0.1` o `nuevo`), **heredando `clase_modelo` y `fold` del artículo** (todas las figuras de un artículo, mismo fold).
**Validación R3:** ningún artículo en dos folds; no se repite ninguna figura; las cifras de nuevas figuras por clase cuadran con `figuras_candidatas.csv`. **Reporta honestamente** cuántas imágenes nuevas se consiguieron: si son pocas, dilo.

## R4. Separar paneles compuestos (prioridad 4; prueba de concepto)
Sin torch ni OpenCV, con PIL y numpy.
Carpeta nueva: `RAIZ\modelos\recortes\`.
1. Heurística de **franjas blancas**: para cada figura de `producto\imagenes\`, calcula los perfiles de proyección (filas y columnas casi blancas) y corta recursivamente por las franjas vacías (ancho mínimo configurable; recortes demasiado pequeños se descartan). Guarda los recortes en `RAIZ\producto\imagenes_recortes\<pmcid>\<archivo>_pN.png` (no va a Git).
2. **Evaluación visual:** elige 60 figuras al azar con semilla fija y genera **hojas de contacto** (`hoja_contacto_01.png`…) con la figura original y sus recortes, para que Claude las inspeccione. Estadísticas: número de recortes por figura, % de figuras que quedaron sin cortar, tamaño medio.
3. Anota en el informe los fallos típicos (paneles con barras de color, ejes pegados, figuras de una sola pieza cortadas por error) y qué umbral usaste.
**No filtres micrografía frente a gráfica**: eso requiere un modelo de visión y lo hará el clúster. Entrega solo recortes candidatos + estadísticas.
**Validación R4:** reproducible con la misma configuración; no se borra ni modifica ninguna imagen original.

---
## Entrega
Un checkpoint por tarea (hora, validado, fallos). Reporte final corto en el chat: lo hecho, cifras, lo que no pudiste verificar y las tres conclusiones más importantes. **No uses git: Claude revisa y sube.** Prioridad si falta tiempo: R1 y R2 antes del sábado a las 12 m; R3 y R4 antes de las 2 pm (lo que no esté validado a las 3 pm no entra a los modelos).

