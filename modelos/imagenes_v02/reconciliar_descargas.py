import csv
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"modelos"/"imagenes_v02"
NEW=ROOT/"producto"/"imagenes_v02"
path=OUT/"descargas_v02.csv"
with path.open(encoding="utf-8-sig",newline="") as f:
    rows=list(csv.DictReader(f)); fields=["pmcid","archivo","ok","bytes","motivo"]
known={(r["pmcid"],r["archivo"]):i for i,r in enumerate(rows)}
added=0
for f in NEW.glob("*/*"):
    if not f.is_file(): continue
    key=(f.parent.name,f.name)
    try:
        with Image.open(f) as im: im.verify()
        value=dict(pmcid=key[0],archivo=key[1],ok="1",bytes=str(f.stat().st_size),motivo="disponible en imagenes_v02; PIL verificado")
    except Exception as e:
        value=dict(pmcid=key[0],archivo=key[1],ok="0",bytes="0",motivo=f"archivo inválido: {str(e)[:100]}")
    if key in known: rows[known[key]]=value
    else: known[key]=len(rows); rows.append(value); added+=1
with path.open("w",encoding="utf-8-sig",newline="") as f:
    w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)
ok=[r for r in rows if r["ok"]=="1"]
fresh=[r for r in ok if r["motivo"]=="disponible en imagenes_v02; PIL verificado"]
print(f"added={added} rows={len(rows)} ok={len(ok)} failed={len(rows)-len(ok)} verified_in_new_folder={len(fresh)}")
