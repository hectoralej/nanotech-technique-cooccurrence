# Guion del video Nano2Predict (v1, viernes 23 de octubre)

**Duración total:** 10:00 como máximo (objetivo: terminar en 9:50). **Demo del Atlas:** 2:30 (el mínimo exigido es 2:00 y el máximo 3:00).
**Cómo leerlo:** la columna «Se ve en pantalla» dice qué mostrar mientras se lee el texto de «Narración». Las frases son cortas para leerse en voz alta, a unas 140 palabras por minuto. Las cifras están escritas con punto de miles (1.824) y se leen «mil ochocientos veinticuatro».
**Pantalla de apoyo:** la presentación interactiva (`producto/presentacion/index.html`, 11 secciones; la tabla de correspondencia con los bloques está en su `LEEME.md`). Se avanza con las flechas del teclado y `P` agranda la letra para grabar. Se puede grabar la pantalla directamente de ahí.

> **Voces propuestas** (a confirmar el sábado): **Voz A** (la persona con mejor dicción): problema, base y cierre. **Voz B**: modelos y limitaciones. La demo del Atlas la narra quien la grabe (Carlos), con el texto de abajo.

## Reglas de cifras (obligatorio)
**Sí decir, con estas cifras:** 1.824 artículos leídos · 1.707 con evidencia (1.130 E1 + 577 E2) · 2.726 micrografías · 3.116 filas de medidas · 4.015 espectros · cada dato con cita verificada por código (solo 2 artículos con citas rechazadas) · tamaño: R² ≈ 0,24 frente a 0,18 de la línea base, con error relativo mediano ≈ 44 % · clase de portador con medidas: F1 ≈ 0,51 frente a 0,12 de la clase mayoritaria · solo imagen: F1 ≈ 0,44 [0,42–0,47] frente a 0,16 de la clase mayoritaria · imagen + medidas ≈ 0,56 [0,54–0,59] frente a 0,53 [0,50–0,55] de las medidas (diferencia +0,035 [0,014–0,056]) · todo evaluado por artículo con intervalos de confianza.
**No decir:** «datos validados por humanos» · «el modelo acierta/predice bien» · «predecimos el tamaño» sin decir que el error mediano es ≈ 44 % · cifras de las banderas de formulación como resultado principal · «una red neuronal resuelve el problema» · «funciona en producción».
**Si Héctor actualiza un número** (ajuste fino, validación anidada), se cambia aquí, en `GUION_EN.md` y en `producto/presentacion/construir_datos.py` (bloque «ÚNICO SITIO», luego se vuelve a ejecutar) antes de grabar. Ver la tabla «Cifras y su origen» al final.

---

## Bloque 1 · El problema (0:00–1:00) · Voz A
**Se ve en pantalla:** portada de la presentación (5 s) → sección «El problema» con la **Figura 1** (`figuras/figuras_para_el_video/figura_1.png`).

**Narración:**
> Una nanopartícula puede llevar un fármaco justo a donde hace falta.
> Pero diseñar una buena sigue siendo, en buena parte, prueba y error.
> Cada laboratorio mide el tamaño, la carga y la forma de sus partículas. Y lo publica en un artículo.
> Esos datos existen. Pero están encerrados en PDFs: en tablas, en pies de figura, en frases sueltas.
> Para entrenar un modelo hacen falta tres cosas juntas: la imagen de la micrografía, las medidas de esa misma muestra, y la fuente de donde salen.
> Sin esa base, no hay modelos. Así que empezamos por construirla.
> Leímos 1.824 artículos de acceso abierto. En 1.707 encontramos evidencia útil.
> En total: 2.726 micrografías, 3.116 filas de medidas y 4.015 espectros.
> Y cada dato viene con su cita.

*(≈ 150 palabras · 1:00)*

---

## Bloque 2 · Cómo se construyó la base (1:00–3:00) · Voz A
**Se ve en pantalla:** sección «Cómo se construyó»: **Figura 8** (el flujo) → el **ejemplo interactivo de extracción con cita** (elegir el de NLC, que tiene una frase limpia) → **Figura 9** (control de calidad).

