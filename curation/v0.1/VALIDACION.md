# Validación de la base v0.1

Validación sobre los cuatro `ext_*.csv`, leídos con `utf-8-sig`. Las cifras se recogen también en `RESUMEN_NUMEROS.json`; los SHA-256 están en `checksums.txt`.

## Integridad y trazabilidad

- Referencias huérfanas de `pmcid`: paneles 0, descriptores 0, espectros 0.
- `image_file`: 0 vacíos; 0 discrepancias entre archivo gráfico y etiqueta/recurso gráfico del XML JATS del artículo; 0 no verificables por falta de XML.
- Columnas y orden preservados: artículos (18), paneles (9), descriptores (10), espectros (8).
- Artículos E1/E2 sin panel: 0. Artículos E1 sin descriptor: 0. E1 sin espectro: 0.
- `license_color`: verde en 1.824/1.824 artículos. `license_epmc`: cc by en 1.823 y cc0 en 1 (por eso no se afirma que todos sean CC BY). `quotes_rejected > 0`: 2 artículos; `numbers_not_found > 0`: 13 artículos.
- `scale_bar_in_caption`: 451 `True`, 2.275 vacíos; ningún `False`.

## Valores y duplicados

Se encontraron 5 valores fuera de los rangos de plausibilidad; se conservan en la base y se listan en `valores_extremos.csv` (hasta 50 filas): cuatro PDI (1,6; 1,8; 2,313; 3,8) y un tamaño (5.958,8 nm). No se corrigieron ni eliminaron.

Filas descriptor idénticas en todas sus columnas: 0. Se detectó una repetición de la misma muestra y los mismos valores numéricos en PMC7309969 (`MSNs`, 188,6 nm, PDI 0,267, zeta −18,4 mV), pero difieren `medium` y `source`; ambas filas permanecen. La unión no debe colapsar registros incompatibles.

## Distribuciones

| Artículos por familia | n | Artículos por `carrier_type` | n |
|---|---:|---|---:|
| inorganic | 985 | nanomaterial | 761 |
| polymeric | 492 | polymeric_NP | 328 |
| liposome | 143 | inorganic_NP | 272 |
| SLN_NLC | 140 | liposome | 128 |
| LNP | 52 | resto de tipos | 335 |
| PLN | 12 | | |

`tier`: E1 1.130; E2 577; no 117. `categoria_uso`: nanoportador 1.063; nanomaterial 761. Por año: 2016 35, 2017 60, 2018 89, 2019 98, 2020 137, 2021 198, 2022 280, 2023 278, 2024 208, 2025 259, 2026 182.

Paneles por `variant`: TEM_prep_not_declared 1.351; SEM 969; HRTEM 117; TEM_negstain 87; TEM_dried_unstained 79; cryoTEM 64; STEM 47; TEM_posstain 12.

Descriptores por tamaño: <10 nm 53; 10–<100 nm 827; 100–<500 nm 1.730; 500–1.000 nm 109; >1.000 nm 31; sin tamaño 366. Espectros por técnica: FTIR 1.559; XRD 885; UVVis 847; EDS 500; Raman 143; SAXS 81.

## Alcance

Se comprobó que los archivos gráficos enlazan con figura/recurso del XML, no una revisión visual de cada imagen ni de su atribución/licencia independiente. Tampoco se revalidó manualmente cada extracción; eso corresponde a la revisión posterior de Claude. La revisión de licencia aquí confirma el campo `license_color` y la regla de selección de Europe PMC, no una auditoría jurídica externa.
