from pathlib import Path
import json, hashlib, subprocess, sys, runpy
import pandas as pd
from datetime import datetime, timezone
ROOT=Path(r'C:\Users\Hector\Desktop\Quimioinformatica Proyecto\nanotech-technique-cooccurrence')
FLOW=ROOT/'modelos/flujo_figuras'
BOX=FLOW/'segmentacion/cajas'
OUT=BOX/'resultados/codex'
STAGE=OUT/'_validacion_ronda4'
STAGE.mkdir(exist_ok=True)
files=sorted(OUT.glob('C[0-9][0-9][0-9].json'))
data={}
for p in files:
    d=json.loads(p.read_text(encoding='utf-8-sig'))
    data.update({k:v for k,v in d.items() if not k.startswith('_')})
plan=pd.read_csv(BOX/'plan_cajas.csv',dtype=str,encoding='utf-8-sig')
plan=plan[plan.fig_id.isin(data)].copy()
assert set(plan.fig_id)==set(data)
plan['imagen']=[str(ROOT/str(p)) for p in plan.imagen]
plan.to_csv(STAGE/'plan_cajas.csv',index=False,encoding='utf-8-sig')
classfile=FLOW/'resultados/codex/_validacion_ronda4/figuras_vision.csv'
(STAGE/'figuras_vision.csv').write_bytes(classfile.read_bytes())
review=STAGE/'resultados/codex'
review.mkdir(parents=True,exist_ok=True)
for p in files: (review/p.name).write_bytes(p.read_bytes())
source=FLOW/'segmentacion/consolidar_cajas.py'
code=source.read_text(encoding='utf-8-sig')
code=code.replace('RAIZ = Path(__file__).resolve().parents[3]',f'RAIZ = Path({str(STAGE)!r})')
code=code.replace('OUT = Path(__file__).resolve().parent / "cajas"','OUT = RAIZ')
code=code.replace('DEST = RAIZ / "producto/imagenes_recortes/paneles_v02"','DEST = RAIZ / "recortes"')
code=code.replace('OUT.parent.parent / "figuras_vision.csv"','OUT / "figuras_vision.csv"')
copy=STAGE/'consolidar_cajas_aislado.py'
copy.write_text(code,encoding='utf-8')
result=subprocess.run([sys.executable,str(copy)],capture_output=True,text=True,encoding='utf-8')
(STAGE/'consolidacion.log').write_text(result.stdout+'\n'+result.stderr,encoding='utf-8')
assert result.returncode==0, result.stderr
validate=runpy.run_path(str(source))['validar']
errors=[]
for fid,panels in data.items():
    err,_=validate(panels,sum(p['tipo'] in ('micro','espectro') and 'padre' not in p for p in panels))
    if err: errors.append({'fig_id':fid,'error':err})
assert not errors, errors
queue=pd.read_csv(STAGE/'cola_cajas.csv',encoding='utf-8-sig')
report={'fecha_utc':datetime.now(timezone.utc).isoformat(),'lotes':[p.stem for p in files], 'figuras':len(data),'errores_estructurales':errors,'figuras_en_cola':len(queue),'motivos_cola':queue[['fig_id','motivo']].to_dict('records'),'solo_codex':True,'fuente_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'salida':result.stdout,'validacion_formato':'PASS','conteos': 'REQUIEREN_REVISION' if len(queue) else 'PASS'}
(OUT/'VALIDACION_RONDA4.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
with (OUT/'CHECKPOINTS_RONDA4.md').open('a',encoding='utf-8') as f: f.write(f'\n- Validación aislada {report["fecha_utc"]}: {len(files)} lotes, {len(data)} figuras, 0 errores estructurales, {len(queue)} en cola por conteo.\n')
print(result.stdout)
print('PASS estructura; cola:',len(queue))