**Narración:**
> El proceso tiene cuatro pasos.
> Primero, la búsqueda. Usamos Europe PMC y solo artículos de acceso abierto con licencia Creative Commons. Eso nos permite mostrar las imágenes, con crédito al artículo original.
> Segundo, la extracción. Un modelo de lenguaje lee el texto completo y propone qué micrografías hay, qué técnica se usó, y los valores de tamaño, PDI y potencial zeta.
> Pero una IA puede equivocarse. O inventar.
> Por eso el tercer paso es la regla central del proyecto: cada dato debe traer una cita textual del artículo. Y un programa comprueba que esa cita, y esos números, de verdad aparecen en el texto.
> *[Mostrar el ejemplo]* Aquí un caso real. El sistema extrajo un tamaño de 161 nanómetros, un PDI de 0,444 y un zeta de menos 28,5 milivoltios. Y esta es la frase del artículo de donde salió.
> Si la cita no aparece, el dato se rechaza. En toda la base, el código rechazó citas en solo dos artículos.
> El cuarto paso es el control de calidad. Revisamos una muestra de 20 artículos, con ayuda de una IA.
> De lo que se pudo comprobar: 19 de 19 micrografías correctas, 9 de 10 descriptores y 14 de 16 espectros.
> Es una muestra pequeña, y la revisión fue asistida por IA, no por personas. La presentamos como una estimación preliminar, no como la precisión de toda la base.

*(≈ 215 palabras · 1:35; deja 25 s para dejar leer la pantalla)*

---

## Bloque 3 · Demo del Atlas (3:00–5:30) · Carlos graba y narra
**Se ve en pantalla:** grabación del Atlas (`producto/web/`). Ajustar los conteos de filtros tras la revisión visual final de Carlos (el texto base viene de `producto/web/GUION_DEMO.md`, ampliado a 2:30).

| Tiempo | Acción en pantalla | Narración |
|---|---|---|
| 3:00–3:15 | Portada del Atlas con las cuatro cifras. | «Este es el Atlas de Nano2Predict. Reúne la evidencia publicada sobre nanoportadores: sus artículos, sus micrografías y las técnicas con que se caracterizaron.» |
| 3:15–3:45 | Explorador: elegir **Liposoma** y microscopía **cryoTEM**. Mostrar cómo baja el número de resultados. | «Puedo combinar el tipo de portador con una técnica. Por ejemplo, liposomas observados con crío-microscopía electrónica. La lista se reduce a los artículos que documentan ambas cosas.» |
| 3:45–4:30 | Abrir una ficha con imagen local y descriptores. Desplegar una cita. Pulsar «Copiar cita/DOI». | «Cada ficha muestra la micrografía, el DOI del artículo y las medidas de tamaño, PDI y zeta. Y junto a cada medida, la cita textual que la respalda. Con un clic copio la cita o el DOI para referenciarla.» |
| 4:30–5:05 | En un artículo con predicción real, mostrar el panel del modelo: clase de la base **separada** de la predicción, y los vecinos. | «Aquí aparece el modelo. La etiqueta de la base y la predicción se muestran por separado, porque la predicción es exploratoria. Debajo, las micrografías más parecidas según el modelo, siempre de otros artículos.» |
| 5:05–5:20 | Filtrar por **XRD** y abrir un artículo de nanomaterial. | «También se puede explorar por técnica espectral, por ejemplo difracción de rayos X, y ver qué material se caracterizó.» |
| 5:20–5:30 | Ir a «Cómo se construyó». | «Y al final, cómo se construyó: cada dato mantiene su ruta de vuelta a la fuente.» |

**Condiciones antes de grabar:** que los JSON del modelo ya no digan `prueba: true` (los actuales dicen `prueba: false`; confirmar que sean los finales de Héctor). Si no son los finales, omitir el segmento de 4:30–5:05. Cronometrar dos ensayos completos; si pasa de 2:40, recortar el segmento de XRD.

---

