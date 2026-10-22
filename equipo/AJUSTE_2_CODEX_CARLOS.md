# Codex (Carlos): respuestas de Héctor y segundo ajuste

Continúa `equipo/AJUSTE_CODEX_CARLOS.md`. Gracias por el informe: está bien hecho y pregunta lo correcto. Estas son las respuestas, comprobadas por Claude sobre los archivos de Héctor.

## 1. «3.122 filas frente a 3.116»: no hay discrepancia
`ext_descriptores.csv` tiene **3.116 filas de datos** (lo que lee un lector CSV o pandas) pero **3.123 líneas físicas**: hay 6 saltos de línea sueltos dentro de campos entre comillas. Contando líneas físicas (`Measure-Object -Line`, `wc -l`) sale 3.123 − 1 de encabezado = **3.122**. Tu generador, que usa un lector CSV, ya procesó bien las 3.116 filas (3.116 − 7 de los artículos excluidos = 3.109). **Cifra canónica: 3.116.** No cambies nada. Cuenta siempre filas con un lector CSV, no con líneas.

## 2. Checksums que no coinciden: era el fin de línea
Solo fallaban `ext_articulos.csv` y `ext_descriptores.csv`: justo los dos con saltos de línea sueltos dentro de campos. Git de Windows (`core.autocrlf=true`) los convertía al hacer checkout. Héctor ya añadió `.gitattributes` (`curation/ext_*.csv -text`, `curation/v0.1/*.csv -text`) para que se conserven los bytes exactos. Cuando haya subido ese cambio:
1. `git pull --ff-only origin main`.
2. Restaura los CSV con los bytes correctos: `git checkout -- curation/ext_articulos.csv curation/ext_paneles.csv curation/ext_descriptores.csv curation/ext_espectros.csv`.
3. Comprueba los cuatro SHA-256 contra `curation/v0.1/checksums.txt` (`Get-FileHash`). Deben coincidir.
Si a pesar de eso no coinciden, repórtalo con los hashes; no modifiques `checksums.txt`.

## 3. Exclusión AAV/virus: cambia el criterio
La regla del proyecto excluye **virus o AAV usados como vector/portador** (virus, cápside viral, fago, VLP). **No** excluye nanopartículas sintéticas que actúan contra virus o llevan antígenos (antivirales de plata, vacunas con quitosano, LNP con ARNm): esas son nanoportadores válidos. Un filtro por palabras del título excluye de más (p. ej. «SARS-CoV-2», «antiviral», «vaccine», «virus» de una planta).

La base **ya aplica la regla correcta**: el extractor marca los artículos con virus como vector y quedan fuera de las tablas `ext_paneles`, `ext_descriptores` y `ext_espectros`. Por eso:
1. **Quita el filtro propio por título/palabras** de `build_data.py`. No excluyas nada más por AAV/virus.
2. Conserva `producto/web/data/EXCLUIDOS_AAV.csv` solo como **lista de contraste**: renómbrala `EXCLUIDOS_POR_TITULO_PROVISIONAL.csv` y no la apliques. Héctor y Claude revisarán esos 10.
3. Si tras quitar el filtro algún artículo mostrado usa de verdad un virus como vector (p. ej. la ficha dice «virus oncolítico» como portador), anótalo en `producto/web/PROGRESO.md` con el `pmcid`; no lo borres tú.

## 4. Qué artículos muestra el Atlas
`ext_articulos.csv` tiene 1.824 artículos, pero **117 son `tier = no`** y no tienen ni micrografías, ni descriptores ni espectros en las tablas. **El Atlas lista solo `tier` E1 y E2: 1.707 artículos** (1.130 + 577). Coincide con el número de artículos distintos de `curation/v0.1/tabla_modelo.csv`. La portada muestra estas cifras (tras quitar el filtro de título): 1.707 artículos, 2.726 micrografías, 3.116 descriptores, 4.015 espectros; contrástalas con `RESUMEN_NUMEROS.json` y explica cualquier diferencia en `PROGRESO.md`.

## 5. Siguiente
1. Aplicar los puntos 2–4, regenerar los JSON y validar que los conteos de la portada = conteos de los JSON.
2. Comprobar visualmente el sitio en el navegador de Carlos (consola sin errores, filtros, fichas, laptop y móvil).
3. Imágenes: cuando Héctor pase el zip, integrarlas en `producto/imagenes/<pmcid>/<image_file>` y comparar con `producto/imagenes/descargas.csv`.
4. Git: Carlos entrega a Héctor un zip de `producto/web/` y `equipo/qc_carlos/` cada noche (o rama `web-carlos` si tiene permiso de escritura). Sin imágenes en Git.
Cierra cada paso solo cuando pase su validación.
