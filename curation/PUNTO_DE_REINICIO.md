# Punto de reinicio (21 de octubre, mediodía). Lee esto primero.

## Quién es quién
Héctor (dueño, decide), Bryan (usa Claude, descarga figuras y define el esquema), Carlos (usa Codex, verifica a mano; lee GitHub pero no escribe), ChatGPT/Codex «Luna» (extractor con acceso a archivos locales), Claude (orquesta, verifica con código, corre agentes Haiku). Héctor prefiere respuestas en español, concisas, con checkpoints, y que se pida visto bueno antes de gastar mucho.

## Plazo
Hackatón: el video se entrega el **domingo 25 de octubre, 5:45 pm (Costa Rica)**. Congelar la **v0.1 el 22 de octubre**. Repositorio privado: https://github.com/hectoralej/nanotech-technique-cooccurrence (rama `main`, raíz del proyecto en `C:\Users\Hector\Desktop\Quimioinformatica Proyecto\nanotech-technique-cooccurrence`).

## Dos conjuntos (no mezclar)
1. **Repositorio estricto** (`curation/articles_curated.csv`, `measurements.csv`): **87 artículos** (68 CC BY verde, 19 NC/ND). Puerta: micrografía + DLS + zeta con medio, de una misma muestra. Licencia: manda la página del editor; clasificador corregido para «cc by-nc». Retractados excluidos automáticamente. Política en `curation/POLITICA_PUERTA.md`. Hoja de verificación de Carlos: `curation/verificacion_repositorio_verde.csv`.
2. **Conjunto ampliado para imágenes** (nuevo): regla flexible = micrografía + (descriptor nanométrico o espectro FTIR/XRD/UV-Vis/SAXS/EDS/Raman). Categorías E1 (micrografía+descriptor+espectro) y E2. `categoria_uso`: `nanoportador` o `nanomaterial` (síntesis verde, comerciales; lignina = polimérica). Solo CC BY/CC0. Código: `curation/extended.py` (`rank`, `fetch`, `screen`, `packets`, `export`, `apply`). Salidas: `curation/ext_articulos.csv`, `ext_paneles.csv` (con archivo de imagen), `ext_descriptores.csv`, `ext_espectros.csv`.

## Estado del conjunto ampliado
- `python -m curation.extended apply` → **1.824 artículos leídos: E1 932, E2 717, no 175; 2 citas rechazadas**; 2.092 paneles, 2.314 descriptores, 3.005 espectros (21 oct, noche; extracción COMPLETA EX001–EX185).
- Descarga de textos terminada (2.435/2.435). Lotes de 10 artículos: EX001–EX185 (EX001–EX054 y EX068–EX152 y EX153–EX185 son E1; EX055–EX067 son E2). `work/ext/exportados.csv` es la fuente de verdad.
- **Reparto:** Codex hizo EX001–EX036 y está haciendo EX078–EX102 (`BRIEF_CODEX_CORRIDA_3.md`, va por ~50 %); Claude hizo EX037–EX054, EX068–EX077, EX103–EX127 y EX161–EX185 (hecho). Codex: EX078–EX102, EX128–EX160 y ahora EX055–EX067 (E2, `BRIEF_CODEX_CORRIDA_5.md`, hecho). **No queda nada por repartir.** Duda abierta: Codex tardó 17 min en 33 lotes (EX128–EX160) y sacó 0,54 descriptores/artículo frente a 1,65–1,80 de Claude; revisar con muestra a mano (posible lectura superficial).
- Flujo: Haiku (o Codex) lee `work/ext/batches/EX###.json` + `packets/` y escribe `work/llm/E/EX###.json` según `curation/prompts/extended_schema.md`; `apply` verifica citas (aproximadas ≥90; etiquetas cortas solo literales) y que los números existan en el artículo.
- Costo medido: Haiku ≈ 8–9 mil tokens por artículo (≈ 2,3 M tokens para 250 artículos hoy; 5 % del límite semanal). Hacer checkpoints a 20/40/60/80 % y revisar `get_usage` entre tandas.

## Pendiente (en orden)
1. Verificar con `apply` lo que entregue Codex (EX078–EX102) y repartir EX103–EX185 (≈ 83 lotes) y EX055–EX067 sin solapes.
2. **Unir filas partidas** de descriptores (tamaño y zeta de una misma muestra en dos filas, por nombre de muestra) en `apply`.
3. Carlos: `TAREAS_CARLOS_v2.md` (decidir casos dudosos de la hoja verde; verificar 20 artículos del conjunto ampliado en `verificacion_conjunto_ampliado.csv`; lista de 78 si sobra tiempo). Bryan: `TAREAS_BRYAN.md` (descargar figuras y recortar paneles; esquema v0.1).
4. UI simple (idea): HTML de un solo archivo que lea los 4 CSV `ext_*`, con lista y filtros, y por artículo: micrografías (imagen solo si licencia verde y archivo existente), descriptores y espectros; sin inventar datos; aviso «datos provisionales extraídos por IA y verificados solo por código». No está hecha.
5. 22 oct: congelar v0.1 (etiqueta en GitHub). Después: modelos del hackatón (tabular por artículo con GroupKFold; imágenes con backbone congelado, no CNN desde cero; evaluación honesta).

## Reglas que no hay que olvidar
- Imágenes solo de artículos con licencia verde; los valores numéricos se pueden usar de todos, citando la fuente.
- No se comparten `clave_modelo.csv` ni `qc_codex/` (gitignorados) para no romper la independencia de las revisiones humanas.
- Todo modelo se parte **por artículo** (`pmcid`). Sin AAV ni virus.
- Los nombres de los límites de uso: el semanal se reinició el 21 oct (7:00 UTC); el de 5 horas se reinicia a las 21:10 UTC.
- Si el equipo se duerme se detienen las descargas y las sesiones: conectar el cargador y desactivar la suspensión.



