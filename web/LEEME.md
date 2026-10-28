# Abrir y compartir el Atlas

## Paquete de revisión `atlas_web.zip`

El ZIP contiene esta carpeta `web/` y omite `web/img/`, tal como se solicitó. Incluye el runtime local `web/vendor/onnxruntime-web/` para ejecutar la demo, además de `TECNICAS.md`, los datos generados y este LEEME. Para revisarlo, extrae `web/` dentro de la carpeta `producto/` de un checkout que conserve sus carpetas hermanas (`imagenes/` e `imagenes_v02/`). No es un paquete de despliegue autónomo: no incluye los 8.108 archivos de miniaturas guardados en `web/img/`, los originales de las carpetas hermanas ni `producto/modelo_onnx/`. Para ejecutar la demo también hay que extraer `02_onnx/` y `03_verificacion/` del paquete `05_para_web.zip` en `producto/modelo_onnx/` y volver a ejecutar `python web/build_data.py`. En el ZIP aislado las imágenes y miniaturas no estarán disponibles hasta aportar esos recursos por separado.

> **IMPORTANTE: no abras `index.html` con doble clic (`file://`).** Las páginas usan `fetch()` para leer los JSON y necesitan un servidor local. Si se abre como archivo, los datos pueden quedar vacíos o aparecer un error de carga. Usa los comandos de abajo.

## Abrir en esta computadora

1. Instala Python 3 si aún no está instalado.
2. Abre PowerShell en la carpeta `producto` del repositorio.
3. Ejecuta `python -m http.server 8000`.
4. Abre <http://localhost:8000/web/> en Chrome, Edge o Firefox. Para la vista de figuras, abre <http://localhost:8000/web/figuras.html>.
5. Para detener el servidor, vuelve a PowerShell y presiona `Ctrl+C`.

Páginas preparadas: portada/explorador (`/web/`), figuras y paneles (`/web/figuras.html`), galería de recortes (`/web/galeria.html`), construcción y fuentes (`/web/construccion.html`), modelos (`/web/modelos.html`) y demo local (`/web/demo.html`).

El servidor local solo entrega archivos estáticos. No requiere una cuenta, una clave ni conexión a una API. Para abrir el Atlas desde otro checkout, primero regenera los datos desde las fuentes del repositorio:

```powershell
cd producto
python web/build_data.py
python -m http.server 8000
```

`build_data.py` lee los CSV canónicos en `curation/`, `modelos/flujo_figuras/` y `modelos/descriptores_v02/`. Escribe los JSON generados en `producto/web/data/`. No modifica los CSV fuente ni los archivos del modelo de `producto/modelo/`.

Al regenerar, también copia a `producto/web/data/` los análisis de recortes y fusión presentes en `modelos/comparacion/`. El informe NFFA se copia solo si existe en el checkout. La demo se habilita solo cuando están todos los archivos locales del modelo, las 20 imágenes de verificación y la versión fijada del runtime.

## Demo del modelo ONNX

- El paquete local de Héctor se encuentra en `producto/modelo_onnx/02_onnx/` y `producto/modelo_onnx/03_verificacion/`. El modelo de 67 MB y las imágenes se excluyen de Git mediante `.gitignore`.
- La demo usa ONNX Runtime Web **1.30.0**, instalado localmente en `producto/web/vendor/onnxruntime-web/` con licencia y WASM. El runtime también se excluye de Git. No se carga desde CDN.
- El ZIP `entrega/atlas_web.zip` contiene el runtime local y su licencia, pero no el modelo de `producto/modelo_onnx/`; esta demo verificada funciona en este checkout local y al colocar el paquete ONNX en la estructura indicada. No distribuyas el paquete de modelo sin respetar las condiciones del repositorio.
- Ejecuta `python web/build_data.py` desde `producto/`. La página solo se activa cuando el modelo, runtime, licencia, versión y entradas de verificación están presentes.
- La entrada sigue el contrato acordado: tensor float32 NCHW `[1,3,256,256]`, RGB 0–255; lienzo cuadrado blanco, imagen centrada y reducción con suavizado alto. El modelo reduce y normaliza internamente.
- La equivalencia compara las 20 imágenes con las columnas `onnx_int8_*`; el criterio de aprobación es una diferencia absoluta media menor que 0,03. La interfaz muestra el promedio y el máximo, además del tiempo de carga e inferencia medido en el navegador.
- Junto a cada resultado se muestran las métricas de referencia por artículo: exactitud 0,561 y F1 macro 0,521; la línea base de clase mayoritaria tiene exactitud 0,442.
- El archivo de imagen seleccionado se procesa dentro del navegador y no se envía a un servidor. La predicción es exploratoria, no calibrada, y corresponde a la clase del artículo de origen; solo tiene sentido con micrografías de partículas.
- Si falta cualquier pieza, la página explica el estado pendiente y desactiva carga, inferencia y comparación.

