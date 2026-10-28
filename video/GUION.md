# Guion del video Nano2Predict (v4, 24 de octubre)

**Duración total:** 10:00 como máximo (objetivo: terminar en 9:50). **Demo del Atlas:** 2:30 (mínimo 2:00, máximo 3:00).
**Presupuesto por bloque:** problema 1:00 · cómo se construyó la base 1:30 · **de la figura al recorte 1:30 (nuevo)** · Atlas 2:30 · modelos y decisiones 2:00 · limitaciones y cierre 1:20 = 9:50. Si no cabe, se recorta «cómo se construyó» y las decisiones; no se acelera la lectura.
**Idioma del video:** la **narración es en español**, con **subtítulos en inglés** (decisión original). El texto de los subtítulos está en `GUION_EN.md`.
**Cómo leerlo:** «Se ve en pantalla» dice qué mostrar mientras se lee la «Narración». Frases cortas, para leerse en voz alta (≈ 140–150 palabras por minuto). Las cifras llevan punto de miles (1.824 = «mil ochocientos veinticuatro»).
**Pantalla de apoyo:** la presentación interactiva (`producto/presentacion/`, 17 secciones; la correspondencia con los bloques está en su `LEEME.md`). Flechas del teclado para avanzar, `P` para agrandar la letra.

> **Voces propuestas** (a confirmar): **Voz A**: problema, base, figura al recorte y cierre. **Voz B**: modelos y decisiones. La demo del Atlas la narra quien la grabe (Carlos).

## Reglas de cifras (obligatorio)
**Sí decir, con estas cifras:** 1.824 artículos leídos · 1.707 con evidencia · 2.726 micrografías · 3.116 filas de medidas, de las que **2.538 son utilizables** tras la auditoría v03 (decir «utilizables», no «validadas») · 4.015 espectros · cada dato con cita verificada por código (solo 2 artículos con citas rechazadas) · **5.539 figuras clasificadas una por una** · **8.108 recortes de panel** · **4.670 recortes de micrografías de partículas con clase** · auditoría a ciegas **47/48** figuras con el número de paneles exacto · cajas del modelo contra cajas humanas **IoU 0,89 en 22 figuras** · tamaño: R² ≈ 0,24 frente a 0,18, con error relativo mediano ≈ 44 % · clase con medidas: F1 ≈ 0,51 frente a 0,12 · solo imagen: F1 ≈ 0,44 [0,42–0,47] frente a 0,16 · ajuste fino en GPU: 0,46 [0,44–0,48], sin mejora clara · con recortes de panel (otras muestras: n = 1.112 y 786): mejora un poco, pero buena parte viene de más vistas por artículo y el IC de la fusión incluye el cero · NFFA: no mejora (B − A = −0,019 [−0,042, +0,005]) · modelo final (n = 1.114, validación cruzada por artículo): exactitud 0,56 y F1 0,52 frente a 0,44 de la clase mayoritaria (492 de 1.114 artículos) · todo evaluado por artículo con intervalos de confianza.
**No decir:** «datos validados por humanos» · «el modelo acierta/predice bien» · «predecimos el tamaño» sin su error (≈ 44 %) · «funciona en producción» · «una red neuronal resuelve el problema» · cifras de banderas de formulación como resultado principal · **«IoU 0,88 contra Codex» (no tiene informe)** · **«revisamos 20 artículos» como eje del control de calidad** (queda como una frase en las limitaciones) · **mezclar cifras de muestras distintas en una misma frase o tabla** (cada cifra con su n).
**Si Héctor actualiza un número:** se cambia en este archivo, en `GUION_EN.md` y en `producto/presentacion/construir_datos.py` (bloque «ÚNICO SITIO»; luego se vuelve a ejecutar). Ver la tabla «Cifras y su origen» al final.

---

## Bloque 1 · El problema (0:00–1:00) · Voz A
**Se ve en pantalla:** portada (5 s) → «El problema» con la **Figura 1**.

