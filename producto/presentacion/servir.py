"""Servidor local sin caché para la presentación (y el Atlas).

`python -m http.server` deja que el navegador guarde copias viejas de app.js y estilo.css, y la página se ve
a medias después de una actualización. Este servidor envía `Cache-Control: no-store`, así que siempre se ve la
versión actual. Sirve la carpeta que contiene a `presentacion/` (producto/ en el repositorio).

Uso:
    python producto/presentacion/servir.py              # abre http://localhost:8000/presentacion/
    python producto/presentacion/servir.py --sin-navegador
    python producto/presentacion/servir.py 8010         # otro puerto
"""
import functools
import http.server
import socketserver
import sys
import threading
import webbrowser
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
args = [a for a in sys.argv[1:] if not a.startswith("--")]
PUERTO = int(args[0]) if args else 8000


class SinCache(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store, max-age=0")
        super().end_headers()

    def log_message(self, *a):  # menos ruido en la consola
        pass


socketserver.TCPServer.allow_reuse_address = True
with socketserver.ThreadingTCPServer(("", PUERTO), functools.partial(SinCache, directory=str(RAIZ))) as srv:
    url = f"http://localhost:{PUERTO}/presentacion/"
    print(f"Presentación en {url}   (Ctrl+C o cierra esta ventana para terminar)")
    if "--sin-navegador" not in sys.argv:
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