## Preparar una carpeta para un hosting estático

1. Regenera los JSON con los comandos anteriores.
2. Conserva `producto/` como raíz del paquete: la carpeta `web/` usa datos e imágenes que están en sus carpetas hermanas.
3. Incluye `producto/imagenes/`, `producto/imagenes_v02/` y `producto/web/img/` solo si el paquete se va a distribuir y los términos de cada artículo permiten esa redistribución. En esta copia, `imagenes_v02/` y `web/img/` son archivos locales ignorados por Git; no aparecen en la rama.
4. Los CSV generados distinguen las imágenes disponibles de las ausentes. Los artículos sin licencia reutilizable confirmada o sin archivo conservan el enlace al DOI y muestran un marcador; los recortes solo se muestran cuando su archivo existe y la licencia del artículo permite reutilizarlos.
5. Sube la carpeta `producto/` a Netlify Drop o Cloudflare Pages siguiendo el flujo de carga del proveedor. Configura `producto/` como raíz publicada. No se probó ni publicó un sitio remoto en esta entrega.

## GitHub Pages

El repositorio es público. GitHub Pages requiere que Héctor configure una publicación compatible con `producto/` como raíz de los archivos estáticos y aporte los recursos locales que quedan fuera de Git.

## Imágenes de figuras y paneles

El paquete `web_paneles_miniaturas.zip` ya fue integrado localmente: están `producto/web/img/paneles_web.csv` y 8.108 miniaturas en `producto/web/img/paneles/<PMCID>/`. El manifiesto coincide con el índice canónico y la regeneración habilita las miniaturas presentes con licencia reutilizable. La carpeta `producto/web/img/` está excluida de Git por su tamaño; inclúyela expresamente en el paquete estático de despliegue solo después de confirmar la redistribución.

El paquete `web_figuras_v02_reducidas.zip` se extrajo en `producto/imagenes_v02/`. De las 3.425 rutas v02 citadas por el CSV de figuras, el ZIP contiene 3.424; la ausente es `PMC10390827/Beilstein_J_Nanotechnol-14-804-g008.jpg`. Su registro tiene `estado=cola_revision` y `destino_vision=excluir`, por lo que la vista actual no lo muestra. El DOI y la falta de imagen constan en los datos generados, pero no se ve un marcador en la interfaz mientras el registro siga excluido. Las demás imágenes se resuelven desde `producto/imagenes/` o `producto/imagenes_v02/` según la ruta canónica.

Para volver a generar los JSON después de modificar o recuperar una imagen:

```powershell
cd producto
python web/build_data.py
```

Las rutas a imágenes originales son locales y se generan solo cuando el archivo existe y la licencia del artículo permite reutilizarlo. Cada ficha muestra el DOI y la licencia registrada. No redistribuyas imágenes fuera de esos términos.

## Reconstruir el modelo y el runtime desde un checkout nuevo

