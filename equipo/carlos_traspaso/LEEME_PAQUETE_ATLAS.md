# Paquete de traspaso del Atlas

**Fecha de corte:** 24 de octubre de 2026  
**Estado:** paquete local preliminar, sin capturas de QA visual y sin publicación remota.

## Archivos principales

- [Resumen completo de cambios, pendientes y pasos siguientes](RESUMEN_TRASPASO_ATLAS_2026-10-24.md)
- [Tablero Excel de tareas y referencias](../outputs/atlas_traspaso_2026-10-24/Traspaso_Atlas.xlsx)
- [Paquete ZIP para transferir al equipo](Atlas_traspaso_2026-10-24_sin_capturas.zip)

## Abrir la vista local

Extrae el ZIP conservando las carpetas. En PowerShell, abre la carpeta `producto` y ejecuta:

```powershell
python -m http.server 8000
```

Después abre [http://localhost:8000/web/](http://localhost:8000/web/). El servidor y esa dirección solo funcionan en la computadora donde se ejecuta.

## Estado esencial

- La web contiene 1.707 artículos E1/E2, 2.726 paneles, 3.116 descriptores y 4.015 espectros.
- Los cambios están en el commit local `534096a`, rama local `web-carlos`, basado en `origin/main` `739576a`. El intento de crear la rama remota fue rechazado por la integración GitHub con HTTP 403; no hay push ni PR y `main` no se modificó.
- El modelo figura como no disponible; los fixtures de prueba no se presentan como resultados reales.
- El ZIP no contiene las imágenes ni capturas. El inventario registra 2.149 JPG disponibles y 44 faltantes de 30 PMCID.
- La revisión visual actual en Chrome, la entrega de JSON finales del modelo, los ensayos de demo, la transferencia externa del ZIP y la decisión de publicar en nube continúan pendientes.

El Excel ofrece el detalle de responsables, estados, bloqueos y referencias. El informe Markdown explica qué se hizo, qué falta, por qué y el orden recomendado para continuar.
