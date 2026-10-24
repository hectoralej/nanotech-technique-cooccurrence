# Instrucciones: pasada de contenido biológico (lotes B)

**Objetivo.** Las 2.066 figuras que alimentan hoy el modelo de clase (prioridad 1) se clasificaron antes de la regla de contenido del 25-oct. Hay que saber, por figura, si contienen **imágenes de bacterias, células, orgánulos o tejido, o nanopartículas dentro/sobre células**, porque esas imágenes no deben entrar al entrenamiento de morfología de partículas (opción C: la técnica TEM/SEM se conserva, el contenido decide si es apta).

Reglas de siempre: solo la imagen (no el pie), sin git, solo escribes en `resultados\codex\`, no mires `resultados\claude\`, no inventes; si la hoja no deja ver, baja la confianza.

## Pasos
1. `python modelos\flujo_figuras\siguiente_lote.py codex 5` → lotes **B001, B002…** (69 lotes de 30 figuras; hojas de contacto 3×2 como en los lotes L; mismo número rojo por figura).
2. Abre `lotes\Bxxx.json`, mira cada hoja `miniaturas\Bxxx_hN.jpg` y escribe `resultados\codex\Bxxx.jsonl`: **una línea JSON por figura**, orden del lote:
```
{"n": 1, "n_bio": 0, "contenido": "particulas", "confianza": 3, "nota": ""}
```
- `n_bio`: nº de paneles de la figura que muestran **bacterias, células, orgánulos o tejido** (microscopía electrónica, óptica, de fluorescencia, confocal o histología), o **nanopartículas dentro/sobre células**. 0 si no hay.
- `contenido` (una sola etiqueta por figura): `"particulas"` (todo son partículas, materiales o formulaciones), `"biologico"` (solo bacterias/células/tejido), `"particulas_en_contexto_biologico"` (nanopartículas en células o tejido), `"mixto"` (hay paneles de partículas y paneles biológicos), `"indeterminado"`.
- `confianza`: 3 seguro, 2 probable, 1 dudoso. `nota`: ≤ 12 palabras, solo si ayuda (p. ej. «TEM de E. coli en C-D»).
3. Guarda cada lote al terminarlo (checkpoint). Cada 5 lotes valida que el archivo tiene una línea por figura y `n` en orden.

## Criterios
- **Vesículas, liposomas, exosomas, micelas** son nanoportadores: cuentan como `particulas`, no como biológico. Sí es biológico: bacterias enteras, células, núcleos, mitocondrias, cortes de tejido, histología (H&E), inmunofluorescencia, hongos.
- Una célula con nanopartículas visibles dentro o pegadas → `particulas_en_contexto_biologico`.
- Fotos de animales, placas de cultivo o frascos no cuentan como `n_bio` (no son micrografías); ignóralas.
- No clasifiques el tipo de panel ni cuentes paneles: solo el contenido biológico.

## Entrega
Tandas de 10 lotes; responde solo: lotes terminados, nº de figuras con `contenido` distinto de `particulas` y problemas. Prioridad: estos B van **antes** que los L y los de cajas que te queden.
