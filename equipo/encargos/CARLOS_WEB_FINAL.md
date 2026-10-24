# Carlos: Atlas final (acceso para todos + datos nuevos de figuras, recortes y descriptores)

Prompt para pegar en tu sesión de Codex/Claude, con este archivo como contexto. Reglas de siempre: no inventes cifras (toda cifra sale de un archivo del repositorio y se cita), no dejes credenciales en ningún archivo, no toques `curation\`, `modelos\` ni `producto\modelo\`; trabaja en una rama `web-carlos` y avisa a Héctor para unirla a `main`.

## 1. Que todo el equipo (y luego cualquiera) pueda abrir el Atlas
El repositorio `hectoralej/nanotech-technique-cooccurrence` es **privado** y es de Héctor: solo Héctor puede dar acceso. **Héctor debe** (Settings → Collaborators → Add people) añadir a Bryan y a Carlos con permiso de escritura. Tú, Carlos:
1. Comprueba que `git pull origin main` y `git push origin web-carlos` funcionan con tu cuenta; si no, dile a Héctor qué error sale.
2. Deja el Atlas como **sitio 100 % estático** (HTML, CSS, JS y JSON; rutas relativas, sin servidor, sin claves) para que se pueda abrir de tres maneras: (a) local con `python -m http.server 8000` desde `producto/`, (b) arrastrando la carpeta a un hosting estático (Netlify Drop o Cloudflare Pages), (c) GitHub Pages si Héctor decide hacer público el repositorio tras el congelado.
3. Escribe `producto/web/LEEME.md` con los tres pasos exactos, probados por ti, para que Bryan lo abra sin ayuda.
4. **No publiques nada en internet por tu cuenta**: el hosting público (que expone datos e imágenes de artículos CC BY) lo decide Héctor. Prepara el paquete y di cómo se despliega.

## 2. Qué datos nuevos incorporar (todo ya está en el repositorio; `build_data.py` debe leerlos, no copiarlos a mano)
- **Figuras clasificadas** (5.539): `modelos/flujo_figuras/figuras_vision.csv` (una fila por figura: paneles, n_micro/n_espectro/n_otro, curvas superpuestas, destino `simple | pareja | compuesta | superpuesto | excluir`, `estado` `aceptada_auto | aceptada_arbitrada | cola_revision`, imagen original). Por defecto muestra solo lo **aceptado**; lo de la cola, con un aviso visible.
- **Paneles recortados** (8.108 recortes de 1.702 figuras): `modelos/flujo_figuras/segmentacion/cajas/paneles.csv` y `indice_recortes.csv` (caja normalizada x0,y0,x1,y1 sobre la figura original, tipo micro/espectro/otro, `tecnica`, `contenido`, `elegible_morfologia`, hijas `padre`/`rel` para insets, `cascada`, clase de portador y fold). Los recortes no están en Git: Héctor te pasa `web_paneles_miniaturas.zip` (94 MB, miniaturas JPEG de 320 px con `paneles_web.csv` incluido); descomprímelo en `producto/web/img/` (`img/paneles/<pmcid>/*.jpg`). Decide con Héctor si las miniaturas van a Git (≈ 94 MB: probablemente no) o solo al despliegue.
- **Descriptores v03** (3.116 filas, 1.229 artículos): `modelos/descriptores_v02/descriptores_v03.csv`: valores originales (`size_nm`, `pdi`, `zeta_mV`) y finales (`*_final`), `usable_v03`, `etiqueta_muestra`, `metodo_tamano_audit`, `revisar_v03`. Muestra por defecto solo `usable_v03 = True`; marca `revisar_v03`.
- **Calidad (para la sección «Cómo se verificó»)**: `equipo/ESTADO_FIGURAS_24OCT_NOCHE.md`, `modelos/flujo_figuras/PROGRESO.md`, `modelos/descriptores_v02/DESCRIPTORES_V03.md`, y el diagrama `figuras/flujo_calidad_figuras_es.png` / `_en.png` (también `.svg`). Cifras citables: auditoría a ciegas 47/48 figuras con el número de paneles exacto; cajas de Haiku contra cajas humanas IoU 0,89 (22 figuras) y contra Codex IoU 0,88 (31 figuras); 4.670 recortes de micrografía de partículas con clase.
- **Modelo**: `producto/modelo/*.json` seguirá igual; cuando Héctor entregue los resultados del cuaderno 04 (recortes), se añaden como «resultados preliminares». Mientras tanto, conserva el aviso «modelo con resultados modestos».

## 3. Mejoras de la web
- Nueva vista **«Figuras y paneles»**: filtro por destino (simple / pareja / compuesta / espectro superpuesto), por técnica y por clase; ficha con la **figura original y sus cajas dibujadas** (SVG sobre la imagen) y los recortes al lado.
- **Espectros limpios vs. superpuestos** claramente distinguidos; los superpuestos, marcados (no son espectros utilizables para entrenar).
- **Rendimiento**: miles de paneles → paginación o carga diferida (`loading="lazy"`), búsqueda local, sin bloquear el navegador.
- **Atribución**: cada imagen muestra artículo, DOI y licencia CC BY; pie de página con la licencia de los datos.
- **Calidad visual**: móvil a 375 px, contraste, teclado, consola sin errores; 3 capturas nuevas en `producto/web/capturas/`.
- Español con opción de inglés para los textos principales, si da tiempo (la demo y el vídeo van en español con subtítulos en inglés).

## 4. Entrega y plazos
- Rama `web-carlos` con: `producto/web/` actualizado, `LEEME.md`, `build_data.py` reproducible y un `PROGRESO.md` que diga qué se hizo y qué quedó pendiente.
- **Congelado de la web: el que acuerde Héctor antes de la entrega** (entrega del hackatón: domingo 25 de octubre, 5:45 pm, Costa Rica). Dos ensayos cronometrados de la demo (2–3 min) y grabación de la demo con la web congelada.
- Antes de congelar: abrir el Atlas en un navegador limpio (sin tus archivos locales) siguiendo tu propio `LEEME.md`, para comprobar que alguien más puede abrirlo.
