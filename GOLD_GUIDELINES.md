# Guía de anotación del conjunto de validación (gold set)

**Estado actual:** `data/gold_set.csv` contiene una anotación **provisional de un solo anotador (Claude)**, hecha leyendo
frases de recall amplio por técnica (sin ver la salida del detector). **No sustituye** la doble anotación humana que pide
el brief. Para completarla: dos personas del equipo anotan de forma independiente los mismos 56 artículos de
`data/gold_sample.csv` (7 familias × 8) y añaden sus filas a `data/gold_set.csv` con su nombre en `annotator`;
`python -m src.gold evaluate` calculará entonces kappa de Cohen por técnica y usará como verdad terreno solo las celdas
donde ambos coinciden (los desacuerdos se resuelven por consenso y se registran).

Plantilla en blanco: `data/gold_set_human_template.csv` (una fila por artículo, columnas por técnica).

## Definición de verdad terreno

Una técnica es **verdadera** en un artículo si los autores **la usaron en ese estudio y presentan sus datos** en el
texto, figuras o tablas (da igual si la describen en Métodos o solo en Resultados). **No cuenta** nombrarla en la
Introducción o Discusión, citar otros estudios, ni usarla sin presentar datos.

## Convenciones adoptadas (revisar y, si el equipo discrepa, cambiar y reevaluar)

- `cryoEM`: criomicroscopía/crio-tomografía de la muestra. Los criosecciones de tejido (cryostat) y criopreservación **no** cuentan.
- `TEM`: TEM a temperatura ambiente (incluye HRTEM, tinción negativa/positiva). Un artículo con solo cryo-EM no es `TEM`.
- `SEM`: microscopía electrónica de barrido. "mean ± SEM" (error estándar) **no** cuenta.
- `DLS` / `zeta`: separadas. Reportar "tamaño hidrodinámico, PDI" medido con un Zetasizer cuenta como DLS aunque no diga "DLS".
  El tamaño medido por NTA o por imágenes (ImageJ) no es DLS.
- `UVVis`: espectroscopía/espectrofotometría UV-Vis del material o su carga (espectros, banda plasmónica, cuantificación
  de fármaco por absorbancia a λmax). **No** cuenta: lectura colorimétrica de ensayos en lector de placa (MTT, ELISA, BCA),
  detector UV de un HPLC, ni resonancia de plasmón superficial tipo Biacore.
- `XRD`: difracción de rayos X de polvo/película; se anota **literalmente**, de modo que la cristalografía de proteínas también cuenta.
- `FTIR`: infrarrojo; "near-infrared" de imagen in vivo no cuenta.
- `DSC_TGA`: calorimetría diferencial de barrido o termogravimetría; la calorimetría de titulación isotérmica (ITC) no cuenta.
- `NTA`: seguimiento de nanopartículas (NanoSight/ZetaView); "Ni-NTA" (cromatografía) no cuenta.

## Reglas de calidad

1. Anotar sin mirar la salida del detector. 2. Si la técnica está solo en el material suplementario no accesible, marcar `False`
y anotarlo en `notes`. 3. Registrar dudas en `notes` para el consenso.
