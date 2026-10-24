"""Consulta metadatos oficiales; no instala paquetes ni descarga pesos."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
from pathlib import Path
import time
import requests

ROOT = Path(__file__).resolve().parent


def fetch(item):
    name, url = item
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        value = {'url': url, 'http': response.status_code}
        if name.endswith('commit'):
            value.update(sha=data[0]['sha'], fecha=data[0]['commit']['committer']['date'])
        elif name.startswith('pypi'):
            info = data['info']
            value.update(version=info['version'], autor=info.get('author'),
                         mantenedor=info.get('maintainer'), enlaces=info.get('project_urls'),
                         licencia=info.get('license'), licencia_expresion=info.get('license_expression'))
        else:
            value.update(sha=data.get('sha'), cardData=data.get('cardData'),
                         archivos=[x['rfilename'] for x in data.get('siblings', [])])
        return name, value
    except (requests.RequestException, ValueError, KeyError) as error:
        return name, {'url': url, 'error': str(error)}


def main():
    start = time.monotonic()
    endpoints = [
        ('original_commit', 'https://api.github.com/repos/MaterialEyes/exsclaim/commits?per_page=1'),
        ('actual_commit', 'https://api.github.com/repos/MaterialEyes/exsclaim2.0/commits?per_page=1'),
        ('pypi_actual', 'https://pypi.org/pypi/exsclaim/json'),
        ('pypi_original', 'https://pypi.org/pypi/exsclaim/0.1.0/json'),
        ('figex2_pesos', 'https://huggingface.co/api/models/Huang-AI4Medicine-Lab/FigEx2-8B')]
    with ThreadPoolExecutor(max_workers=4) as pool:
        result = dict(pool.map(fetch, endpoints))
    result['fecha_utc'] = datetime.now(timezone.utc).isoformat()
    result['duracion_consultas_segundos'] = time.monotonic()-start
    output = ROOT / 'resultados'
    output.mkdir(exist_ok=True)
    (output / 'auditoria_fuentes.json').write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