El archivo que ejecuta la demo es el ensamble de tres semillas `ensamble3_int8.onnx` (67.151.951 bytes). Se obtiene en la [release modelo-v1.0](https://github.com/hectoralej/nanotech-technique-cooccurrence/releases/tag/modelo-v1.0). Desde la raíz del repositorio:

```powershell
New-Item -ItemType Directory -Force producto/modelo_onnx/02_onnx, producto/modelo_onnx/03_verificacion | Out-Null
Copy-Item modelos/modelo_final/02_onnx/*.json producto/modelo_onnx/02_onnx/ -Force
Copy-Item modelos/modelo_final/03_verificacion/* producto/modelo_onnx/03_verificacion/ -Recurse -Force
Invoke-WebRequest 'https://github.com/hectoralej/nanotech-technique-cooccurrence/releases/download/modelo-v1.0/ensamble3_int8.onnx' -OutFile producto/modelo_onnx/02_onnx/ensamble3_int8.onnx
Get-FileHash producto/modelo_onnx/02_onnx/ensamble3_int8.onnx -Algorithm SHA256
python producto/web/instalar_runtime.py
python producto/web/build_data.py
```

El SHA-256 del ensamble debe ser `faed3852850e0b882111a1995b76a6fead15448975981f2f4372bf5ea263d623`, igual que en `modelos/modelo_final/SHA256_onnx.txt`. La versión de una semilla (`semilla0_int8.onnx`) no se utiliza en la demo. Si ya existe el modelo y coincide su huella, basta con conservarlo y copiar los archivos pequeños actualizados.

`instalar_runtime.py` descarga ONNX Runtime Web **1.30.0** del registro npm, verifica el tarball completo mediante `sha512-q0y+JrrtukXSzsBWEMccVfqX25LRmosXHF+CaRJmg8pZClzcV7svNc4rKY3jL02Vb7QmRMDs1SigqR4CXAfKYQ==` y copia únicamente JS/WASM, metadatos y la licencia MIT conservada en `recursos/ONNXRuntime-LICENSE.txt`. La variante WASM `ort.wasm.min.js` se guarda como `vendor/onnxruntime-web/ort.min.js`. Para comprobar una instalación existente: `python producto/web/instalar_runtime.py --verify-only`. El runtime y los ONNX siguen fuera de Git.

## Técnicas y alcances de conteo

El mapa está en `build_data.py` y se describe completo en [TECNICAS.md](TECNICAS.md). Agrupa cryo-EM/cryo-TEM, HAADF-STEM/STEM, H&E/HE/histología H&E, UVVis/UV-vis, EDX/EDS, RMN y potencial zeta; fluorescencia/confocal/CLSM se reúnen para navegación. Los métodos térmicos combinados se desdoblan en DSC, TGA o DTA. Los marcadores y etiquetas sin método definido se omiten del filtro, conservando su texto original en la ficha.

Las familias son Microscopía electrónica y de sonda (incluye AFM), Espectroscopías, Térmicas, Dispersión de luz/rayos X, Fluorescencia y óptica y Otras. Las diez técnicas principales quedan visibles; las demás están en «Otras técnicas», desplegable. Las barras cuentan figuras, con posibilidad de varias técnicas por figura.

«Sin técnica» tenía 1.974 figuras en las 3.873 aceptadas y visibles frente a 2.886 en las 5.539 fuente. Tras depurar marcadores pasa a **1.975 visibles** y **2.892 fuente**. El gráfico y los chips usan el primer alcance, indicado explícitamente; activar la cola amplía los resultados del filtro.

## Modelos, fuentes y uso del visor

Las tres figuras españolas de `figuras/modelos/` se muestran arriba en Modelos; clic para ampliar, Escape para cerrar y botones para descargar PNG/SVG/PDF. Las tablas se despliegan debajo. NFFA presenta brazos A/B/C, diferencias e IC desde `ANALISIS_06_NFFA.md` y `metricas_06.json`. Las muestras de recortes (1.112 artículos), fusión (786) y NFFA/modelo final (1.114) permanecen identificadas.

El modelo final se entrenó con todos los recortes. Las cifras 0,561 / 0,521 corresponden a validación cruzada por artículo, no a evaluar de nuevo el modelo sobre su entrenamiento. En Figuras, flechas izquierda/derecha recorren el visor y Escape lo cierra; el botón de cajas permite ocultar o mostrar sus límites. Los cinco destinos visuales de Construcción incluyen ejemplo, DOI y licencia.
