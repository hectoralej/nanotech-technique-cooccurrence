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

Grupos observados: 578. Los 25 mayores:

| Grupo | Mediciones | Articulos |
|---|---|---|
| `zeta|unspecified|nanoparticle_loaded|med:water|pH:nd|I:nd|model:not_declared` | 242 | 54 |
| `zeta|unspecified|nanoparticle_loaded|med:nd|pH:nd|I:nd|model:not_declared` | 93 | 44 |
| `UVVis|b_quantification|nanoparticle_loaded` | 68 | 47 |
| `micrograph|TEM_negstain|nanoparticle_loaded|scale_nd|nosize` | 57 | 32 |
| `zeta|ELS|nanoparticle_loaded|med:water|pH:nd|I:nd|model:not_declared` | 52 | 11 |
| `DSC|DSC|nanoparticle_loaded` | 46 | 29 |
| `micrograph|SEM|nanoparticle_loaded|scale_nd|nosize` | 41 | 28 |
| `DSC|DSC|pure_component` | 39 | 22 |
| `zeta|unspecified|nanoparticle_empty|med:water|pH:nd|I:nd|model:not_declared` | 38 | 20 |
| `UVVis|a_intrinsic|nanoparticle_empty` | 30 | 13 |
| `XRD|powder|nanoparticle_loaded|rad:nd` | 26 | 21 |
| `micrograph|TEM_prep_not_declared|nanoparticle_loaded|scale_nd|nosize` | 26 | 20 |
| `zeta|unspecified|nanoparticle_empty|med:nd|pH:nd|I:nd|model:not_declared` | 25 | 20 |
| `micrograph|TEM_prep_not_declared|nanoparticle_empty|scale_nd|nosize` | 24 | 16 |
| `FTIR|KBr|nanoparticle_loaded|state:nd` | 24 | 17 |
| `FTIR|KBr|pure_component|state:nd` | 21 | 13 |
| `UVVis|a_intrinsic|nanoparticle_loaded` | 20 | 18 |
| `SAXS|SAXS|nanoparticle_empty` | 20 | 10 |
| `zeta|ELS|nanoparticle_loaded|med:nd|pH:nd|I:nd|model:not_declared` | 20 | 5 |
| `micrograph|TEM_dried_unstained|nanoparticle_loaded|scale_nd|nosize` | 19 | 15 |
| `FTIR|unspecified|pure_component|state:nd` | 18 | 13 |
| `micrograph|cryoTEM|nanoparticle_loaded|scale|nosize` | 18 | 10 |
| `XRD|powder|pure_component|rad:nd` | 18 | 13 |
| `NMR|NMR|pure_component` | 17 | 13 |
| `micrograph|TEM_negstain|nanoparticle_loaded|scale|nosize` | 16 | 8 |
