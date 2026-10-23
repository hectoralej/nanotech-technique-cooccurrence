"""Rebuild the complete experiment, reusing matching per-fold caches."""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
for script in ("tabular_data.py", "modelo_tamano.py", "modelo_clase.py", "generar_reporte.py", "validar_resultados.py"):
    subprocess.run([sys.executable, str(HERE / script)], check=True)
