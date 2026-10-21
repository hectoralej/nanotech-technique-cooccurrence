# Guía de verificación humana

Archivo de trabajo: `curation/verificacion_humana_80.csv` (80 artículos). **Cada persona hace su propia copia** con su nombre
(`verificacion_humana_80_hector.csv`, `..._carlos.csv`, …) y la llena **sin mirar la copia del otro**. No miren `work/clave_modelo.csv`: es lo que dijo el modelo.

Cómo se trabaja, artículo por artículo:
1. Copien el enlace de la columna `doi_link` (es `https://doi.org/...`) en el navegador. Se abre el artículo.
2. Busquen en el texto, las figuras y las tablas lo que pide cada columna.
3. Rellenen **solo** las columnas con fondo vacío, con los valores permitidos.

| Columna | Valores permitidos |
|---|---|
| `micrografia_util` | `si` / `no`. «Sí» = hay una figura de la **partícula del nanoportador** (no de un control ni de un componente), con la técnica identificable y ligada a una formulación concreta |
| `variante_micrografia` | `cryoTEM`, `TEM_negstain`, `TEM_posstain`, `TEM_dried_unstained`, `TEM_prep_not_declared`, `HRTEM`, `STEM`, `SEM`, `cryoSEM`, `ESEM`, `ninguna` |
| `dls_util` | `si` / `no`. «Sí» = valor numérico de tamaño con el **medio indicado** (agua, PBS, tampón, suero…), de una muestra identificable |
| `dls_medio` | `agua`, `PBS`, `tampon`, `suero`, `medio_cultivo`, `otro`, `no_declarado`, `sin_dls` |
| `zeta_util` | `si` / `no`. «Sí» = valor numérico con **medio o pH indicado**, de una muestra identificable |
| `zeta_medio` | igual que `dls_medio` (`sin_zeta` si no hay zeta) |
| `misma_muestra` | `si` / `no`. «Sí» = la micrografía, el DLS y el zeta son de la **misma formulación** |
| `pasa_puerta` | `si` solo si `micrografia_util`, `dls_util`, `zeta_util` y `misma_muestra` son `si` |
| `tecnicas_complementarias` | lista separada por `;` de: `UVVis_intrinseca`, `FTIR`, `XRD`, `EDS`, `DSC`, `TGA`, `Raman`, `NMR`, `XPS`, `NTA`, `SAXS`. Solo si se aplican a la **partícula**, no a un componente puro ni a un ensayo |
| `pertinente` | `si` / `no`. «Sí» = es un artículo de investigación donde el nanoportador es el objeto de estudio (no solo una herramienta) y no es AAV ni virus |
| `licencia_ok` | `si` / `no`. «Sí» = en la página del editor dice CC BY o CC0 |
| `notas` | dudas o casos raros |

Regla: **si dudan, `no` / `no_declarado`**.

Cuando las dos copias estén completas: `python -m curation.human_sheet agreement a.csv b.csv` (acuerdo y kappa por campo).
