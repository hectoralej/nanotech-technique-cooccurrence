# Codex: tabla lista para modelar (sobre la v0.1)

`RAIZ` = `C:\Users\Hector\Desktop\Quimioinformatica Proyecto\nanotech-technique-cooccurrence`. Parte de la etiqueta `v0.1` (ya subida). Reglas de siempre: no abrir `curation\work\clave_modelo.csv` ni `curation\qc_codex\`; no tocar `work\llm\E`, `E_v2` ni los 4 `ext_*.csv`; no hacer git; no inventar. Plazo: **jueves 22, 6 pm**. Esta tarea es de Héctor y Bryan (modelos, viernes 23); no depende de Carlos.

## Respuesta a tu duda de cierre
Sí: **un lote (o una entrega) no se da por cerrado hasta que pase su validación**. Aplícalo aquí: cada paso termina con su comprobación y, si falla, se corrige antes de seguir.

## Parte 1 (pequeña, hazla primero): marcar los valores extremos sin cambiar la v0.1
Los 5 valores de `curation\v0.1\valores_extremos.csv` (4 PDI > 1,5 y un tamaño de 5.958,8 nm) **no se editan en la v0.1**. Solo se marcan en la tabla nueva (parte 2) con una columna de bandera. Anota en `curation\v0.1\NOTA_VALORES_EXTREMOS.md` (5 líneas) qué hiciste y por qué. Validación: la cuenta de filas marcadas debe ser exactamente la de `valores_extremos.csv`.

## Parte 2: `curation\v0.1\tabla_modelo.csv` (una fila por micrografía)
Se genera con un script reproducible `curation\tabla_modelo.py` (pandas; lee con `utf-8-sig`, escribe con `utf-8-sig`). Una fila por cada `(pmcid, image_file)` único de `ext_paneles.csv` (si una figura tiene varias filas de panel, une `variant` con `|` y `sample` con `; `).

Columnas, en este orden:
`pmcid, image_file, ruta_imagen, variant, microscopia (TEM|SEM|cryoTEM|STEM|otra), family, carrier_type, clase_modelo, categoria_uso, tier, year, n_descriptores, size_nm_mediana, zeta_mV_mediana, pdi_mediana, tamano_rango, tiene_FTIR, tiene_XRD, tiene_UVVis, tiene_SAXS, tiene_EDS, tiene_Raman, flag_extremo, fold`

Reglas:
- `ruta_imagen` = `producto/imagenes/<pmcid>/<image_file>`.
- `clase_modelo` (la etiqueta que predecirá Bryan): `lipidico` (liposome, LNP, SLN, NLC, PLN), `polimerico` (polymeric_NP, nanogel, micelle), `inorganico` (inorganic_NP), `nanomaterial` (nanomaterial). `other` y `not_a_nanocarrier` → vacío (se excluyen del modelo). Revisa con `ext_articulos.csv` que la regla cubra todos los `carrier_type` existentes y repórtalo.
- Descriptores a nivel de **artículo** (no de figura): `n_descriptores`, medianas de `size_nm`, `zeta_mV` y `pdi` de sus filas válidas (ignora vacíos y valores marcados como extremos). `tamano_rango`: `<100`, `100-200`, `>200` según la mediana de tamaño; vacío si no hay.
- `tiene_*`: 1 si el artículo tiene esa técnica en `ext_espectros.csv`, 0 si no.
- `flag_extremo`: 1 si el artículo tiene alguno de los 5 valores extremos, 0 si no. Esos valores **no entran** en las medianas.
- `fold`: entero 0–4, asignado **por `pmcid`** (todas las figuras de un artículo, mismo fold), de forma determinista (hash estable del `pmcid`, no `random` sin semilla) y razonablemente balanceado en `clase_modelo`. Es el reparto oficial de validación cruzada: Bryan y Carlos usan el mismo.

### Validación (obligatoria antes de dar la tarea por cerrada)
1. Filas = número de `(pmcid, image_file)` únicos de `ext_paneles.csv`.
2. Ningún `pmcid` en dos folds distintos.
3. Distribución de `clase_modelo` por fold (tabla) y número de filas sin clase.
4. `ruta_imagen` existe en disco para las figuras ya descargadas (la descarga puede seguir en curso: **solo cuenta cuántas existen y cuántas faltan**, no las descargues).
5. Cuántos `size_nm_mediana` y `zeta_mV_mediana` vacíos.

## Entrega
`curation\v0.1\tabla_modelo.csv`, `curation\tabla_modelo.py`, `curation\v0.1\NOTA_VALORES_EXTREMOS.md` y el informe de validación en `curation\v0.1\VALIDACION_TABLA_MODELO.md`. Reporte corto en el chat con cifras y lo que no verificaste. No ejecutes git: Claude revisa y sube.
