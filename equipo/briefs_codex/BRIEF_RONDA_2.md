# Codex: ronda 2 (todo lo que no necesita el clúster)

`RAIZ` = `C:\Users\Hector\Desktop\Quimioinformatica Proyecto\nanotech-technique-cooccurrence`. Python: `%LOCALAPPDATA%\Programs\Python\Python313\python.exe` (pandas, numpy, scikit-learn 1.9.1, matplotlib instalados; sin torch).

**Reglas de siempre:** no abrir `curation\work\clave_modelo.csv` ni `curation\qc_codex\`; no modificar `curation\ext_*.csv`, `curation\v0.1\`, `curation\work\llm\` ni los resultados de tu ronda 1 (`modelos\tabular\`: se quedan como están; lo nuevo va en carpetas nuevas); no usar git; no inventar; **un paso se cierra solo si pasa su validación**. Tu ronda 1 salió muy bien (informe honesto, prueba de fuga de etiquetas, IC por bootstrap): mantén ese nivel.

**Contexto:** el equipo corre en paralelo, en el clúster Kabré, los embeddings de las imágenes (ResNet50 y DINOv2) y su clasificador. Nada de eso es tuyo ni lo toques. Plazo del proyecto: domingo 25 de octubre, 5:45 pm. Hoy es viernes por la tarde: **ordena el trabajo por prioridad (A → B → C → D) y entrega en cada checkpoint lo que ya esté validado.**

---

## A. Figuras del video (prioridad 1)
Sigue `equipo\briefs_codex\BRIEF_FIGURAS_VIDEO.md` **completo** (estilo común, 9 figuras, validación por figura, entregables en `RAIZ\figuras\figuras_para_el_video\` y scripts en `RAIZ\figuras\scripts\`), con estas **modificaciones**:
1. **Añade la figura 10:** la escalera de modelos de tamaño y la de clasificación **simplificadas para video**: un solo panel por tarea, la variante B para tamaño, barras horizontales con IC 95 %, la línea base destacada y el título con la conclusión («El mejor modelo explica solo el 24 % de la variación del tamaño»). Los números salen de `producto\modelo_tabular\metricas_tabular.json`. No uses la tabla de ΔR² (confunde); muestra R² con su intervalo.
2. **Reserva la figura 11** («¿Aporta algo la imagen?»: solo mediciones frente a solo imagen frente a ambas): escribe `figura_11.py` que lea `modelos\comparacion\resultados\comparacion_justa.json` **si existe** (lo crea la tarea C) y, si no existe, termine con un mensaje claro sin fallar. No inventes datos.
3. Tras generar todo, **autorevisión visual**: abre cada PNG y comprueba que no haya texto cortado o superpuesto y que los colores por clase coincidan entre figuras. Claude revisará después las imágenes y te dará correcciones.
4. Dimensiones: 1920×1080 px; títulos ≥ 36 pt; etiquetas ≥ 20 pt.

## B. Modelos tabulares, segunda versión (prioridad 2)
Carpeta nueva: `RAIZ\modelos\tabular_v2\`. Reutiliza `modelos\tabular\tabular_common.py` (impórtalo, no lo copies ni lo modifiques) y los mismos `fold` por artículo. Mismas reglas de validación que en la ronda 1 (prueba de columnas prohibidas, misma semilla = mismas métricas, sin artículos compartidos entre entrenamiento y prueba).

**B1. Características de formulación (lo más importante).** La limitación nº 1 de la ronda 1 fue que la base no trae información de formulación. Constrúyela **con reglas de texto, verificables y reproducibles**:
- Script `modelos\formulacion\extraer_formulacion.py` que, para cada artículo de `curation\ext_articulos.csv` (E1/E2), lea el texto completo del artículo con las utilidades locales (`curation\textprep.py`: mira cómo la usa `curation\extended.py`; usa la sección de métodos si se puede separar, y si no, el texto completo; **documenta cuál usaste**) y calcule banderas 0/1 por coincidencia de palabras clave (en inglés, con variantes y plurales):
  - **Método:** nanoprecipitación, evaporación de solvente/emulsificación, hidratación de película lipídica, gelificación iónica, microfluídica, sonicación, homogeneización a alta presión, extrusión, síntesis verde/extracto de planta, sol-gel, coprecipitación, hidrotermal.
  - **Material:** quitosano, PLGA, PEG/pegilado, colesterol, fosfatidilcolina/lecitina, ácido esteárico/lípido sólido, plata, oro, sílice, óxido de hierro, óxido de zinc, óxido de titanio, grafeno, almidón/celulosa.
  - **Contexto:** carga de fármaco («loaded»/«encapsulat»), y presencia de DLS (`dynamic light scattering`, `zetasizer`).
- Salida: `modelos\formulacion\formulacion_articulos.csv` (`pmcid` + una columna por bandera) y `modelos\formulacion\evidencia_formulacion.csv`: para **30 banderas elegidas al azar con semilla fija**, el `pmcid`, la bandera y la frase exacta (≤ 200 caracteres) donde se encontró la palabra, para que Claude audite los falsos positivos.
- **Validación B1:** (a) todos los artículos con evidencia están en el CSV, (b) tasa de cada bandera (si una bandera está en < 10 artículos, descártala y dilo), (c) los 30 ejemplos de evidencia revisados por ti con una nota «correcto/dudoso» y el porcentaje de acierto.

**B2. Tamaño con formulación.** Repite la regresión de tamaño (log10) con la escalera de la ronda 1 (media por clase → lineal múltiple → Ridge → Random Forest → HistGradientBoosting) en tres variantes: **A** (ronda 1), **A+F** (A más banderas de formulación) y **B+F** (B más banderas). Reporta R² con IC 95 % por bootstrap de artículos y la **mejora pareada A+F frente a A** con IC. Importancia por permutación de las banderas. Conclusión honesta: si la formulación no aporta, dilo.

**B3. Clasificación sin fuga.** **No uses las banderas de material** (quitosano, plata, sílice…) para predecir la clase de portador: delatan la respuesta. Para la clase solo puedes añadir las banderas de **método** y **contexto**, y explícitamente **tienes que demostrar con una prueba** que ninguna columna de material está en la matriz.

**B4. Dos tareas más** (mismo formato y validación que en la ronda 1): signo del zeta (negativo/positivo) y PDI < 0,3 (monodisperso). Con la escalera: mayoritaria → logística → Random Forest → HistGradientBoosting.

**B5. Predicciones con probabilidades.** Para todos los clasificadores guarda `modelos\tabular_v2\resultados\predicciones_<tarea>_<modelo>.csv` con `pmcid, sample, y_real, y_pred, fold` **y una columna de probabilidad por clase** (`p_lipidico`, `p_polimerico`, `p_inorganico`, `p_nanomaterial`, según corresponda). Esto es lo que usa la tarea C.

**Entregables B:** scripts, resultados, `modelos\tabular_v2\REPORTE_TABULAR_V2.md` (tablas simples: R² con IC por variante, sin la columna «ΔR² previo»; secciones: qué aporta la formulación, limitaciones, reproducción) y `producto\modelo_tabular\metricas_tabular_v2.json`.

## C. Comparación justa y fusión (prioridad 3)
Prepara el código para comparar **solo mediciones, solo imagen y ambas** sobre **exactamente los mismos artículos y los mismos `fold`**. Los embeddings los calcula el clúster: tú no los tienes todavía, y **no debes inventarlos ni correrlos**.
1. `RAIZ\modelos\comparacion\conjunto_comparacion.py`: define el conjunto de comparación: artículos que tienen al menos una imagen usable en `curation\v0.1\tabla_modelo.csv` (clase y `fold` presentes, imagen existente en `producto\imagenes\`) **y** al menos una fila de descriptores con tamaño, zeta o PDI. Escribe `modelos\comparacion\conjunto_comparacion.csv` (`pmcid, clase_modelo, fold, n_imagenes, n_descriptores`) e imprime los recuentos por clase y por `fold`.
2. `RAIZ\modelos\comparacion\fusion.py`: lee (a) las probabilidades tabulares por artículo de B5 (promediadas por artículo) y (b) cuando existan, `modelos\comparacion\entrada_kabre\predicciones_<modelo>.csv` (columnas `pmcid, image_file, real, prediccion, confianza, fold` más una probabilidad por clase si las trae; si solo trae `confianza`, trabaja con eso y dilo). Calcula por artículo: **solo tabular, solo imagen, fusión tardía** (media de probabilidades y media ponderada con el peso elegido **solo con los folds de entrenamiento**), con exactitud, F1 macro, matriz de confusión e IC 95 % por bootstrap de artículos, **y las tres sobre el mismo conjunto**. Escribe `modelos\comparacion\resultados\comparacion_justa.json`.
3. **Prueba con datos sintéticos explícitamente marcados:** un modo `--sintetico` que genere predicciones de imagen falsas **solo para probar el código**, escriba sus resultados en una carpeta aparte `resultados_sintetico\` y los marque con `"sintetico": true`. Nunca debe escribir en `resultados\` con datos falsos.
4. **Validación C:** el conjunto de comparación no repite artículos; los tres métodos usan los mismos artículos y `fold`; sin datos de Kabré, `fusion.py` termina con un mensaje claro y no crea `comparacion_justa.json`.

## D. Revisión crítica de tu propio trabajo (prioridad 4, 20 minutos)
Escribe `RAIZ\modelos\REVISION_CRITICA.md`: ¿qué podría estar mal en los resultados de la ronda 1 y la ronda 2 que no hayas comprobado? (fuga por artículo repetido, banderas de formulación que correlacionan con el año o con la editorial, filas por artículo que inflan la métrica, etc.). Al menos 5 puntos concretos y, para cada uno, una comprobación hecha o una propuesta.

## Entrega y checkpoints
- Checkpoint al terminar cada letra (A, B, C, D): una línea en `RAIZ\modelos\CHECKPOINTS_RONDA2.md` con la hora, lo validado y lo que falló.
- Reporte final corto en el chat con cifras, lo que no pudiste verificar y las 3 conclusiones más importantes. **No uses git:** Claude revisa y sube.
- **No hagas:** tocar `producto\web\`, `curation\`, la ronda 1, ni nada del clúster; inventar embeddings; presentar un resultado exploratorio como definitivo.
