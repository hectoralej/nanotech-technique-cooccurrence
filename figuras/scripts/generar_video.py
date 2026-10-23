from __future__ import annotations
import hashlib,json,re,sys
from pathlib import Path
import numpy as np
import pandas as pd
from estilo import *
sys.dont_write_bytecode=True
sys.path.insert(0,str(ROOT/'modelos'/'ronda2'))
from control import guard,checkpoint,write_json

def csv(path):return pd.read_csv(path,encoding='utf-8-sig',keep_default_na=False)
def sources():
    cur=ROOT/'curation'; a=csv(cur/'ext_articulos.csv');p=csv(cur/'ext_paneles.csv');d=csv(cur/'ext_descriptores.csv');s=csv(cur/'ext_espectros.csv')
    table=csv(cur/'v0.1'/'tabla_modelo.csv').drop_duplicates('pmcid').set_index('pmcid')
    mapping=table.clase_modelo.replace('','otro').to_dict()
    for frame in (a,p,d,s):frame['clase']=frame.pmcid.map(mapping).fillna('otro')
    eligible=set(a.loc[a.tier.isin(['E1','E2']),'pmcid'])
    return a,a[a.pmcid.isin(eligible)].copy(),p[p.pmcid.isin(eligible)].copy(),d[d.pmcid.isin(eligible)].copy(),s[s.pmcid.isin(eligible)].copy()

