# Codex (Carlos): ajuste y aclaraciones sobre el Atlas

Este archivo corrige y completa `equipo/INSTRUCCIONES_CODEX_CARLOS.md`; en lo que choquen, manda este. Leíste bien lo de fondo (el Atlas se construye con los 4 CSV `ext_*`), pero trabajaste con un repositorio local desactualizado y con malentendidos. Esto es lo que hay que corregir.

## 1. Qué son los 4 CSV (respuesta a tu duda)
Son **la base de datos del proyecto**, producida por el pipeline de Héctor (extracción de artículos con IA, con cada cita y cada número verificados por código). **No son los CSV de revisión de Carlos** (`verificacion_*`, `equipo/qc_carlos/`): esos son otro asunto (control de calidad) y el Atlas solo cita su resumen.

| Archivo | Una fila es |
|---|---|
| `curation/ext_articulos.csv` | un artículo |
| `curation/ext_paneles.csv` | una micrografía |
| `curation/ext_descriptores.csv` | una muestra con tamaño/PDI/zeta |
| `curation/ext_espectros.csv` | un espectro |

Están en GitHub, en `main`, y la versión congelada tiene la etiqueta **`v0.1`**. Cifras oficiales de la v0.1: **1.824 artículos, 2.726 paneles, 3.116 descriptores, 4.015 espectros**.

## 2. Sincroniza el repositorio ANTES de seguir
Tu copia local no trae `equipo/PLAN_EQUIPO_FINAL.md` ni `curation/v0.1/`. Haz `git pull origin main` (o clona de nuevo) y verifica que existan:
- `curation/ext_articulos.csv`, `ext_paneles.csv`, `ext_descriptores.csv`, `ext_espectros.csv`
- `curation/v0.1/` con `LEEME.md` (diccionario de columnas), `RESUMEN_NUMEROS.json` (cifras para la portada), `VALIDACION.md`, `tabla_modelo.csv` (una fila por micrografía)
- `equipo/PLAN_EQUIPO_FINAL.md`

Si no tienes permiso de `git pull`, pídele a Carlos el zip del repo a Héctor. **No trabajes con copias temporales de otra rama o de otra fecha**: los datos del Atlas deben salir de la v0.1.

## 3. Datos: qué cambiar
1. Regenera los JSON con `python producto/web/build_data.py` (lee `curation/` con `utf-8-sig`) sobre los CSV sincronizados.
2. **Cifras de la portada:** toma los números de `curation/v0.1/RESUMEN_NUMEROS.json` o de los JSON generados, y que ambas fuentes coincidan. Tu copia anterior mostraba 1.814/2.712/3.109/3.997: son las cifras de la v0.1 menos las filas de los 10 artículos que excluiste por mencionar AAV/virus. Esa exclusión **se mantiene** (el proyecto no incluye AAV ni virus), pero:
   - Escribe `producto/web/data/EXCLUIDOS_AAV.csv` (`pmcid, titulo, motivo`) con esos 10 artículos para que Héctor los revise.
   - En la portada muestra las cifras **después** de excluirlos y añade la nota en `PROGRESO.md` («v0.1: 1.824 artículos; el atlas muestra N tras excluir 10 por AAV/virus»).
3. **Panel del modelo:** usa `curation/v0.1/tabla_modelo.csv` (2.193 filas, una por `(pmcid, image_file)`) para mostrar, en cada micrografía, su `clase_modelo` (lipidico, polimerico, inorganico, nanomaterial), la `microscopia` y el `fold`. Es la etiqueta real de la base; **no es la predicción del modelo**, que llega de Bryan el sábado en `producto/modelo/predicciones.json`. Mientras no llegue, rotula el panel «Clase del artículo (base de datos)» y no presentes nada como predicción.
4. No uses ni borres `producto/web/.build_input/`: queda fuera de Git y la interfaz no lo carga. Borra su contenido a mano cuando puedas.

## 4. Imágenes
Héctor ya descargó **2.149 de las 2.193 figuras** (98 %). **Faltan 44** (30 artículos) que no venían en el paquete de Europe PMC; esas fichas mantienen el marcador con el enlace al DOI.
- Las imágenes **no van a Git**. Héctor las pasa en un zip; se descomprimen en `producto/imagenes/<pmcid>/<image_file>` (la tabla `tabla_modelo.csv` ya trae esa ruta en `ruta_imagen`).
- El registro de descargas está en `producto/imagenes/descargas.csv`.
- Cada imagen se muestra con su crédito: DOI del artículo y la leyenda «Imagen de un artículo de acceso abierto; ver licencia en el enlace».

## 5. Reglas que no cambian
- No modificar `curation/` (es de Héctor). Tu carpeta es `producto/web/` y `equipo/qc_carlos/`.
- No abrir `curation/work/clave_modelo.csv` ni `curation/qc_codex/`.
- Sin AAV ni virus; sin inventar datos (campo vacío = vacío o «no reportado»).
- La revisión de Carlos es **asistida por IA y no una revisión humana**; en la página de método se dice así.
- Git: si Carlos tiene permiso, rama `web-carlos` y commits pequeños; si no, envía a Héctor un zip de `producto/web/` y `equipo/qc_carlos/` cada noche.

## 6. Lo que sigue (calendario)
- **Hoy/jueves 22:** repo sincronizado, JSON regenerados desde la v0.1, comprobación visual del sitio (el servidor local no se pudo abrir en tu prueba: prueba con `python -m http.server 8000` y `http://localhost:8000`, y si el navegador de pruebas no conecta, que Carlos lo abra él en su Chrome y te describa o pegue lo que ve).
- **Viernes 23:** imágenes reales integradas, comprobación en laptop y móvil, `PROGRESO.md` al día.
- **Sábado 24:** JSON de Bryan al mediodía (`producto/modelo/`), web congelada a las 5 pm, demo grabada.

Al terminar cada paso, valida antes de darlo por cerrado: conteos de la portada = conteos de los JSON = `RESUMEN_NUMEROS.json` (o diferencia explicada), y cada ficha abre sin errores en la consola.
