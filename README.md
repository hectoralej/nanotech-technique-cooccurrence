# Nano2Predict · AI Atlas for Nanoscience

**An open, verified database linking micrographs, spectra and measurements of nanocarriers, built from open-access (CC BY) articles, plus an exploratory vision model that runs in the browser.**
*Base abierta y verificada que une micrografías, espectros y mediciones de nanoportadores a partir de artículos de acceso abierto (CC BY), y un modelo de visión exploratorio que corre en el navegador.*

| | |
|---|---|
| **Sitio, Atlas y demo** | <https://hectoralej.github.io/nanotech-technique-cooccurrence/> |
| **Presentación** | <https://hectoralej.github.io/nanotech-technique-cooccurrence/presentacion/index.html> |
| **Atlas (explorador de la base)** | <https://hectoralej.github.io/nanotech-technique-cooccurrence/web/index.html> |
| **Demo del modelo (en el navegador)** | <https://hectoralej.github.io/nanotech-technique-cooccurrence/web/demo.html> |
| **Modelo ONNX** | Release [`modelo-v1.0`](https://github.com/hectoralej/nanotech-technique-cooccurrence/releases/tag/modelo-v1.0) (ver `modelos/modelo_final/`) |

## Qué es
Los datos de caracterización de nanoportadores (tamaño, PDI, potencial zeta, micrografías, espectros) están dispersos en PDFs. Nano2Predict los reúne en una base donde **cada dato lleva una cita textual del artículo, comprobada por código**, y prueba qué se puede predecir con ellos.

**Cifras de la versión actual** (fuentes en `curation/v0.1/RESUMEN_NUMEROS.json`, `modelos/flujo_figuras/PROGRESO.md` y `modelos/comparacion/`):
- 1.824 artículos leídos · **1.707 con evidencia** (E1 + E2) · 2.726 micrografías · ≈ 4.000 espectros · 3.116 filas de medidas (**2.538 utilizables** tras la auditoría)
- **5.539 figuras clasificadas** una por una (simple, pareja, compuesta, espectros superpuestos, excluir) · 8.108 paneles recortados · **4.670 micrografías de partículas** con clase de portador
- Control de calidad: auditoría a ciegas 47/48 figuras con el número de paneles exacto; cajas frente a cajas dibujadas a mano, IoU 0,89 (22 figuras)

**Modelo (exploratorio).** DINOv2 ViT-S/14, ajuste fino con los recortes, ensamble de 3 semillas, exportado a ONNX. Validación cruzada por artículo (1.114 artículos): **exactitud 0,561 y F1 macro 0,521**, frente a 0,442 de exactitud de la clase mayoritaria. Predice la **clase del portador del artículo de origen**, no tamaño ni otros parámetros. Las probabilidades no están calibradas y no hay validación externa. Un preentrenamiento intermedio con NFFA-EUROPE **no mejoró** el resultado (`modelos/comparacion/ANALISIS_06_NFFA.md`).

## Equipo
Héctor Rojas (líder del proyecto, estudiante), Carlos y Bryan, en el marco del curso de Quimioinformática.

## Estructura
| Ruta | Contenido |
|---|---|
| `curation/` | Extracción y curación de la base (v0.1 congelada en `curation/v0.1/`), prompts y verificación de citas |
| `modelos/flujo_figuras/` | Clasificación de figuras, cajas de panel, recortes y su validación |
| `modelos/descriptores_v02/` | Descriptores (tamaño, PDI, zeta) con su cita y la auditoría v03 |
| `modelos/tabular/`, `modelos/tabular_v2/` | Modelos con medidas (tamaño y clase) |
| `modelos/comparacion/` | Resultados de imagen, recortes, fusión y experimento NFFA, con intervalos de confianza |
| `modelos/kabre/` | Cuadernos para Kabré (HPC): ajuste fino, NFFA, modelo final y exportación a ONNX |
| `modelos/modelo_final/` | Ficha, contrato y verificación del modelo final (el ONNX va en la release) |
| `producto/web/`, `producto/presentacion/` | Atlas, demo del modelo y presentación (código fuente del sitio) |
| `figuras/` | Figuras de los modelos y del flujo de datos (español e inglés) |
| `equipo/DECISIONES.md` | Registro de decisiones y su evidencia |
| `src/`, `data/`, `figures/`, `config/`, `tests/` | Análisis original de co-ocurrencia de técnicas (ver `README_ANALISIS_ORIGINAL.md`) |

## Reproducir el sitio y la demo
```bash
cd producto
python web/build_data.py        # regenera los JSON del Atlas desde los CSV del repositorio
python -m http.server 8000      # abrir http://localhost:8000/web/ (no abrir los HTML con doble clic)
```
La demo necesita el ONNX de la release `modelo-v1.0` (ver `modelos/modelo_final/LEEME.md`) y ONNX Runtime Web (`producto/web/instalar_runtime.py`). Las imágenes originales y las miniaturas no están en Git.

## Datos, licencias y límites
- Solo se usan artículos de **acceso abierto con licencia CC BY (o CC0)**, de Europe PMC; cada imagen se muestra con su artículo, DOI y licencia.
- Los resultados son **exploratorios**; la etiqueta de entrenamiento es la clase del artículo, no la del recorte; la categoría «nanomaterial» es general.
- **Licencia del código y de los datos derivados: aún no definida por el equipo.** Los artículos y figuras reutilizados conservan la licencia de su fuente.

## Agradecimientos
Europe PMC (acceso abierto a la literatura), **Kabré — CeNAT · CNCA** (cómputo), NFFA-EUROPE (conjunto SEM, CC BY 4.0, usado en un experimento).
