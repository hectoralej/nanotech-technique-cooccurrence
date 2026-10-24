# Modelos y limitaciones

> Texto para la página «Modelos y limitaciones» del Atlas (Carlos lo integra). Todas las cifras salen de `modelos/tabular/REPORTE_TABULAR.md`, `modelos/comparacion/ANALISIS_RAPIDO_EMBEDDINGS.md` y `modelos/REVISION_CRITICA.md`. **Si Héctor actualiza un número, se cambia aquí.** Los resultados son modestos y se presentan como modestos.

## Qué hicimos
Probamos qué se puede predecir con esta base, **de lo simple a lo complejo**: media global → media por clase → regresión lineal → Ridge → Random Forest → Gradient Boosting → vectores de imagen → fusión de imagen y medidas. En cada peldaño comparamos con una **línea base**, para ver cuánto aporta de verdad.

**Todo se evalúa separando por artículo** (5 particiones): ninguna figura ni muestra de un artículo está en el entrenamiento y en la prueba a la vez. Las cifras llevan intervalos de confianza al 95 % (bootstrap de artículos).

## Resultados

### 1. El tamaño de partícula
| Modelo | R² (IC 95 %) |
|---|---|
| Media global (línea base) | −0,003 |
| Media por clase de portador (línea base) | 0,180 (0,127–0,226) |
| **Ridge, con técnicas y medidas** | **0,240 (0,189–0,287)** |
| Random Forest | 0,198 (0,129–0,263) |
| Gradient Boosting | 0,167 (0,090–0,239) |

El mejor modelo explica cerca de **una cuarta parte** de la variación del tamaño. El error relativo mediano sigue en **≈ 44 %**, casi igual al de la línea base (43,6 %). Los modelos más complejos no mejoraron. **No decimos que «predecimos el tamaño».** La base no trae proporciones ni condiciones de preparación, y eso es lo que más pesa en el tamaño.

### 2. El tipo de portador, con medidas
Cuatro clases: lipídico, polimérico, inorgánico y nanomaterial.

| Modelo | F1 macro (IC 95 %) |
|---|---|
| Responder siempre la clase más común | 0,118 (0,108–0,127) |
| **Regresión logística** | **0,513 (0,482–0,544)** |
| Random Forest | 0,488 (0,456–0,516) |
| Gradient Boosting | 0,473 (0,442–0,502) |

Para evitar trampas, los modelos de clase **no pueden usar** como entrada la familia, el tipo de portador, la categoría de uso, el título ni el nombre de la muestra: serían la respuesta disfrazada. Hay una prueba automática que lo garantiza.

### 3. El tipo de portador, desde la imagen
Usamos vectores de dos redes ya entrenadas (ResNet50 y DINOv2), congeladas, y un clasificador sencillo encima, sobre la **figura completa**.

| Entradas | F1 macro (IC 95 %) |
|---|---|
| Clase mayoritaria | 0,16 (0,15–0,16) |
| Solo imagen (el modelo que muestra el Atlas) | 0,44 (0,42–0,47) |
| Solo medidas | 0,53 (0,50–0,55) |
| **Imagen + medidas** | **0,56 (0,54–0,59)** |

La imagen sola es débil: mejor que el azar, pero modesta. Combinarla con las medidas ayuda un poco: la diferencia es de +0,035 (0,014–0,056), pequeña pero con un intervalo que no incluye el cero. El vecino más cercano de una imagen es del mismo artículo solo en el 2,7 % de los casos: no hay fuga por el reparto de los datos. *(Sobre 2.100 figuras de 1.641 artículos, 1.000 remuestreos por artículo. Son cifras exploratorias: el intervalo no incluye la incertidumbre de reentrenar ni la de haber probado varias variantes, y el ajuste fino en el clúster puede sustituirlas. Fuente: `modelos/comparacion/METRICAS_CON_IC.md`.)*

## Cómo leer el panel del modelo en el Atlas
- La **«Clase del artículo (base de datos)»** es la etiqueta extraída de la base. La **«Predicción del modelo»** es otra cosa: es exploratoria y se muestra siempre por separado.
- El porcentaje junto a la predicción es la confianza del clasificador y **no está calibrado**: no es una probabilidad real.
- Las **micrografías parecidas** se ordenan por similitud de los vectores de imagen y nunca son del mismo artículo.

## Limitaciones
1. **Unidad de evaluación.** La separación es por artículo. No hay artículos compartidos entre entrenamiento y prueba, pero eso no descarta datos reutilizados entre artículos distintos.
2. **Figura completa, no panel.** Muchas figuras mezclan varias micrografías, espectros y texto. No verificamos visualmente que cada imagen sea una micrografía pura. Es la principal limitación del modelo de imágenes.
3. **Una mención no prueba un método.** Las «banderas» de formulación (materiales, métodos) se detectan por texto: en una muestra auditada, 9 de 30 fueron dudosas. Son indicios ruidosos y no son nuestro resultado principal.
4. **Variables que no existen antes del experimento.** Los modelos usan zeta y PDI ya medidos. Explican la base, no predicen una formulación antes de prepararla.
5. **Las clases mezclan composición y uso.** «Nanomaterial» se solapa con «inorgánico». Un F1 mayor con otras clases no prueba mejor capacidad sobre los mismos artículos.
6. **Intervalos condicionales.** El bootstrap remuestrea predicciones ya hechas; no incluye todos los reentrenamientos ni la búsqueda entre modelos, y puede dar una impresión excesiva de certeza.
7. **Control de calidad asistido por IA.** Fue una muestra de 20 artículos revisada con ayuda de una IA. Falta una auditoría humana a ciegas.
8. **Alcance.** Se excluyen los vectores virales. No hay validación externa.

## Qué no afirmamos
- Que los datos estén validados por personas.
- Que el modelo «acierte» o funcione en producción.
- Que se pueda predecir el tamaño de una nanopartícula con estos datos.

## Siguientes pasos
Separar las figuras compuestas y recoger más figuras por artículo · ajuste fino de las redes en GPU · entrenar quitando una clase, para ver cuánto depende el modelo de cada una · validación anidada o externa · extraer las condiciones de preparación · revisión humana a ciegas de una muestra. Ver `equipo/DECISIONES.md`, sección D.
