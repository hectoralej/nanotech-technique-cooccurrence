# Bryan: presentación, guion y textos de la web, cierre. Qué falta, dónde está todo y cómo entregarlo

Prompt para pegar en tu sesión, con este archivo como contexto. **Actualiza y reemplaza lo que contradiga a `BRYAN_PRESENTACION_FINAL.md`** (sigue vigente en lo que no se cambia aquí; léelo primero). Reglas de siempre: toda cifra sale de un archivo del repositorio y se cita; no inventes cifras; no toques `curation\`, `modelos\`, `producto\modelo\` ni `producto\web\` (es de Carlos). **El repositorio es PÚBLICO** (comprobado con `gh`): no subas credenciales ni imágenes sin licencia reutilizable; las imágenes de artículos solo con crédito (artículo, DOI y licencia).

## 0. Todo está ya en GitHub (rama `main`); haz `git pull origin main`
Los colaboradores con permiso de escritura son `juanabarcaurena-creator` y `BryanRZ02-org`; usa la cuenta con la que estás autorizado. Qué encuentras ahora (no pidas zips aparte):
| Qué | Dónde |
|---|---|
| **Figuras** (es/en; PNG 300 ppp, SVG, PDF): flujo de datos (`fig_hero_flujo_*`, fondo oscuro) y 3 de modelos (`fig_modelos_1/2/3_*`, fondo blanco) | `figuras/modelos/` |
| Figuras originales con cajas (2 por destino), rejilla de recortes por clase y `creditos.csv` | `entrega/ejemplos_presentacion/` |
| Diagrama del flujo de calidad (es/en) | `figuras/flujo_calidad_figuras_{es,en}.{png,svg}` |
| Resultados del modelo y del experimento NFFA | `modelos/comparacion/` (`ANALISIS_04_RECORTES.md`, `ANALISIS_FUSION_04.md`, `ANALISIS_06_NFFA.md`) |
| Modelo final: ficha, contrato, verificación | `modelos/modelo_final/` (el ONNX está en Releases, tag `modelo-v1.0`) |

## 1. Qué figuras usar en la presentación (mínimo 2 o 3; Héctor lo exige)
| Figura | Dónde va | Qué dice |
|---|---|---|
| **`fig_hero_flujo`** (flujo de datos) | Sección nueva «De la figura al recorte» (Bloque 2 del guion) y como imagen de apoyo en la portada del vídeo | De 5.539 figuras a 8.108 paneles y 4.670 recortes; qué entra al modelo y qué no |
| **`fig_modelos_2`** (figura completa → recortes) | Bloque 4 «Modelos» | La ventaja de los recortes, con el control de «mismo número de vistas» y el IC de la fusión que incluye 0 |
| **`fig_modelos_3`** (NFFA) | Bloque 4 «Modelos», como «lo que probamos y no funcionó» | Resultado negativo honesto (B − A incluye 0; mezclar etiquetas daña) |
| `fig_modelos_1` (opcional) | Solo si falta una escalera estática; ya tienes la escalera interactiva | Medidas → imagen → fusión (v0.1) |
Cómo mostrarlas: las de fondo blanco van sobre una tarjeta clara también en el modo oscuro (que no se vea un recuadro raro); la de flujo va en una tarjeta oscura. Visor con clic para ampliar y Esc para cerrar; siempre con su pie (fuente y n) copiado de la imagen, y texto alternativo. En el vídeo, mantén cada figura al menos 8 s en pantalla.

## 2. Pendiente de la ronda anterior (si no lo has hecho)
Sección nueva «De la figura al recorte» (tipos de figura con ejemplos y cajas, de la figura a los recortes en 3 pasos, qué recortes entran y cuáles no, muestra sin retoques con su nota honesta); tabla de decisiones en 4 grupos con las decisiones nuevas **como propuestas** (D25–D33, las confirma Héctor, y agrégalas a `equipo/DECISIONES.md`); bajar de peso la muestra de 20 artículos a una frase en Limitaciones; recursos visuales sin librerías externas (barras por destino, línea de proceso, contadores con `prefers-reduced-motion`); visor de imágenes. **No cites «IoU 0,88 contra Codex»** (no tiene informe); sí «IoU 0,89 contra las cajas humanas, 22 figuras» y «auditoría a ciegas 47/48».

## 3. Cifras del modelo: ya pueden entrar (todas de los archivos citados)
- **Tabla v0.1** (figura completa): déjala como línea base.
- **Con recortes (preliminar), por artículo:** `ANALISIS_04_RECORTES.md` (n = 1.112) y `ANALISIS_FUSION_04.md` (n = 786). **No mezcles columnas entre muestras distintas** (n = 2.100 figuras/1.641 artículos; 1.112; 786; 1.114) y pon el n junto a cada cifra. Salvedades obligatorias: la ventaja de los recortes se debe en buena parte a más vistas por artículo (con el mismo número de vistas baja a +0,006 en ResNet50 y +0,008 en DINOv2); el IC de «fusión 04 − fusión 03» incluye 0.
- **Modelo final:** DINOv2 ViT-S/14, ensamble de 3 semillas, entrenado con 4.670 recortes; **desempeño de referencia por validación cruzada por artículo: exactitud 0,561 y F1 macro 0,521** (1.114 artículos), frente a **0,442** de exactitud de la clase mayoritaria. El modelo final se entrenó con todos los datos: no se puede evaluar; esa es la única estimación honesta. Exploratorio; probabilidades sin calibrar.
- **Experimento NFFA:** `ANALISIS_06_NFFA.md` (A, B, C; diferencias con IC) y su lectura. Resultado: **no mejora**; el control con etiquetas mezcladas empeora.
- **Demo «sube tu micrografía»:** ya funciona en el navegador con ONNX (la hizo Carlos, verificada con 20/20 entradas). Actualiza `EVALUACION_APP_VS_WEB.md` y el guion: ya **no** es «trabajo futuro»; descríbela con sus advertencias (solo micrografías de partículas; sin calibrar; la clase es la del artículo).

## 4. Textos para la web de Carlos (entrega tuya)
Actualiza y deja en `producto/web_contenido/` (los integra Carlos con `git pull`): `como_se_construyo.md` (con el flujo de figuras y recortes, 5.539 → 1.702 figuras con paneles → 8.108 paneles → 4.670 recortes; reglas de elegibilidad; auditoría a ciegas 47/48; IoU 0,89) y `modelos_y_limitaciones.md` (cifras de la sección 3, cada una con su n y su fuente). Mantén el registro D1–D8.

## 5. Guion del vídeo (español e inglés) y cifras
Actualiza `video/GUION.md` y `video/GUION_EN.md`: presupuesto de 10:00 máximo (objetivo 9:50) con problema 1:00 · cómo se construyó 1:30 · **de la figura al recorte 1:30** · Atlas 2:30 (narra Carlos) · modelos y decisiones 2:00 (con las figuras de la sección 1) · limitaciones y cierre 1:20. Descriptores: «3.116 filas, **2.538 utilizables** tras la auditoría v03». Mantén las reglas de «no decir». Revisa que ninguna cifra contradiga los archivos citados.

## 6. Entrega
1. Rama **`presentacion-bryan`**: `git switch -c presentacion-bryan`, commit de `producto/presentacion/`, `video/` y `producto/web_contenido/`, y `git push -u origin presentacion-bryan`. Avisa a Héctor para el merge. Si el push falla por credenciales: `gh auth login`; si no sale, entrega un zip.
2. Verificación: abre la presentación con servidor local (`python -m http.server 8000` desde `producto/`), consola sin errores, 1920×1080 y 375 px, modo claro/oscuro y modo presentar; cada imagen con su crédito.
3. `PROGRESO.md` con qué se hizo, qué quedó pendiente y qué espera a Héctor. No publiques nada; el alojamiento lo decide Héctor.
