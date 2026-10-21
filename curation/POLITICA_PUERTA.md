# Política de la puerta (vigente desde el 2026-10-20)

La puerta sigue exigiendo: micrografía útil, DLS útil y zeta útil **de una misma muestra**, con el medio declarado. Se agregan dos reglas para recuperar artículos que se descartaban por falsos negativos. Las adoptó Claude como valor por defecto para no frenar el trabajo. **Héctor puede cambiarlas** y, si lo hace, se rehace el rescate.

## Regla 1: medio declarado en otra parte de Métodos
Se acepta si el mismo instrumento y la misma medición tienen el medio indicado en cualquier sección de Métodos (por ejemplo, «las muestras se diluyeron 1:100 en agua» en otro párrafo). Se exige una **cita textual** que el código encuentre en el artículo. La fila queda con la bandera `medio_rescatado`.

## Regla 2: valores leídos de una figura
Se aceptan **solo como aproximados**, con la bandera `valor_de_figura`. No se les asigna desviación estándar. Para el hackatón no entran en el modelo de tamaño; sí pueden servir para imágenes y para describir la base.

## Lo que no cambia
- NTA y difracción láser no sustituyen a DLS.
- Los datos que están solo en el suplemento no cumplen la puerta.
- Un artículo retractado nunca entra.
- Las imágenes solo salen de artículos CC BY o CC0. Cuando el editor y las otras fuentes discrepan, manda la página del editor.
