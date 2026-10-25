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
| D14 | Primero **vectores de imagen congelados** (ResNet50, DINOv2) y solo después ajuste fino | Con ~1.600 artículos, una red completa sobreajusta; el congelado es barato y reproducible | `modelos/comparacion/ANALISIS_RAPIDO_EMBEDDINGS.md` | Cerrada: el ajuste fino se probó y no superó a los congelados (D23) |
| D15 | Usar **Kabré** para lo que necesite GPU (ajuste fino) y los vectores; el producto **no depende** de él | Plazo y riesgo (nodos interrumpibles, cuenta por curso) | `equipo/KABRE_PLAN.md`; términos de uso | Cerrada |
| D16 | La **etiqueta de la base y la predicción del modelo se muestran siempre por separado** | Honestidad: la predicción es exploratoria | Atlas, panel del modelo | Cerrada |
| D17 | **Resultados modestos presentados como modestos** (tamaño R² 0,24; imagen sola F1 0,44 [0,42–0,47]; imagen + medidas 0,56 [0,54–0,59]; ajuste fino 0,46 [0,44–0,48]; fusión tardía del ajuste fino con medidas 0,58 [0,55–0,60]), siempre con su intervalo y su línea base | Es lo que se puede defender; la base carece de parámetros de formulación | `modelos/comparacion/METRICAS_CON_IC.md`, `METRICAS_AJUSTE_FINO_CON_IC.md`, `REVISION_CRITICA.md` | Cerrada |
| D18 | Las banderas de **formulación** (método, material) son menciones de texto, **proxies ruidosos**; el 30 % de una muestra auditada fue dudoso | No son recetas confirmadas | `modelos/tabular_v2/REPORTE_TABULAR_V2.md` | Cerrada |

| D23 | **Probar el ajuste fino de ResNet50 y DINOv2** (10 épocas, GPU L40S de Kabré, 5 particiones por artículo) antes de concluir que la red no es el problema | Comprobar con evidencia si más capacidad de modelo ayuda | F1 0,406 (ResNet50) y 0,443 (DINOv2); promedio 0,460 [0,437–0,484]; frente al modelo del Atlas 0,442 la diferencia es +0,018 [−0,008, +0,045]: no es clara. DINOv2 sobreajusta (0,96 en entrenamiento frente a 0,48 en prueba). `modelos/kabre/03_ajuste_fino.ipynb`, `modelos/comparacion/METRICAS_AJUSTE_FINO_CON_IC.md` | Cerrada: el límite está en las imágenes, no en la arquitectura |
| D24 | Combinar las predicciones afinadas con las medidas por **fusión tardía con peso fijo 50/50 elegido de antemano** | Evitar ajustar el peso con los datos de prueba | F1 0,580 [0,554–0,603]; +0,054 [+0,032, +0,077] sobre las medidas solas. Exploratorio | Cerrada |

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

## E. Decisiones propuestas el 24 de octubre (las confirma Héctor)
Propuestas de Bryan a partir del encargo de Héctor; cada cifra sale del archivo citado. No cambian D1–D24.
| # | Decisión | Por qué | Evidencia / dónde | Estado |
|---|---|---|---|---|
| D25 | Clasificar cada figura **mirándola** (hojas de contacto) y no solo por su pie de figura, en cinco destinos: simple, pareja, compuesta, superpuesto, excluir | Los pies de figura fallan: imagen y pie coinciden en el 67,8 % de las 5.539 figuras | `modelos/flujo_figuras/PROGRESO.md`, `modelos/tipologia_figuras/` | Propuesta, la confirma Héctor |
| D26 | **Dos revisores independientes** (Claude y Codex) y un **árbitro** para los desacuerdos; lo dudoso va a una **cola de revisión** | No fiarse de una sola IA | En 678 figuras comunes coinciden en el destino el 89,8 % y en el número de paneles el 88,8 %; 354 figuras se aceptan por arbitraje y 1.512 quedan en la cola. `modelos/flujo_figuras/PROGRESO.md`, `cola_desacuerdos.csv`, `INSTRUCCIONES_ARBITRO.md` | Propuesta, la confirma Héctor |
| D27 | **Recortar paneles** con cajas normalizadas sobre la figura completa; insets como cajas hijas; cascadas como una caja por curva; biología como «otro» | Una micrografía por muestra, sin gráficos mezclados | 8.108 recortes (4.987 micrografía, 1.065 espectro, 2.056 otro). `modelos/flujo_figuras/segmentacion/INSTRUCCIONES_CAJAS.md`, `cajas/paneles.csv` | Propuesta, la confirma Héctor |
| D28 | **Validación humana**: cajas dibujadas a mano por Héctor en 22 figuras, comparadas con las del modelo | Medir la calidad contra una referencia humana | IoU 0,89 en 22 figuras (120 paneles) y auditoría a ciegas 47/48 en número de paneles. `equipo/ESTADO_FIGURAS_24OCT_NOCHE.md`, `segmentacion/evaluar_contra_humano.py` | Propuesta, la confirma Héctor |
| D29 | **Partición por artículo** (5 particiones): nunca un mismo artículo en entrenamiento y en prueba | Evitar fuga de información (refuerza D9) | D9 y la columna `fold` de `curation/v0.1/tabla_modelo.csv` | Propuesta, la confirma Héctor |
| D30 | **No elegir nada con los datos de prueba**: épocas fijas (última época) y peso de fusión 50/50 fijado de antemano (D24) | Evitar cifras infladas | `modelos/comparacion/METRICAS_AJUSTE_FINO_CON_IC.md`, `ANALISIS_FUSION_04.md` | Propuesta, la confirma Héctor |
| D31 | **Control de «mismo número de vistas por artículo»** al comparar recortes con figura completa | Los recortes dan ≈ 3 veces más vistas por artículo (4,18 frente a 1,32); sin el control la mejora se sobreestima: en ResNet50 la diferencia de exactitud baja a ≈ +0,006 | `modelos/comparacion/ANALISIS_04_RECORTES.md` | Propuesta, la confirma Héctor |
| D32 | **Intervalos por bootstrap de artículos** en todas las comparaciones, y decir «no concluyente» cuando el intervalo incluye 0 | Honestidad con muestras pequeñas | Por ejemplo, el intervalo de la fusión con recortes frente a la fusión con figura completa incluye el cero. `modelos/comparacion/ANALISIS_FUSION_04.md` | Propuesta, la confirma Héctor |
| D33 | Probar el **preentrenamiento intermedio con NFFA-EUROPE** (SEM, CC BY 4.0) antes de ajustar con nuestros recortes, con un **control de etiquetas mezcladas** y el criterio fijado antes de ver los resultados | Una idea razonable que se prueba y se descarta con datos | **No mejora**: B − A = −0,019 [−0,042, +0,005] (incluye el cero); mezclar las etiquetas daña (C − A = −0,045 [−0,070, −0,020]). 1.114 artículos, 3 semillas por brazo. `modelos/comparacion/ANALISIS_06_NFFA.md` | Propuesta, la confirma Héctor |
| D34 | **Ensamble de 3 semillas** para el modelo final | Reducir la variación del azar | En el brazo A mejora ≈ +0,013 de exactitud y +0,016 de F1 macro frente a una semilla. `modelos/comparacion/ANALISIS_06_NFFA.md`, `modelos/modelo_final/LEEME.md` | Propuesta, la confirma Héctor |
