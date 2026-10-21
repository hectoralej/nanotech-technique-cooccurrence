# Bryan: qué tienes que hacer

**Para ti y tu sesión de Claude (con acceso a GitHub).** Este archivo se entiende solo.

## El proyecto en cinco líneas
Base de datos abierta que empareja micrografías (TEM, SEM, cryo) con la formulación y las mediciones de tamaño (DLS) y potencial zeta de la misma muestra, para nanoportadores. Hoy hay **85 artículos** (66 CC BY, 19 NC/ND), con citas textuales verificadas por código. Las imágenes aún no están extraídas. Encima irá un modelo y una herramienta para el hackatón.

**Plazo duro: domingo 25 de octubre, 5:45 pm (hora de Costa Rica).** Los datos se congelan el **22 de octubre**. Tu tarea 1 es la que decide si hay imágenes para los modelos.

## Cómo trabajamos en GitHub
Repositorio: https://github.com/hectoralej/nanotech-technique-cooccurrence
- Haz `git pull` primero. Crea tu rama `bryan/…` y trabaja en tu carpeta (`bryan/` o `images/`). **Nada va directo a `main`:** abre un pull request y Héctor lo aprueba.
- **Imágenes solo de artículos con `license_color == "verde"`** (CC BY o CC0). Los valores numéricos se pueden usar de todos.
- No abras `curation/work/clave_modelo.csv` (no está en el repositorio, no la pidas).
- Sin AAV ni virus.

## Tarea 1 (urgente, 21 y 22 de octubre): figuras y paneles
Entrada: `curation/articles_curated.csv` (una fila por artículo) y `curation/measurements.csv` (una fila por medición). Los artículos que te importan son los 66 verdes que tienen filas con `technique == "micrograph"` (171 registros de micrografía en total; cada uno trae `evidence_location`, la figura o tabla de donde sale).

1. **Descargar las figuras** de cada artículo verde desde el paquete Open Access de PMC o la API de Europe PMC. Máximo 3 peticiones por segundo, con reintentos y un `User-Agent` identificable. Guarda en `images/raw/<pmcid>/` y registra pmcid, archivo, URL, licencia y fecha en `images/manifest.csv`.
2. **Herramienta de recorte** (Streamlit o Tkinter): muestra la figura, la cita de evidencia y el `sample_id` esperado, y permite dibujar un recuadro, elegir muestra y variante, o marcar «el panel no corresponde». Guarda los recortes en `images/panels/<pmcid>__<sample_id>__<n>.png` y cada acción en `images/panel_labels.csv` (pmcid, sample_id, archivo, revisor, veredicto, nota). **No borres las barras de escala**: guarda el recorte tal cual.
3. Revisar los paneles. Una buena meta son unos 170 paneles en 2 o 3 horas. Esto cuenta como verificación humana de esas filas.

## Tarea 2 (21 de octubre): esquema v0.1
Redacta `docs/esquema_v0.1.md` con los campos de la base. El plan pide como obligatorios: familia, estado de la muestra (cryo, tinción negativa, seca, SEM), instrumento, carga (molécula pequeña, ARNm, ARNip, proteína), clase de ligando, identidad de la muestra (componente puro, vacía o cargada) y el endpoint cuando aplique. Añade licencia por fila, ID de estudio, cita textual de evidencia, nivel de confianza y confianza del vínculo (explícito, inferido o a nivel de artículo).
Indica qué campos ya existen en `measurements.csv` y cuáles faltan. Claude los implementa después.

## Tarea 3 (21 de octubre): espectros
Decide qué espectros entran en la v0.1 (FTIR, XRD, UV-Vis, SAXS): una lista corta y una frase de por qué. El plan los marca como módulo opcional.

## Tarea 4 (22 de octubre): revisar el rescate
Claude va a releer unos 30 artículos CC BY que tenían micrografía, DLS y zeta, pero el medio sin declarar. Te pasará `curation/rescate_para_bryan.csv` con una fila por artículo. Marca `aceptar` o `rechazar` y una nota. Si el rescate no termina, esta tarea pasa a la v0.2.

## Tarea 5 (después del hackatón): vacíos y semillas
- Palabras de búsqueda para inorgánicas (hoy 3 artículos verdes) y SAXS.
- Listas de DOI de LipoDB, LNP Atlas y PLGA NP, con su licencia verificada. Guarda en `bryan/doi_semilla.csv`.

## Entregas
Pull request a `main` con: `images/` (manifiesto, paneles, etiquetas), `docs/esquema_v0.1.md` y la lista de espectros. Avisa a Héctor cuando esté abierto.
