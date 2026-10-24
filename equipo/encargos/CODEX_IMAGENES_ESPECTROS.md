# Codex: depuración de imágenes y espectros (tarea larga, por lotes y con checkpoints)

**Esta tarea reemplaza a R3 y R4 de `CODEX_RONDA_3.md`** (las amplía con los espectros y con el muestreo visual). Si hay contradicción, manda este archivo.
`RAIZ` = `C:\Users\Hector\Desktop\Quimioinformatica Proyecto\nanotech-technique-cooccurrence`. Python: `%LOCALAPPDATA%\Programs\Python\Python313\python.exe` (pandas, numpy, scikit-learn, matplotlib, PIL, lxml; **sin torch ni OpenCV**: no entrenes ni uses redes).

**Reglas de siempre:** no abrir `curation\work\clave_modelo.csv` ni `curation\qc_codex\`; no modificar `curation\ext_*.csv`, `curation\v0.1\`, `curation\work\llm\`, `producto\web\`, `producto\imagenes\` ni tus rondas anteriores (todo lo nuevo va en carpetas nuevas); no usar git; no inventar; **ningún paso se da por cerrado sin su validación**.

## 0. Para qué sirve
El profesor (23/10) señaló que la calidad de las imágenes es probablemente lo que limita el modelo: hoy hay **una sola figura por artículo** y muchas son **compuestas** (micrografía + gráficas + espectros, tratadas como una). Queremos una base de imágenes más rica y más limpia: **todas las figuras de micrografía y de espectros de cada artículo, separadas en paneles, con una etiqueta provisional de tipo**. Esto alimentará el ajuste fino de los modelos en el clúster Kabré; **tú no entrenas nada**.

## 1. Economía de tokens y checkpoints (obligatorio: es una tarea larga)
1. **Trabaja por lotes de 100 artículos** (en el orden de `curation\ext_articulos.csv`, E1 antes que E2). Los scripts deben **reanudarse solos** leyendo `modelos\imagenes_v02\progreso.json` (lote actual, artículos hechos, errores); si te cortan, se retoma sin repetir.
2. **Checkpoint al terminar cada lote** (y nunca más de 40 minutos sin uno): 
   - actualiza `progreso.json` y añade una sección corta a `modelos\imagenes_v02\CHECKPOINTS.md` (hora, lote, cifras acumuladas, fallos, siguiente paso);
   - **muestreo visual (sección 6)** y muéstralo en la sesión;
   - escribe en el chat **un resumen de máximo 12 líneas**. Después **continúa con el lote siguiente sin esperar**, salvo que Héctor escriba «para» o «ajusta».
3. **No imprimas tablas largas ni listados** en el chat: los scripts escriben a archivos y tú solo resumes. No releas archivos grandes; usa `head`/recuentos. No reimprimas código que no cambió.
4. Los pasos caros (descarga, recortes) se ejecutan **una vez por lote**, con registro de lo hecho. Si algo falla en un artículo, **regístralo y sigue** (no detengas el lote).

## 2. Entradas
- `curation\ext_articulos.csv` (1.707 artículos E1/E2; `pmcid`, `carrier_type`, `tier`), `curation\ext_paneles.csv` (micrografías ya extraídas; columnas `fig`, `image_file`, `variant`), `curation\ext_espectros.csv` (`technique`, `fig`, `applies_to`, `quote`), `curation\v0.1\tabla_modelo.csv` (`clase_modelo`, `fold`).
- El texto/XML JATS de cada artículo en la caché local: mira cómo `curation\extended.py` (`fig_graphics`, `_fignum`) y `curation\textprep.py` obtienen figuras, pies y archivos gráficos.
- Imágenes ya disponibles: `RAIZ\producto\imagenes\<pmcid>\` (2.149).
- Descargador de referencia: `RAIZ\modelos\descargar_imagenes.py` (zip de Europe PMC; **los nombres dentro del zip tienen barra invertida `\`**: normalízalos; extrae solo imágenes por nombre exacto).

## 3. Fase 1: inventario de figuras candidatas (sin IA)
Para cada artículo, recorre **todas** sus figuras y clasifica por el **pie de figura** (palabras clave en inglés, con variantes):
- **Micrografía:** TEM, SEM, STEM, HRTEM, cryo-EM/cryoTEM, «transmission electron», «scanning electron», micrograph, AFM.
- **Espectro/difractograma:** XRD, diffraction, FTIR, infrared, UV-Vis, absorbance, «absorption spectrum», SAXS, EDS/EDX, Raman, SERS, DLS (distribución de tamaño), zeta (distribución).
Escribe `modelos\imagenes_v02\inventario_figuras.csv`: `pmcid, figura, archivo_grafico, pie (≤300 car.), tipo_figura (micrografia|espectro|mixta|otra), tecnicas_en_pie, ya_en_base (0/1 si está en ext_paneles o ext_espectros), clase_modelo, fold`. Las figuras **mixtas** (pie con micrografía y espectro) se marcan así. Informa por lote cuántas figuras nuevas hay (micrografía y espectro) y por clase.
**Validación F1:** cada artículo en un solo fold; ninguna figura duplicada; `ya_en_base` coherente con `ext_paneles.csv`.

## 4. Fase 2: descarga de las figuras nuevas (por lote)
Solo las que no estén ya en `producto\imagenes\`. Hasta 4 hilos, reanudable, con pausa entre peticiones. Destino: `RAIZ\producto\imagenes_v02\<pmcid>\` (no va a Git: añade la ruta a `.gitignore`). Registro `modelos\imagenes_v02\descargas_v02.csv` (`pmcid, archivo, ok, bytes, motivo`). Los archivos `.webp` que no estén en el zip se registran como faltantes: no inventes otra fuente.
**Validación F2:** los archivos descargados abren con PIL; los faltantes están registrados con motivo.

## 5. Fase 3: separar paneles compuestos y estimar el tipo (heurística, sin IA)
Para cada figura disponible (las 2.149 antiguas y las nuevas):
1. **Corte por franjas blancas:** perfiles de proyección de filas y columnas casi blancas; corta recursivamente por las franjas vacías (anchura mínima configurable); descarta recortes muy pequeños; **conserva la figura entera** si no se puede cortar. Guarda en `RAIZ\producto\imagenes_recortes\<pmcid>\<archivo>_pN.png` (no va a Git). Documenta los umbrales; **no borres ni modifiques ninguna imagen original**.
2. **Tipo estimado por estadística de píxeles** (sin redes): para cada recorte calcula fracción de píxeles casi blancos, grado de gris (saturación), densidad de bordes y relación de aspecto, y asigna `tipo_estimado` ∈ {`micrografia_probable` (mayormente gris, con textura y poco fondo blanco), `grafica_probable` (fondo blanco, líneas y ejes, poca textura), `mixto_o_dudoso`} con sus puntuaciones. **Es una etiqueta provisional**: la confirmará un modelo de visión en el clúster. Dilo así en los informes.
3. **Vínculo con la técnica:** para cada recorte de una figura cuyo pie nombra técnicas (inventario), guarda `tecnicas_en_pie`; si el pie tiene etiquetas de subpanel («(a) SEM, (b) XRD…»), intenta asignarlas por orden de lectura (izquierda→derecha, arriba→abajo) **solo si el número de recortes coincide con el número de etiquetas**; si no, deja la asignación vacía (no adivines).
Escribe `modelos\imagenes_v02\recortes_v02.csv`: `pmcid, figura, archivo_original, archivo_recorte, n_recortes_figura, tipo_estimado, p_micrografia, p_grafica, tecnica_asignada (o vacío), clase_modelo, fold, origen (v0.1|nuevo)`.
**Validación F3:** reproducible con la misma configuración; todo recorte apunta a una figura existente; cada artículo conserva un solo fold.

## 6. Muestreo visual por lote (obligatorio; lo ve Héctor en la sesión)
Al cerrar cada lote, elige **5 elementos al azar con semilla fija por lote** (mezcla: al menos 2 `micrografia_probable` y 2 recortes de espectro/gráfica con técnica) y genera `modelos\imagenes_v02\muestras\muestra_lote_NN.png`: una hoja de contacto de 5 recortes, cada uno con una etiqueta en la imagen (`pmcid · figura · tipo_estimado · técnica`) y debajo la **figura original reducida** al lado del recorte para ver si el corte tiene sentido. **Muéstrala en la sesión** (muestra la imagen en el chat; si no puedes mostrarla, da la ruta exacta y describe cada una en una línea). Añade a cada una una autoevaluación en una frase: ¿el recorte es una micrografía/espectro completo?, ¿se cortó a medias?, ¿la etiqueta de tipo es correcta?
Cuenta en el checkpoint cuántas de las 5 consideras **bien extraídas**; si en **2 lotes seguidos** bajan de 3 de 5, **para y propón un ajuste de umbrales** antes de seguir.

## 7. Entregables finales (o parciales en cada checkpoint, siempre utilizables)
- `modelos\imagenes_v02\inventario_figuras.csv`, `descargas_v02.csv`, `recortes_v02.csv`, `progreso.json`, `CHECKPOINTS.md`, carpeta `muestras\`.
- `modelos\imagenes_v02\tabla_modelo_v02.csv`: una fila por **recorte** `micrografia_probable` (y otra tabla `tabla_espectros_v02.csv` con los recortes de espectro y su técnica), heredando `clase_modelo` y `fold` del artículo. **Cuenta cuántas imágenes hay en total comparado con las 2.149 originales.**
- `INFORME_IMAGENES_V02.md` (una página y media): cifras por lote y por clase, umbrales, hallazgos por revista o editorial si los notas, cuántos artículos ganaron imágenes, porcentaje de figuras que no pudieron cortarse, limitaciones, y las muestras revisadas con tu veredicto.

## 8. Qué NO hacer
No entrenar ni usar redes neuronales; no filtrar «micrografía vs gráfica» como si fuera definitivo; no extraer valores numéricos de gráficas; no modificar las imágenes originales ni los CSV congelados; no usar git; no reportar como hecho un lote cuya validación falló.

## 9. Plazos
- **Sábado 24, 12 m:** primer conjunto utilizable (lo hecho hasta entonces, con su tabla y su informe parcial).
- **Sábado 24, 2 pm:** versión final. **Sábado 3 pm:** lo que no esté validado no entra a los modelos del clúster.
