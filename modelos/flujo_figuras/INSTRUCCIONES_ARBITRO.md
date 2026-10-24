# Instrucciones para el árbitro (lotes A)

Tarea: figuras donde la clasificación visual previa y la tipología del pie **no coinciden**. Para cada una, **mira la imagen** y decide el resultado final. Tienes el pie de figura y los dos veredictos previos; úsalos como pistas, pero **manda lo que ves**.

## Pasos
1. `python modelos/flujo_figuras/siguiente_lote.py claude 3` (o lee el lote que se te asigne). Abre `modelos/flujo_figuras/lotes/Axxx.json`: por figura trae `imagen` (ruta relativa al repositorio), `pie`, `imagen_dijo` (paneles, tipos, curvas, destino, nota) y `pie_dijo` (tipología y destino).
2. Mira cada imagen con la herramienta de lectura y cuenta los paneles con **las reglas de `INSTRUCCIONES_REVISOR.md`** (léelo completo antes de empezar: fluorescencia/histología/células y TEM-SEM biológicos → `n_otro`; espectros en cascada = un panel por curva; curvas solapadas = un panel; insets no cuentan).
3. Escribe `modelos/flujo_figuras/resultados/claude/Axxx.jsonl`: **una línea JSON por figura**, en el orden del lote, con los **mismos campos** de `INSTRUCCIONES_REVISOR.md` (`n, paneles, n_micro, n_espectro, n_otro, curvas_superpuestas, espectro_limpio, tecnicas, calidad, confianza, nota`; opcionales `cascada`, `n_bio`) **más** `"veredicto"`: `"imagen"` si la clasificación visual previa tenía razón, `"pie"` si la tenía la tipología del pie, `"ninguno"` si ambas fallaban (explícalo en `nota`, máx. 12 palabras).
4. Guarda cada lote al terminarlo. No leas `resultados/` de otros revisores ni `auditoria/`. Sin git; no modifiques nada más.

## Criterios
- Si el pie dice «(a)…(d)» y la imagen muestra 4 paneles, el pie suele acertar; si la imagen muestra más o menos paneles que las letras, cuenta lo que ves.
- No fuerces: si la imagen es ilegible, `confianza: 1` y di por qué.
- Responde al terminar solo: lotes escritos, nº de veredictos `imagen` / `pie` / `ninguno` y problemas.
