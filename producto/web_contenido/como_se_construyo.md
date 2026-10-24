# Cómo se construyó

> Texto para la sección «Cómo se construyó» del Atlas (Carlos lo integra). Español claro, frases cortas. Cifras de `curation/v0.1/RESUMEN_NUMEROS.json`; si cambian, se cambian aquí.

## En una frase
Leímos 1.824 artículos de acceso abierto sobre nanoportadores y nanomateriales. En 1.707 encontramos evidencia útil. **Cada dato de esta base trae la cita textual del artículo de donde sale, y un programa comprueba que esa cita existe.**

## Los cuatro pasos

### 1. Búsqueda
Buscamos en **Europe PMC**, solo artículos de **acceso abierto** con licencia Creative Commons (1.823 CC BY y 1 CC0). Esa licencia nos permite mostrar las micrografías, siempre con el crédito al artículo original (su DOI).

### 2. Extracción con IA
Un modelo de lenguaje lee el texto completo de cada artículo y propone:
- las **micrografías** (imágenes de microscopía electrónica) y la técnica usada (TEM, SEM, cryo-TEM, HRTEM, STEM);
- las **medidas** de cada muestra: tamaño, PDI y potencial zeta;
- los **espectros** (FTIR, XRD, UV-Vis, SAXS, EDS, Raman).

### 3. Verificación por código
Una IA puede equivocarse o inventar. Por eso **cada dato debe traer una cita textual**, y un programa comprueba que esa cita y esos números aparecen de verdad en el texto del artículo. Si no aparecen, el dato se rechaza. En toda la base, el código rechazó citas en solo 2 artículos.

### 4. Control de calidad
Revisamos una muestra de **20 artículos** con ayuda de una IA, que contrastó lo extraído con el artículo:

| Campo | Correctos | Incorrectos | No comprobables |
|---|---:|---:|---:|
| Micrografías | 19 | 0 | 1 |
| Descriptores (tamaño, PDI, zeta) | 9 | 1 | 10 |
| Espectros | 14 | 2 | 4 |

Sobre lo que se pudo comprobar: micrografías 19 de 19, descriptores 9 de 10, espectros 14 de 16.

> **Aviso (siempre visible):** Datos extraídos por IA y verificados por código. Precisión estimada en una muestra revisada.
> La muestra es pequeña y la revisión fue **asistida por IA, no humana**. «No comprobable» no significa error: el dato no pudo contrastarse con lo visible del artículo. Es una estimación preliminar por campo, no la precisión de toda la base.

## Qué significan E1 y E2
- **E1** (1.130 artículos): tiene micrografía, medidas y espectro.
- **E2** (577 artículos): tiene micrografía y medidas, o micrografía y espectro.
- Los 117 artículos restantes no aportaron evidencia y **no aparecen en el Atlas**.

## Decisiones que conviene conocer
- **Solo licencias abiertas para las imágenes.** Las medidas se aceptan de cualquier licencia; las imágenes, solo de licencia CC BY (D1, D5).
- **Sin vectores virales.** Excluimos los AAV y otros virus usados como portador: se caracterizan con técnicas distintas. Las nanopartículas *contra* virus o con antígenos sí están (D3).
- **Figuras completas.** Cada imagen es la figura completa del artículo, que a menudo incluye varios paneles, espectros o gráficas. No hay recortes de cada micrografía (D6).
- **La clase de la base y la predicción del modelo se muestran siempre por separado** (D16).

El registro completo, con 22 decisiones, su porqué y su evidencia, está en `equipo/DECISIONES.md` y en la presentación (`producto/presentacion/`).

## Glosario mínimo
- **Micrografía:** imagen de microscopía electrónica de las partículas.
- **DLS (dispersión dinámica de luz):** técnica que estima el tamaño de partícula en suspensión.
- **PDI (índice de polidispersidad):** qué tan uniforme es el tamaño; valores bajos indican partículas más parecidas entre sí.
- **Potencial zeta (mV):** carga eléctrica efectiva en la superficie de la partícula; da una idea de su estabilidad en suspensión.
- **Cita verificada:** frase del artículo que respalda un dato y que el código comprobó que existe en el texto.
