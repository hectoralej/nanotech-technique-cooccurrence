# Carlos y su Codex: qué sigue en el Atlas (jueves 22 de octubre)

Continúa `equipo/AJUSTE_2_CODEX_CARLOS.md`. Está muy bien hecho: datos regenerados desde la v0.1, checksums coincidentes, conteos por lector CSV, 2.149 imágenes integradas y contrastadas con `descargas.csv`, etiquetas del modelo separadas de las predicciones. Este documento corrige **una cosa** y fija los pasos siguientes, **cada uno con su porqué**.

## 1. Corrección obligatoria: quitar las dos fichas «excepción» (1.709 → 1.707)
**Qué:** el Atlas debe listar **solo los artículos E1 y E2: 1.707**. Quita PMC10239954 y PMC10535558.

**Por qué:**
- Héctor y Claude **no aprobaron** incluirlas; el informe dice «aprobadas», pero esa aprobación no existe. Si fue una decisión de Carlos, debe revertirse.
- Son justo los dos artículos de virus (un virus oncolítico encapsulado y un virus de planta usado como andamio). La regla del proyecto excluye el virus como portador, y la base ya los dejó fuera por eso (`tier = no`).
- Aunque se incluyeran, no tienen ni micrografías, ni descriptores ni espectros: serían fichas vacías que restan credibilidad en la demo.
- La portada debe decir lo mismo que `curation/v0.1/RESUMEN_NUMEROS.json`: 1.707 artículos con evidencia, 2.726 micrografías, 3.116 descriptores, 4.015 espectros.

## 2. Los diez títulos provisionales: falta un paso de verificación
**Qué:** el informe dice «según tu revisión, ninguno usa un virus como portador». Esa revisión fue de Claude sobre **otra lista** (22 títulos que mencionan virus en la base), no sobre la lista de 10 de Carlos. Hay que contrastarlas.

**Qué hacer:** copia `producto/web/data/EXCLUIDOS_POR_TITULO_PROVISIONAL.csv` dentro del zip que envíes a Héctor (sección 5). Claude revisará los 10 contra la regla («virus/AAV/fago/cápside como vector»). Mientras tanto se quedan en el Atlas.

**Por qué:** la regla del proyecto es sobre el portador, no sobre la palabra «virus» en el título (muchas son nanopartículas de plata o quitosano que actúan contra virus, y eso sí es válido). Mejor comprobarlo que suponerlo.

## 3. Revisión visual: es lo más importante que falta
**Qué:** el navegador integrado de Codex no conecta al servidor local. No lo intentes más ahí. **Carlos abre el sitio en su propio Chrome:**
```
cd producto
python -m http.server 8000
```
y abre `http://localhost:8000/web/`. Lista de comprobación (Carlos va diciendo qué ve; Codex corrige):
1. Portada: cifras = 1.707 / 2.726 / 3.116 / 4.015, sin errores.
2. Consola (F12 → Console): **0 errores en rojo**. Si hay alguno, copia el texto exacto a Codex.
3. Explorador: probar cada filtro (familia, tier, uso, microscopía, técnica) y la búsqueda; el número de resultados cambia y no queda vacío sin razón.
4. Tres fichas: una con imagen, una de las 44 sin imagen (marcador y enlace al DOI funcionan) y una con muchos descriptores (la cita se despliega).
5. Móvil: F12 → icono de dispositivo → iPhone/Android; nada se sale de la pantalla y se puede leer.
6. Velocidad: las imágenes cargan al desplazar (sin bajarlas todas de golpe) y no se traba con 1.707 fichas.

**Por qué:** hasta ahora solo hay comprobaciones de código y de datos. El jurado y el video ven **la pantalla**; un error visible (imagen rota, consola roja, texto desbordado) pesa más que cualquier verificación interna.

## 4. Panel del modelo: déjalo listo para el sábado
**Qué:** Bryan entrega el sábado antes del mediodía tres archivos con el formato de `INSTRUCCIONES_CODEX_CARLOS.md` (sección 3). Deja el código preparado para que, **al soltarlos en `producto/modelo/`**, aparezcan:
- una insignia nueva «Predicción del modelo: clase (confianza %)» **junto a**, pero claramente distinta de, «Clase del artículo (base de datos)»;
- cinco micrografías parecidas en la ficha;
- una página o sección «Modelo» con las métricas (exactitud, F1, línea base, matriz de confusión) y el texto «evaluado por artículo, sin mezclar figuras de un mismo artículo entre entrenamiento y prueba».
Si los archivos no existen, ese panel no se muestra (como ahora). Probar con un archivo de prueba **solo en tu computadora y sin subirlo**.

**Por qué:** el jurado va a querer ver que el modelo funciona dentro del producto. Y separar «lo que dice la base» de «lo que predice el modelo» es la honestidad que hace creíble toda la demo.

## 5. Entrega a Héctor (esta noche, antes de dormir)
**Qué:** un zip con `producto/web/` (sin `.build_input/` ni imágenes), `equipo/qc_carlos/` y la lista de los 10 títulos, más **una captura de pantalla** de la portada y de una ficha.

**Por qué:** Carlos no tiene permiso de escritura en GitHub; el zip es la forma de que Héctor y Claude revisen y suban su trabajo. Sin esto, todo vive solo en su computadora.

## 6. Video: Carlos y Bryan llevan el peso
**Qué:** esta semana Carlos debe preparar su parte del video:
1. Escribir el **guion de la demo de 2–3 minutos** (`producto/web/GUION_DEMO.md`): qué se abre, qué se dice y cuánto dura cada paso. Guion sugerido en `INSTRUCCIONES_CODEX_CARLOS.md` (sección 5).
2. **Ensayar la demo dos veces** con cronómetro y ajustar la web para que el recorrido sea fluido (filtro «liposoma» + «cryo-TEM» → ficha → cita desplegable → panel del modelo → «Cómo se construyó»).
3. **El sábado a las 5 pm la web se congela** y se graba la demo en 1920×1080.

**Por qué:** el video dura 10 minutos y el producto es 2–3. Es donde el jurado decide si la solución promete. Héctor ya llevó la parte técnica; el video lo hacen Carlos y Bryan.

## Calendario
- **Hoy (jueves):** puntos 1–3 y entrega del punto 5.
- **Viernes:** móvil y velocidad bien; preparar el panel del modelo; guion de la demo.
- **Sábado:** JSON de Bryan al mediodía, integrarlos y verificar; **congelar a las 5 pm**; grabar.

Cada paso se da por cerrado solo cuando pasa su comprobación.
