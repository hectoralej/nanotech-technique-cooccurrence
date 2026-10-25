"""Guarda decisiones manuales de cola; no detecta paneles automáticamente."""
from pathlib import Path
import json,runpy,sys
from datetime import datetime,timezone
OUT=Path(__file__).resolve().parent
PLAN=json.loads((OUT/'PLAN_COLA_D.json').read_text(encoding='utf-8'))
source=OUT.parents[2]/'consolidar_cajas.py'
code=source.read_text(encoding='utf-8-sig')
assert 'if area(c) < 0.005:' in code
code=code.replace('if area(c) < 0.005:', 'if area(c) <= 0:')  # excepción autorizada: conservar paneles e insets reales pequeños
code=code.replace('if m > 0 and inter(top[i]["caja"], top[j]["caja"]) / m > 0.3:', 'if m > 0 and inter(top[i]["caja"], top[j]["caja"]) / m > 0.3 and not (top[i]["tipo"] == top[j]["tipo"] == "espectro" and top[i].get("cascada") and top[j].get("cascada")):')
ns={'__file__':str(source),'__name__':'validacion_d_aislada'}
exec(compile(code,str(source),'exec'),ns)
validar=ns['validar']
n=int(sys.argv[1]);p=PLAN[n-1];assert p['n']==n
d=json.loads(sys.stdin.read());assert 'paneles' in d and 'nota' in d
for b in d['paneles']:
 b['caja']=[round(float(x),3) for x in b['caja']]
 assert all(0<=x<=1 for x in b['caja'])
 if b['tipo']=='micro':b.setdefault('contenido','particulas')
 if b.get('contenido') in ['biologico','particulas_en_contexto_biologico']:assert b['tipo']=='otro' and b.get('tecnica')
err,aviso=validar(d['paneles'],p['esperado'] if p['esperado'] is not None else 0)
assert not err,(n,p['fig_id'],err)
dec=OUT/'D_decisiones.jsonl'
prev=[json.loads(l) for l in dec.read_text(encoding='utf-8').splitlines()] if dec.exists() else []
assert n not in {x['n'] for x in prev},'Decisión ya guardada'
small=[k for k,b in enumerate(d['paneles'],1) if (b['caja'][2]-b['caja'][0])*(b['caja'][3]-b['caja'][1])<.005]
row=dict(n=n,fig_id=p['fig_id'],lote=p['lote'],paneles=d['paneles'],nota=d['nota'],aviso_conteo=aviso,paneles_pequenos=small,fecha_utc=datetime.now(timezone.utc).isoformat(),imagen=p['imagen'],revision_visual_original=True)
with dec.open('a',encoding='utf-8') as h:h.write(json.dumps(row,ensure_ascii=False)+'\n')
prev.append(row);group=[x for x in prev if x['lote']==p['lote']];expected=[x for x in PLAN if x['lote']==p['lote']]
if len(group)==len(expected):
 target=OUT/(p['lote']+'.json');assert not target.exists()
 result={x['fig_id']:x['paneles'] for x in sorted(group,key=lambda x:x['n'])}
 result['_revision']=dict(reglas='INSTRUCCIONES_CAJAS v2 + contenido 25-oct',metodo='Revisión manual de originales de cola',excepciones_autorizadas=['paneles e insets menores de 0.5% conservados y reportados','solape permitido entre espectros en cascada'],paneles_pequenos={x['fig_id']:x.get('paneles_pequenos',[]) for x in group if x.get('paneles_pequenos')},notas={x['fig_id']:x['nota'] for x in group if x['nota']},discrepancias_conteo={x['fig_id']:x['aviso_conteo'] for x in group if x['aviso_conteo']})
 tmp=target.with_suffix('.json.tmp');tmp.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');tmp.replace(target)
 with (OUT/'CHECKPOINTS_COLA_D.md').open('a',encoding='utf-8') as h:h.write(f"\n- {row['fecha_utc']}: {p['lote']} guardado, {len(group)} figuras; {sum(bool(x['aviso_conteo']) for x in group)} discrepancias de conteo vigente, 0 errores estructurales.\n")
 print('LOTE GUARDADO',p['lote'])
print(n,p['fig_id'],len(d['paneles']),'cajas;',aviso or 'conteo coincide')
