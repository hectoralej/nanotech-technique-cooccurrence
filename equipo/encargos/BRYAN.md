# Bryan: nuevo rol (presentación interactiva, guion del video y apoyo al sitio)

**Para:** Bryan y su sesión de Claude. **Fecha:** viernes 23 de octubre, tarde. **Entrega del hackatón: domingo 25 de octubre, 5:45 pm (Costa Rica).** Objetivo interno: subir el video el **domingo antes de las 2 pm**, para tener casi cuatro horas de margen.

## 0. Qué cambió
Héctor lleva los modelos (con Kabré y Codex). **Tú dejas el modelo de imágenes** y pasas a lo que más pesa en la evaluación: **que se entienda y se vea bien**. Tienes tres encargos, en este orden de prioridad:
1. **Guion y estructura del video** (10 minutos; 2–3 son la demo del producto).
2. **Presentación interactiva** (una página web de presentación que cuente el proyecto).
3. **Apoyo a Carlos** con el sitio (contenido y pruebas, sin tocar su código).

Lee primero: `equipo/DECISIONES.md` (qué decidimos y por qué: es el hilo conductor), `equipo/PLAN_EQUIPO_FINAL.md`, `modelos/REVISION_CRITICA.md` (limitaciones honestas), `figuras/figuras_para_el_video/INDICE.md`. **Haz `git pull origin main`** (o pide el zip a Héctor). Lo mismo que ve el equipo está en `main`; el sitio se abre con `python -m http.server 8000` desde `producto/` y `http://localhost:8000/web/`.

## 1. Guion del video (primera entrega: sábado 9 am)
Estructura sugerida de 10 minutos, con quién habla y qué se muestra (ajústala, pero respeta que la demo del Atlas dure 2–3 min):

| Min | Bloque | Contenido | Material |
|---|---|---|---|
| 0:00–1:00 | Problema | Los datos de nanoportadores están dispersos en PDFs; sin micrografías emparejadas con medidas no hay modelos | Figura 1 |
| 1:00–3:00 | Cómo se construyó la base | Europe PMC → extracción con IA → **cada cita verificada por código** → control de calidad; solo CC BY | Figuras 8 y 9; `DECISIONES.md` (D1–D8) |
| 3:00–5:30 | **Demo del Atlas** (2–3 min) | Filtro liposoma + cryoTEM → ficha → cita → panel del modelo → «Cómo se construyó» | Grabación de Carlos |
| 5:30–8:00 | Modelos | Escalera: lineal → Random Forest → imágenes (CNN y transformer) → fusión. **Resultados modestos, presentados como modestos** | Figura 10 y la figura de comparación (Héctor la entrega) |
| 8:00–9:00 | Decisiones y limitaciones | Excluir vectores virales; figuras completas; sin parámetros de formulación; QC asistido por IA | `DECISIONES.md`, `REVISION_CRITICA.md` |
| 9:00–10:00 | Siguientes pasos y créditos | Recortar paneles, más figuras por artículo, ajuste fino en GPU, validación externa; **agradecimiento a Kabré (CeNAT/CNCA)**; Europe PMC; el profesor | — |

Entrega `video/GUION.md` con el texto de narración por bloque (palabras reales, no solo títulos), tiempos y qué se ve en pantalla. Escríbelo para **leerse en voz alta**: frases cortas.

### Qué se puede decir y qué NO (obligatorio)
| Sí, con estas cifras | No decir |
|---|---|
| 1.824 artículos leídos; **1.707 con evidencia**; 2.726 micrografías, 3.116 filas de medidas, 4.015 espectros | «Datos validados por humanos» (el QC fue en 20 artículos y asistido por IA) |
| Cada dato tiene una cita verificada por código (2 rechazadas) | «El modelo acierta/predice bien» |
| Tamaño: mejor modelo simple R² ≈ 0,24 frente a 0,18 de la línea base | «Predecimos el tamaño» sin decir que el error mediano es ≈ 44 % |
| Clase de portador con medidas: F1 ≈ 0,51 frente a 0,12 de la mayoritaria | Cifras de las banderas de formulación como resultado principal (son proxies ruidosos) |
| Solo con la imagen: F1 ≈ 0,47; imagen + medidas ≈ 0,55 frente a 0,52 de las medidas | «Una red neuronal resuelve el problema» |
| Todo se evalúa **por artículo** con intervalos de confianza | Que el modelo funciona «en producción» |

Las cifras exactas y su origen están en `equipo/DECISIONES.md` y en `modelos/`. **Si Héctor actualiza un número (ajuste fino), úsalo; no cites cifras de memoria.**

## 2. Presentación interactiva (primera versión: sábado 12 m; final: sábado 3 pm)
Una página HTML estática en `producto/presentacion/` (no en `producto/web/`, que es de Carlos), con el mismo estilo del Atlas (`producto/web/styles.css`: paleta y tipografía). Una sección por bloque del guion, que se recorre con flechas o desplazamiento. Debe incluir: la línea de tiempo del proyecto, las figuras de `figuras/figuras_para_el_video/`, una vista de **cómo se extrae un dato con su cita** (un ejemplo real de `curation/ext_descriptores.csv`), la tabla de decisiones, y un enlace al Atlas. Sin dependencias externas ni servidores: debe abrirse con `python -m http.server`.

## 3. Apoyo a Carlos (sin chocar con su código)
Carlos es dueño de `producto/web/app.js`, `styles.css`, `build_data.py` y `index.html`. **No los edites.** Tu aporte:
- **Texto** para la página «Cómo se construyó» y para una página «Modelos y limitaciones» (usa `DECISIONES.md` y `REVISION_CRITICA.md`; en español, claro). Entrégalo en `producto/web_contenido/*.md` y Carlos lo integra.
- **Pruebas:** usa `equipo/qc_carlos/` y la lista de comprobación de `equipo/CORRECCIONES_ATLAS_CARLOS.md`; reporta errores a Carlos con captura y pasos.
- Coordinen por el chat de WhatsApp; cada uno entrega zips a Héctor.

## 4. Calendario
- **Hoy (viernes):** leer, `git pull`, borrador de la estructura del video.
- **Sábado 9 am:** `video/GUION.md` v1. **12 m:** presentación v1. **3 pm:** guion y presentación finales; **los resultados de modelos se congelan**.
- **Sábado 5 pm:** el Atlas se congela; Carlos graba la demo. **Tarde-noche:** grabación de la narración (Héctor y quien tenga mejor voz).
- **Domingo 9 am:** montaje. **12 m:** video final revisado. **2 pm:** subir.

## 5. Cómo trabajar sin gastar tokens de más
Escribir texto y HTML estático es barato; **no pidas a Claude que abra las 2.000 imágenes ni que reentrene nada**. Lo pesado (modelos, Kabré) es de Héctor. Si necesitas un número nuevo, pídeselo.
