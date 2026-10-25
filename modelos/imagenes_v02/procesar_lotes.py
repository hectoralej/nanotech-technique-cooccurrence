from __future__ import annotations

import csv, hashlib, json, random, re, sys, time, zipfile, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import Counter, defaultdict
from pathlib import Path, PurePosixPath
from urllib.request import Request, urlopen

import numpy as np
import pandas as pd
from PIL import Image, ImageFilter, ImageOps, ImageDraw, ImageFont
from lxml import etree

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "modelos" / "imagenes_v02"
OLD = ROOT / "producto" / "imagenes"
NEW = ROOT / "producto" / "imagenes_v02"
CROPS = ROOT / "producto" / "imagenes_recortes"
FT = ROOT / "data" / "cache" / "fulltext"
XLINK = "http://www.w3.org/1999/xlink"
MICRO = re.compile(r"\bTEM\b|\bSEM\b|\bSTEM\b|HRTEM|cryo[- ]?(?:EM|TEM)|transmission electron|scanning electron|micrograph|\bAFM\b", re.I)
SPECT = re.compile(r"\bXRD\b|diffraction|FT\s?-?IR|infrared|UV\s?-?Vis|absorbance|absorption spectrum|\bSAXS\b|\bEDS\b|\bEDX\b|Raman|\bSERS\b|\bDLS\b|zeta", re.I)
TECHS = [(x, re.compile(p, re.I)) for x, p in [("TEM", r"\bTEM\b|transmission electron"),("SEM",r"\bSEM\b|scanning electron"),("STEM",r"\bSTEM\b"),("HRTEM",r"HRTEM"),("cryo-EM",r"cryo[- ]?(?:EM|TEM)"),("AFM",r"\bAFM\b"),("XRD",r"\bXRD\b|diffraction"),("FTIR",r"FT\s?-?IR|infrared"),("UVVis",r"UV\s?-?Vis|absorbance|absorption spectrum"),("SAXS",r"\bSAXS\b"),("EDS",r"\bEDS\b|\bEDX\b"),("Raman",r"Raman|\bSERS\b"),("DLS",r"\bDLS\b"),("zeta",r"zeta")]]
EXT_OK = {".jpg", ".jpeg", ".png", ".gif", ".tif", ".tiff", ".webp"}
MIN_PANEL = 0.055
WHITE = 0.97
GAP_MIN = 0.012
_request_lock = threading.Lock()
_last_request = 0.0

def read_csv(name):
    return pd.read_csv(ROOT / "curation" / name, dtype=str, keep_default_na=False, encoding="utf-8-sig")

def figkey(s):
    m = re.search(r"(\d+)", s or "")
    return m.group(1) if m else re.sub(r"\W+", "", (s or "").lower())

def get_figures(pmc):
    path = FT / f"{pmc}.xml"
    if not path.exists():
        return None
    root = etree.fromstring(path.read_bytes(), parser=etree.XMLParser(recover=True, resolve_entities=False, no_network=True, load_dtd=False, huge_tree=True))
    out=[]
    for fig in root.xpath(".//fig[not(ancestor::ref-list)]"):
        lab=fig.find("label"); cap=fig.find("caption")
        label=" ".join("".join(lab.itertext()).split()) if lab is not None else (fig.get("id") or "fig")
        caption=" ".join("".join(cap.itertext()).split()) if cap is not None else ""
        hrefs=fig.xpath(".//graphic/@xlink:href | .//inline-graphic/@xlink:href",namespaces={"xlink":XLINK})
        files=[]
        for h in hrefs:
            n=PurePosixPath(str(h).replace("\\","/")).name
            if n and Path(n).suffix.lower() in EXT_OK and n not in files: files.append(n)
        if not files:
            files=[""]
        out.append({"label":label,"key":figkey(label),"caption":caption[:300],"files":files})
    return out

