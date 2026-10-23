# Registro de decisiones del proyecto Nano2Predict

Para exponer (en la presentación, el video y el informe del seminario) **qué decidimos, por qué y con qué evidencia**. Cada decisión tiene su estado. Lo que no está respaldado con datos se marca como tal: no se afirma más de lo que sabemos.

## A. Datos
| # | Decisión | Por qué | Evidencia / dónde | Estado |
|---|---|---|---|---|
| D1 | Solo artículos de **acceso abierto con licencia CC BY** (y 1 CC0) | Poder redistribuir imágenes y datos con crédito al DOI | `curation/v0.1/VALIDACION.md` (1.823 CC BY + 1 CC0) | Cerrada |
| D2 | **Cada dato lleva una cita textual verificada por código** (cita y números deben aparecer en el artículo) | Que la IA no invente: trazabilidad hasta la fuente | 2 citas rechazadas en toda la base; `curation/extended.py` | Cerrada |
| D3 | **Excluir vectores virales (AAV, virus como portador)** | Se caracterizan con técnicas distintas a las de nanopartículas; el alcance del proyecto son nanoportadores y nanomateriales. Las nanopartículas **contra** virus o con antígenos sí se incluyen | Discusión con el profesor (23/10); el Atlas conserva 8 artículos con «virus» en el título que no usan virus como portador. **Falta respaldarlo con una figura** (técnicas más comunes por artículo con micrografía) | Cerrada; evidencia por completar |
| D4 | Dos niveles de evidencia: **E1** (micrografía + medidas + espectro) y **E2** (micrografía + medidas o espectro) | Regla flexible para ampliar la base sin perder la micrografía | 1.130 E1 y 577 E2 | Cerrada |
| D5 | Las medidas (tamaño, PDI, zeta) se aceptan **de cualquier licencia**, las **imágenes solo de licencia verde** | Permiso de redistribución | Política de la puerta | Cerrada |
| D6 | Se trabaja con la **figura completa**, no con paneles recortados | El extractor identifica figuras; no hay coordenadas de paneles | Mediana de 1 figura por artículo | **Abierta: es la principal limitación del modelo de imágenes** |
| D7 | Clases de portador en 4 grupos: lipídico, polimérico, inorgánico, nanomaterial | Suficientes ejemplos por clase | `curation/v0.1/tabla_modelo.csv`; «nanomaterial» se solapa con inorgánico (ver `modelos/REVISION_CRITICA.md`, punto 6) | Abierta |
| D8 | **QC en 20 artículos, asistido por IA**, no humano | La revisión manual completa no escala; el jurado no revisa dato a dato | `equipo/qc_carlos/` (micrografías 19/19, espectros 14/16, descriptores 9/10 sobre lo comprobable) | Cerrada; se declara como asistida por IA |

## B. Evaluación y modelos
| # | Decisión | Por qué | Evidencia / dónde | Estado |
|---|---|---|---|---|
| D9 | **Toda evaluación separa por artículo** (5 particiones, `fold`) | Figuras o muestras del mismo artículo se parecen; mezclarlas inflaría el resultado | Comprobado: el vecino más cercano de una imagen es del mismo artículo solo en el 2,7 % de los casos | Cerrada |
| D10 | **Escalera de complejidad**: media global → media por clase → lineal → Ridge → Random Forest → Gradient Boosting → vectores de imagen → fusión | Ver cuánto aporta cada peldaño y no saltar a lo complejo sin base | `modelos/tabular*/`, `producto/modelo_tabular/` | Cerrada |
| D11 | **Intervalos de confianza por bootstrap de artículos** y línea base siempre visible | No presentar un número sin su incertidumbre | `REPORTE_TABULAR*.md` | Cerrada |
| D12 | Para predecir la clase **se prohíben `family`, `carrier_type`, `categoria_uso`, el título y la muestra** como entradas (con prueba automática) | Son la respuesta disfrazada | `modelos/tabular/modelo_clase.py` | Cerrada |
| D13 | Banderas de **material** (quitosano, plata, sílice…) **no** entran en los clasificadores de clase | También delatan la respuesta | `modelos/tabular_v2/` | Cerrada |
| D14 | Primero **vectores de imagen congelados** (ResNet50, DINOv2) y solo después ajuste fino | Con ~1.600 artículos, una red completa sobreajusta; el congelado es barato y reproducible | `modelos/comparacion/ANALISIS_RAPIDO_EMBEDDINGS.md` | En curso |
| D15 | Usar **Kabré** para lo que necesite GPU (ajuste fino) y los vectores; el producto **no depende** de él | Plazo y riesgo (nodos interrumpibles, cuenta por curso) | `equipo/KABRE_PLAN.md`; términos de uso | Cerrada |
| D16 | La **etiqueta de la base y la predicción del modelo se muestran siempre por separado** | Honestidad: la predicción es exploratoria | Atlas, panel del modelo | Cerrada |
| D17 | Resultados **modestos presentados como modestos** (tamaño R² 0,24; imagen sola F1 ~0,47; fusión F1 ~0,55) | Es lo que se puede defender; la base carece de parámetros de formulación | `modelos/comparacion/`, `REVISION_CRITICA.md` | Cerrada |
| D18 | Las banderas de **formulación** (método, material) son menciones de texto, **proxies ruidosos**; el 30 % de una muestra auditada fue dudoso | No son recetas confirmadas | `modelos/tabular_v2/REPORTE_TABULAR_V2.md` | Cerrada |

## C. Producto y proceso
| # | Decisión | Por qué | Estado |
|---|---|---|---|
| D19 | El Atlas lista solo artículos E1/E2 (**1.707**); los 117 sin evidencia quedan fuera | Una ficha sin micrografía, medidas ni espectros no aporta | Cerrada |
| D20 | La web no depende de nadie: se regenera con `python web/build_data.py` desde los CSV congelados | Reproducible | Cerrada |
| D21 | La versión de datos se **congela como `v0.1`** (checksums, `.gitattributes`) | Todo el equipo trabaja sobre los mismos bytes | Cerrada |
| D22 | **Agradecer a Kabré (CeNAT/CNCA)** en el informe, README y créditos del video | Lo exigen sus términos de uso | Pendiente de escribir |

## D. Próximos experimentos propuestos por el profesor (23/10)
1. **Mejorar las figuras**: separar figuras compuestas (varios paneles tratados como uno) y aumentar las figuras recogidas por artículo.
2. **Entrenar sin una clase** (sin inorgánicos, sin poliméricas…): mide cuánto depende el modelo de cada clase y si generaliza.
3. **Ajuste fino en Nukwa** (con GPU) de la CNN y del transformer.
4. Otra validación (anidada o externa) y exponer todas las decisiones, como este registro.
5. Contacto con el CNCA por alianzas y proyectos (a través del profesor).
