# Plan del equipo hasta la entrega (21 → 25 de octubre)

Entrega del hackatón: **domingo 25 de octubre, 5:45 pm (Costa Rica)**. Video de **10 minutos máximo**, con **2–3 minutos del producto funcionando**. El jurado no lee cada línea de código: evalúa si la solución promete, si hay pruebas suficientes y si se entiende en video.

## Qué tenemos ya (no hay que rehacerlo)
- **1.824 artículos de acceso abierto (todos CC BY)** leídos por IA y verificados por código: cada dato tiene una cita textual comprobada contra el artículo.
- **1.649 artículos útiles** (E1 932 con micrografía + descriptor + espectro; E2 717 con micrografía + descriptor).
- **2.092 micrografías** (TEM 1.031, SEM 752, HRTEM, cryo-TEM…) con nombre de archivo de imagen; **2.320 filas de descriptores** (tamaño DLS, PDI, zeta); **3.005 espectros** (FTIR, XRD, UV-Vis, SAXS, EDS, Raman).
- Control de calidad independiente de Carlos en 20 artículos: micrografías correctas 19/19 comprobables; espectros 14 sí, 2 no; descriptores 9 sí, 1 no (el resto no comprobable o no extraído). Esto es la **estimación de precisión** que mostramos en el video.
- Repositorio estricto aparte: 87 artículos con micrografía + DLS + zeta de la misma muestra.

## Quién hace qué (sin depender unos de otros)

| Persona | Herramienta | Responsabilidad | Carpeta donde escribe |
|---|---|---|---|
| **Héctor** | Claude + ChatGPT | Datos (Codex congela la v0.1 y Claude la revisa), descarga de imágenes, **apoyo en el modelo** (tiene experiencia con CNN), integración final | `curation/` |
| **Bryan** (desde el viernes 23) | Claude | Modelos sobre la base ya congelada e imágenes ya descargadas: backbone congelado, métricas honestas, archivos de predicción para la web, gráficas y 1 minuto del video | `modelos/` y `producto/modelo/` |
| **Carlos** | Codex | Producto web: el atlas navegable que se muestra en el video (2–3 min), cierre corto de su revisión | `producto/web/` |

Nadie escribe en la carpeta de otro. Así no hay choques en Git.

## El contrato de datos (lo que permite trabajar en paralelo)
Todos leen los mismos 4 archivos, que **ya existen hoy** y no cambian de columnas:

| Archivo | Una fila es | Columnas |
|---|---|---|
| `curation/ext_articulos.csv` | un artículo | `pmcid, doi, doi_link, title, year, family, carrier_type, license_epmc, license_color, tier, n_panels, n_descriptors, n_spectra, categoria_uso, spectra, image_files, quotes_rejected, numbers_not_found` |
| `curation/ext_paneles.csv` | una micrografía | `pmcid, categoria_uso, doi_link, fig, variant, sample, scale_bar_in_caption, image_file, quote` |
| `curation/ext_descriptores.csv` | una muestra medida | `pmcid, categoria_uso, doi_link, sample, size_nm, pdi, zeta_mV, medium, source, quote` |
| `curation/ext_espectros.csv` | un espectro | `pmcid, categoria_uso, doi_link, technique, fig, applies_to, sample, quote` |

Los CSV están en UTF-8 con BOM: léanse con `encoding="utf-8-sig"`. El 22 de octubre se congela la **v0.1** (etiqueta `v0.1` en GitHub). Hasta entonces pueden cambiar los números de filas, **no las columnas**. Cada script debe poder volver a correrse sobre la v0.1 sin tocar código.

Imágenes: Héctor las descarga el jueves 22 en `producto/imagenes/<pmcid>/<image_file>` (no van a Git; se comparten en un zip o se regeneran con `modelos/descargar_imagenes.py`).

Archivos que Bryan entrega a Carlos **el sábado 24 antes de las 12 m** (Carlos trabaja con versiones de prueba hasta entonces):
- `producto/modelo/metricas.json`
- `producto/modelo/predicciones.json`
- `producto/modelo/similares.json`

## Calendario

| Día | Héctor | Bryan | Carlos |
|---|---|---|---|
| **Mié 21 (noche)** | Enviar instrucciones; **Codex congela la v0.1** (`BRIEF_CODEX_CONGELAR_V01.md`) | (no disponible) | Cerrar revisión (máx. 1 h); leer instrucciones |
| **Jue 22** | Fusionar repaso, **congelar v0.1 antes de las 6 pm**; Claude de Héctor **descarga todas las micrografías** (script, sin tokens) | (no disponible) | Esqueleto de la web con datos reales y modelo de prueba |
| **Vie 23** | Guion del video (borrador) | Empieza con **datos v0.1 congelados e imágenes ya descargadas**: embeddings + modelo principal | Integrar imágenes reales; fichas por artículo |
| **Sáb 24** | Guion final, grabar narración | JSON para la web **antes de las 12 m**; gráficas y 1 min de video en la tarde | Integrar JSON de Bryan; **web congelada a las 5 pm**; grabar demo de 2–3 min |
| **Dom 25** | Editar y **subir antes de las 2 pm** | Apoyo | Apoyo |

## Estructura sugerida del video (10 min)
1. Problema (1 min): los datos de nanoportadores están dispersos en PDFs; sin micrografías + descriptores emparejados no hay modelos.
2. Cómo construimos la base (2 min): búsqueda en Europe PMC, extracción con IA, **cada dato con cita verificada por código**, licencias CC BY, control de calidad.
3. **Producto en vivo (2–3 min):** el atlas web (Carlos).
4. Modelos (1,5 min): qué predice el modelo de imágenes, métricas por artículo, limitaciones honestas (Bryan).
5. Números de la base y precisión estimada (1 min).
6. Limitaciones y siguientes pasos (1 min). Cierre (30 s).

## Reglas que valen para todos
- Imágenes solo de artículos CC BY (en el conjunto ampliado lo son todos); siempre mostrar el crédito (DOI) junto a la imagen.
- Toda evaluación de modelos se parte **por artículo** (`pmcid`), nunca por imagen.
- Nada de AAV ni virus.
- No abrir `curation/work/clave_modelo.csv` ni `curation/qc_codex/`.
- Mensaje visible en la web y en el video: «Datos extraídos por IA y verificados por código; precisión estimada en una muestra revisada».

## Quién lleva el video
Héctor ya cargó la parte técnica. **El peso del video recae en Bryan y Carlos**: Carlos graba la demo del producto (2–3 min) y Bryan el minuto del modelo; juntos arman el guion y el montaje con la estructura de arriba. Héctor revisa los números, ayuda con el modelo y narra si hace falta.

## Estado de la descarga de imágenes (21 oct)
El script modelos/descargar_imagenes.py está probado: 40 artículos, 48 figuras, 0 fallos, ~4 s por artículo con 4 hilos. Descarga completa estimada: ~2 h y menos de 1 GB. Se lanza con python modelos/descargar_imagenes.py 0 4 (reanudable).
