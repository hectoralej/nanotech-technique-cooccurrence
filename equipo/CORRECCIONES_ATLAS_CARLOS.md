# Atlas: revisión de Héctor/Claude y correcciones (22 de octubre)

Claude abrió el zip de Carlos, lo sirvió en un navegador real (con las 2.149 imágenes enlazadas) y lo probó. **Resultado: el Atlas funciona y se ve bien.** Lo que sigue son las correcciones, en orden de prioridad, **con su porqué**. Aplícalas en `producto/web/` y valida cada una antes de cerrarla.

## Lo que ya está bien (no tocar)
- Portada: 1.707 / 2.726 / 3.116 / 4.015, igual que la base; consola sin errores propios del sitio.
- Fichas: las imágenes cargan; las 44 sin imagen muestran el marcador con el enlace al DOI y el nombre del archivo.
- Filtros: «liposome» → 139 artículos; + «cryoTEM» → 16; + «XRD» → 3 (los números cambian de forma coherente).
- Móvil (375 px): sin desbordes horizontales; se lee bien.
- Las etiquetas «Clase del artículo (base de datos)» están separadas de cualquier predicción. El aviso «Datos extraídos por IA y verificados por código» está visible.

## Correcciones

### 1. Títulos con etiquetas HTML visibles (364 de 1.707, el 21 %)
**Qué:** muchos títulos muestran texto como `<i>Naja naja</i>`, `&lt;i&gt;Senna italica&lt;/i&gt;` o `&amp;`. **Cómo:** en `build_data.py`, al generar `articulos.json`, decodifica las entidades (`html.unescape`, también para `&lt;i&gt;` doble escapado), y conserva solo cursiva: convierte `<i>…</i>` en un marcador (por ejemplo `*…*`) o elimina las etiquetas, y que la web nunca inserte HTML crudo (usar `textContent`, no `innerHTML`). Aplica lo mismo a cualquier otro campo de texto (muestras, citas). **Por qué:** es lo primero que ve el jurado en la lista y se nota como un error aunque los datos estén bien. **Validación:** 0 títulos con `<`, `&lt;` o `&amp;` en `articulos.json`.

### 2. Filtro «Familia / portador» confuso
**Qué:** la lista mezcla dos columnas y muestra códigos internos duplicados: `inorganic | inorganic_NP | polymeric | polymeric_NP | SLN | SLN_NLC | nanomaterial | other…`. **Cómo:** usa **solo `carrier_type`** y etiquetas legibles en español, en este orden: Liposoma, LNP (nanopartícula lipídica), SLN, NLC, PLN, Micela, Nanogel, Nanoemulsión, Cubosoma, Polimérica, Inorgánica, Nanomaterial, Otro. Cada opción con su conteo entre paréntesis. **Por qué:** es el filtro principal de la demo («liposoma + cryo-TEM»); con códigos duplicados parece que la base está desordenada y el filtro engaña (inorganic ≠ inorganic_NP en pantalla). **Validación:** ninguna opción se repite y la suma de conteos = 1.707.

### 3. Consola en rojo por las 44 imágenes que faltan
**Qué:** al abrir una ficha sin imagen, el navegador intenta cargarla y registra un `404` en rojo. **Cómo:** al generar `paneles.json`, marca cada panel con `imagen_local: true/false` leyendo `producto/imagenes/descargas.csv` (`ok=1`); si es `false`, ni siquiera se pide el archivo. **Por qué:** durante la grabación del video Carlos abrirá la consola y no debe haber rojo; además evita descargas inútiles. **Validación:** recorrer 30 fichas con la consola abierta sin 404.

### 4. Los diez títulos de virus: veredicto
Claude los revisó con la regla «virus/AAV/fago/cápside como vector o portador». **Ninguno de los 8 que están en el Atlas usa un virus como portador:** son nanopartículas de plata/quitosano contra virus o contra plantas, LNP adyuvantes, un virus oncolítico administrado junto con nanopartículas PLGA (el portador es el PLGA), una vacuna de ADN en quitosano y nanopartículas «tipo virus» sintéticas. Los dos `tier = no` (PMC10239954: virus oncolítico dentro de quitosano como carga; PMC10535558: virus de planta como andamio) **siguen fuera**, con razón. **Acción:** deja los 8 en el Atlas y en `PROGRESO.md` cambia «pendiente de contraste» por «revisado el 22/10: se mantienen 8; los 2 `tier=no` quedan fuera».

### 5. Detalles menores (si queda tiempo)
- La franja fija «Datos extraídos por IA…» tapa los últimos píxeles de la pantalla; hazla colapsable o súbele un margen inferior.
- Muestra 5 micrografías por ficha y un botón «ver todas» en los artículos con muchas figuras, para que la ficha cargue rápido.
- Añade a cada ficha el botón «Copiar cita/DOI».

## Siguiente (misma agenda)
1. **Hoy:** correcciones 1–4 y un zip nuevo de `producto/web/` a Héctor, con **capturas de pantalla** de la portada, de una ficha con imagen y de otra sin imagen.
2. **Viernes:** correcciones 5, panel del modelo listo (insignia «Predicción del modelo» separada de la clase de la base) y guion de la demo de 2–3 minutos con dos ensayos cronometrados.
3. **Sábado:** JSON de Bryan al mediodía, integración y verificación; **congelar a las 5 pm** y grabar.
