# Técnicas de figura: normalización para el Atlas

Fuente: `modelos/flujo_figuras/figuras_vision.csv`, columna `tecnicas`. La etiqueta original permanece en cada ficha y en `data/figuras.json`. `build_data.py` añade `tecnicas_normalizadas` y `familias_tecnicas` sin modificar el CSV.

| Etiquetas fuente | Etiqueta de filtro | Familia |
| --- | --- | --- |
| `cryo-EM`, `cryo-TEM`, `cryoem`, `cryotem` | cryo-TEM | Microscopía electrónica y de sonda |
| `HAADF`, `HAADF-STEM`, `STEM` | STEM | Microscopía electrónica y de sonda |
| `FT-IR`, `FTIR` | FTIR | Espectroscopías |
| `UV-Vis`, `uvvis`, `UV-vis` | UV-vis | Espectroscopías |
| `EDX`, `EDS`, `EDS-mapas` | EDS | Espectroscopías |
| `NMR`, `1H-NMR` | RMN | Espectroscopías |
| `zeta`, `potencial zeta` | Potencial zeta | Dispersión de luz/rayos X |
| `fluorescencia`, `confocal`, `CLSM` | Fluorescencia/confocal | Fluorescencia y óptica |
| `H&E`, `HE`, `histologia H&E` | Histología H&E | Fluorescencia y óptica |
| `DSC-TGA`, `TGA/DSC` | DSC **y** TGA | Térmicas |
| `TGA/DTA` | TGA **y** DTA | Térmicas |
| `DAPI`, `FITC`, `PI`, `DIC`, `BF`, `DiOC6`, `N2`, `citometria`, `Au M`, `PAS`, `distribucion de tamano` | No se cuenta como técnica | — |

Las etiquetas compuestas térmicas se desdoblan: DSC y TGA son métodos distintos. `cryo-EM` y `cryo-TEM`, así como `HAADF` y `STEM`, se reúnen para navegación; la etiqueta original conserva el detalle. `Fluorescencia/confocal` es una agrupación visual, no una afirmación de equivalencia instrumental. Las etiquetas que no están en este mapa se conservan tal como aparecen en la fuente y se ubican por nombre en la familia correspondiente; una etiqueta nueva sin familia explícita cae en «Otras».

Las seis familias son: Microscopía electrónica y de sonda, Espectroscopías, Térmicas, Dispersión de luz/rayos X, Fluorescencia y óptica, y Otras. Los gráficos de técnicas muestran las diez etiquetas normalizadas más frecuentes, «Otras» (cualquier etiqueta fuera de esas diez) y «Sin técnica». Una figura puede tener varias técnicas y sumar en varias barras; «Otras» cuenta figuras únicas.

El gráfico y el filtro usan por defecto figuras **aceptadas y visibles**. El total de la fuente incluye además la cola y destinos excluidos. El resumen generado en `data/figuras_summary.json` conserva los conteos de ambos alcances y los de etiquetas originales, para auditar la diferencia anterior de 1.974 frente a 2.886.

AFM pertenece a Microscopía electrónica y de sonda. Las diez técnicas principales quedan visibles por familia; las demás se consultan en «Otras técnicas», desplegable.