def classify(cap):
    m=bool(MICRO.search(cap)); s=bool(SPECT.search(cap))
    return "mixta" if m and s else "micrografia" if m else "espectro" if s else "otra"

def list_zip_members(zf):
    out={}
    for raw in zf.namelist():
        normalized=raw.replace("\\","/")
        name=PurePosixPath(normalized).name
        if name and Path(name).suffix.lower() in EXT_OK:
            out.setdefault(name,raw)
    return out

def safe_download(pmc, names):
    target=NEW/pmc; target.mkdir(parents=True,exist_ok=True)
    missing=[n for n in names if n and not (OLD/pmc/n).exists() and not (target/n).exists()]
    if not missing: return [[pmc,n,1,(OLD/pmc/n).stat().st_size if (OLD/pmc/n).exists() else (target/n).stat().st_size,"ya presente"] for n in names if n]
    url=f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmc}/supplementaryFiles"
    try:
        global _last_request
        with _request_lock:
            wait=max(0.,.6-(time.monotonic()-_last_request))
            if wait: time.sleep(wait)
            _last_request=time.monotonic()
        req=Request(url,headers={"User-Agent":"nanotech-image-curation/0.2"})
        with urlopen(req,timeout=10) as r: blob=r.read()
        ztmp=OUT/"tmp"/f"{pmc}.zip"; ztmp.parent.mkdir(parents=True,exist_ok=True); ztmp.write_bytes(blob)
        rows=[]
        with zipfile.ZipFile(ztmp) as z:
            members=list_zip_members(z)
            for n in missing:
                if n not in members:
                    rows.append([pmc,n,0,0,"no está en el zip"]); continue
                dest=target/n
                try:
                    data=z.read(members[n]); dest.write_bytes(data)
                    with Image.open(dest) as im: im.verify()
                    rows.append([pmc,n,1,len(data),"Europe PMC zip"])
                except Exception as e:
                    dest.unlink(missing_ok=True); rows.append([pmc,n,0,0,f"imagen inválida: {str(e)[:100]}"])
        ztmp.unlink(missing_ok=True)
        by={r[1]:r for r in rows}
        return [by.get(n,[pmc,n,1,(OLD/pmc/n).stat().st_size if (OLD/pmc/n).exists() else (target/n).stat().st_size,"ya presente"]) for n in names if n]
    except Exception as e:
        return [[pmc,n,0,0,f"descarga fallida: {str(e)[:120]}"] for n in missing] + [[pmc,n,1,0,"ya presente"] for n in names if n and ((OLD/pmc/n).exists() or (target/n).exists())]

def split_white(im):
    im=ImageOps.exif_transpose(im).convert("RGB")
    w,h=im.size
    if w*h<40000: return [im]
    arr=np.asarray(im.resize((min(1200,w),min(1200,h))))/255.0
    H,W=arr.shape[:2]; white=np.min(arr,axis=2)>WHITE
    pieces=[(0,0,W,H)]
    # recursively use the widest qualifying full-width/full-height white band
    for _ in range(12):
        best=None
        for idx,(x0,y0,x1,y1) in enumerate(pieces):
            sub=white[y0:y1,x0:x1]; sh,sw=sub.shape
            for axis,profile in [(0,sub.mean(axis=1)),(1,sub.mean(axis=0))]:
                mask=profile>=0.985; i=0
                while i<len(mask):
                    if not mask[i]: i+=1; continue
                    j=i+1
                    while j<len(mask) and mask[j]: j+=1
                    span=(j-i)/(sh if axis==0 else sw)
                    if span>=GAP_MIN and i>0 and j<(sh if axis==0 else sw):
                        score=span*(sw if axis==0 else sh)
                        if best is None or score>best[0]: best=(score,idx,axis,i,j)
                    i=j
        if best is None: break
        _,idx,axis,a,b=best; x0,y0,x1,y1=pieces.pop(idx)
        if axis==0: cuts=[(x0,y0,x1,y0+a),(x0,y0+b,x1,y1)]
        else: cuts=[(x0,y0,x0+a,y1),(x0+b,y0,x1,y1)]
        for box in cuts:
            xx0,yy0,xx1,yy1=box
            if (xx1-xx0)*(yy1-yy0)>=MIN_PANEL*W*H and (xx1-xx0)>=max(80,.08*W) and (yy1-yy0)>=max(80,.08*H):
                # Avoid treating isolated caption text or nearly empty margins as a panel.
                if 1-float(white[yy0:yy1,xx0:xx1].mean()) >= .008: pieces.append(box)
        if len(pieces)<2: pieces=[(0,0,W,H)]; break
    if len(pieces)<=1: return [im]
    pieces.sort(key=lambda b:(b[1],b[0]))
    result=[]
    for x0,y0,x1,y1 in pieces:
        box=(int(x0*w/W),int(y0*h/H),int(x1*w/W),int(y1*h/H))
        if box[2]>box[0] and box[3]>box[1]: result.append(im.crop(box))
    return result or [im]

