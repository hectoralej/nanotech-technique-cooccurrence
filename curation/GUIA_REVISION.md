# Guía de revisión humana (Bryan y Carlos)

Revisen **de forma independiente** los 60 artículos de `hoja_revision_humana.csv` (no comenten entre ustedes hasta terminar). Abran el artículo con el enlace
(texto completo en Europe PMC) y rellenen **solo** las columnas con sufijo de su revisor (`_r1` o `_r2`). No miren la salida del modelo.

Valores permitidos:

| Columna | Valores |
|---|---|
| `micrografia_util` | `si` / `no`. «Sí» = hay figura de la **partícula del nanoportador** (no un control ni un componente), con técnica identificable y que se puede enlazar a una formulación concreta |
| `variante_micrografia` | `cryoTEM`, `TEM_negstain`, `TEM_posstain`, `TEM_dried_unstained`, `TEM_prep_not_declared`, `HRTEM`, `STEM`, `SEM`, `cryoSEM`, `ESEM`, `ninguna` |
| `estado_preparacion` | `negstain`, `posstain`, `seco_sin_teñir`, `vitrificado`, `recubierto_SEM`, `no_declarado`, `ninguna` |
| `dls_util` | `si` / `no`. «Sí» = valor numérico de tamaño con **medio indicado**, de una muestra identificable |
| `dls_medio` | `agua`, `PBS`, `tampon`, `suero`, `medio_cultivo`, `otro`, `no_declarado`, `sin_dls` |
| `zeta_util` | `si` / `no`. «Sí» = valor numérico con **medio o pH indicado**, de una muestra identificable |
| `zeta_medio` | igual que `dls_medio` (`sin_zeta` si no hay zeta) |
| `identidad_muestra` | de la muestra principal medida: `nanoparticle_loaded`, `nanoparticle_empty`, `pure_component`, `physical_mixture`, `process_intermediate`, `unclear` |
| `pasa_puerta` | `si` solo si `micrografia_util`, `dls_util` y `zeta_util` son `si` |
| `tecnicas_complementarias_sobre_particula` | lista separada por `;` de: `UVVis_intrinseca`, `FTIR`, `XRD`, `EDS`, `DSC`, `TGA`, `Raman`, `NMR`, `XPS`, `NTA`, `SAXS` (solo si se aplican a la **partícula**, no a componentes puros ni a ensayos) |
| `licencia_color` | `verde` (CC BY, CC0), `amarillo` (CC BY-NC, -ND, -SA), `rojo` (otra o sin licencia), según la página del editor |
| `notas` | dudas, casos raros |

Regla: **si dudan, `no` / `no_declarado` / `unclear`**. Cuando terminen: `python -m curation.human_sheet agreement`.
