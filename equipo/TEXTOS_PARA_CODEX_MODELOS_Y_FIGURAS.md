# Textos para pegar en ChatGPT/Codex (uno por sesión; pueden correr en paralelo)

Modelo sugerido: **GPT 6 Luna** para ambas (son tareas estructuradas). Sol solo si el resultado sale flojo. Evitar Astra.

## Sesión 1: modelos tabulares
Hola Codex. La base v0.1 del proyecto está lista y verificada. Quiero que hagas los primeros modelos tabulares livianos (regresión lineal múltiple/Ridge y Random Forest) como línea base honesta: uno que prediga el tamaño de las nanopartículas a partir de la clase de portador y otras variables, y otro que prediga la clase de portador a partir de las mediciones. En el segundo, `family` y `carrier_type` están prohibidos como entradas porque serían la respuesta disfrazada: escribe una prueba automática que lo garantice. Todo se valida por artículo con la columna `fold` que ya existe.

Las instrucciones completas, con validaciones y entregables, están en `equipo\briefs_codex\BRIEF_MODELOS_TABULARES.md`, dentro de `C:\Users\Hector\Desktop\Quimioinformatica Proyecto\nanotech-technique-cooccurrence`. Léelo entero antes de empezar. Cierra cada paso solo si pasa su validación, no uses git, y al terminar dame un reporte corto con cifras y lo que no pudiste verificar; Claude lo revisará.

## Sesión 2: figuras para el video (CAMBIO 23 oct: las hace Claude; este texto queda de respaldo)
Hola Codex. Necesito una carpeta de figuras limpias para el video del proyecto, a partir de los CSV de la base v0.1: cobertura de la base, artículos por año y por tipo de portador, micrografías por tipo de microscopía, espectros por técnica y clase, distribución de tamaños, zeta frente a tamaño, el flujo de construcción de la base y la precisión estimada. Deben verse como parte del mismo producto que la web: usa la paleta y tipografía de `producto\web\styles.css` y un color fijo por clase de portador en todas las figuras.

Las instrucciones completas, con el estilo, la validación por figura y los entregables, están en `equipo\briefs_codex\BRIEF_FIGURAS_VIDEO.md`, dentro de `C:\Users\Hector\Desktop\Quimioinformatica Proyecto\nanotech-technique-cooccurrence`. Léelo entero antes de empezar. Cada figura se cierra solo si pasa su validación (los números salen de los CSV y coinciden con los totales oficiales), no uses git, y al terminar dame un reporte corto; Claude lo revisará.


## Ronda 2 (23 oct, tarde): figuras, formulacion, comparacion justa y revision critica
Hola Codex. Tu ronda 1 salio muy bien: la revise, esta subida, y me gusto la prueba de fuga de etiquetas y la honestidad del informe. Ahora la ronda 2, que no necesita el cluster: (A) las figuras del video, (B) una segunda version de los modelos de tamano y clase en la que construyes caracteristicas de formulacion con reglas de texto verificables para ver si explican el tamano, mas dos tareas nuevas (signo del zeta y PDI menor que 0,3), (C) el codigo para comparar de forma justa solo mediciones, solo imagen y ambas sobre los mismos articulos (las imagenes las procesa el cluster; no inventes embeddings) y (D) una revision critica de tu propio trabajo. Las instrucciones, con validaciones y entregables, estan en equipo\briefs_codex\BRIEF_RONDA_2.md dentro de C:\Users\Hector\Desktop\Quimioinformatica Proyecto\nanotech-technique-cooccurrence. Leelo entero antes de empezar. Orden de prioridad A, B, C, D, con un checkpoint al terminar cada letra. Cada paso se cierra solo si pasa su validacion. No uses git y no toques curation, producto\web ni la ronda 1.

