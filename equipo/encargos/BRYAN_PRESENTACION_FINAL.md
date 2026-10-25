# Bryan: presentación y guion, versión casi final (antes de los resultados nuevos del modelo)

Prompt para pegar en tu sesión, con este archivo como contexto. Es una tarea larga: analiza primero, luego haz los cambios, luego verifica. Reglas de siempre: **toda cifra sale de un archivo del repositorio y se cita (no de memoria)**; no inventes cifras; no toques `curation\`, `modelos\`, `producto\modelo\` ni `producto\web\` (es de Carlos); no publiques nada; no dejes credenciales en archivos.

**Lo que ya está bien y se conserva:** la forma, el modo claro/oscuro, el modo presentar, la tabla filtrable de decisiones, el ejemplo con verificación de la cita en vivo, la regla visible «Datos extraídos por IA y verificados por código…» y las reglas de «no decir» del guion. **Lo que NO se hace en esta ronda:** poner las cifras nuevas del modelo (recortes, fusión, NFFA, modelo final): Héctor las entrega después. Deja un espacio marcado «pendiente» donde irán (sección 4).

**Material nuevo que recibes:** carpeta `Para_Bryan` (te la pasa Héctor): 10 figuras originales con sus cajas dibujadas (2 por destino: simple, pareja, compuesta, superpuesto, excluir), `recortes_por_clase.jpg`, `creditos.csv` (artículo, DOI, licencia de cada imagen), y el diagrama del flujo de calidad en español e inglés (`flujo_calidad_figuras_es/en.png` y `.svg`). Todas las imágenes son de artículos CC BY: **muestra siempre su crédito** (artículo y DOI, de `creditos.csv`).

---

## 1. Qué se hizo con las figuras y cómo se eligieron (sección nueva, la más importante)
Héctor pide mostrar **ejemplos reales de los recortes y de las muestras**, para que se entienda el criterio con que se tomaron las figuras de los artículos. Crea una sección nueva «**De la figura al recorte: cómo elegimos qué usar**» (entre «Cómo se construyó» y «La base en figuras»). Contenido:

1. **El problema** (1 pantalla): muchas figuras de artículos son **compuestas** (varios paneles: micrografías, espectros, fotos, gráficos) y algunas tienen **espectros superpuestos de varias corridas**. Un modelo no puede aprender bien de una figura entera mezclada; hay que separar. Frase-guía: la calidad de las imágenes, no la arquitectura del modelo, es lo que más limitaba el resultado.
2. **Tipos de figura** (pantalla interactiva): un selector con los cinco destinos y, al elegir uno, la figura de ejemplo con sus cajas y una frase de qué es y qué se hace con ella:
   - **simple** (un panel), **pareja** (dos paneles), **compuesta** (tres o más paneles), **superpuesto** (varias curvas espectrales superpuestas: **no sirve para entrenar**), **excluir** (no es micrografía ni espectro útil).
   - Leyenda de colores de las cajas: verde = micrografía, azul = espectro, naranja = otro (fotos, esquemas, fluorescencia, biología…).
   - Fuente de las cifras de cada destino: `modelos/flujo_figuras/PROGRESO.md` y `figuras_vision.csv` (cuenta tú los porcentajes y cita el archivo).
3. **De la figura a los recortes** (interactivo de 3 pasos con botones «1 · figura original → 2 · cajas de panel → 3 · recortes»), usando `ejemplo_compuesta_1.jpg` y sus recortes (si necesitas los recortes sueltos de ese ejemplo, pídeselos a Héctor; están en `modelos/flujo_figuras/segmentacion/cajas/`).
4. **Qué recortes entran al modelo y cuáles no** (tabla corta con las reglas, de `modelos/flujo_figuras/segmentacion/INSTRUCCIONES_CAJAS.md`): solo **micrografía de partículas** (TEM/SEM/AFM/cryo) de nivel superior; **no** entran los insets (cajas hijas dentro de un panel), los espectros, la fluorescencia/confocal/histología, ni la biología (bacterias, células, tejido). Cifras (léelas de `cajas/paneles.csv` / `indice_recortes.csv`): total de recortes, cuántos son micrografía, espectro u otro, y **4.670** recortes elegibles con clase de portador.
5. **Muestra sin retoques:** muestra `recortes_por_clase.jpg` (3 recortes al azar por clase del artículo, **sin elegir los mejores**). Debajo, una nota honesta: algunos recortes incluyen una franja del panel vecino o márgenes (se ve en la rejilla); la clase es la del **artículo**, no la del recorte.
6. **Cómo se comprobó la calidad de esta etapa** (esto reemplaza el énfasis en «20 artículos», ver sección 3): auditoría a ciegas de la clasificación (47 de 48 figuras con el número de paneles exacto), cajas contra las cajas humanas de Héctor (IoU 0,89 en 22 figuras, ver `equipo/ESTADO_FIGURAS_24OCT_NOCHE.md`), arbitraje de desacuerdos y cola de revisión para lo dudoso. **No cites «IoU 0,88 contra Codex»**: no tiene informe.
7. **El diagrama completo:** inserta `flujo_calidad_figuras_es.png` (y la versión en inglés para los subtítulos) con zoom al hacer clic.

## 2. Más contenido sobre las decisiones (lo que Héctor quiere reforzar)
Hoy la tabla de decisiones llega a D22. Reorganízala en **cuatro grupos filtrables**: «Datos», «Figuras», «Evaluación estadística», «Modelos». Y añade estas decisiones nuevas como **propuestas** (márcalas «propuesta, la confirma Héctor» y agrégalas también a `equipo/DECISIONES.md` como D25–D33 con la misma tabla, sin cambiar las anteriores):

| Grupo | Decisión (resumida) | Por qué | Evidencia (archivo) |
|---|---|---|---|
| Figuras | Clasificar cada figura **mirándola** (hojas de contacto) y no solo por su pie de figura; separar en simple/pareja/compuesta/superpuesto/excluir | Los pies de figura fallan; la tipología por texto no acertaba el número de paneles | `modelos/flujo_figuras/`, `modelos/tipologia_figuras/` |
| Figuras | Tres revisores independientes (Claude, Haiku, Codex) y **árbitro** para los desacuerdos; lo dudoso va a **cola de revisión** | No fiarse de una sola IA | `modelos/flujo_figuras/cola_desacuerdos.csv` |
| Figuras | **Recortar paneles** con cajas normalizadas; insets como cajas hijas; cascadas como una caja por curva; biología como «otro» | Una micrografía por muestra, sin gráficos mezclados | `INSTRUCCIONES_CAJAS.md` |
| Figuras | **Validación humana** con 22 figuras recortadas a mano por Héctor | Medir la calidad contra una referencia humana | `segmentacion/evaluar_contra_humano.py` |
| Evaluación | **Partición por artículo** (5 particiones): nunca un mismo artículo en entrenamiento y prueba | Evitar fuga de información | D8/D11 y `modelos/` |
| Evaluación | **No elegir nada con los datos de prueba**: épocas fijas, peso de fusión 50/50 fijado de antemano (D24) | Evitar cifras infladas | `ANALISIS_FUSION_04.md` |
| Evaluación | **Control de «mismo número de vistas por artículo»** al comparar recortes con figura completa | Los recortes dan ≈ 3 veces más vistas; sin el control la mejora se sobreestima (baja a ≈ +0,006 de exactitud) | `ANALISIS_04_RECORTES.md` |
| Evaluación | **Intervalos por bootstrap de artículos** en todo y declarar «no concluyente» cuando el IC incluye 0 | Honestidad con n pequeño | `ANALISIS_06_NFFA.md` |
| Modelos | Probar **preentrenamiento intermedio con NFFA-EUROPE** (SEM, CC BY 4.0) con un **control de etiquetas mezcladas**; resultado: **no mejora** y se descarta | Una idea razonable que se prueba y se descarta con datos | `modelos/comparacion/ANALISIS_06_NFFA.md` |
| Modelos | **Ensamble de 3 semillas** para el modelo final (en validación cruzada +0,013 de exactitud) | Reducir la variación del azar | `ANALISIS_06_NFFA.md` |

Verifica cada fila contra su archivo antes de publicarla; si una cifra no está, quítala. La tabla debe seguir filtrable por palabra y por grupo.

## 3. Qué recortar o bajar de peso
- **La muestra de 20 artículos asistida por IA** (Figura 9 y el bloque «Control de calidad»): ya no es el eje. Redúcela a **una frase** dentro de «Limitaciones» («una muestra de 20 artículos se revisó con ayuda de IA; falta una auditoría humana a ciegas amplia») y quita la sección propia. El control de calidad que se destaca ahora es el de las figuras (sección 1.6).
- **No usar** la carpeta `web\` del zip anterior para el botón «Abrir el Atlas»: es la versión vieja. Apunta a la web de Carlos de la rama `web-carlos` cuando Héctor la una a `main`; mientras tanto el botón puede mostrar «Atlas (versión local)».

## 4. Modelos: solo preparar el espacio (no poner cifras nuevas)
- Deja la tabla actual como «**Línea base v0.1 (figura completa)**».
- Añade debajo un bloque «**Resultados con recortes de panel y modelo final: se incorporan al cierre**» con una tabla vacía y el texto de advertencia que irá fijo: *resultados preliminares; evaluación por artículo; la mejora de los recortes se debe en buena parte a que aportan más vistas por artículo; los intervalos de las comparaciones clave incluyen el cero.*
- Reescribe `EVALUACION_APP_VS_WEB.md` y el texto de limitaciones: la demo «sube tu micrografía» **corre en el navegador con ONNX** (modelo exportado en un cuaderno ya escrito); hasta que Héctor entregue los archivos, escribe «en preparación» y no afirmes que funciona. Mantén la advertencia: solo micrografías de partículas; las probabilidades no están calibradas; la etiqueta es la clase del artículo.
- Mantén las limitaciones; añade: una micrografía es solo parte de la información; la clase «nanomaterial» es una categoría general; sin validación externa.

## 5. Interfaz y visuales (donde se puede mejorar el aspecto)
- Hoy es limpia pero sobria. Añade recursos visuales **sin librerías externas** (SVG/CSS): una **gráfica de barras apiladas** con los cinco destinos de figura, una **línea de proceso** animada (búsqueda → extracción → verificación → figuras → recortes → modelo), y **contadores** que suben al entrar en pantalla (respeta `prefers-reduced-motion`).
- Ampliar imágenes con un visor (clic para ampliar, Esc para cerrar); texto alternativo en todas; contraste en ambos temas.
- La sección nueva debe verse bien en proyector y en el modo presentar.

## 6. Guion del vídeo (español e inglés)
- Duración total máxima **10:00** (objetivo 9:50), demo del Atlas 2:30 narrada por Carlos. Presupuesto sugerido: problema 1:00 · cómo se construyó la base 1:30 · **de la figura al recorte 1:30 (nuevo)** · Atlas 2:30 · modelos y decisiones 2:00 (con las cifras que entregue Héctor) · limitaciones y cierre 1:20. Si no cabe, recorta el bloque de «cómo se construyó» y el de decisiones, no aceleres.
- Actualiza `video\GUION.md` y `video\GUION_EN.md` con las cifras y las reglas de arriba: **quita** «revisamos 20 artículos» como eje, **quita** «IoU 0,88 Codex», **añade** el bloque de figuras (qué se ve en pantalla en cada pantalla de la sección 1) y un texto de narración corto para cada una.
- Mantén las reglas de «no decir»: nada de «datos validados por humanos», «el modelo acierta», «predecimos el tamaño» sin su error, ni «funciona en producción».
- Cifras de descriptores: 3.116 filas de las que **2.538 son utilizables** tras la auditoría v03 (`modelos/descriptores_v02/DESCRIPTORES_V03.md`); en el guion di «utilizables» y no «validadas».

## 7. Verificación y entrega
1. Abre la presentación **con servidor** (`python -m http.server 8000` desde `producto/`), no con doble clic, si usa `fetch`; comprueba consola sin errores, imágenes sin romper, 1920×1080 y 375 px, modo claro y oscuro, modo presentar.
2. Revisa que **ninguna cifra** contradiga `figuras_vision.csv`, `paneles.csv`, `indice_recortes.csv` ni `PROGRESO.md`, y que cada imagen de artículo tenga su crédito.
3. Entrega un zip nuevo de `producto/presentacion/` (con `assets/`), los guiones actualizados y un `PROGRESO.md` que diga qué se hizo, qué quedó pendiente y qué cifras esperan a Héctor.
4. No publiques nada; Héctor decide el alojamiento.
