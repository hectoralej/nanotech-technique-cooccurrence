# Base ampliada de coocurrencia — v0.1

Base de artículos de nanomateriales/nanotransportadores con micrografías y evidencia de caracterización. Se construyó mediante búsqueda en Europe PMC, extracción asistida por IA y verificación automática de las citas y los números contra el texto completo; después se aplicaron controles de calidad. Reproducción: `python -m curation.extended apply`.

## Archivos

- `ext_articulos.csv`: un registro por artículo; clasificación, licencia, nivel de evidencia y conteos.
- `ext_paneles.csv`: figuras/micrografías, técnica, muestra, escala y archivo gráfico.
- `ext_descriptores.csv`: tamaño, PDI, potencial zeta, medio, fuente y cita.
- `ext_espectros.csv`: técnica espectroscópica, figura, muestra/aplicación y cita.

## Diccionario de columnas

| CSV | Columnas: tipo — significado |
|---|---|
| CSV | Columnas (tipo; ejemplo → significado / valores) |
|---|---|
| artículos | `pmcid` (texto; PMC123) → ID; `doi` (texto; 10.x/abc) y `doi_link` (URL; https://doi.org/…) → DOI; `title` (texto; título del artículo); `year` (entero; 2024); `family` (categoría; inorganic); `carrier_type` (categoría; liposome); `license_epmc` (texto; cc by); `license_color` (categoría; verde); `tier` (E1/E2/no); `n_panels`, `n_descriptors`, `n_spectra` (enteros; 2); `categoria_uso` (nanoportador/nanomaterial); `spectra`, `image_files` (listas de texto separadas por `|`); `quotes_rejected`, `numbers_not_found` (enteros; 0) → controles de evidencia. |
| paneles | `pmcid` (texto); `categoria_uso` (nanoportador/nanomaterial); `doi_link` (URL); `fig` (texto; Figure 2); `variant` (categoría; SEM); `sample` (texto); `scale_bar_in_caption` (booleano True o vacío → solo marca escala indicada explícitamente); `image_file` (nombre del gráfico completo); `quote` (texto → evidencia). |
| descriptores | `pmcid` (texto); `categoria_uso` (nanoportador/nanomaterial); `doi_link` (URL); `sample` (texto); `size_nm` (número en nm; 120), `pdi` (número; 0.2), `zeta_mV` (número en mV; −20) → valores extraídos sin redondeo; `medium` (texto; PBS/not_declared); `source` (texto; Table 1); `quote` (texto → evidencia). |
| espectros | `pmcid` (texto); `categoria_uso` (nanoportador/nanomaterial); `doi_link` (URL); `technique` (categoría: FTIR/XRD/UVVis/SAXS/EDS/Raman); `fig` (etiqueta; Figure 3); `applies_to`, `sample`, `quote` (texto → asignación y evidencia). |

Las categorías concretas observadas están enumeradas en `RESUMEN_NUMEROS.json`. Las celdas vacías significan que el dato no se declaró/no se verificó; `|` separa varios valores.

## Licencia y límites

Los 1.824 artículos tienen `license_color=verde`; `license_epmc` registra 1.823 CC BY y 1 CC0. Los gráficos se enlazan con DOI para atribución y se conservan completos, no se recortan paneles. La extracción fue asistida por IA y puede contener omisiones o clasificación imperfecta; los CSV mantienen citas para revisión. En una muestra revisada de 20 artículos se estimó: micrografías 19/19 comprobables; espectros 14 sí y 2 no; descriptores 9 sí y 1 no. Es una muestra pequeña, no una estimación estadística global. Los valores extremos se reportan, no se corrigen automáticamente.
