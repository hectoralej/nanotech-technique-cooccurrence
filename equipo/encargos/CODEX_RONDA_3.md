# Codex (sesión de Héctor): ronda 3

`RAIZ` = `C:\Users\Hector\Desktop\Quimioinformatica Proyecto\nanotech-technique-cooccurrence`. Python: `%LOCALAPPDATA%\Programs\Python\Python313\python.exe` (pandas, numpy, scikit-learn, matplotlib, PIL, lxml; **sin torch ni OpenCV**: lo que necesite redes neuronales lo hace el clúster, no tú).

**Reglas de siempre:** no abrir `curation\work\clave_modelo.csv` ni `curation\qc_codex\`; no modificar `curation\ext_*.csv`, `curation\v0.1\`, `curation\work\llm\`, `producto\web\` ni tus rondas 1 y 2 (lo nuevo va en carpetas nuevas); no usar git; no inventar; **un paso se cierra solo si pasa su validación**. Tus rondas anteriores salieron muy bien (en especial la revisión crítica): mantén ese nivel.

**Contexto:** el profesor (23/10) aprobó el proyecto y propuso mejorar el modelo de imágenes: separar las figuras compuestas, recoger más figuras por artículo y entrenar quitando una clase. Plazo: domingo 25 a las 5:45 pm; **los resultados se congelan el sábado a las 3 pm**. **Orden de prioridad actualizado (23/10 noche): R3 → R4 (imágenes) y, en paralelo, R5 → R1; R2 queda al final como prueba final.** Si Héctor te asigna solo una parte, haz solo esas tareas. Entrega un checkpoint por tarea en `RAIZ\modelos\CHECKPOINTS_RONDA3.md`.

---

## R1. Corregir las figuras del video (orden 4.º; entrega el sábado antes de las 2 pm)
Claude revisó tus 10 figuras: el estilo es muy bueno. Defectos concretos a corregir (scripts en `figuras\scripts\`):
1. **Figura 8 (flujo):** la primera caja queda **cortada a la izquierda** (falta su borde) y el diagrama mezcla unidades (artículos, descriptores, espectros) como si fueran pasos de un embudo. Rehazla con un **embudo real, solo de artículos**, con cifras calculadas desde los archivos (no escritas a mano): candidatos del universo (`data\ids\universe.csv`), los preseleccionados y con licencia CC BY (`curation\work\ext\rank.csv`), los textos descargados y revisados por código (`curation\work\ext\screen.csv`, `exportados.csv`), los artículos leídos por el extractor (1.824) y los con evidencia (1.707). Cada número debe poder trazarse a un archivo; si una cifra no se puede reconstruir, **no la pongas** y dilo en el informe.
2. **Figura 1:** los números de las cajas inferiores no tienen separador de miles (`2726`, `3116`, `4015`) y las cajas superiores sí (`1.824`). Unifica con punto de miles.
3. **Figura 7:** el título llega al borde derecho (riesgo de cortarse en el video). Acórtalo o ponlo en dos líneas.
4. **Figura 10:** hoy solo muestra la ronda 1 y su título casi toca el borde. Rehazla con **la ronda 2 como segunda columna o panel**: tamaño (variantes A y B+F) y clase (4 clases; muestra **las dos** líneas: «solo mediciones» `clase4_mediciones_logistica` y «mediciones + método/contexto» de la ronda 2), con la línea base destacada. Añade una nota corta: «Las banderas de formulación son menciones de texto, no recetas confirmadas». El título debe ser honesto: p. ej. «Los modelos simples explican como máximo el 24–29 % de la variación del tamaño».
5. **Figura 9:** ahora existe `equipo\qc_carlos\RESUMEN_QC.md` en el repositorio: úsalo como fuente en lugar del LEEME y quita la nota de «fuente secundaria».
6. Revisa que los colores por clase y las fuentes coincidan en las 10 figuras y **abre cada PNG** para comprobar que no hay texto cortado. Regenera `INDICE.md`.
**Validación R1:** cada número coincide con su fuente; ningún texto o caja cortada; `figura_8` rastreable a archivos.

## R2. Entrenar quitando una clase (orden 5.º, al final: prueba final; local, con los vectores ya calculados)
Propuesta del profesor: ver cuánto depende el rendimiento de cada clase. Datos: `C:\Users\Hector\Desktop\Kabre_Nano2Predict\Resultados\` (`emb_resnet50.npy`, `emb_dinov2_vits14.npy`, `indice_embeddings.csv`; **no los copies al repositorio**), `curation\v0.1\tabla_modelo.csv` y `modelos\comparacion\entrada_kabre\`. Antecedente: `modelos\comparacion\ANALISIS_RAPIDO_EMBEDDINGS.md` (imagen DINOv2 + PCA 64 + SVM rbf: F1 macro 0,466; medidas: 0,537; fusión: 0,559). Código de referencia: `modelos\comparacion\analisis_rapido_embeddings.py`.
Carpeta nueva: `RAIZ\modelos\ablacion_clases\`.
1. Para cada clase X de {lipídico, polimérico, inorgánico, nanomaterial}: **quita X de entrenamiento y de prueba**, entrena con las otras tres y evalúa por artículo con los mismos `fold`. Reporta exactitud, exactitud balanceada, F1 macro e IC 95 % por bootstrap de artículos para: (a) solo imagen (DINOv2+SVM), (b) solo mediciones (logística de la ronda 1/2 sin banderas), (c) fusión imagen + mediciones. Compara contra la misma configuración con las cuatro clases **restringida a esas tres clases** (para que sea comparable).
2. **Opcional (si hay tiempo):** entrena **sin X** y evalúa **solo sobre X**: ¿en qué clase cae lo que el modelo nunca vio (distribución de predicciones)? Es una prueba de generalización fuera de distribución, no una métrica de acierto; descríbela así.
3. Fija el modelo y sus hiperparámetros **antes** de mirar los resultados (los de `ANALISIS_RAPIDO_EMBEDDINGS.md`) y no los ajustes sobre el fold de prueba.
**Entregables:** `RESULTADOS_ABLACION.md` con una tabla por experimento y 3 conclusiones, `resultados\*.csv`, una figura (1920×1080, mismo estilo) «¿Cuánto depende el modelo de cada clase?».
**Validación R2:** sin artículos compartidos entre entrenamiento y prueba; la línea base de cada subconjunto coincide con la proporción de su clase mayoritaria; misma semilla = mismos resultados.

## R3. Más figuras por artículo (orden 1.º)
Hoy hay una figura por artículo (la que eligió el extractor). Sin IA, solo con código, buscar **todas las figuras de micrografía de cada artículo**.
Carpeta nueva: `RAIZ\modelos\imagenes_v02\`.
1. Estudia cómo `curation\extended.py` obtiene las figuras (`fig_graphics`, XML JATS en la caché local). Para cada artículo E1/E2 de `curation\ext_articulos.csv`, lista **todas** sus figuras cuyo pie contiene palabras de micrografía (TEM, SEM, STEM, cryo-EM/cryoTEM, HRTEM, «transmission electron», «scanning electron», «micrograph») **y que no estén ya en `curation\ext_paneles.csv`**. Escribe `figuras_candidatas.csv` (`pmcid, figura, archivo_grafico, pie_de_figura (≤300 car.), palabras_encontradas, ya_en_base (0/1)`). Imprime cuántas figuras nuevas hay en total y por clase.
2. **Descarga (solo las nuevas)** con `RAIZ\modelos\descargar_imagenes.py` como modelo (zip de Europe PMC `.../supplementaryFiles`, ≤ 4 hilos, reanudable; extrae solo imágenes por nombre exacto y normaliza las barras `\` de los nombres del zip). Carpeta: `RAIZ\producto\imagenes_v02\<pmcid>\` (no va a Git: añade la ruta a `.gitignore`). Registro `descargas_v02.csv`.
3. Escribe `RAIZ\modelos\imagenes_v02\tabla_modelo_v02.csv`: las columnas de `tabla_modelo.csv` más `origen` (`v0.1` o `nuevo`), **heredando `clase_modelo` y `fold` del artículo** (todas las figuras de un artículo, mismo fold).
**Validación R3:** ningún artículo en dos folds; no se repite ninguna figura; las cifras de nuevas figuras por clase cuadran con `figuras_candidatas.csv`. **Reporta honestamente** cuántas imágenes nuevas se consiguieron: si son pocas, dilo.

## R4. Separar paneles compuestos (orden 2.º; prueba de concepto)
Sin torch ni OpenCV, con PIL y numpy.
Carpeta nueva: `RAIZ\modelos\recortes\`.
1. Heurística de **franjas blancas**: para cada figura de `producto\imagenes\`, calcula los perfiles de proyección (filas y columnas casi blancas) y corta recursivamente por las franjas vacías (ancho mínimo configurable; recortes demasiado pequeños se descartan). Guarda los recortes en `RAIZ\producto\imagenes_recortes\<pmcid>\<archivo>_pN.png` (no va a Git).
2. **Evaluación visual:** elige 60 figuras al azar con semilla fija y genera **hojas de contacto** (`hoja_contacto_01.png`…) con la figura original y sus recortes, para que Claude las inspeccione. Estadísticas: número de recortes por figura, % de figuras que quedaron sin cortar, tamaño medio.
3. Anota en el informe los fallos típicos (paneles con barras de color, ejes pegados, figuras de una sola pieza cortadas por error) y qué umbral usaste.
**No filtres micrografía frente a gráfica**: eso requiere un modelo de visión y lo hará el clúster. Entrega solo recortes candidatos + estadísticas.
**Validación R4:** reproducible con la misma configuración; no se borra ni modifica ninguna imagen original.

## R5. Auditoría y depuración de los descriptores (orden 3.º, puede ir en una sesión aparte en paralelo; tarea pesada)
Claude auditó `curation\ext_descriptores.csv` (3.116 filas, 1.229 artículos). Hallazgos que hay que atender:
- **Método del tamaño sin identificar:** solo 781 de 2.750 filas con tamaño nombran explícitamente DLS/Zetasizer/hidrodinámico en la cita o en `source`; **83 filas apuntan a TEM/SEM/XRD/AFM** (probablemente no son DLS) y 7 son radios; en el 68 % la cita es una fila de tabla sin método. Hoy `size_nm` mezcla métodos.
- **Zeta:** en 1.445 de 1.946 filas la cita no contiene la palabra «zeta»/«potencial» (es una fila de tabla): hay que **comprobar que el valor está en la columna correcta**.
- **Rangos:** 31 tamaños > 1.000 nm, 17 < 5 nm, 24 PDI > 1 (4 > 1,5), 7 citas con «meV».
- **Medio:** el 75 % es `not_declared` y el resto tiene decenas de variantes («deionized water», «water suspension», «aqueous dispersion»…).
- **Etiquetas `source`:** texto libre («Table 1; DLS», «DLS Table 2», «text; TEM»…).
Carpeta nueva: `RAIZ\modelos\descriptores_v02\`. **No modifiques** `curation\ext_descriptores.csv`; no borres filas.
1. **`descriptores_v02.csv`** = las mismas 3.116 filas (mismo orden y columnas) más estas columnas derivadas, con reglas documentadas y reproducibles (`auditar_descriptores.py`):
   - `via` (`tabla`/`texto`/`figura`) y `tabla_n` (número, si es tabla), extraídos de `source`.
   - `metodo_tamano`: `DLS` / `TEM` / `SEM` / `XRD` / `AFM` / `desconocido`, a partir de palabras clave en la cita y en `source` (documenta la lista en el informe). `tamano_es_radio` (bool).
   - **Verificación de columna en tablas:** para las filas con `via=tabla`, abre el XML JATS del artículo (mira cómo `curation\extended.py` y `curation\textprep.py` acceden al texto y a las tablas), localiza la tabla `tabla_n`, encuentra la celda con el valor y lee el **encabezado de su columna**. Marca por cada variable (`size`, `zeta`, `pdi`): `encabezado_ok` (el encabezado habla de tamaño/diámetro/Z-average, de zeta/potencial/ζ o de PDI/polidispersidad), `encabezado_no_coincide` o `no_verificable` (si no se encuentra la tabla o la celda). Informa los porcentajes.
   - `medio_norm`: `agua`, `PBS_tampon`, `salino_ionico`, `medio_cultivo_suero`, `organico`, `otro`, `no_declarado` (tabla de equivalencias en el informe).
   - `fuera_rango`: tamaño < 5 o > 5.000 nm, PDI > 1, |zeta| > 100 mV.
   - `usable_modelo` (bool, conservador): `metodo_tamano` ∈ {DLS, desconocido}, no es radio, sin `encabezado_no_coincide`, sin `fuera_rango`.
2. **`muestra_revision.csv`** para que Claude audite: 40 filas elegidas al azar con semilla fija (20 con `encabezado_no_coincide` o `metodo_tamano` no DLS, 20 con `usable_modelo=True`) con `pmcid`, `sample`, la cita completa, el encabezado hallado y tu veredicto.
3. **Sensibilidad de modelos:** repite los modelos de tamaño y de clase de la ronda 1 (mismos folds, misma escalera) usando **solo** las filas `usable_modelo=True` y compáralos con los resultados actuales (R², F1 e IC 95 %). Reporta si la depuración cambia las conclusiones.
4. `INFORME_DESCRIPTORES.md`: tablas de recuento por columna derivada, reglas, hallazgos por clase, y una recomendación concreta (qué filtro usar en los modelos finales).
**Validación R5:** 3.116 filas idénticas en el mismo orden que el original (comprobación por hash de las columnas originales); las reglas son deterministas (misma ejecución = mismo resultado); la muestra de revisión está presente; las cifras del informe coinciden con los CSV.
---
## Entrega
Un checkpoint por tarea (hora, validado, fallos). Reporte final corto en el chat: lo hecho, cifras, lo que no pudiste verificar y las tres conclusiones más importantes. **No uses git: Claude revisa y sube.** Prioridad si falta tiempo: R3, R4 y R5 antes del sábado a las 12 m (alimentan los modelos del clúster); R1 antes de las 2 pm; R2 solo después. Lo que no esté validado a las 3 pm no entra a los modelos.