**Narración:**
> Una nanopartícula puede llevar un fármaco justo a donde hace falta.
> Pero diseñar una buena depende mucho de la experimentación: se sintetiza, se mide y se vuelve a intentar.
> Cada laboratorio publica el tamaño, la carga y la forma de sus partículas en un artículo. Esos datos existen, pero están encerrados en PDFs: en tablas, en pies de figura, en frases sueltas.
> Para entrenar un modelo hacen falta tres cosas juntas: la imagen de la micrografía, las medidas de esa misma muestra, y la fuente de donde salen.
> Sin esa base, no hay modelos. Así que empezamos por construirla.
> Con ella, nos preguntamos qué se puede predecir desde la imagen y las medidas. Si funcionara, un laboratorio podría orientarse antes de sintetizar. Hoy es exploratorio, y así lo presentamos.
> Leímos 1.824 artículos de acceso abierto. En 1.707 encontramos evidencia útil: 2.726 micrografías, 3.116 filas de medidas y 4.015 espectros.
> Y cada dato viene con su cita.

*(≈ 150 palabras · 1:00)*

---

## Bloque 2 · Cómo se construyó la base (1:00–2:30) · Voz A
**Se ve en pantalla:** «Cómo se construyó»: la línea de proceso se anima (búsqueda → extracción → verificación → figuras → recortes → modelo) → el **ejemplo de extracción con cita** (pestaña «Lípidos (NLC)»; opcional: pulsar «¿Y si la IA inventa el tamaño?»).

**Narración:**
> Primero, la búsqueda. Usamos Europe PMC y solo artículos de acceso abierto con licencia Creative Commons. Eso nos permite mostrar las imágenes, con crédito al artículo original.
> Segundo, la extracción. Un modelo de lenguaje lee el texto completo y propone qué micrografías hay, qué técnica se usó, y los valores de tamaño, PDI y potencial zeta.
> Pero una IA puede equivocarse. O inventar.
> Por eso, la regla central: cada dato debe traer una cita textual del artículo. Y un programa comprueba que esa cita, y esos números, de verdad aparecen en el texto.
> *[Mostrar el ejemplo]* Aquí un caso real: 161 nanómetros, PDI de 0,444, y un zeta de menos 28,5 milivoltios. Y esta es la frase del artículo de donde salió. Si la cita no aparece, el dato se rechaza. En toda la base, el código rechazó citas en solo dos artículos.
> Después, una auditoría de los descriptores: de 3.116 filas, 2.538 son utilizables.

*(≈ 150 palabras · 1:00; quedan ≈ 30 s para que se vea la línea de proceso y el ejemplo)*

---

## Bloque 3 · De la figura al recorte (2:30–4:00) · Voz A
**Se ve en pantalla:** las pantallas de la sección «De la figura al recorte». Las imágenes de artículos llevan su crédito (artículo, DOI, licencia CC BY) en la pantalla. **La figura del flujo (`fig_hero_flujo`) se queda al menos 8 s en pantalla.**

| Pantalla | Qué se ve | Narración |
|---|---|---|
| 1 · El problema | Barras apiladas de los cinco destinos; 4,41 paneles por figura | «Aquí hay un problema: una figura de artículo casi nunca es una sola micrografía. Clasificamos una por una las 5.539 figuras, mirando la imagen. Seis de cada diez son compuestas: tres o más paneles mezclados. Y algunas traen espectros superpuestos. Un modelo no aprende bien de eso. La calidad de las imágenes, no la arquitectura, era lo que más limitaba el resultado.» |
| 2 · Cinco destinos | Pulsar «Compuesta» y luego «Superpuesto» | «Cada figura va a uno de cinco destinos: simple, pareja, compuesta, superpuesta o excluir. Las superpuestas no sirven para entrenar.» |
| 3 · Tres pasos | Botones «figura original → cajas de panel → recortes» | «Para las compuestas, un modelo dibuja una caja por panel, y cada caja se recorta.» |
| 4 · El flujo | **`fig_hero_flujo`** (≥ 8 s) | «Este es el recorrido completo: de 5.539 figuras, 1.702 tienen paneles. De ahí salen 8.108 recortes de panel, y 4.670 son micrografías de partículas con clase de portador: eso es lo que entra al modelo. No entran los insets, ni los espectros, ni la fluorescencia o la biología.» |
| 5 · Muestra sin retoques | Rejilla de 3 recortes al azar por clase | «Esta es una muestra al azar, sin elegir los mejores. Algunos recortes traen un pedazo del panel vecino, y la clase es la del artículo, no la del recorte.» |
| 6 · Calidad | Cifras, diagrama (clic para ampliar; botón EN para subtítulos) | «¿Cómo comprobamos esta etapa? Una auditoría a ciegas acertó el número de paneles en 47 de 48 figuras, y las cajas del modelo coinciden con las dibujadas a mano por una persona, con un IoU de 0,89 en 22 figuras. Son muestras pequeñas. Lo dudoso va a una cola de revisión: precisión antes que cantidad.» |

