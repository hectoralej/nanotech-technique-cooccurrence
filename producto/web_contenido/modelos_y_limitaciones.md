# Modelos y limitaciones

> Texto para la página «Modelos y limitaciones» del Atlas (Carlos lo integra). **Cada cifra lleva su n y su fuente. No se mezclan columnas de muestras distintas**: tabla v0.1 (2.100 figuras de 1.641 artículos), recortes (1.112 y 786 artículos), modelo final y NFFA (1.114 artículos). Todo es exploratorio y se presenta como modesto.

## Qué hicimos
Probamos qué se puede predecir con esta base, **de lo simple a lo complejo**: media global → media por clase → regresión lineal → Ridge → Random Forest → Gradient Boosting → vectores de imagen → fusión de imagen y medidas → recortes de panel → modelo final. En cada peldaño comparamos con una **línea base**.

**Todo se evalúa separando por artículo** (5 particiones): ninguna figura ni muestra de un artículo está en el entrenamiento y en la prueba a la vez. Las cifras llevan intervalos de confianza al 95 % (bootstrap de artículos).

## 1. El tamaño de partícula
Muestra: 2.749 tamaños válidos de 1.080 artículos. Fuente: `modelos/tabular/REPORTE_TABULAR.md`.

| Modelo | R² (IC 95 %) |
|---|---|
| Media global (línea base) | −0,003 |
| Media por clase de portador (línea base) | 0,180 (0,127–0,226) |
| **Ridge, con técnicas y medidas** | **0,240 (0,189–0,287)** |
| Random Forest | 0,198 (0,129–0,263) |
| Gradient Boosting | 0,167 (0,090–0,239) |

El mejor modelo explica cerca de **una cuarta parte** de la variación del tamaño. El error relativo mediano sigue en **≈ 44 %**, casi igual al de la línea base (43,6 %). Los modelos más complejos no mejoraron. **No decimos que «predecimos el tamaño»**: la base no trae proporciones ni condiciones de preparación.

## 2. El tipo de portador, con medidas
Cuatro clases (lipídico, polimérico, inorgánico, nanomaterial). Muestra: 3.028 filas de 1.201 artículos. Fuente: `modelos/tabular/REPORTE_TABULAR.md`.

| Modelo | F1 macro (IC 95 %) |
|---|---|
| Responder siempre la clase más común | 0,118 (0,108–0,127) |
| **Regresión logística** | **0,513 (0,482–0,544)** |
| Random Forest | 0,488 (0,456–0,516) |
| Gradient Boosting | 0,473 (0,442–0,502) |

Para evitar trampas, los modelos de clase **no pueden usar** como entrada la familia, el tipo de portador, la categoría de uso, el título ni el nombre de la muestra (hay una prueba automática).

## 3. El tipo de portador, desde la imagen (figura completa, v0.1)
Línea base v0.1. Muestra: 2.100 figuras de 1.641 artículos. Fuentes: `modelos/comparacion/METRICAS_CON_IC.md` y `METRICAS_AJUSTE_FINO_CON_IC.md`.

| Entradas | F1 macro (IC 95 %) |
|---|---|
| Clase mayoritaria | 0,16 (0,15–0,16) |
| Solo imagen, vectores congelados (el modelo del Atlas) | 0,44 (0,42–0,47) |
| Solo imagen, ajuste fino de ResNet50 y DINOv2 en GPU | 0,46 (0,44–0,48) |
| Solo medidas | 0,53 (0,50–0,55) |
| Imagen (congelados) + medidas | 0,56 (0,54–0,59) |
| **Fusión tardía: ajuste fino + medidas** | **0,58 (0,55–0,60)** |

La imagen sola es débil. Ajustar las redes completas en GPU tampoco mejora de forma clara (+0,018 [−0,008, +0,045]: incluye el cero) y DINOv2 sobreajusta (0,96 de acierto en entrenamiento frente a 0,48 en prueba): el límite está en las imágenes, no en la arquitectura. La fusión tardía (peso fijo 50/50 elegido de antemano) supera a las medidas solas por +0,054 [+0,032, +0,077]. El vecino más cercano de una imagen es del mismo artículo solo en el 2,7 % de los casos: no hay fuga por el reparto.

## 4. Con recortes de panel (preliminar)
**Son otras muestras: no se comparan con la tabla 3.** Fuentes: `modelos/comparacion/ANALISIS_04_RECORTES.md` y `ANALISIS_FUSION_04.md`. Figura: `figuras/modelos/fig_modelos_2_es.png` (y `_en`).

**A · Imagen sola, por artículo (n = 1.112 artículos), F1 macro**

| Red | Figura completa | Recortes | Recortes, mismas vistas | Recortes − completa [IC 95 %] |
|---|---:|---:|---:|---|
| ResNet50 | 0,416 | 0,472 | 0,447 | +0,056 [+0,020, +0,091] |
| DINOv2 | 0,458 | 0,509 | 0,471 | +0,052 [+0,013, +0,086] |
| Promedio | 0,472 | 0,515 | — | +0,042 [+0,007, +0,079] |

**B · Fusión con medidas, por artículo (n = 786 artículos; clase mayoritaria: exactitud 0,363)**

| Modelo | Exactitud | F1 macro |
|---|---:|---:|
| Solo medidas | 0,471 | 0,406 |
| Imagen, figura completa | 0,499 | 0,475 |
| Imagen, recortes | 0,541 | 0,519 |
| Fusión medidas + figura completa | 0,547 | 0,504 |
| Fusión medidas + recortes | 0,576 | 0,535 |

