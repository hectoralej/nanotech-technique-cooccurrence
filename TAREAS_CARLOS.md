# Carlos: qué tienes que hacer

**Para ti y para tu Codex.** Este archivo se entiende solo. Lee todo antes de empezar.

## El proyecto en cinco líneas
Estamos armando una base de datos abierta que empareja micrografías (TEM, SEM, cryo) con la formulación y las mediciones de tamaño (DLS) y potencial zeta de la misma muestra, para nanoportadores (liposomas, LNP, SLN/NLC, PLN, poliméricas e inorgánicas). Los datos salen de artículos de acceso abierto, con citas textuales verificadas. Hoy hay **85 artículos**; **66 tienen licencia CC BY** (verde). Todo es provisional hasta que personas lo verifiquen, y esa es tu parte.

**Plazo duro del hackatón: domingo 25 de octubre, 5:45 pm (hora de Costa Rica).** Los datos se congelan el **22 de octubre**; por eso tu tarea 1 es la urgente.

## Dónde está todo
Repositorio (privado, puedes leerlo): https://github.com/hectoralej/nanotech-technique-cooccurrence

Los archivos que usarás están en la carpeta `curation/`:
- `verificacion_repositorio_verde.csv`: tu tarea 1 (66 artículos).
- `verificacion_humana_80.csv` y `GUIA_REVISION.md`: tu tarea 2.
- `articles_curated.csv` y `measurements.csv`: los datos completos, solo para consultar.

No tienes acceso de escritura a GitHub, y no hace falta. **Cómo entregar:** guarda tu archivo completado con tu nombre (por ejemplo `verificacion_repositorio_verde_carlos.csv`) y envíaselo a Héctor por el chat del equipo. Él o Bryan lo suben al repositorio.

## Tarea 1 (urgente, para el 22 de octubre): verificar el repositorio verde
**Archivo:** `curation/verificacion_repositorio_verde.csv`. Una fila por artículo (66). Cada fila trae el enlace al artículo y lo que el modelo extrajo de **una** muestra: tamaño, zeta, medio y variante de micrografía, con la figura o tabla donde buscarlo.

Por cada fila:
1. Abre el enlace de `doi_link` (es `https://doi.org/...`). Si falla, copia el DOI en el navegador.
2. Llena estas columnas:

| Columna | Qué poner |
|---|---|
| `licencia_en_pagina_del_editor` | La licencia que dice la **página del editor** (por ejemplo `CC BY`, `CC BY-NC`, `no la encuentro`) |
| `aviso_editorial` | `ninguno`, `errata`, `retractado` o `expresion_de_preocupacion`. Busca avisos en la página del artículo |
| `tamano_correcto` | `si` / `no`: ¿el tamaño en nm de `muestra_a_verificar` coincide con el artículo? |
| `zeta_correcto` | `si` / `no`: ¿el zeta en mV coincide? |
| `medio_correcto` | `si` / `no`: ¿el medio (agua, PBS, tampón…) es el correcto para esa medición? |
| `micrografia_es_de_esa_muestra` | `si` / `no`: ¿la micrografía mostrada corresponde a esa misma muestra? |
| `notas` | Lo que veas raro |

Regla: **si dudas, escribe `no` y explica en `notas`.** No cambies las otras columnas.

Tiempo estimado: de 3 a 4 minutos por artículo, unas 4 horas en total [estimación].

## Tarea 2 (si te sobra tiempo, hasta el 24 de octubre): revisión independiente
**Archivo:** `curation/verificacion_humana_80.csv`. Revisa los artículos con `n` del **1 al 39**. Haz tu propia copia (`verificacion_humana_80_carlos.csv`) y llena solo las columnas vacías, siguiendo `GUIA_REVISION.md`.

Aquí **no** estás verificando lo que dijo el modelo: lo juzgas tú desde cero. Por eso:
- No abras `clave_modelo.csv` ni ninguna carpeta de revisión por IA. No están en el repositorio y no las pidas.
- Tu Codex puede ayudarte a abrir artículos y encontrar tablas, pero **la respuesta `si` o `no` la decides tú**.
- No comentes tus respuestas con nadie hasta entregar el archivo.
- El **n49 está retractado**: sáltalo y escribe `retractado` en `notas`.

## Tarea 3 (después del hackatón): doble anotación del detector
`GOLD_GUIDELINES.md` y `data/gold_set_human_template.csv`. No es urgente.

## Reglas
- Los artículos con licencia distinta de CC BY o CC0 no se usan para imágenes. No descargues figuras por tu cuenta.
- No tomes decisiones por AAV ni por virus: están fuera del proyecto.
- Si algo del archivo no se entiende, pregúntale a Héctor antes de adivinar.