*(≈ 215 palabras · ≈ 1:25; quedan ≈ 5 s para cambiar de pantalla. Si no cabe, quitar la pantalla 2)*

---

## Bloque 4 · Demo del Atlas (4:00–6:30) · Carlos graba y narra
**Se ve en pantalla:** grabación del Atlas actualizado de Carlos (no la carpeta `web/` del zip de la presentación: es una copia vieja, solo para la vista previa).

| Tiempo | Acción en pantalla | Narración |
|---|---|---|
| 4:00–4:12 | Portada del Atlas con las cuatro cifras. | «Este es el Atlas de Nano2Predict: la evidencia publicada sobre nanoportadores, con sus artículos, sus micrografías y las técnicas con que se caracterizaron.» |
| 4:12–4:38 | Explorador: elegir **Liposoma** y microscopía **cryoTEM**. Mostrar cómo baja el número de resultados. | «Puedo combinar el tipo de portador con una técnica. Por ejemplo, liposomas observados con crío-microscopía electrónica. La lista se reduce a los artículos que documentan ambas cosas.» |
| 4:38–5:10 | Abrir una ficha con imagen local y descriptores. Desplegar una cita. Pulsar «Copiar cita/DOI». | «Cada ficha muestra la micrografía, el DOI del artículo y las medidas de tamaño, PDI y zeta. Junto a cada medida, la cita textual que la respalda, que se copia con un clic.» |
| 5:10–5:25 | Vista **«Figuras y paneles»**: una figura compuesta con sus cajas y los recortes al lado; mostrar un filtro. | «En «Figuras y paneles», cada figura aparece con las cajas que separan sus paneles, y a su lado los recortes. Se filtra por tipo de figura, técnica y clase.» |
| 5:25–5:50 | En un artículo con predicción real, mostrar el panel del modelo: clase de la base **separada** de la predicción, y los vecinos. | «Aquí aparece el modelo. La etiqueta de la base y la predicción se muestran por separado, porque la predicción es exploratoria. Debajo, las micrografías más parecidas, siempre de otros artículos.» |
| 5:50–6:20 | **Demo «sube tu micrografía»:** subir el recorte de una partícula y mostrar la clase predicha. | «Y esta es la demo: subo la micrografía de una partícula, y el modelo, que corre dentro del navegador, devuelve la clase de portador que predice. Con tres advertencias: solo funciona con micrografías de partículas, sus probabilidades no están calibradas, y la clase es la del artículo.» |
| 6:20–6:30 | Ir a «Cómo se construyó». | «Y cada dato conserva su ruta de vuelta a la fuente.» |

**Antes de grabar:** (1) comprobar la narración de «Figuras y paneles» y de la demo contra el Atlas de Carlos (rama `web-carlos`) antes de grabar; (2) para la demo, usar un recorte de una micrografía de partículas, nunca una gráfica; (3) confirmar que los JSON del modelo ya no digan `prueba: true`; si no son los finales, omitir 5:25–5:50; (4) verificar el número de resultados de «Liposoma + cryoTEM» (hoy: 15); (5) cronometrar dos ensayos: si pasa de 2:30, recortar el último segmento.

---

## Bloque 5 · Modelos y decisiones (6:30–8:30) · Voz B
**Se ve en pantalla:** «Modelos» (pestañas tamaño, clase, imagen) → pestaña «Con recortes de panel (preliminar)» con **`fig_modelos_2`** (≥ 8 s) → «Lo que no funcionó: NFFA» con **`fig_modelos_3`** (≥ 8 s) → «Modelo final» → «Decisiones» (grupo «Figuras»).

