# Paquete actualizado del Atlas Nano2Predict

**Fecha:** 24 de octubre de 2026  
**ZIP:** `Atlas_traspaso_2026-10-24_QA.zip`

Contiene la web, los JSON generados, los tres JSON reales del modelo, las métricas tabulares, el informe de cierre y siete capturas de QA de Chrome. No contiene las 2.149 imágenes JPG; esos archivos (273,7 MB) deben enviarse por separado desde `imagenes_v0.1.zip` y extraerse en `producto/imagenes/<pmcid>/`.

## Cómo abrir

Extrae el ZIP y entra a `producto/`. Ejecuta:

```powershell
python -m http.server 8000
```

Abre [http://localhost:8000/web/](http://localhost:8000/web/).

## Estado

Se hizo QA automatizado con Chrome en 1365×900 y 375×812, con cero errores de consola/HTTP y sin imágenes rotas entre los recursos disponibles. No sustituye los dos ensayos humanos ni la grabación a 1920×1080, aún pendientes. La web actualizada está en el checkout local sincronizado con `main` (`de48aa7`), sin commit ni push.

Informe completo: [RESUMEN_TRASPASO_ATLAS_2026-10-24.md](RESUMEN_TRASPASO_ATLAS_2026-10-24.md).
