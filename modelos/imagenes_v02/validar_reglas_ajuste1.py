"""Comprobaciones concretas de fallos anteriores y reglas; sin modificar datos de artículos."""
import json
import numpy as np
from PIL import Image,ImageDraw
import ajuste1 as a
cases=[]
empty=a.ROOT/'producto/imagenes_recortes/PMC11945751/pharmaceuticals-18-00414-g002_p1.png'
with Image.open(empty) as im: st,reasons=a.statistics(im)
assert 'tinta_menor_2pct' in reasons and 'proporcion_mayor_8_a_1' in reasons
cases.append({'caso':'texto drying del fallo anterior','resultado':'rechazado','motivos':reasons})
drawing=a.ROOT/'producto/imagenes_recortes/PMC10172346/41598_2023_33893_Fig4_HTML_p4.png'
with Image.open(drawing) as im: st,reasons=a.statistics(im)
assert st['tipo_estimado'] not in ['grafica_probable','micrografia_probable']
cases.append({'caso':'ilustración con gradientes del fallo anterior','resultado':st['tipo_estimado'],'limite':'El dibujo con gradientes queda dudoso; no todas las ilustraciones reales se reconocen como ilustracion_probable.'})
fixture=Image.new('RGB',(300,300),'white');d=ImageDraw.Draw(fixture)
for box,color in [((20,20,130,130),'red'),((150,20,270,140),'blue'),((70,150,230,280),'green')]: d.ellipse(box,fill=color)
st,reasons=a.statistics(fixture);assert st['tipo_estimado']=='ilustracion_probable'
cases.append({'caso':'fixture sintético de colores planos (solo prueba, fuera del dataset)','resultado':st['tipo_estimado']})
assert a.panel_tech('(a) TEM image; (b) Histogram derived from TEM measurements.',2)[0]==['TEM','']
assert a.panel_tech('(a) TEM image; (b) XRD spectrum.',3)[0]==['','','']
assert a.panel_tech('DLS (A), SEM (B).',2)[0]==['','']
assert a.panel_tech('Characterization of silver nanoparticles. (a) UV-Vis spectrum of synthesized AgNPs. (b) Image of FESEM and (c) FTIR spectrum of synthesized AgNPs.',3)[0]==['','','']
assert 'SEM' not in a.tech('Data are mean ± SEM.')
assert 'DLS' not in a.tech('Particle size distribution derived from TEM')
cases.append({'caso':'técnica panel, conteo incompatible, SEM estadístico y DLS no inferido','resultado':'PASS'})
(a.OUT/'REGRESIONES_AJUSTE1.json').write_text(json.dumps({'estado':'PASS','casos':cases},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'estado':'PASS','casos':len(cases)}))