**Narración:**
> Con esta base nos preguntamos: ¿se puede predecir algo útil? Construimos una escalera, de lo simple a lo complejo, y en cada peldaño comparamos con una línea base.
> El tamaño: nuestro mejor modelo llega a 0,24, contra 0,18 de la línea base. Es una mejora real, pero pequeña: el error típico sigue en 44 por ciento.
> El tipo de portador, con las medidas: F1 de 0,51, frente a 0,12 de responder siempre la clase más común. Con la imagen sola, 0,44 contra 0,16: es débil, y ajustar las redes completas no lo mejora de forma clara.
> *[Figura de recortes]* ¿Y con recortes de panel, en lugar de la figura completa? Mejora un poco: de 0,42 a 0,47 con ResNet50 y de 0,46 a 0,51 con DINOv2. Pero en buena parte es porque los recortes dan más vistas por artículo: con el mismo número de vistas, la ventaja en exactitud baja a menos de un punto. Y en la fusión con medidas, el intervalo incluye el cero. Son otras muestras: 1.112 y 786 artículos.
> *[Figura de NFFA]* También probamos preentrenar con imágenes de microscopía de otra base, NFFA. No funcionó: no mejora, y con las etiquetas mezcladas empeora. Es un resultado negativo, y lo presentamos como tal.
> *[Modelo final]* El modelo final es DINOv2, con tres semillas, entrenado con 4.670 recortes. Su desempeño de referencia, por validación cruzada por artículo: exactitud de 0,56 y F1 de 0,52, frente a 0,44 de la clase mayoritaria. Es exploratorio.
> Todo se evalúa por artículo, con su intervalo de confianza. Y dejamos escritas nuestras decisiones, con su porqué y su evidencia.

*(≈ 265 palabras · ≈ 1:50; quedan ≈ 10 s: es el bloque más justo. Si no cabe, quitar la frase del tamaño o la de las decisiones)*

---

## Bloque 6 · Limitaciones y cierre (8:30–9:50) · Voz A
**Se ve en pantalla:** «Limitaciones» (tarjetas) → «Siguientes pasos» → créditos (Europe PMC, Kabré CeNAT/CNCA).

**Narración:**
> Y sabemos lo que nos falta. Los recortes de panel son preliminares: mejoran la imagen, pero en parte porque dan más vistas por artículo. La base no tiene parámetros de formulación: proporciones, condiciones de preparación. La clase «nanomaterial» es una categoría general. Una muestra de 20 artículos se revisó con ayuda de IA; falta una auditoría humana amplia. Y no hay validación externa.
> ¿Qué sigue? Más figuras por artículo. Entrenar quitando una clase, para saber cuánto depende el modelo de cada una, si aprendió rasgos reales de las partículas o solo sigue a la clase más abundante, y dónde reunir más datos primero. Modelos específicos por clase, con espectros de referencia. Validación externa. Y extraer más condiciones de preparación.
> Gracias a Europe PMC, por abrir el acceso a la literatura. Gracias al clúster Kabré, del CeNAT y su Colaboratorio Nacional de Computación Avanzada, donde se entrenaron los recortes, el experimento NFFA y el modelo final. Y gracias al profesor William Zamora, por sus preguntas y su guía.
> Nano2Predict: de la literatura, a evidencia que se puede comprobar.

*(≈ 190 palabras · ≈ 1:20; sin colchón. Si no cabe, acortar la explicación de «entrenar quitando una clase»)*

---

## Cifras y su origen (comprobar antes de grabar)
**No se mezclan columnas de muestras distintas; cada cifra va con su n.**

