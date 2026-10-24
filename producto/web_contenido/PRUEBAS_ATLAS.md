# Pruebas del Atlas (para Carlos) · viernes 23 de octubre

Probado en el navegador integrado (Chromium), sirviendo `producto/` con `python -m http.server 8000` y abriendo `http://localhost:8000/web/`. **No se tocó ningún archivo de `producto/web/`.** Esto es una prueba rápida de humo, no la revisión completa en Chrome con capturas que pide `producto/web/PROGRESO.md`.

## Lo que está bien
- Portada: 1 707 artículos · 2 726 micrografías · 3 116 filas de descriptores · 4 015 espectros (coinciden con la base v0.1).
- Consola sin errores ni advertencias al cargar la portada, aplicar filtros y abrir una ficha.
- Filtro de portador: 13 opciones con conteos; suma 1.707. Orden y etiquetas como pide `CORRECCIONES_ATLAS_CARLOS.md`.
- Ficha de «Nanovesicles and Human Skin Interaction…» (PMC12196110): las 6 imágenes cargan; muestra clase de la base, **predicción del modelo con 5 micrografías parecidas** (de otros artículos), descriptores con «Ver cita» y espectros.
- El panel «Predicción y evaluación» ya usa los JSON con `prueba: false` (2.100 imágenes, 1.641 artículos).

## Hallazgos, de más a menos importante

### 1. La matriz de confusión sale como JSON crudo (importante para el video)
**Dónde:** sección «Predicción y evaluación» → «Matriz de confusión».
**Qué se ve:** una lista vertical de corchetes y números (`[ [ 93, 13, 230, 35 ], …`), sin nombres de clase.
**Qué sugerimos:** una tabla 4×4 con las clases en filas y columnas, en el orden de `metricas.json` → `clases` (inorgánico, lipídico, nanomaterial, polimérico), con el porcentaje por fila y sombreado. Es lo que se va a ver en pantalla durante el minuto del modelo.

### 2. La «Línea base» compara una métrica distinta
**Qué se ve:** Exactitud 52,62 % · F1 macro 44,2 % · Línea base 45,38 %.
**Problema:** 45,38 % es la exactitud de la clase mayoritaria; al lado del F1 parece que el modelo apenas supera a la línea base. La línea base del F1 macro es ≈ 0,16. **Sugerencia:** dos líneas base, «Línea base (exactitud) 45,4 %» y «Línea base (F1 macro) ≈ 16 %», o mostrar solo el F1 con su línea base.

### 3. Cifra de F1: resuelto
Había dos cifras (0,442 en `metricas.json` y ≈ 0,47 en el análisis rápido). Héctor aclaró (23 oct) que son la misma entrada con reglas de decisión distintas: **la cifra del video es la del Atlas, 0,44** (0,442 [0,416–0,467]); el 0,475 es una variante exploratoria. El Atlas, el guion y la presentación ya coinciden. Si el ajuste fino cambia la cifra (Héctor, sábado 3 pm), hay que cambiarla también en `producto/modelo/metricas.json`.

### 4. «Confianza» y «similitud» en porcentaje
- «Predicción del modelo: lipidico (69,5 %)»: es la confianza del clasificador y **no está calibrada** (`modelos/REVISION_CRITICA.md`, punto 8). Sugerencia: rotularla «confianza del modelo (no calibrada)».
- «Similitud: 81,5 %»: es similitud coseno entre vectores, no un porcentaje de parecido visual. Sugerencia: «similitud coseno 0,82».

### 5. Etiquetas internas visibles (cosmético)
En la ficha: «Clase del artículo (base de datos): **lipidico**» (sin acento y en código interno), «Barra: **True**», «**Fold: 2**», «**not_declared**» en medio, «**No reportado**» en zeta. Sugerencia: «Lipídico», «Barra de escala: sí», ocultar «Fold» y mostrar «no declarado».

### 6. Separador de miles
El Atlas escribe «1 707» (con espacio) y las figuras y los textos del equipo escriben «1.707». Conviene unificar antes de grabar.

### 7. Conteos del guion de la demo
Con **Liposoma + cryoTEM** hoy salen **15** artículos (la revisión del 22 de octubre decía 16). Si la narración dice una cifra, hay que verificarla en el momento de grabar.

## Pendiente de probar
Vista móvil de 375 px, ficha sin imagen (una de las 44), ficha con muchos descriptores, botón «Copiar cita/DOI», filtro XRD + nanomaterial, y dos ensayos cronometrados de la demo (2:00–3:00). Si Carlos corrige algo, avísenme y repito la prueba con captura.