def score_crop(im):
    a=np.asarray(im.convert("RGB").resize((min(320,im.width),min(320,im.height))))/255.
    white=float((np.min(a,axis=2)>.94).mean())
    sat=float((a.max(axis=2)-a.min(axis=2)).mean())
    gray=1-min(1.,sat/.28)
    gray_img=np.asarray(Image.fromarray(np.uint8(a*255)).convert("L").filter(ImageFilter.FIND_EDGES))/255.
    edge=float((gray_img>.10).mean())
    texture=min(1.,edge/.16)
    aspect=im.width/max(1,im.height)
    pm=max(0.,min(1.,.52*gray+.48*texture*(1-white)))
    pg=max(0.,min(1.,.55*white+.28*min(1.,edge/.11)+.17*(1-min(1.,abs(np.log(max(aspect,.01)))/2))))
    kind="mixto_o_dudoso" if sat>.30 else "micrografia_probable" if pm>=.60 and pm>pg+.08 else "grafica_probable" if pg>=.58 and pg>pm+.04 else "mixto_o_dudoso"
    return kind,round(pm,4),round(pg,4),round(white,4),round(sat,4),round(edge,4),round(aspect,4)

def main():
    OUT.mkdir(parents=True,exist_ok=True); (OUT/"muestras").mkdir(exist_ok=True)
    arts=read_csv("ext_articulos.csv").reset_index(names="source_order")
    arts=arts[arts.tier.isin(["E1","E2"])].copy()
    arts["tier_order"]=arts.tier.map({"E1":0,"E2":1}).fillna(2)
    arts=arts.sort_values(["tier_order","source_order"],kind="stable").reset_index(drop=True)
    panels=read_csv("ext_paneles.csv"); specs=read_csv("ext_espectros.csv")
    model=pd.read_csv(ROOT/"curation"/"v0.1"/"tabla_modelo.csv",dtype=str,keep_default_na=False)
    classes=model.drop_duplicates("pmcid").set_index("pmcid")["clase_modelo"].to_dict()
    folds=model.drop_duplicates("pmcid").set_index("pmcid")["fold"].to_dict()
    pbase=defaultdict(set); sbase=defaultdict(set)
    for _,r in panels.iterrows(): pbase[r.pmcid].add(figkey(r.fig))
    for _,r in specs.iterrows(): sbase[r.pmcid].add(figkey(r.fig))
    progress_path=OUT/"progreso.json"
    prog=json.loads(progress_path.read_text(encoding="utf-8")) if progress_path.exists() else {"articulos_hechos":0,"lote_actual":0,"errores":[],"lotes":[]}
    if prog.get("pausa_por_calidad_visual"):
        raise SystemExit("PAUSA: dos lotes consecutivos quedaron por debajo de 3/5; ajuste pendiente.")
    start=int(prog.get("articulos_hechos",0)); previous=prog.get("ultimo_lote",{})
    # An incomplete visual checkpoint is not a closed batch: replay that batch.
    if start and int(previous.get("muestra_n",5)) < 5:
        start=max(0,start-100); prog["articulos_hechos"]=start; prog["lote_actual"]=max(0,int(prog.get("lote_actual",1))-1)
    end=min(start+100,len(arts)); batch=int(prog.get("lote_actual",0))+1
    if start>=len(arts): print("COMPLETO",len(arts)); return
    batch_pmc=set(arts.iloc[start:end].pmcid)
    inv=[]; downloads=[]; crops=[]; errors=[]; pending_downloads=[]
    inventory_path=OUT/"inventario_figuras.csv"
    already=set()
    if inventory_path.exists():
        prev=pd.read_csv(inventory_path,dtype=str,keep_default_na=False)
        already=set(zip(prev.pmcid,prev.figura,prev.archivo_grafico))
    for ix in range(start,end):
        pmc=arts.iloc[ix].pmcid
        try:
            figs=get_figures(pmc)
            if figs is None: raise FileNotFoundError("XML JATS ausente")
            all_names=[]
            for f in figs:
                typ=classify(f["caption"])
                if typ=="otra": continue
                techniques="|".join(t for t,rx in TECHS if rx.search(f["caption"]))
                base=bool((typ in ("micrografia","mixta") and f["key"] in pbase[pmc]) or (typ in ("espectro","mixta") and f["key"] in sbase[pmc]))
                for name in f["files"]:
                    key=(pmc,f["label"],name)
                    if key in already: continue
                    inv.append([pmc,f["label"],name,f["caption"],typ,techniques,int(base),classes.get(pmc,""),folds.get(pmc,"")])
                    already.add(key)
                    if name: all_names.append(name)
            pending_downloads.append((pmc,sorted(set(all_names))))
        except Exception as e:
            errors.append({"pmcid":pmc,"error":str(e)[:200]})
    with ThreadPoolExecutor(max_workers=4) as pool:
        futs=[pool.submit(safe_download,pmc,names) for pmc,names in pending_downloads]
        for fut in as_completed(futs):
            try: downloads.extend(fut.result())
            except Exception as e: errors.append({"error":f"descarga: {str(e)[:180]}"})
    # Persist inventory and download ledger append-only / idempotent.
    cols=["pmcid","figura","archivo_grafico","pie","tipo_figura","tecnicas_en_pie","ya_en_base","clase_modelo","fold"]
    if inv:
        new=pd.DataFrame(inv,columns=cols)
        allinv=pd.concat([pd.read_csv(inventory_path,dtype=str,keep_default_na=False) if inventory_path.exists() else pd.DataFrame(columns=cols),new],ignore_index=True).drop_duplicates(["pmcid","figura","archivo_grafico"])
        allinv.to_csv(inventory_path,index=False,encoding="utf-8-sig")
    dpath=OUT/"descargas_v02.csv"; dcols=["pmcid","archivo","ok","bytes","motivo"]
    if downloads:
        old=pd.read_csv(dpath,dtype=str,keep_default_na=False) if dpath.exists() else pd.DataFrame(columns=dcols)
        pd.concat([old,pd.DataFrame(downloads,columns=dcols)],ignore_index=True).drop_duplicates(["pmcid","archivo"],keep="last").to_csv(dpath,index=False,encoding="utf-8-sig")
    invall=pd.read_csv(inventory_path,dtype=str,keep_default_na=False) if inventory_path.exists() else pd.DataFrame(columns=cols)
    new_invall=invall[invall.pmcid.isin(batch_pmc)]
    for _,r in new_invall.iterrows():
        name=r.archivo_grafico
        if not name: continue
        src=OLD/r.pmcid/name
        origin="v0.1" if src.exists() else "nuevo"
        if not src.exists(): src=NEW/r.pmcid/name
        if not src.exists(): continue
        try:
            with Image.open(src) as raw:
                raw.load(); panels_out=split_white(raw)
            tech_list=[x for x in (r.tecnicas_en_pie or "").split("|") if x]
            technique=tech_list[0] if len(tech_list)==1 else ""
            # subpanel technique assignment is conservative: assign only exact label count.
            labels=re.findall(r"\(([a-z])\)\s*([^,;.)]{2,50})",r.pie,re.I)
            label_tech=[next((t for t,rx in TECHS if rx.search(text)),"") for _,text in labels]
            assigned=label_tech if len(label_tech)==len(panels_out) and len(panels_out)>1 else [""]*len(panels_out)
            for i,im in enumerate(panels_out,1):
                dest=CROPS/r.pmcid/f"{Path(name).stem}_p{i}.png"; dest.parent.mkdir(parents=True,exist_ok=True)
                im.save(dest,format="PNG",optimize=True)
                kind,pm,pg,white,sat,edge,aspect=score_crop(im)
                crops.append([r.pmcid,r.figura,name,str(dest.relative_to(ROOT)).replace("\\","/"),len(panels_out),kind,pm,pg,assigned[i-1] or technique,r.clase_modelo,r.fold,origin,white,sat,edge,aspect])
        except Exception as e:
            errors.append({"pmcid":r.pmcid,"archivo":name,"error":str(e)[:160]})
    cpath=OUT/"recortes_v02.csv"; ccols=["pmcid","figura","archivo_original","archivo_recorte","n_recortes_figura","tipo_estimado","p_micrografia","p_grafica","tecnica_asignada","clase_modelo","fold","origen","fraccion_blanca","saturacion_media","densidad_bordes","relacion_aspecto"]
    if crops:
        old=pd.read_csv(cpath,dtype=str,keep_default_na=False) if cpath.exists() else pd.DataFrame(columns=ccols)
        pd.concat([old,pd.DataFrame(crops,columns=ccols)],ignore_index=True).drop_duplicates(["pmcid","archivo_original","archivo_recorte"],keep="last").to_csv(cpath,index=False,encoding="utf-8-sig")
    # Fixed, reproducible stratified visual sample; requires two of each target type when available.
    allc=pd.read_csv(cpath,dtype=str,keep_default_na=False) if cpath.exists() else pd.DataFrame(columns=ccols)
    bc=allc[allc.pmcid.isin(batch_pmc)].copy()
    sample_seed=20261023+batch
    rng=random.Random(sample_seed)
    mic=bc[bc.tipo_estimado=="micrografia_probable"].to_dict("records")
    graph=bc[(bc.tipo_estimado=="grafica_probable")&bc.tecnica_asignada.ne("")].to_dict("records")
    other=bc.to_dict("records")
    chosen=[]
    for pool,n in [(mic,2),(graph,2)]:
        rng.shuffle(pool); chosen.extend(pool[:n])
    remaining=[x for x in other if x not in chosen]; rng.shuffle(remaining); chosen.extend(remaining[:max(0,5-len(chosen))])
    samplepath=OUT/"muestras"/f"muestra_lote_{batch:02d}.png"
    if chosen:
        W,H=1500,5*410; sheet=Image.new("RGB",(W,H),"white"); d=ImageDraw.Draw(sheet); font=ImageFont.truetype("arial.ttf",18) if Path("C:/Windows/Fonts/arial.ttf").exists() else ImageFont.load_default()
        for j,r in enumerate(chosen[:5]):
            y=j*410; d.text((15,y+8),f"{r['pmcid']} · {r['figura']} · {r['tipo_estimado']} · {r['tecnica_asignada'] or 'técnica no asignable'}",fill="black",font=font)
            crop=ROOT/Path(r["archivo_recorte"]); orig=OLD/r["pmcid"]/r["archivo_original"]
            if not orig.exists(): orig=NEW/r["pmcid"]/r["archivo_original"]
            for x,path in [(20,crop),(770,orig)]:
                if path.exists():
                    with Image.open(path) as im:
                        im.thumbnail((700,330)); sheet.paste(im.convert("RGB"),(x,y+42))
            d.text((770,y+375),"Figura original" if orig.exists() else "Original no disponible",fill="#444",font=font)
        samplepath.parent.mkdir(parents=True,exist_ok=True); sheet.save(samplepath)
    invbatch=invall[invall.pmcid.isin(batch_pmc)]
    failed_dl=0 if not dpath.exists() else int((pd.read_csv(dpath,dtype=str,keep_default_na=False).pmcid.isin(batch_pmc)&(pd.read_csv(dpath,dtype=str,keep_default_na=False).ok=="0")).sum())
    pms=arts.iloc[:end].pmcid.tolist(); done=set(pms)
    invall_now=pd.read_csv(inventory_path,dtype=str,keep_default_na=False) if inventory_path.exists() else pd.DataFrame(columns=cols)
    c_all=pd.read_csv(cpath,dtype=str,keep_default_na=False) if cpath.exists() else pd.DataFrame(columns=ccols)
    # F1/F3 invariants across everything produced so far.
    assert not invall_now.duplicated(["pmcid","figura","archivo_grafico"]).any(),"figuras duplicadas"
    assert all(invall_now.groupby("pmcid").fold.nunique(dropna=False)<=1),"fold inconsistente"
    assert all(c_all.groupby("pmcid").fold.nunique(dropna=False)<=1),"fold inconsistente recortes"
    previous_errors=[e for e in prog.get("errores",[]) if not (e.get("pmcid") in batch_pmc and "WinError 5" in e.get("error",""))]
    prog.update({"lote_actual":batch,"articulos_hechos":end,"total_articulos":len(arts),"errores":(previous_errors+errors)[-500:],"ultimo_lote":{"lote":batch,"articulos_lote":len(batch_pmc),"figuras_candidatas":len(invbatch),"nuevas_micrografias":int(invbatch.tipo_figura.isin(["micrografia","mixta"]).sum()),"nuevos_espectros":int(invbatch.tipo_figura.isin(["espectro","mixta"]).sum()),"recortes":len(bc),"muestra":str(samplepath),"muestra_n":len(chosen),"descargas_fallidas":failed_dl,"errores":len(errors),"siguiente_paso":f"lote {batch+1}" if end<len(arts) else "validación final"},"lotes":prog.get("lotes",[])+[{"lote":batch,"inicio_indice":start,"fin_indice":end,"pmcid_desde":arts.iloc[start].pmcid,"pmcid_hasta":arts.iloc[end-1].pmcid}]})
    progress_path.write_text(json.dumps(prog,ensure_ascii=False,indent=2),encoding="utf-8")
    check=OUT/"CHECKPOINTS.md"; stamp=time.strftime("%Y-%m-%d %H:%M:%S")
    with check.open("a",encoding="utf-8") as f:
        f.write(f"\n## {stamp} · Lote {batch:02d}\n- Artículos acumulados: {end}/{len(arts)}; figuras candidatas acumuladas: {len(invall_now)}; recortes acumulados: {len(c_all)}.\n- Lote: {len(batch_pmc)} artículos; figuras candidatas {len(invbatch)}, nuevas micrografías/mixtas {int(invbatch.tipo_figura.isin(['micrografia','mixta']).sum())}, espectros/mixtas {int(invbatch.tipo_figura.isin(['espectro','mixta']).sum())}; descargas fallidas {failed_dl}; errores {len(errors)}.\n- Muestra aleatoria semilla {sample_seed}: {len(chosen)}/5; inspección humana pendiente; bien extraídas: pendiente.\n- Próximo paso: lote {batch+1 if end<len(arts) else 'validación final'}.\n")
    print(json.dumps(prog["ultimo_lote"],ensure_ascii=False))

if __name__=="__main__":
    raise SystemExit('Flujo anterior retirado. Usar ajuste1.py; las descargas están delegadas a descargar_v02.py de Claude.')
