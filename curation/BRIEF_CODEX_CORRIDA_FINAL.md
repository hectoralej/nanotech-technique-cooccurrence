# Codex: corrida final de esta noche (lotes EX017 a EX036)

Este archivo se suma a `curation\BRIEF_LUNA_REVISION_AMPLIADA.md` y `curation\prompts\extended_schema.md`, que siguen vigentes. Si algo choca, manda este archivo para **qué lotes tocar**, y el esquema para **cómo extraer**.

## 1. Tu parte esta noche
**Procesa los lotes `EX017` a `EX036`, ambos incluidos: 20 lotes, 200 artículos.** Es el doble de la corrida anterior (6 lotes más el repaso de 37 artículos, unos 100 en total). Son todos E1 (micrografía, descriptor y espectro en figura).

- Los lotes están en `RAIZ\curation\work\ext\batches\EX###.json` y sus paquetes en `RAIZ\curation\work\ext\packets\`. `RAIZ` = `C:\Users\Hector\Desktop\Quimioinformatica Proyecto\nanotech-technique-cooccurrence`.
- Escribe cada salida en la ruta `output` del lote, dentro de `RAIZ\curation\work\llm\E\`.
- Ve **en orden**, `EX017` primero. Un lote con salida válida no se repite.
- **Para en `EX036`.** No toques `EX037` ni los siguientes: los reparte otro extractor para que nadie repita trabajo.

## 2. Reparto de lotes (para que nadie repita)
| Rango | Quién | Cuándo |
|---|---|---|
| EX001–EX016 | Codex (hecho y verificado) | listo |
| **EX017–EX036** | **Codex** | **esta noche** |
| EX052–EX054 | Claude (agentes Haiku, tanda corta) | esta noche, si Héctor aprueba |
| EX037–EX051 | Claude | mañana, con el uso reiniciado |
| EX068–EX140 (E1 nuevos) | Codex primero, luego Claude lo que quede | mañana |
| EX055–EX067 (E2) | Claude | mañana, al final |

No existe otro lote que debas crear: **no corras `screen` ni `packets`** en esta corrida. Ya los corrió Claude y asignó los lotes hasta `EX140`. Si los corres tú, se pueden pisar los números.

## 3. Lo aprendido en la corrida anterior (aplícalo)
1. **Nanopartículas que no son de entrega** (síntesis verde, biogénica, antimicrobianas, comerciales): se extraen igual con `carrier_type: "nanomaterial"` y `nanocarrier_is_object_of_study: true`. Lignina = `polymeric_NP`. `not_a_nanocarrier` solo para reseñas o artículos sin nanopartícula propia.
2. **`scale_bar_in_caption`:** `true` o `null`, nunca `false`.
3. **Citas de descriptores:** el verificador comprueba que cada cita esté en el artículo, y además que los números extraídos aparezcan en el texto. Para que sea fácil, **copia la parte de la fila que contiene los números que extraes** (tamaño, PDI y zeta), en vez de cortar la fila al llegar a 25 palabras. Si no caben todos, extrae solo los que sí caben en la cita.
4. **Citas cortas de subfigura** («XRD (B)», «EDX spectrum»): ahora se aceptan solo si aparecen **tal cual** en el artículo. No las parafrasees ni las completes.
5. **Citas parafraseadas:** fueron las únicas rechazadas. Copia literal, con los símbolos originales (−, ±, µ).
6. Si un paquete no trae nada útil, devuelve el registro con `context` y listas vacías. No omitas artículos.

## 4. Qué entregas al terminar
- `EX017.json` a `EX036.json` en `work\llm\E\`, uno por lote, con un registro por artículo en el orden del lote.
- Una línea por lote en `work\ext\luna_progress.md` con la hora, el lote y los problemas.
- **Un reporte final** corto con: lotes procesados (debe decir 20), artículos de cada tipo de portador (`nanomaterial` frente a portadores de entrega), casos raros, y lo que **no verificaste**.
- Si te cortan por límite de uso, deja anotado hasta qué lote llegaste. No marques un lote como hecho si su archivo no es un JSON válido.

## 5. Lo que no debes hacer
- No toques lotes fuera de `EX017`–`EX036`.
- No corras `screen`, `packets`, `fetch` ni `apply`. Esta noche solo extraes.
- No modifiques `rank.csv`, `screen.csv`, el código ni los archivos del repositorio.
- No abras `clave_modelo.csv` ni `qc_codex\`. No hagas push a GitHub.
- No inventes: sin cita textual no hay fila.