## Bloque 4 · Modelos (5:30–8:00) · Voz B
**Se ve en pantalla:** sección «Modelos» de la presentación (escalera interactiva) → **Figura 10** (resultados de ronda 1) → la gráfica de comparación imagen/medidas/fusión (la entrega Héctor; ver pendientes).

**Narración:**
> Con esta base nos preguntamos: ¿se puede predecir algo útil?
> Construimos una escalera. Empezamos por lo más simple y subimos peldaño a peldaño. En cada uno comparamos con una línea base.
> Primera pregunta: el tamaño de la partícula.
> Predecir siempre el promedio no explica nada: R² igual a cero. Predecir el promedio de cada tipo de portador explica un 18 por ciento.
> Nuestro mejor modelo, una regresión lineal con técnicas y medidas, llega a 0,24.
> Es una mejora real, pero pequeña. El error típico sigue siendo de alrededor de 44 por ciento.
> Y los modelos más complejos, como Random Forest y boosting, no lo mejoraron.
> Segunda pregunta: el tipo de portador. Lipídico, polimérico, inorgánico o nanomaterial.
> Con las medidas, el F1 es de 0,51. Responder siempre la clase más común da 0,12.
> Tercera pregunta: ¿alcanza con mirar la imagen?
> Usamos vectores de dos redes ya entrenadas, ResNet y DINOv2, congeladas, y un clasificador sencillo encima.
> El resultado: F1 de 0,44, con un intervalo de 0,42 a 0,47. La línea base es 0,16. Es mejor que el azar, pero la imagen sola es débil. Y ojo: usamos la figura completa, que muchas veces mezcla varios paneles.
> Cuarta: juntar imagen y medidas. Sube de 0,53 a 0,56. Es una mejora pequeña, pero su intervalo de confianza no incluye el cero.
> Todo esto se evalúa separando por artículo: nunca hay figuras del mismo artículo en entrenamiento y en prueba. Y cada cifra lleva su intervalo de confianza.
> Son cifras exploratorias. Los resultados son modestos. Y los presentamos como modestos.

*(≈ 260 palabras · 1:50; deja 40 s para las gráficas)*

---

## Bloque 5 · Decisiones y limitaciones (8:00–9:00) · Voz B
**Se ve en pantalla:** sección «Decisiones» (tabla filtrable de `equipo/DECISIONES.md`) → sección «Limitaciones».

**Narración:**
> Tomamos decisiones, y las dejamos escritas.
> Excluimos los vectores virales, como los AAV. Se caracterizan con otras técnicas, y nuestro alcance son nanopartículas.
> Trabajamos con la figura completa, no con paneles recortados. Es la principal limitación del modelo de imágenes.
> A los modelos de clase les prohibimos usar el tipo de portador o el título como entrada, porque serían la respuesta disfrazada. Hay una prueba automática que lo garantiza.
> Y sabemos lo que nos falta. La base no tiene parámetros de formulación: proporciones, condiciones de preparación. Por eso el tamaño es tan difícil de predecir.
> Las etiquetas vienen de una IA, y el control de calidad fue en 20 artículos, asistido por IA.
> Y todavía no hay una validación externa.

*(≈ 125 palabras · 0:55)*

---

## Bloque 6 · Siguientes pasos y créditos (9:00–10:00) · Voz A
**Se ve en pantalla:** sección «Siguientes pasos» → pantalla de créditos (logos o nombres: Europe PMC, Kabré CeNAT/CNCA).

**Narración:**
> ¿Qué sigue?
> Primero, recortar los paneles de cada figura y recoger más figuras por artículo. Así el modelo de imágenes verá micrografías, no gráficas.
> Segundo, ajuste fino de las redes en GPU, y entrenar quitando una clase para ver cuánto depende el modelo de cada una.
> Tercero, extraer las condiciones de preparación, y validar con artículos nuevos y con revisión humana a ciegas.
> Gracias a Europe PMC, por abrir el acceso a la literatura.
> Gracias al clúster Kabré, del CeNAT y su Laboratorio Nacional de Computación Avanzada, donde calculamos los vectores de imagen.
> Y gracias al profesor William [apellido por confirmar], por sus preguntas y su guía.
> Nano2Predict: de la literatura, a evidencia que se puede comprobar.

