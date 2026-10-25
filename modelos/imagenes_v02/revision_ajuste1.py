"""Autoevaluaciones visuales del asistente: no son etiquetas humanas."""
import argparse
from ajuste1 import review
def si(t): return {'ok':True,'veredicto':t}
def no(t): return {'ok':False,'veredicto':t}
DECISIONES={
1:[
 si('Cryo-TEM C completa; separación y tipo correctos.'),
 si('Par TEM completo conservado como figura entera, con escalas; tipo correcto y sin separar explícito, no dos paneles aislados.'),
 si('Gráfica DLS simple completa, con curvas, ejes y leyenda; conservación entera correcta.'),
 si('UV-visible completo con ejes y anotación del máximo; tipo correcto, técnica de panel sin asignar.'),
 si('TEM A completa y correctamente aislada del SAXS y del dibujo; técnica TEM explícita en el pie del subpanel.')],
2:[
 si('Micrografía SEM C completa, escala incluida; tipo correcto.'),
 si('TEM b completa con escala de 100 nm; no se recortaron partículas.'),
 si('Gráfica de área de lesión completa y tipo gráfica correcto; UV-visible solo figura en el pie general, no se atribuye al panel.'),
 si('Espectro EDS b completo con ejes y tabla; no se hereda SEM.'),
 si('Distribución de diámetro completa con ambos ejes; técnica de panel vacía tras corregir la notación en sufijo del pie.')],
3:[
 si('SEM A completa con barra de 100 µm; separación correcta.'),
 si('SEM simple completa, con escala y anotaciones; conservación entera válida.'),
 si('UV-visible c completo, con anotaciones e inserto, aislado del TEM y Raman.'),
 si('Raman d completo, con ejes, picos y anotaciones; técnica de panel sin atribución automática.'),
 no('Par de micrografías completo pero conservado sin separar y etiquetado dudoso; no se confirma el tipo.')],
4:[
 si('Columna SEM d–h completa con ambas escalas: agrupación parcial útil, no dos paneles individuales.'),
 si('TEM A completa con escala de 100 nm, aislada de histogramas y distribuciones.'),
 si('Par de distribuciones de tamaño completo y tipo gráfica correcto; no se atribuye STEM como técnica del panel.'),
 si('FTIR D completo con curvas, ejes y anotaciones, aislado de las otras técnicas.'),
 si('Figura completa de micrografías preservada con escalas; tipo correcto y sin separar explícito, no paneles individuales.')],
5:[
 si('TEM b completa con escala, separada del panel a.'),
 si('Micrografía b completa con rótulo y escala; el tipo es correcto y no se hereda TEM al panel.'),
 si('Dos gráficas completas de XRD y liberación agrupadas; útiles como bloque de gráficas, técnica de panel vacía.'),
 si('Gráfica de liberación completa con ejes y leyenda; sobra el encabezado del bloque siguiente, limitación menor registrada.'),
 no('Composición TEM de seis paneles conservada entera y dudosa; separación individual no conseguida.')],
6:[si('SEM a completa con escala de 500 nm; separación correcta.'),si('SEM b completa con escala y rótulo; tipo correcto.'),si('UV-visible c completo con curvas, leyenda y ejes.'),si('XRD C completo con picos y ejes, aislado del TEM y otras gráficas.'),no('SEM B completo pero de textura poco contrastada y etiquetado dudoso; tipo sin confirmar.')],
7:[si('TEM A completa con barra de 100 nm, separada de las gráficas.'),si('HRTEM c completa con escala y anotaciones; sin cortar la imagen.'),si('Distribución DLS B completa y técnica explícita correctamente asignada.'),si('Distribución de diámetro e completa con ejes; no se hereda TEM.'),no('Dibujo esquemático completo pero quedó dudoso, no ilustración probable; se conserva para etiquetado humano.')],
8:[si('TEM A completa con escala y anotaciones.'),si('SEM A completa con escala de 50 µm; separación correcta.'),no('Bloque de tabla con espectros, histogramas y TEM mezclados; no es una gráfica simple.'),no('El panel es TEM y está completo, pero el estimador lo llamó gráfica por su fondo blanco y marco.'),no('SEM A completa pero marcada dudosa; el tipo requiere revisión humana.')],
9:[si('HRTEM b completa con escala de 20 nm y etiqueta.'),si('TEM simple completa con escala de 200 nm; conservación entera válida.'),si('Curva de magnetización completa con ejes; correctamente clasificada como gráfica, sin técnica de panel inventada.'),si('Distribución de zeta b completa y técnica asignada explícitamente correcta.'),no('Figura mixta completa y etiquetada dudosa; no se consiguió aislar sus gráficas, TEM y esquema.')],
10:[si('TEM de la fila inferior izquierda completo con rótulo y escala.'),no('Figura biológica compuesta con micrografías, fluorescencia y muchas gráficas; quedó entera y mal etiquetada como micrografía.'),si('FTIR B completo con ejes y anotaciones, aislado de las micrografías.'),si('Gráfica de tamaño frente al tiempo A completa con leyenda y ejes.'),no('Distribución de tamaño A completa, pero el tipo quedó dudoso; no se confirma la etiqueta estadística.')],
11:[no('Bloque de TEM, difracción, AFM y gráfica de perfil conservado junto; no es micrografía pura.'),no('TEM c completa pero incluye un histograma superpuesto; el panel sigue mezclando imagen y gráfica y no cuenta como recorte limpio.'),no('Gráfica UV-visible y TEM C quedaron unidos y etiquetados como gráfica; falta separación.'),si('Distribución de tamaño d completa, con título y ejes.'),si('Figura completa uniforme de micrografías con escalas; conservación entera válida y sin separar explícito, no seis paneles individuales.')],
12:[si('Micrografía a completa con escala de 200 nm; etiqueta de tipo correcta aunque sin técnica de panel.'),si('Dos micrografías TEM completas agrupadas, con escalas: recorte parcial útil, no dos paneles individuales.'),si('Espectro C completo con ejes y picos; técnica de panel sin atribución automática.'),no('TEM F y gráficas G–H quedaron unidos; el tipo gráfica es incorrecto para el bloque mixto.'),si('SEM a completa con escala y rótulo; separación correcta.')],
13:[si('Columna central de cuatro SEM completa, con rótulos y escalas; bloque parcial útil, no paneles individuales.'),si('Columna derecha de cuatro SEM completa; tipo correcto y agrupación explícita.'),si('XRD f completo con ejes y técnica explícita asignada correctamente.'),si('Distribución de tamaño B completa con ejes, separada de TEM y EDS.'),no('Bloque que combina ilustración, histograma y TEM sin separación; queda dudoso y no cuenta como extracción limpia.')],
14:[si('TEM A–B completas agrupadas, con escalas e inserto HRTEM; bloque útil sin otras modalidades.'),si('Micrografía TEM simple completa; conservación entera válida.'),si('Distribución de zeta G completa y técnica correcta; resolución nativa pequeña, limitación conservada.'),si('Distribución DLS b completa con ejes y etiqueta de técnica explícita.'),si('TEM simple completa con barra de 50 nm; tipo y conservación correctos.')],
15:[si('SEM a completa con escala y franja de instrumento.'),si('SEM b completa con anotaciones y escala; se separó de EDS y otras imágenes.'),si('XRD c completo, con curvas, anotaciones y ejes.'),si('UV-visible A completo con leyenda e inserto; separado de TEM/HRTEM.'),si('Figura uniforme de micrografías SEM e insertos conservada entera, con escalas; sin separar explícito, no paneles individuales.')],
16:[si('HRTEM completa con escala e insertos de transformada; conservación entera de la micrografía válida.'),si('Composición uniforme SEM de fibras conservada entera y marcada sin separar; escalas y anotaciones intactas.'),si('EDS B completo con ejes y técnica explícita correcta.'),si('Par de gráficas XRD y magnetización completo y correctamente etiquetado como bloque de gráficas; no paneles individuales.'),no('Figura de varias micrografías conservada entera y dudosa; separación no conseguida y tipo sin confirmar.')],
17:[si('SEM a completa, con escala y franja de instrumento.'),si('TEM inferior derecha completa con barra de 100 nm; separación correcta.'),no('UV-visible c completo, pero el pie publicado contradice la imagen y se había asignado FTIR. Se retiran todas las técnicas de esa figura y se registra la abstención; no cuenta como validación positiva.'),si('Gráfica de barras d completa con ejes; no se le hereda la técnica EDS de la figura.'),si('SEM a completa con escala e inserto; separada de b y c.')],
18:[si('Composición uniforme SEM completa con escalas; fallback entero explícito, no seis paneles aislados.'),si('SEM A completa con barra de 200 nm, separada de las otras imágenes.'),si('TEM B completa con escala y rótulo.'),no('SEM C–D y FTIR E quedaron unidos; no es un panel aislado y permanece dudoso.'),no('Micrografía y espectro EDS conservados juntos; etiquetado dudoso correcto pero no separación útil.')],
}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('lote',type=int);a=p.parse_args();review(a.lote,DECISIONES[a.lote])
