"""Freeze the article intersection with existing images and valid descriptors."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'modelos'/'ronda2'))
from control import guard,write_json

def main():
    guard();table=pd.read_csv(ROOT/'curation'/'v0.1'/'tabla_modelo.csv',encoding='utf-8-sig',keep_default_na=False)
    desc=pd.read_csv(ROOT/'modelos'/'tabular'/'dataset_descriptores.csv',encoding='utf-8-sig',keep_default_na=False)
    for c in ['size_nm','zeta_mV','pdi']:desc[c]=pd.to_numeric(desc[c],errors='coerce')
    desc=desc[desc[['size_nm','zeta_mV','pdi']].notna().any(axis=1)];counts=desc.groupby('pmcid').size()
    images=table[table.clase_modelo.ne('')&table.fold.astype(str).ne('')].copy()
    images=images[images.ruta_imagen.map(lambda p:(ROOT/p).is_file() and (ROOT/p).stat().st_size>0)].drop_duplicates(['pmcid','image_file'])
    images=images[images.pmcid.isin(counts.index)]
    assert images.groupby('pmcid').fold.nunique().eq(1).all() and images.groupby('pmcid').clase_modelo.nunique().eq(1).all()
    cohort=images.groupby('pmcid',sort=True).agg(clase_modelo=('clase_modelo','first'),fold=('fold','first'),n_imagenes=('image_file','size')).reset_index()
    cohort['n_descriptores']=cohort.pmcid.map(counts).astype(int)
    assert cohort.pmcid.is_unique and cohort.fold.notna().all()
    HERE.mkdir(exist_ok=True);cohort.to_csv(HERE/'conjunto_comparacion.csv',index=False,encoding='utf-8-sig')
    images[['pmcid','image_file','fold']].to_csv(HERE/'imagenes_comparacion.csv',index=False,encoding='utf-8-sig')
    summary={'articulos':len(cohort),'imagenes':len(images),'por_clase':cohort.clase_modelo.value_counts().to_dict(),'por_fold':{str(k):int(v) for k,v in cohort.fold.value_counts().sort_index().items()},'nota':'Instantánea de imágenes existentes no vacías; no se descargan ni procesan imágenes.'}
    write_json(HERE/'validacion_conjunto.json',summary);print(summary);guard()

if __name__=='__main__':main()