*(≈ 105 palabras · 0:45; deja 15 s de colchón)*

---

## Cifras y su origen (comprobar antes de grabar)
| Cifra | Valor | Origen |
|---|---|---|
| Artículos leídos / con evidencia / E1 / E2 | 1.824 / 1.707 / 1.130 / 577 | `curation/v0.1/RESUMEN_NUMEROS.json`; Figura 1 |
| Micrografías, medidas, espectros | 2.726, 3.116, 4.015 | ídem |
| Licencias | 1.823 CC BY + 1 CC0 | ídem; `equipo/DECISIONES.md` D1 |
| Artículos con citas rechazadas | 2 | `RESUMEN_NUMEROS.json` (`articulos_con_quotes_rejected_mayor_0`) |
| QC (20 artículos, asistido por IA) | micrografías 19/19, descriptores 9/10, espectros 14/16 comprobables | `equipo/qc_carlos/RESUMEN_QC.md`; Figura 9 |
| Tamaño, mejor modelo (Ridge B) | R² 0,240 [0,189–0,287]; error relativo mediano 43,7 % | `modelos/tabular/REPORTE_TABULAR.md`; Figura 10 |
| Tamaño, línea base (media por clase) | R² 0,180 [0,127–0,226] | ídem |
| Clase con medidas (logística, 4 clases) | F1 0,513 [0,482–0,544] | ídem |
| Clase, mayoritaria | F1 0,118 [0,108–0,127] | ídem |
| Clase mayoritaria (2.100 figuras) | F1 0,156 [0,149–0,162] | `modelos/comparacion/METRICAS_CON_IC.md` |
| Imagen sola (modelo del Atlas, SVM con probabilidades) | F1 0,442 [0,416–0,467]; exactitud 0,526 | ídem; coincide con `producto/modelo/metricas.json` |
| Solo medidas (logística) | F1 0,526 [0,500–0,553] | ídem |
| Imagen + medidas (fusión) | F1 0,561 [0,535–0,585] | ídem |
| Fusión − solo medidas | +0,035 [+0,014, +0,056] | ídem (IC pareado) |
| Variante SVM con otra regla de decisión | F1 0,475 [0,451–0,499]: **no se usa como titular** | ídem; exploratoria |

## Pendientes y discrepancias que hay que resolver antes de grabar
1. **Cifra de imagen: resuelta el 23 de octubre.** Héctor aclaró que 0,442 y ≈ 0,47 son la misma entrada con reglas de decisión distintas. La cifra del video es la del Atlas: **0,44** (0,442 [0,416–0,467]). El 0,475 es una variante exploratoria y no se usa. **Las cifras de imagen son exploratorias y pueden cambiar:** Héctor corre el ajuste fino en el clúster y entrega las finales el **sábado a las 3 pm**. Entonces se cambian en `producto/presentacion/construir_datos.py` (un solo sitio, bloque «ÚNICO SITIO»), se vuelve a ejecutar, y se actualizan a mano este guion, `GUION_EN.md`, `producto/web_contenido/modelos_y_limitaciones.md` y la Figura 11.
2. **Figura de comparación imagen/medidas/fusión** (la «Figura 11»): todavía no existe (`figuras/figuras_para_el_video/datos/figura_11.csv` está pendiente de datos reales). Héctor la entrega; la presentación ya muestra una versión interactiva con las cifras de `METRICAS_CON_IC.md`.
3. **Figura 8** tiene el primer recuadro cortado en el borde izquierdo (defecto de la ronda 3 de Codex). Y la Figura 1 escribe «2726» sin punto de miles, a diferencia del resto.
4. **`equipo/DECISIONES.md`, D17,** todavía cita «imagen sola F1 ~0,47; fusión F1 ~0,55». Debe decir ~0,44 y ~0,56 (lo dice el aviso de `construir_datos.py`). Es archivo de Héctor.
5. **Voces y nombre del profesor** por confirmar.
6. **Agradecimiento a Kabré:** lo exigen sus términos de uso (D22); también va en el README y el informe.
