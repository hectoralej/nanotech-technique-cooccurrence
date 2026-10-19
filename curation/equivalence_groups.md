# Grupos de equivalencia

Regla: dos mediciones son del mismo grupo solo si coinciden en tecnica, variante, magnitud, identidad de la muestra y en las condiciones que cambian su interpretacion; una condicion no declarada (`nd`) **separa** el grupo. Si hay duda, se separa.

- **micrograph**: variante + clase de identidad + escala presente + tamano medido (con n o sin n); el estado de preparacion esta en la variante
- **DLS**: variante (z_average|intensity|number|volume|unspecified) + magnitud + identidad + medio + temperatura + angulo + dilucion; 'nd' separa
- **zeta**: metodo (ELS|PALS|unspecified) + identidad + medio + pH (0.5) + fuerza ionica + modelo; 'nd' separa
- **UVVis**: variante (a intrinseca | b cuantificacion | c ensayo | d turbidez) + identidad
- **FTIR**: variante (ATR|KBr|transmision) + identidad + estado de la muestra
- **XRD**: variante + identidad + radiacion
- **EDS**: variante (SEM|TEM|independiente) + identidad
- **otras**: tecnica + variante + identidad

Grupos observados: 480. Los 25 mayores:

| Grupo | Mediciones | Articulos |
|---|---|---|
| `zeta|unspecified|nanoparticle_loaded|med:water|pH:nd|I:nd|model:not_declared` | 181 | 40 |
| `zeta|unspecified|nanoparticle_loaded|med:nd|pH:nd|I:nd|model:not_declared` | 93 | 44 |
| `UVVis|b_quantification|nanoparticle_loaded` | 55 | 38 |
| `micrograph|TEM_negstain|nanoparticle_loaded|scale_nd|nosize` | 52 | 28 |
| `DSC|DSC|nanoparticle_loaded` | 37 | 23 |
| `micrograph|SEM|nanoparticle_loaded|scale_nd|nosize` | 34 | 23 |
| `UVVis|a_intrinsic|nanoparticle_empty` | 30 | 13 |
| `DSC|DSC|pure_component` | 30 | 17 |
| `zeta|unspecified|nanoparticle_empty|med:water|pH:nd|I:nd|model:not_declared` | 26 | 15 |
| `zeta|unspecified|nanoparticle_empty|med:nd|pH:nd|I:nd|model:not_declared` | 25 | 20 |
| `XRD|powder|nanoparticle_loaded|rad:nd` | 20 | 17 |
| `micrograph|TEM_prep_not_declared|nanoparticle_empty|scale_nd|nosize` | 20 | 13 |
| `zeta|ELS|nanoparticle_loaded|med:water|pH:nd|I:nd|model:not_declared` | 20 | 6 |
| `zeta|ELS|nanoparticle_loaded|med:nd|pH:nd|I:nd|model:not_declared` | 20 | 5 |
| `micrograph|TEM_prep_not_declared|nanoparticle_loaded|scale_nd|nosize` | 19 | 15 |
| `FTIR|KBr|pure_component|state:nd` | 17 | 9 |
| `micrograph|TEM_dried_unstained|nanoparticle_loaded|scale_nd|nosize` | 17 | 13 |
| `FTIR|unspecified|pure_component|state:nd` | 17 | 12 |
| `UVVis|a_intrinsic|nanoparticle_loaded` | 17 | 16 |
| `micrograph|TEM_dried_unstained|nanoparticle_empty|scale_nd|nosize` | 16 | 4 |
| `XRD|powder|pure_component|rad:nd` | 16 | 11 |
| `micrograph|TEM_negstain|nanoparticle_loaded|scale|nosize` | 16 | 8 |
| `NMR|NMR|pure_component` | 16 | 12 |
| `FTIR|unspecified|nanoparticle_loaded|state:nd` | 16 | 14 |
| `XRD|powder|nanoparticle_empty|rad:nd` | 15 | 10 |
