# Flujo de revisión visual de figuras

Objetivo: separar la base en **figuras simples** (una micrografía o un espectro), **parejas**, **compuestas** (3 o más paneles o con contenido no útil) y **espectros con curvas superpuestas**, mirando la imagen, no leyendo cada figura a mano. Cada decisión de la IA se contrasta con la tipología estimada a partir del pie (`../tipologia_figuras/`); solo lo que no coincide va a la cola de revisión humana.

```
preparar_lotes.py      → plan_lotes.csv, lotes/Lxxx.json, miniaturas/ (hojas 3×2, 30 figuras por lote; miniaturas no van a Git)
INSTRUCCIONES_REVISOR  → reglas para Claude/Codex (campos, conteo de paneles, casos frecuentes)
siguiente_lote.py      → lotes pendientes de un revisor (reanudable)
resultados/<revisor>/  → Lxxx.jsonl (un archivo por lote; cada revisor escribe solo en su carpeta)
consolidar.py          → valida, calcula destino visual, acuerdo con el pie y entre revisores; escribe
                         figuras_vision.csv, cola_desacuerdos.csv, bases/{simple,pareja,compuesta,superpuesto,excluir}.csv, PROGRESO.md
```

Reparto: 103 lotes (3.061 figuras con imagen local; prioridad 1 = imágenes del modelo de clase v0.1, prioridad 2 = resto útil). 52 Claude, 39 Codex, 12 «ambos» (control de acuerdo entre modelos).

Reanudar tras un corte: `python modelos/flujo_figuras/siguiente_lote.py claude` (o `codex`) y seguir; `python modelos/flujo_figuras/consolidar.py` en cualquier momento.
Piloto: L001 (30 figuras) hecho por Claude; resultado en `resultados/claude/L001.jsonl`.
