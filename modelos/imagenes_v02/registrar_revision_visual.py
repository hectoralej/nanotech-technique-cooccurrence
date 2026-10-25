import csv, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"modelos"/"imagenes_v02"
reviews=[
    [1,1,"PMC11421787","Fig 1",1,"Micrografías C–D completas y reconocibles; el recorte coincide con los paneles indicados."],
    [1,2,"PMC12071938","Figure 5",0,"No separa TEM de histogramas; devuelve una composición mixta como micrografía."],
    [1,3,"PMC10172346","Figure 4",0,"Recorte de ilustración esquemática dentro de una figura TEM/SAXS; no es un espectro."],
    [1,4,"PMC11945751","Figure 2",0,"Recorte casi vacío con texto; la micrografía quedó fuera."],
    [1,5,"PMC12940844","Figure 2",0,"Conserva una composición SEM/mapas sin separar los paneles."],
    [2,1,"PMC9647953","Fig. 1",0,"Composición con distribuciones y TEM sin separar; clasificada como micrografía."],
    [2,2,"PMC10135330","Figure 5",0,"Recorte parcial de la composición SEM; faltan paneles presentes en la figura original."],
    [2,3,"PMC11672701","Figure 2",0,"Recorta histogramas de tamaño, no espectros, y hereda TEM de otro panel."],
    [2,4,"PMC11152947","Fig 1",1,"Panel FTIR completo y reconocible; técnica correcta."],
    [2,5,"PMC10799878","Figure 3",1,"Distribución de zeta completa y reconocible; técnica correcta."],
]
with (OUT/"revision_muestras.csv").open("w",newline="",encoding="utf-8-sig") as f:
    w=csv.writer(f); w.writerow(["lote","muestra","pmcid","figura","bien_extraida","veredicto"]); w.writerows(reviews)
p=OUT/"progreso.json"
d=json.loads(p.read_text(encoding="utf-8"))
d["total_articulos"]=1707
d["errores"]=[e for e in d.get("errores",[]) if "WinError 5" not in e.get("error","")]
dedup={}
for x in d.get("lotes",[]): dedup[x["lote"]]=x
d["lotes"]=list(dedup.values())
d["pausa_por_calidad_visual"]=True
d["calidad_muestras"]={"lote_1":"1/5","lote_2":"2/5","regla":"Dos lotes consecutivos por debajo de 3/5: pausar antes del lote 3.","muestras_revisadas":10}
d["ultimo_lote"]["bien_extraidas_muestra"]=2
d["ultimo_lote"]["validacion_calidad_visual"]="FAIL: 2 lotes consecutivos <3/5; corrida pausada según brief"
d["ultimo_lote"]["siguiente_paso"]="ajustar y revalidar lotes 1–2 antes de reanudar"
p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8")
print("registradas 10 evaluaciones visuales; corrida pausada por regla de calidad")