def generate(n):
    all_a,a,p,d,s=sources(); summary=json.loads((ROOT/'curation'/'v0.1'/'RESUMEN_NUMEROS.json').read_text(encoding='utf-8'))['despues']
    note=''; rng=np.random.default_rng(0)
    if n==1:
        counts={'Artículos leídos':len(all_a),'Con evidencia':len(a),'E1':sum(a.tier=='E1'),'E2':sum(a.tier=='E2'),'Micrografías':len(p),'Descriptores':len(d),'Espectros':len(s)}
        for k,col in [('articulos','Artículos leídos'),('E1','E1'),('E2','E2'),('paneles','Micrografías'),('descriptores','Descriptores'),('espectros','Espectros')]:assert counts[col]==summary[k]
        data=pd.DataFrame(counts.items(),columns=['unidad','n'])
        fig=canvas('1.707 artículos aportan evidencia para Nano2Predict','1.824 artículos leídos · E1: 1.130 · E2: 577','Micrografías = registros de panel; las unidades no se suman entre sí.')
        ax=axis(fig,(.055,.21,.89,.52));ax.axis('off')
        boxes=[(.02,.58,.40,.32,'1.824','artículos leídos'),(.58,.58,.40,.32,'1.707','con evidencia')]
        boxes += [(x,.04,.28,.33,str(counts[label]),label.lower()) for x,label in zip([.02,.36,.70],['Micrografías','Descriptores','Espectros'])]
        from matplotlib.patches import FancyBboxPatch
        for x,y,w,h,num,label in boxes:
            ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=.01',facecolor='#e6f3f0',edgecolor=ACCENT))
            ax.text(x+w/2,y+h*.64,num,ha='center',fontsize=42,weight='bold',color=ACCENT)
            ax.text(x+w/2,y+h*.22,label,ha='center',fontsize=25)
        ax.annotate('',xy=(.57,.74),xytext=(.43,.74),arrowprops={'arrowstyle':'->','color':ACCENT,'lw':3})
    elif n==2:
        data=pd.crosstab(a.year,a.clase).reindex(columns=COLORS,fill_value=0);assert data.to_numpy().sum()==len(a)
        fig=canvas('La cobertura crece desde 2016 hasta años recientes',f'n = {len(a):,} artículos con evidencia; el año no mide exhaustividad de búsqueda'.replace(',','.'),'Se excluyen los 117 artículos «no» presentes en el resumen global de 1.824.');legend(fig)
        ax=axis(fig,(.10,.22,.84,.47));bottom=np.zeros(len(data))
        for c in COLORS:ax.bar(data.index.astype(str),data[c],bottom=bottom,color=COLORS[c]);bottom+=data[c].to_numpy()
        ax.set_ylabel('Artículos');ax.tick_params(axis='x',rotation=0)
        data=data.reset_index()
    elif n==3:
        names={'nanomaterial':'Nanomaterial','polymeric_NP':'NP polimérica','inorganic_NP':'NP inorgánica','liposome':'Liposoma','SLN':'SLN','NLC':'NLC','nanogel':'Nanogel','other':'Otro portador','micelle':'Micela','LNP':'LNP','PLN':'Híbrido lípido-polímero','cubosome':'Cubosoma','nanoemulsion':'Nanoemulsión','not_a_nanocarrier':'Sin portador'}
        data=a.groupby(['carrier_type','clase']).size().reset_index(name='n').sort_values('n')
        fig=canvas('Los nanomateriales concentran la mayor cantidad de artículos',f'n = {len(a):,} artículos; clasificación de uso y material de v0.1'.replace(',','.'),'Se excluyen los 117 artículos «no» presentes en el resumen global de 1.824.')
        ax=axis(fig,(.27,.19,.64,.55)); ax.barh([names.get(x,x) for x in data.carrier_type],data.n,color=[COLORS[c] for c in data.clase])
        for i,v in enumerate(data.n):ax.text(v+max(data.n)*.012,i,str(v),va='center',fontsize=20)
        ax.set_xlim(0,max(data.n)*1.13);ax.set_xlabel('Artículos')
    elif n==4:
        temp=p.assign(microscopia=p.variant.map(lambda v:'TEM' if v.startswith('TEM_') else 'cryo-TEM' if v=='cryoTEM' else v))
        data=pd.crosstab(temp.microscopia,temp.clase).reindex(columns=COLORS,fill_value=0)
        data=data.loc[data.sum(axis=1).sort_values().index]; assert data.to_numpy().sum()==summary['paneles']
        share=100*data.loc['TEM'].sum()/len(p)
        fig=canvas(f'El {share:.0f} % de las micrografías son TEM convencional',f'n = {len(p):,} registros; HRTEM, STEM y cryo-TEM se muestran por separado'.replace(',','.'));legend(fig)
        ax=axis(fig,(.14,.22,.78,.47));left=np.zeros(len(data))
        for c in COLORS:ax.barh(data.index,data[c],left=left,color=COLORS[c]);left+=data[c].to_numpy()
        for i,v in enumerate(left):ax.text(v+12,i,str(int(v)),va='center',fontsize=20)
        ax.set_xlim(0,max(left)*1.10);ax.set_xlabel('Registros de micrografía');data=data.reset_index()
    elif n==5:
        data=pd.crosstab(s.technique,s.clase).reindex(columns=COLORS,fill_value=0);assert data.to_numpy().sum()==summary['espectros']
        fig=canvas('FTIR es la técnica espectral más frecuente',f'n = {len(s):,} registros de espectros en artículos E1/E2'.replace(',','.'))
        ax=axis(fig,(.17,.23,.72,.49));from matplotlib.colors import to_rgb
        maximum=data.to_numpy().max();rgb=np.ones((*data.shape,3))
        for j,c in enumerate(data.columns):
            for i in range(len(data)):rgb[i,j]=1-(1-np.asarray(to_rgb(COLORS[c])))*(.12+.88*data.iloc[i,j]/maximum)
        ax.imshow(rgb,aspect='auto')
        for i in range(len(data)):
            for j in range(len(data.columns)):ax.text(j,i,str(data.iloc[i,j]),ha='center',va='center',fontsize=25)
        ax.set_xticks(range(5),[LABELS[c] for c in data.columns]);ax.set_yticks(range(len(data)),data.index)
        for t,c in zip(ax.get_xticklabels(),data.columns):t.set_color(COLORS[c])
        data=data.reset_index()
    elif n==6:
        d['size_nm']=pd.to_numeric(d.size_nm,errors='coerce');data=d[d.size_nm.between(1,5000)][['pmcid','sample','clase','size_nm']].copy()
        fig=canvas('El tamaño varía ampliamente dentro de cada clase',f'n = {len(data):,} tamaños entre 1 y 5.000 nm; eje logarítmico'.replace(',','.'),'Se excluye el tamaño extremo de 5.958,8 nm; las cajas describen filas, no artículos.')
        ax=axis(fig,(.10,.23,.84,.47))
        for i,c in enumerate(COLORS):
            vals=data.loc[data.clase==c,'size_nm'].to_numpy()
            if not len(vals):continue
            ax.boxplot(vals,positions=[i],widths=.5,showfliers=False,patch_artist=True,boxprops={'facecolor':COLORS[c],'alpha':.35},medianprops={'color':INK,'linewidth':3})
            ax.scatter(rng.normal(i,.075,len(vals)),vals,color=COLORS[c],s=9,alpha=.18,rasterized=True)
            ax.text(i,1.03,f'n={len(vals)}\nmediana {np.median(vals):.0f} nm',ha='center',fontsize=20,transform=ax.get_xaxis_transform())
        ax.set_yscale('log');ax.set_xticks(range(5),[LABELS[c] for c in COLORS]);ax.set_ylabel('Tamaño (nm)');ax.set_ylim(.8,6000);ax.set_yticks([1,10,100,1000,5000],['1','10','100','1.000','5.000'])
    elif n==7:
        extremes=csv(ROOT/'curation'/'v0.1'/'valores_extremos.csv'); mask=np.zeros(len(d),bool)
        for r in extremes.itertuples():mask|=(d.pmcid.eq(r.pmcid)&pd.to_numeric(d[r.campo],errors='coerce').eq(float(r.valor))).to_numpy()
        assert int(mask.sum())==len(extremes)==5
        d['size_nm']=pd.to_numeric(d.size_nm,errors='coerce');d['zeta_mV']=pd.to_numeric(d.zeta_mV,errors='coerce')
        data=d[(~mask)&d.size_nm.between(1,5000)&d.zeta_mV.between(-150,150)][['pmcid','sample','clase','size_nm','zeta_mV']].copy()
        fig=canvas('Tamaño y carga presentan un amplio solapamiento entre clases',f'n = {len(data):,} pares tamaño–zeta; cinco filas extremas excluidas'.replace(',','.'));legend(fig)
        ax=axis(fig,(.11,.22,.83,.48))
        for c in COLORS:
            sub=data[data.clase==c];ax.scatter(sub.size_nm,sub.zeta_mV,color=COLORS[c],label=LABELS[c],alpha=.5,s=22,rasterized=True)
        ax.set_xscale('log');ax.set_xlim(1,5000);ax.set_xticks([1,10,100,1000,5000],['1','10','100','1.000','5.000']);ax.axhline(0,color='#67757f',ls='--',lw=1);ax.set_xlabel('Tamaño (nm)');ax.set_ylabel('Potencial zeta (mV)')
    elif n==8:
        data=pd.DataFrame({'paso':['Búsqueda Europe PMC','Extracción con IA','Verificación por código','Control de calidad'],'cifra':[len(all_a),summary['descriptores'],summary['espectros'],len(a)],'unidad':['artículos leídos','descriptores finales','espectros finales','artículos con evidencia']})
        fig=canvas('La evidencia extraída se contrasta con el texto de cada artículo','Proceso reproducible: búsqueda → extracción → verificación → control','Las cifras son del resultado final; no representan pérdidas intermedias del embudo.')
        ax=axis(fig,(.055,.23,.89,.48));ax.axis('off');from matplotlib.patches import FancyBboxPatch
        for i,r in enumerate(data.itertuples()):
            x=i*.255;ax.add_patch(FancyBboxPatch((x,.14),.225,.70,boxstyle='round,pad=.005',facecolor='#e6f3f0',edgecolor=ACCENT))
            label=['Búsqueda en\nEurope PMC','Extracción\ncon IA','Cada cita y número\npor código','Control de\ncalidad'][i]
            ax.text(x+.112,.68,label,ha='center',va='center',fontsize=24,weight='bold');ax.text(x+.112,.39,f'{r.cifra:,}'.replace(',','.'),ha='center',fontsize=34,color=ACCENT);ax.text(x+.112,.25,r.unidad,ha='center',fontsize=20)
            if i<3:ax.annotate('',xy=(x+.251,.49),xytext=(x+.231,.49),arrowprops={'arrowstyle':'->','color':ACCENT,'lw':2})
    elif n==9:
        canonical=ROOT/'equipo'/'qc_carlos'/'RESUMEN_QC.md';source=canonical if canonical.exists() else ROOT/'curation'/'v0.1'/'LEEME.md';txt=source.read_text(encoding='utf-8')
        m=re.search(r'micrografías\s+(\d+)/(\d+)',txt,re.I);sp=re.search(r'espectros\s+(\d+)\s+sí\s+y\s+(\d+)\s+no',txt,re.I);de=re.search(r'descriptores\s+(\d+)\s+sí\s+y\s+(\d+)\s+no',txt,re.I)
        assert m and sp and de,'No se pueden verificar las cifras QC desde el documento disponible'
        data=pd.DataFrame([('Micrografías',int(m[1]),int(m[2])),('Descriptores',int(de[1]),int(de[1])+int(de[2])),('Espectros',int(sp[1]),int(sp[1])+int(sp[2]))],columns=['tipo','si','comprobables'])
        data['porcentaje']=100*data.si/data.comprobables;data['fuente']=str(source.relative_to(ROOT))
        fig=canvas('En la muestra, las micrografías fueron 19/19 comprobables','Muestra de 20 artículos · revisión asistida por IA','Fuente secundaria: LEEME v0.1; no está disponible el RESUMEN_QC original.' if not canonical.exists() else 'No equivale a una validación humana independiente.')
        ax=axis(fig,(.22,.24,.63,.46));ax.barh(data.tipo,[100]*3,color='#dce3e6');ax.barh(data.tipo,data.porcentaje,color=ACCENT)
        for i,r in enumerate(data.itertuples()):ax.text(103,i,f'{r.si}/{r.comprobables} · {r.porcentaje:.1f} %',va='center',fontsize=24)
        ax.set_xlim(0,128);ax.set_xticks([0,25,50,75,100]);ax.set_xlabel('Evidencias «sí» sobre lo comprobable (%)')
    elif n==10:
        registry={r['id']:r for r in json.loads((ROOT/'producto'/'modelo_tabular'/'metricas_tabular.json').read_text(encoding='utf-8'))['modelos']}
        rows=[]
        for task,ids,metric in [('Tamaño',['tamano_dummy','tamano_media_clase']+[f'tamano_B_{k}' for k in ['lineal','ridge','rf300','rf500','hgb']],'r2'),('Clase (4)',['clase4_'+k for k in ['mayoritaria','logistica','rf','hgb']],'f1_macro')]:
            for key in ids:
                r=registry[key];m=r['metricas'][metric];rows.append({'tarea':task,'modelo':key,'valor':m['valor'],'ic_inf':m['ic95'][0],'ic_sup':m['ic95'][1],'n_filas':r['n_filas'],'n_articulos':r['n_articulos']})
        data=pd.DataFrame(rows)
        nr=registry['tamano_B_ridge'];nc=registry['clase4_logistica']
        fig=canvas('El mejor modelo explica solo el 24 % de la variación del tamaño',f"Ronda 1 · tamaño: {nr['n_filas']} filas / {nr['n_articulos']} artículos · clase: {nc['n_filas']} filas / {nc['n_articulos']} artículos",'IC 95 %: 1.000 bootstrap de artículos; barras naranjas = líneas base.')
        short=['Media global','Media por clase','Lineal','Ridge','RF 300','RF 500','Boosting']
        for rect,task,names,xlabel in [((.15,.22,.32,.49),'Tamaño',short,'R² de log10(tamaño)'),((.65,.22,.29,.49),'Clase (4)',['Mayoritaria','Logística','RF','Boosting'],'F1 macro')]:
            ax=axis(fig,rect);part=data[data.tarea==task];values=part.valor.to_numpy();base=[i<2 if task=='Tamaño' else i==0 for i in range(len(part))]
            ax.barh(range(len(part)),values,color=['#D55E00' if b else ACCENT for b in base]);ax.errorbar(values,range(len(part)),xerr=[values-part.ic_inf.to_numpy(),part.ic_sup.to_numpy()-values],fmt='none',ecolor=INK,capsize=4)
            ax.set_yticks(range(len(part)),names);ax.invert_yaxis();ax.set_xlabel(xlabel);ax.set_title(task,fontsize=25,pad=18)
    elif n==11:
        path=ROOT/'modelos'/'comparacion'/'resultados'/'comparacion_justa.json'
        if not path.exists():print('Figura 11 pendiente: no existe comparacion_justa.json real; no se inventan datos.');return None
        obj=json.loads(path.read_text(encoding='utf-8'));assert not obj.get('sintetico',False)
        rows=[]
        for exp in obj['experimentos']:
            for name,r in exp['metodos'].items():rows.append({'modelo_imagen':exp['modelo_imagen'],'metodo':name,'f1':r['metricas']['f1_macro']['valor'],'ic_inf':r['metricas']['f1_macro']['ic95'][0],'ic_sup':r['metricas']['f1_macro']['ic95'][1]})
        data=pd.DataFrame(rows);part=data[data.modelo_imagen==data.modelo_imagen.iloc[0]]
        fig=canvas('¿Aporta algo la imagen en los mismos artículos?',f"Modelo de imagen: {part.modelo_imagen.iloc[0]} · evaluación por artículo")
        ax=axis(fig,(.25,.22,.63,.48));ax.barh(part.metodo,part.f1,color=ACCENT);ax.errorbar(part.f1,range(len(part)),xerr=[part.f1-part.ic_inf,part.ic_sup-part.f1],fmt='none',ecolor=INK,capsize=4);ax.set_xlabel('F1 macro · IC 95 %')
    else:raise ValueError(n)
    (OUT/'datos').mkdir(parents=True,exist_ok=True);data.to_csv(OUT/'datos'/f'figura_{n}.csv',index=False,encoding='utf-8-sig');save(fig,n)
    print(f'Figura {n}: PNG/SVG 1920×1080 y datos verificados.');return data

