# Cómo compartir el Atlas con todo el equipo (viernes 23 de octubre)

Hoy el Atlas solo vive en la computadora de Carlos. Queremos que **Héctor, Bryan y Carlos lo abran sin pedirlo**. Hay tres niveles; haz el 1 ya y el 2 hoy.

## Nivel 1: subir el código y los datos al repositorio privado (obligatorio, hoy)
**Qué sube:** `producto/web/` completo (HTML, CSS, JavaScript, `build_data.py`, los JSON de `data/`, `GUION_DEMO.md`, `PROGRESO.md`) y `equipo/qc_carlos/`. Pesa unos 5 MB. **No sube:** imágenes, `.build_input/`, los JSON de prueba del modelo ni zips.

**Cómo (la ruta más segura, sin permisos de escritura de Carlos):**
1. Carlos envía a Héctor el zip `Atlas_para_Hector_…zip` **ya**, por Drive o WhatsApp (pesa menos de 1 MB).
2. Héctor lo pasa a Claude, que lo descomprime en el repositorio, lo revisa en un navegador y lo sube. Quedará en `main`.
3. Si Carlos tiene permiso de escritura en el repositorio, también puede subirlo él a una rama `web-carlos` con `git add producto/web equipo/qc_carlos; git commit -m "Atlas"; git push origin web-carlos`. Con permiso de escritura o sin él, **no dejar credenciales en ningún archivo ni en el chat**.

**Cómo lo abre cualquiera del equipo después:** `git pull origin main` y, desde la carpeta `producto/`:
```
python -m http.server 8000
```
Abrir `http://localhost:8000/web/`. Las imágenes se ven si están en `producto/imagenes/` (zip aparte, ver nivel 3); sin ellas la web funciona y muestra el marcador con el enlace al DOI.

## Nivel 2: enlace en la nube para ver el Atlas sin instalar nada (hoy)
Para que cualquiera lo abra con un clic desde el celular o la laptop:
- **Opción recomendada:** Claude lo publica como una página privada en el servicio de Artifacts de Claude (enlace que solo ven quienes lo reciban), con los datos y una muestra de unas 150 micrografías (el límite de tamaño impide subir las 2.149). Sirve para que Bryan y Carlos lo revisen y para ensayar la demo. Héctor decide si se hace.
- **Alternativa de hosting estático** (para el final, si el equipo quiere un enlace público de la entrega): subir `producto/web/` y las imágenes a un servicio gratuito (por ejemplo Netlify o Cloudflare Pages). **Esto publica los datos y las imágenes en internet**: las imágenes son de artículos CC BY y llevan crédito al DOI, pero es una decisión de Héctor y se toma después de congelar la web.
- **GitHub Pages** no es recomendable ahora: con un repositorio privado depende del plan de la cuenta y exigiría hacer público el repositorio.

## Nivel 3: las imágenes (260 MB) para todos
No van a GitHub. Héctor sube `imagenes_v0.1.zip` a Drive (o similar) una vez y comparte el enlace con Bryan y Carlos. Se descomprime dentro de `producto/imagenes/` de cada computadora (queda `producto/imagenes/<pmcid>/<archivo>.jpg`).

## Qué debe hacer Carlos ahora, en orden
1. **Enviar el zip más reciente a Héctor hoy** (el que tiene los cambios: limpieza de títulos, filtro en español, `imagen_local`, panel del modelo, guion de demo).
2. **Revisión visual en Chrome** de esa versión: consola sin errores en rojo, filtros, una ficha con imagen y otra sin imagen, móvil (F12 → icono de dispositivo → 375 px). Tomar las 3 capturas y agregarlas al zip.
3. Probar la web con los **tres JSON reales del modelo** cuando Bryan los entregue (o conservar el aviso «modelo no disponible»).
4. **Dos ensayos cronometrados** de la demo (2–3 min). Grabar el **sábado** con la web congelada a las 5 pm.

> Nota: el resumen de Carlos está fechado «24 de octubre»; hoy es viernes 23. El plazo real es el domingo 25 a las 5:45 pm. Los pasos de arriba caben en el sábado.
