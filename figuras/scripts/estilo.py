import os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'figuras'/'figuras_para_el_video'
os.environ.setdefault('MPLCONFIGDIR',str(OUT/'.mplconfig'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
COLORS={'lipidico':'#0072B2','polimerico':'#D55E00','inorganico':'#009E73','nanomaterial':'#CC79A7','otro':'#888888'}
LABELS={'lipidico':'Lipídico','polimerico':'Polimérico','inorganico':'Inorgánico','nanomaterial':'Nanomaterial','otro':'Otro / sin clase'}
INK='#17232d'; PAPER='#f7f9f8'; ACCENT='#087e78'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':20,'axes.labelsize':22,'xtick.labelsize':20,'ytick.labelsize':20,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none','svg.hashsalt':'Nano2Predict-v01','figure.facecolor':PAPER,'axes.facecolor':PAPER,'text.color':INK,'axes.labelcolor':INK,'axes.edgecolor':'#67757f'})
def canvas(title,subtitle,note=''):
    import textwrap
    fig=plt.figure(figsize=(19.2,10.8),dpi=100)
    fig.text(.055,.947,textwrap.fill(title,74),fontsize=36,weight='bold',va='top',linespacing=1.1)
    fig.text(.055,.817,subtitle,fontsize=22,va='top')
    if note: fig.text(.055,.092,note,fontsize=20,va='bottom')
    fig.text(.055,.037,'Fuente: Nano2Predict v0.1 · extraído con IA y verificado por código',fontsize=20,color='#67757f')
    return fig
def legend(fig):
    from matplotlib.patches import Patch
    fig.legend(handles=[Patch(color=COLORS[c],label=LABELS[c]) for c in COLORS],loc='upper left',bbox_to_anchor=(.055,.785),ncol=5,frameon=False,fontsize=20,columnspacing=1.2)
def axis(fig,rect=(.16,.22,.77,.49)):
    return fig.add_axes(rect)
def save(fig,n):
    import re
    OUT.mkdir(parents=True,exist_ok=True)
    for txt in fig.findobj(matplotlib.text.Text):
        if re.fullmatch(r'[\d\s.,%:/+−=·-]+',txt.get_text().strip()):
            txt.set_fontfamily('DejaVu Sans Mono')
    fig.canvas.draw()
    renderer=fig.canvas.get_renderer()
    clipped=[]
    for txt in fig.findobj(matplotlib.text.Text):
        if not txt.get_visible() or not txt.get_text():continue
        bb=txt.get_window_extent(renderer)
        if bb.x0 < -2 or bb.y0 < -2 or bb.x1>1922 or bb.y1>1082:clipped.append(txt.get_text())
    assert not clipped,f'Texto fuera del lienzo: {clipped}'
    fig.savefig(OUT/f'figura_{n}.png',dpi=100)
    path=OUT/f'figura_{n}.svg'
    fig.savefig(path,metadata={'Date':None})
    svg=path.read_text(encoding='utf-8')
    svg=re.sub(r'width="[^"]+" height="[^"]+"', 'width="1920px" height="1080px"',svg,count=1)
    path.write_text(svg,encoding='utf-8')
    plt.close(fig)
