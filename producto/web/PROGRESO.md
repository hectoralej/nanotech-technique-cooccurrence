# Progreso del Atlas Nano2Predict

**24 de octubre de 2026 · correcciones del Atlas aplicadas en el código local**

## Datos y alcance

El Atlas muestra exclusivamente los 1.707 artículos E1/E2: **1.707 artículos, 2.726 paneles/micrografías, 3.116 descriptores y 4.015 espectros**. Los 117 artículos `tier=no`, incluidos PMC10239954 y PMC10535558, permanecen fuera porque no aportan evidencia a esas tablas. Se quitó el filtro por palabras del título.

Los diez títulos que marcaba el filtro anterior se conservan en `data/EXCLUIDOS_POR_TITULO_PROVISIONAL.csv`, sin usarlos para excluir por palabras. Según la revisión de Claude comunicada el 22/10, ocho casos válidos permanecen en el Atlas; PMC10239954 y PMC10535558 son `tier=no` y quedan fuera.

## Correcciones incorporadas

- `build_data.py` decodifica entidades HTML repetidas y limpia etiquetas de títulos, muestras y citas. La cursiva se representa como texto entre asteriscos; la interfaz sigue usando `textContent`.
- El filtro de portador usa solo `carrier_type`, muestra etiquetas en español y el conteo de cada opción en el orden acordado. Los conteos suman 1.707.
- El constructor cruza `paneles.csv` con `producto/imagenes/descargas.csv` y añade `imagen_local`. Cuando es falso, la ficha muestra el marcador y DOI sin solicitar el recurso faltante.
- Las fichas muestran hasta cinco micrografías inicialmente y un botón para ver el resto; incluyen «Copiar cita/DOI».
- La franja fija tiene más espacio reservado al final de la página.
- El panel «Modelo» muestra predicciones y hasta cinco micrografías similares por imagen, métricas y matriz cuando están disponibles. Si los archivos llevan `prueba: true`, aparece un aviso visible de datos de prueba.

Conteos del filtro por portador: Liposoma 119; LNP 19; SLN 69; NLC 63; PLN 15; Micela 22; Nanogel 48; Nanoemulsión 2; Cubosoma 3; Polimérica 311; Inorgánica 269; Nanomaterial 733; Otro 34. **Suma: 1.707.**

## Imágenes

Se integraron localmente 2.149 JPG. Las 44 figuras faltantes de 30 PMCID tienen motivo `no esta en el zip`. Todas se enlazan a una ficha con DOI. Los JPG siguen fuera de Git. El indicador `imagen_local` permite que la interfaz evite pedir las 44 faltantes.

## Panel del modelo

En `producto/modelo/` solo están los tres JSON de prueba, marcados `prueba: true`; no son resultados de Bryan y no se incluyen en el ZIP de entrega. El sitio local los rotula como datos de prueba. La matriz de confusión no aparece en ese fixture y se muestra como «No reportada». Al recibir los archivos finales, sustituir los de prueba, ejecutar `python web/build_data.py` desde `producto/` para actualizar disponibilidad y JSON, y revisar la matriz y los campos antes de grabar.

## Verificaciones

- Los JSON generados mantienen los conteos oficiales.
- Después de la limpieza, `articulos.json` tiene cero títulos con `<`, `&lt;` o `&amp;`.
- Los 2.726 paneles tienen `imagen_local`: 2.669 registros de panel apuntan a imágenes descargadas y 57 registros apuntan a archivos no disponibles (44 archivos únicos ausentes, algunos repetidos en más de un registro).
- El filtro de portador cubre los 1.707 artículos y suma 1.707.
- `node --check producto/web/app.js` y `python -m py_compile producto/web/build_data.py` pasan.
- Las correcciones nuevas aún necesitan revisión visual en Chrome y consola; la prueba visual descrita por Claude corresponde al paquete anterior a estos cambios.

## Cómo abrir

Desde `producto/`, para que la web y las imágenes compartan raíz:

```powershell
python -m http.server 8000
```

Abre `http://localhost:8000/web/`. Comprueba portada, consola, filtros, una ficha con imagen, una ficha con imagen ausente, una ficha con muchos descriptores y vista móvil de 375 px.

## Pendiente

1. Revisar visualmente en Chrome los cambios y tomar capturas de portada, ficha con imagen y ficha sin imagen.
2. El ZIP preliminar `entrega/Atlas_para_Hector_2026-10-24_sin_capturas.zip` ya contiene la web, QC, lista y Markdown de traspaso; excluye `.build_input`, `producto/modelo/` de prueba y `producto/imagenes/`. Falta añadirle tres capturas de Chrome para cerrar la entrega.
3. Recibir los JSON reales de Bryan; comprobar esquema, predicciones, cinco vecinos y matriz de confusión. No presentar el fixture de prueba como resultado.
4. Ensayar dos veces la demo con cronómetro. Congelar la web antes de grabar y actualizar este registro con los resultados de Chrome.

La revisión QC de Carlos es asistida por IA, no una revisión humana. No se hizo commit ni push.