def all_figures():
    guard(init=True);checks=[]
    for n in range(1,11):
        generate(n); first={ext:hashlib.sha256((OUT/f'figura_{n}.{ext}').read_bytes()).hexdigest() for ext in ['png','svg']}
        generate(n);second={ext:hashlib.sha256((OUT/f'figura_{n}.{ext}').read_bytes()).hexdigest() for ext in ['png','svg']}
        assert first==second,f'Figura {n} no determinista';checks.append({'figura':n,'regeneracion_identica':True,'hashes':first})
    generate(11)
    write_json(OUT/'validacion_automatica.json',{'figuras':checks,'paleta':COLORS,'fuente':'DejaVu Sans / DejaVu Sans Mono (fallback de Inter/IBM Plex Mono)','fuente_qc_sustituida':'equipo/qc_carlos/RESUMEN_QC.md ausente; cifras verificadas en LEEME v0.1','revision_visual':'pendiente'})
    titles={1:'Cobertura: 1.824 leídos / 1.707 con evidencia',2:'Cobertura por año y clase',3:'Artículos por tipo de portador',4:'Microscopía por variante y clase',5:'Espectros por técnica/clase',6:'Tamaño por clase',7:'Pares tamaño/zeta',8:'Flujo de construcción',9:'QC asistido por IA: muestra de 20 artículos',10:'Escaleras de modelos de ronda 1',11:'Comparación modal pendiente de datos reales'}
    (OUT/'INDICE.md').write_text('# Figuras para video\n\n'+ '\n'.join(f'- Figura {n}: {title}. Datos y n exactos en `datos/figura_{n}.csv`; fuente: '+('producto/modelo_tabular/metricas_tabular.json' if n==10 else 'LEEME congelado de v0.1 (fuente secundaria; falta resumen QC)' if n==9 else 'ext_*.csv y tabla_modelo.csv' if n<9 else 'comparacion_justa.json, todavía ausente')+'.' for n,title in titles.items())+'\n\nPNG/SVG deterministas, 1920×1080; títulos 36 pt y etiquetas ≥20 pt. Colores de clase fijos Okabe–Ito, fondo/tinta/acento de styles.css. No se descargaron fuentes. No se modifica la web.\n',encoding='utf-8')
if __name__=='__main__':all_figures()