Diferencias pareadas en F1 macro (n = 786): imagen recortes − imagen completa +0,044 [+0,002, +0,086]; **fusión recortes − fusión completa +0,031 [−0,010, +0,071]: el intervalo incluye el cero**; fusión recortes − solo medidas +0,129 [+0,082, +0,172].

**Salvedades obligatorias.** La ventaja de los recortes se debe en buena parte a que aportan **más vistas por artículo** (4,18 frente a 1,32): con el mismo número de vistas baja a **+0,006 de exactitud en ResNet50 y +0,008 en DINOv2** (en F1, +0,031 y +0,014). Y el intervalo de «fusión con recortes − fusión con figura completa» incluye el cero.

## 5. Modelo final
DINOv2 ViT-S/14 con ajuste fino completo, **ensamble de 3 semillas**, entrenado con 4.670 recortes de 1.114 artículos. Fuente: `modelos/modelo_final/LEEME.md` y `02_onnx/modelo_card.json`.

| Medida | Valor |
|---|---:|
| Exactitud (validación cruzada por artículo, n = 1.114) | **0,561** |
| F1 macro (ídem) | **0,521** |
| Exactitud balanceada (ídem) | 0,511 |
| Clase mayoritaria, exactitud (n = 1.112 en `ANALISIS_04_RECORTES.md`; es la cifra que cita la ficha del modelo) | 0,442 |

**El modelo final se entrenó con todos los datos: no se puede evaluar.** La validación cruzada por artículo es la única estimación honesta. Es exploratorio y las probabilidades no están calibradas. El ensamble de 3 semillas mejora ≈ +0,013 de exactitud y +0,016 de F1 macro frente a una semilla (`ANALISIS_06_NFFA.md`).

**Demo «sube tu micrografía».** Corre en el navegador con ONNX (la hizo Carlos; 20 de 20 entradas de prueba verificadas contra PyTorch). Solo para micrografías de partículas; las probabilidades no están calibradas; la etiqueta es la clase del artículo.

## 6. Lo que probamos y no funcionó: preentrenar con NFFA-EUROPE
Muestra: 1.114 artículos, 3 semillas por brazo. Fuente: `modelos/comparacion/ANALISIS_06_NFFA.md`. Figura: `figuras/modelos/fig_modelos_3_es.png` (y `_en`).

| Brazo | F1 macro, ensamble de 3 semillas |
|---|---:|
| A · línea base (LVD → nuestros recortes) | 0,521 |
| B · LVD → NFFA → nuestros recortes | 0,502 |
| C · control: NFFA con etiquetas mezcladas | 0,476 |

B − A = −0,019 [−0,042, +0,005] (incluye el cero); C − A = −0,045 [−0,070, −0,020]; B − C = +0,026 [+0,001, +0,050]. **NFFA no mejora**; mezclar las etiquetas daña el modelo. Es un resultado negativo y lo presentamos como tal. Límites: la etapa 1 corrió una vez y se probó una sola configuración.

## Cómo leer el panel del modelo en el Atlas
- La **«Clase del artículo (base de datos)»** es la etiqueta extraída de la base. La **«Predicción del modelo»** es otra cosa: es exploratoria y se muestra siempre por separado.
- El porcentaje junto a la predicción es la confianza del clasificador y **no está calibrado**: no es una probabilidad real.
- Las **micrografías parecidas** se ordenan por similitud de los vectores de imagen y nunca son del mismo artículo.

## Limitaciones
1. **Unidad de evaluación.** La separación es por artículo. No hay artículos compartidos entre entrenamiento y prueba, pero eso no descarta datos reutilizados entre artículos distintos.
2. **Figura completa frente a recorte.** Las cifras principales usan la figura completa, que a menudo mezcla varios paneles. Los recortes mejoran un poco la imagen, pero buena parte de esa ventaja viene de tener más vistas por artículo (sección 4).
3. **Una mención no prueba un método.** Las «banderas» de formulación (materiales, métodos) se detectan por texto: en una muestra auditada, 9 de 30 fueron dudosas. No son nuestro resultado principal.
4. **Variables que no existen antes del experimento.** Los modelos usan zeta y PDI ya medidos. Explican la base, no predicen una formulación antes de prepararla.
5. **Las clases mezclan composición y uso.** «Nanomaterial» es una categoría general y se solapa con «inorgánico».
6. **Intervalos condicionales.** El bootstrap remuestrea predicciones ya hechas; no incluye todos los reentrenamientos ni la búsqueda entre modelos, y puede dar una impresión excesiva de certeza.
7. **Control de calidad asistido por IA.** Una muestra de 20 artículos se revisó con ayuda de IA; falta una auditoría humana a ciegas amplia.
8. **Una micrografía es solo parte de la información.** No dice cómo se preparó la muestra ni sus proporciones, que hoy faltan en la base.
9. **Alcance.** Se excluyen los vectores virales. No hay validación externa.
10. **La etiqueta del recorte es la clase del artículo.** Una micrografía de otro estilo de laboratorio puede predecirse mal.

## Qué no afirmamos
- Que los datos estén validados por personas.
- Que el modelo «acierte» o funcione en producción.
- Que se pueda predecir el tamaño de una nanopartícula con estos datos.

## Siguientes pasos
Más figuras por artículo · entrenar quitando una clase, para ver cuánto depende el modelo de cada una · validación anidada o externa · extraer las condiciones de preparación · revisión humana a ciegas de una muestra. El ajuste fino en GPU, los recortes de panel y el experimento NFFA ya se hicieron (secciones 3 a 6). Ver `equipo/DECISIONES.md`.
