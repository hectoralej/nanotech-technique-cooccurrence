# ¿Presentación como página web o como app? Evaluación (23 de octubre)

**Decisión: página web estática (HTML + CSS + JS, sin servidor ni dependencias). Se descarta la app.**

## Qué haría falta para una app que corra el modelo
El modelo de imágenes es: figura completa → vector de DINOv2 ViT-S/14 y ResNet50 (congelados) → PCA 64 → SVM. Para clasificar una micrografía nueva «en vivo» haría falta, además de lo que ya existe:

| Pieza | Costo medido o estimado |
|---|---|
| PyTorch (CPU) y timm instalados | ≈ 506 MB en disco (medido en esta computadora) |
| Pesos de DINOv2 ViT-S/14 y de ResNet50 | 84 MB + 98 MB (medidos) |
| PCA y SVM entrenados | **No están guardados en el repositorio**: las cifras salieron de análisis sobre vectores calculados en Kabré, y el SVM final no se ha exportado ni fijado (ver `ANALISIS_RAPIDO_EMBEDDINGS.md`: «hay que fijar el modelo de antemano») |
| Tiempo por imagen | ≈ 0,25 s por imagen en esta CPU con DINOv2 (2.148 figuras en 518 s); es viable |
| Empaquetado (Electron, Tauri o instalador de Python) | > 1 GB con PyTorch; Node ni siquiera está instalado en esta máquina |

## Por qué no vale la pena para la entrega
1. **El jurado ve un video de 10 minutos.** Una app no se instala ni se ejecuta durante la evaluación; una página sí se puede abrir en un clic.
2. **Lo que mostramos ya existe precalculado.** Las predicciones de las 2.100 figuras de la base están en `producto/modelo/predicciones.json` y los vecinos en `similares.json`. Una app no añadiría nada a lo que se ve en el Atlas.
3. **Riesgo y plazo.** Subir una imagen propia exige fijar y exportar el modelo final (que aún está en revisión por Héctor), probar la inferencia y empaquetarla, todo antes del domingo 5:45 pm. Un clasificador en vivo con F1 ≈ 0,44 invita a probarlo con imágenes que no son micrografías (espectros, gráficas) y a contradecir nuestro mensaje de «resultados modestos».
4. **Honestidad.** Predecir sobre una imagen cualquiera sería presentar el modelo como una herramienta de uso, y la validación es solo interna (sin validación externa).

## Qué sí aporta la página web
- Se abre con un doble clic (`index.html`) o con `python -m http.server 8000` desde `producto/`.
- Funciona sin conexión y sin librerías externas; se puede publicar tal cual en GitHub Pages.
- Es interactiva donde importa: ejemplos reales de extracción con verificación de la cita **en vivo**, escalera de modelos con intervalos de confianza, registro de decisiones filtrable, galería de figuras y vista previa del Atlas.
- Se adapta a pantalla de proyector, portátil y móvil, con modo claro y oscuro.

## Si más adelante se quisiera la demo «sube tu micrografía»
Camino realista, **después** del hackatón: exportar DINOv2-S a ONNX (≈ 22 MB en int8), ejecutar el clasificador en el navegador con ONNX Runtime Web y mostrar los vecinos más cercanos de la base. No requiere servidor ni app, pero exige fijar el modelo final, exportar la PCA y el SVM, y validar que el resultado en el navegador coincide con el de Python. Se deja anotado como trabajo futuro.
