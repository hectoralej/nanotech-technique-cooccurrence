from __future__ import annotations
import hashlib, json
from datetime import datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
STATE=ROOT/'modelos'/'ronda2'
def write_json(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def hashes():
    files=list((ROOT/'curation').glob('ext_*.csv'))
    files+=list((ROOT/'curation'/'v0.1').rglob('*'))
    files+=list((ROOT/'modelos'/'tabular').rglob('*'))
    files+=[ROOT/'producto'/'modelo_tabular'/'metricas_tabular.json']
    return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files if p.is_file()}
def guard(init=False):
    path=STATE/'fuentes_protegidas.json'
    if init and not path.exists(): write_json(path,hashes())
    assert json.loads(path.read_text(encoding='utf-8'))==hashes(),'Cambió una fuente protegida'
def checkpoint(letter,message):
    guard()
    with (ROOT/'modelos'/'CHECKPOINTS_RONDA2.md').open('a',encoding='utf-8') as f:
        f.write(f"- {datetime.now().isoformat(timespec='seconds')} · {letter}: {message}\n")
    print(f'CHECKPOINT {letter}: {message}',flush=True)