| Cifra | Valor | Origen |
|---|---|---|
| Artículos leídos / con evidencia | 1.824 / 1.707 | `curation/v0.1/RESUMEN_NUMEROS.json`; Figura 1 |
| Micrografías, medidas, espectros | 2.726, 3.116, 4.015 | ídem |
| Artículos con citas rechazadas | 2 | `RESUMEN_NUMEROS.json` (`articulos_con_quotes_rejected_mayor_0`) |
| Descriptores utilizables | 2.538 de 3.116 (377 filas auditadas) | `modelos/descriptores_v02/DESCRIPTORES_V03.md` |
| Figuras clasificadas | 5.539 (compuesta 3.392 = 61,2 %; pareja 910; simple 546; superpuesto 394; excluir 297) | `modelos/flujo_figuras/PROGRESO.md` y `figuras_vision.csv` |
| Figuras con paneles / paneles recortados | 1.702 / 8.108 (4.987 micrografía, 1.065 espectro, 2.056 otro) | `segmentacion/cajas/paneles.csv`; `figuras/modelos/fig_hero_flujo_es.png` |
| Recortes de micrografías de partículas con clase | 4.670, de 1.114 artículos | `indice_recortes.csv` (`elegible_morfologia` y `clase`) |
| Auditoría a ciegas | 47/48 con el número de paneles exacto (97,9 %) | `equipo/ESTADO_FIGURAS_24OCT_NOCHE.md` |
| Cajas del modelo contra cajas humanas | IoU 0,89 en 22 figuras (120 paneles). **No citar el IoU 0,88 contra Codex** | ídem |
| Acuerdo y cola de revisión | imagen y pie coinciden en el 67,8 %; 354 figuras aceptadas por arbitraje; 1.512 en cola | `PROGRESO.md` |
| Tamaño, mejor modelo (Ridge B) / línea base, **n = 2.749 filas, 1.080 artículos** | R² 0,240 [0,189–0,287] / 0,180 [0,127–0,226]; error relativo mediano 43,7 % | `modelos/tabular/REPORTE_TABULAR.md` |
| Clase con medidas / mayoritaria, **n = 3.028 filas, 1.201 artículos** | F1 0,513 [0,482–0,544] / 0,118 [0,108–0,127] | ídem |
| **v0.1 (2.100 figuras, 1.641 artículos):** clase mayoritaria | F1 0,156 [0,149–0,162] | `modelos/comparacion/METRICAS_CON_IC.md` |
| ídem: imagen sola (modelo del Atlas) | F1 0,442 [0,416–0,467]; exactitud 0,526 | ídem; coincide con `producto/modelo/metricas.json` |
| ídem: solo medidas | F1 0,526 [0,500–0,553] | ídem |
| ídem: ajuste fino ResNet50 + DINOv2 | F1 0,460 [0,437–0,484]; −congelados +0,018 [−0,008, +0,045] (incluye el cero) | `METRICAS_AJUSTE_FINO_CON_IC.md` |
| ídem: fusión tardía (ajuste fino + medidas, 50/50) | F1 0,580 [0,554–0,603]; −medidas +0,054 [+0,032, +0,077] | ídem |
| **Recortes, imagen (n = 1.112 artículos):** F1 completa → recortes | ResNet50 0,416 → 0,472 (+0,056 [+0,020, +0,091]); DINOv2 0,458 → 0,509 (+0,052 [+0,013, +0,086]) | `modelos/comparacion/ANALISIS_04_RECORTES.md` |
| ídem: control de «mismas vistas» (1,32 frente a 4,18 vistas por artículo) | exactitud +0,006 (ResNet50) y +0,008 (DINOv2); F1 +0,031 y +0,014 | ídem (`.json`) |
| **Recortes, fusión (n = 786 artículos):** fusión recortes − fusión completa | F1 +0,031 [−0,010, +0,071] (**incluye el cero**); fusión recortes F1 0,535, completa 0,504, solo medidas 0,406 | `ANALISIS_FUSION_04.md` |
| **Modelo final (n = 1.114 artículos, validación cruzada por artículo)** | exactitud 0,561; F1 macro 0,521; exactitud balanceada 0,511; clase mayoritaria 0,442 (**492 de 1.114 artículos**, «nanomaterial») | `modelos/modelo_final/LEEME.md`, `modelo_card.json`; el 492 sale de `indice_recortes.csv` |
| Ensamble de 3 semillas frente a una | ≈ +0,013 de exactitud y +0,016 de F1 | `ANALISIS_06_NFFA.md` |
| **NFFA (n = 1.114 artículos):** B − A / C − A / B − C | −0,019 [−0,042, +0,005] / −0,045 [−0,070, −0,020] / +0,026 [+0,001, +0,050] | `ANALISIS_06_NFFA.md`, `entrada_kabre/06_nffa/metricas_06.json` |
| Demo «sube tu micrografía» | corre en el navegador con ONNX; 20 de 20 entradas verificadas (diferencia media 0,0051) | `modelos/modelo_final/LEEME.md`; la hizo Carlos |
| Variante SVM con otra regla de decisión | F1 0,475 [0,451–0,499]: **no se usa como titular** | `METRICAS_CON_IC.md` |

## Pendientes y discrepancias que hay que resolver antes de grabar
1. **Comprobar el Bloque 4 contra el Atlas de Carlos** (rama `web-carlos`: «Figuras y paneles» y la demo). La carpeta `web/` del zip de la presentación es una copia vieja, solo para la vista previa.
2. **Línea base del modelo final:** la clase mayoritaria da 0,442 también con los mismos 1.114 artículos (492 de 1.114, «nanomaterial»); coincide con la de `ANALISIS_04_RECORTES.md` (n = 1.112).
3. **Decisiones D25–D34:** son propuestas que confirma Héctor; ya están en `equipo/DECISIONES.md` (sección E).
4. **Voces** por confirmar.
