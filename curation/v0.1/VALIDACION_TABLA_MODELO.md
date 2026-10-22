# Validación de `tabla_modelo.csv`

Generada con `python curation/tabla_modelo.py`; entradas CSV leídas con `utf-8-sig` y salida escrita con `utf-8-sig`. No se descargaron imágenes. El conteo de archivos presentes es una instantánea y puede cambiar mientras continúa la descarga.

## Comprobaciones obligatorias

1. Filas esperadas: **2193** pares únicos `(pmcid, image_file)`; filas generadas: **2193**. Coincidencia exacta: **sí**.
2. Un mismo `pmcid` en más de un fold: **0**; todos los folds entre 0 y 4: **sí**.
3. Distribución de filas por clase y fold:

| clase_modelo | fold 0 | fold 1 | fold 2 | fold 3 | fold 4 |
|---|---:|---:|---:|---:|---:|
| (sin clase) | 11 | 11 | 10 | 10 | 10 |
| inorganico | 75 | 75 | 75 | 75 | 74 |
| lipidico | 65 | 65 | 64 | 64 | 64 |
| nanomaterial | 196 | 195 | 195 | 195 | 195 |
| polimerico | 94 | 94 | 94 | 94 | 93 |

   Filas sin `clase_modelo`: **52**.
4. `ruta_imagen` existente: **1028**; ausente/no descargada: **1165**.
5. `size_nm_mediana` vacío: **869** filas; `zeta_mV_mediana` vacío: **1296** filas.

## Reglas y controles adicionales

- Valores extremos de referencia: **5**; filas con `flag_extremo=1`: **5**. Coinciden: **sí**. Se excluye cada valor marcado solo de la mediana de su campo; otros datos de la fila siguen entrando en su campo respectivo.
- Medianas calculadas por artículo con `Decimal`, sin redondeo. `n_descriptores` cuenta todas las filas descriptor del artículo, incluso si incluyen un valor extremo.
- Mapeo de `carrier_type` (conteo de artículos):

| carrier_type | artículos | clase_modelo |
|---|---:|---|
| `LNP` | 20 | `lipidico` |
| `NLC` | 67 | `lipidico` |
| `PLN` | 16 | `lipidico` |
| `SLN` | 73 | `lipidico` |
| `cubosome` | 3 | `(sin clase)` |
| `inorganic_NP` | 272 | `inorganico` |
| `liposome` | 128 | `lipidico` |
| `micelle` | 25 | `polimerico` |
| `nanoemulsion` | 2 | `(sin clase)` |
| `nanogel` | 52 | `polimerico` |
| `nanomaterial` | 761 | `nanomaterial` |
| `not_a_nanocarrier` | 32 | `(sin clase)` |
| `other` | 45 | `(sin clase)` |
| `polymeric_NP` | 328 | `polimerico` |

   `other` y `not_a_nanocarrier` quedan vacíos; por decisión del usuario, `cubosome` y `nanoemulsion` también quedan vacíos. Tipos existentes sin regla explícita: **0**. Todos los tipos quedan cubiertos por clase o exclusión explícita: **sí**.
- Folds deterministas y agrupados por artículo: dentro de cada clase se ordenan grupos por cantidad de micrografías descendente; SHA-256 del PMCID desempata y cada grupo se asigna al fold con menor carga. Todas las figuras del artículo comparten fold.
- `variant` se une con `|` y `sample` con `; ` dentro de la agrupación. `microscopia` resume TEM/HRTEM como TEM; modalidades mixtas o no reconocidas quedan como `otra`.

## Resultado del gate

- filas_y_pares_unicos: **PASS**
- un_fold_por_pmcid_y_rango_0_4: **PASS**
- distribucion_clase_fold_reportada: **PASS**
- rutas_todas_comprobadas: **PASS**
- medianas_vacias_contabilizadas: **PASS**
- flag_extremo_cuenta: **PASS**
- todos_los_carrier_type_tratados: **PASS**
