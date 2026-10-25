# Cómo se construyó

> Texto para la sección «Cómo se construyó» del Atlas (Carlos lo integra). Español claro, frases cortas. Cifras de `curation/v0.1/RESUMEN_NUMEROS.json`; si cambian, se cambian aquí.

## En una frase
Leímos 1.824 artículos de acceso abierto sobre nanoportadores y nanomateriales. En 1.707 encontramos evidencia útil. **Cada dato de esta base trae la cita textual del artículo de donde sale, y un programa comprueba que esa cita existe.**

## Los cinco pasos

### 1. Búsqueda
Buscamos en **Europe PMC**, solo artículos de **acceso abierto** con licencia Creative Commons (1.823 CC BY y 1 CC0). Esa licencia nos permite mostrar las micrografías, siempre con el crédito al artículo original (su DOI).

### 2. Extracción con IA
Un modelo de lenguaje lee el texto completo de cada artículo y propone:
- las **micrografías** (imágenes de microscopía electrónica) y la técnica usada (TEM, SEM, cryo-TEM, HRTEM, STEM);
- las **medidas** de cada muestra: tamaño, PDI y potencial zeta;
- los **espectros** (FTIR, XRD, UV-Vis, SAXS, EDS, Raman).

### 3. Verificación por código
Una IA puede equivocarse o inventar. Por eso **cada dato debe traer una cita textual**, y un programa comprueba que esa cita y esos números aparecen de verdad en el texto del artículo. Si no aparecen, el dato se rechaza. En toda la base, el código rechazó citas en solo 2 artículos.

### 4. Figuras, paneles y recortes
Una figura de artículo casi nunca es una sola micrografía: muchas son **compuestas** (varios paneles) y algunas traen **espectros superpuestos** de varias corridas. Por eso las separamos:

| Etapa | Cifra | Fuente |
|---|---:|---|
| Figuras clasificadas una por una, mirando la imagen (no solo el pie de figura) | **5.539** | `modelos/flujo_figuras/figuras_vision.csv`, `PROGRESO.md` |
| Figuras con paneles (compuestas y parejas con micrografía o espectro útil) | **1.702** | `segmentacion/cajas/paneles.csv` |
| Paneles recortados (una caja por panel) | **8.108** | ídem |
| **Recortes que entran al modelo**: micrografías de partículas de nivel superior, con clase de portador | **4.670** (1.114 artículos) | `indice_recortes.csv` (`elegible_morfologia` y `clase`) |

Cinco destinos para cada figura: **simple**, **pareja**, **compuesta**, **superpuesto** (varias curvas en los mismos ejes: no sirve para entrenar) y **excluir**. Dos revisores independientes miran cada figura; los desacuerdos van a un árbitro y lo dudoso queda en una cola de revisión (precisión antes que cantidad).

**Qué recorte entra al modelo y cuál no** (`segmentacion/INSTRUCCIONES_CAJAS.md`): entran solo las **micrografías de partículas** (TEM, SEM, STEM, AFM, cryo-EM) de nivel superior. No entran los **insets**, los espectros, los histogramas y esquemas, la fluorescencia, el confocal ni la histología, ni la biología (bacterias, células, tejido). Lo que no entra se conserva en la base, pero no se usa para entrenar. La clase de cada recorte es la del **artículo**, no la del recorte.

### 5. Control de calidad de figuras y descriptores
- **Auditoría a ciegas:** 47 de 48 figuras con el número de paneles exacto. Las cajas del modelo contra cajas dibujadas a mano por una persona dan **IoU 0,89 en 22 figuras**. Son muestras pequeñas: estimaciones preliminares.
- **Descriptores:** de las 3.116 filas, **2.538 son utilizables** tras la auditoría v03 (se auditaron 377 filas dudosas).
- El diagrama del flujo está en `figuras/flujo_calidad_figuras_es.png` y `_en.png`, y el flujo de datos en `figuras/modelos/fig_hero_flujo_es.png` y `_en.png`.

> **Aviso (siempre visible):** Datos extraídos por IA y verificados por código. Precisión estimada en una muestra revisada.
> La clasificación de figuras y los recortes los hacen modelos de IA y no se han revisado todos a mano. Una muestra de 20 artículos se revisó con ayuda de IA; falta una auditoría humana a ciegas amplia.

## Qué significan E1 y E2
- **E1** (1.130 artículos): tiene micrografía, medidas y espectro.
- **E2** (577 artículos): tiene micrografía y medidas, o micrografía y espectro.
- Los 117 artículos restantes no aportaron evidencia y **no aparecen en el Atlas**.

## Decisiones que conviene conocer
Registro de datos (`equipo/DECISIONES.md`, D1–D8):

| # | Decisión | Estado |
|---|---|---|
| D1 | Solo artículos de **acceso abierto con licencia CC BY** (y 1 CC0) | Cerrada |
| D2 | **Cada dato lleva una cita textual verificada por código** | Cerrada |
| D3 | **Excluir vectores virales** (AAV, virus como portador). Las nanopartículas *contra* virus sí están | Cerrada |
| D4 | Dos niveles de evidencia: **E1** y **E2** | Cerrada |
| D5 | Las medidas se aceptan de cualquier licencia; las imágenes, solo de licencia verde | Cerrada |
| D6 | Se trabajó primero con la **figura completa**, no con paneles recortados | **Superada por D27 (recorte de paneles)**; la figura completa sigue como línea base v0.1 |
| D7 | Clases de portador en 4 grupos: lipídico, polimérico, inorgánico, nanomaterial | Abierta |
| D8 | Una muestra de 20 artículos se revisó con ayuda de IA, no por personas | Cerrada |

Además: **la clase de la base y la predicción del modelo se muestran siempre por separado** (D16). Las decisiones D25–D34 (figuras, evaluación y modelos) son **propuestas** que confirma Héctor. El registro completo, con su porqué y su evidencia, está en `equipo/DECISIONES.md` y en la presentación (`producto/presentacion/`).

## Glosario mínimo
- **Micrografía:** imagen de microscopía electrónica de las partículas.
- **DLS (dispersión dinámica de luz):** técnica que estima el tamaño de partícula en suspensión.
- **PDI (índice de polidispersidad):** qué tan uniforme es el tamaño; valores bajos indican partículas más parecidas entre sí.
- **Potencial zeta (mV):** carga eléctrica efectiva en la superficie de la partícula; da una idea de su estabilidad en suspensión.
- **Cita verificada:** frase del artículo que respalda un dato y que el código comprobó que existe en el texto.
