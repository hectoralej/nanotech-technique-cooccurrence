/* Presentación Nano2Predict. Sin dependencias: lee window.DATOS (datos.js, generado por construir_datos.py). */
(() => {
  'use strict';
  const D = window.DATOS;
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const reducido = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const miles = n => String(Math.round(n)).replace(/\B(?=(\d{3})+(?!\d))/g, '.');
  const dec = (n, d = 2) => Number(n).toFixed(d).replace('.', ',');
  const esc = s => String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const md = s => esc(s).replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>').replace(/`(.+?)`/g, '<code>$1</code>');
  const el = (tag, props = {}, html = '') => { const e = document.createElement(tag); Object.assign(e, props); if (html) e.innerHTML = html; return e; };

  if (!D) { document.body.prepend(el('p', { className: 'aviso' }, 'No se cargó datos.js. Ejecuta <code>python producto/presentacion/construir_datos.py</code>.')); return; }

  /* ---------- navegación entre secciones ---------- */
  const dias = $$('.dia');
  const puntos = $('#puntos');
  dias.forEach((d, i) => {
    const a = el('a', { href: '#' + d.id }, '');
    a.dataset.titulo = d.dataset.titulo; a.setAttribute('aria-label', d.dataset.titulo);
    puntos.append(a);
  });
  let actual = 0;
  const ir = i => { i = Math.max(0, Math.min(dias.length - 1, i)); dias[i].scrollIntoView({ behavior: reducido ? 'auto' : 'smooth', block: 'start' }); };
  const marcar = i => {
    actual = i;
    $$('a', puntos).forEach((a, k) => a.classList.toggle('activo', k === i));
    $('#contador').textContent = `${i + 1} / ${dias.length}`;
    const pct = Math.round(100 * (i + 1) / dias.length);
    $('#progreso-relleno').style.width = pct + '%';
    $('.progreso').setAttribute('aria-valuenow', pct);
  };
  const obs = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) marcar(dias.indexOf(e.target)); }), { rootMargin: '-45% 0px -45% 0px' });
  dias.forEach(d => obs.observe(d));
  marcar(0);
  $$('[data-ir="siguiente"]').forEach(b => b.addEventListener('click', () => ir(actual + 1)));
  const presentar = $('#btn-presentar');
  const alternarPresentar = () => { const on = document.body.classList.toggle('presentar'); presentar.setAttribute('aria-pressed', on); };
  presentar.addEventListener('click', alternarPresentar);
  document.addEventListener('keydown', e => {
    if (e.ctrlKey || e.metaKey || e.altKey || /^(INPUT|SELECT|TEXTAREA)$/.test(e.target.tagName)) return;
    const k = e.key;
    if (k === 'ArrowRight' || k === 'PageDown') { e.preventDefault(); ir(actual + 1); }
    else if (k === 'ArrowLeft' || k === 'PageUp') { e.preventDefault(); ir(actual - 1); }
    else if (k === 'Home') { e.preventDefault(); ir(0); }
    else if (k === 'End') { e.preventDefault(); ir(dias.length - 1); }
    else if (k === 'p' || k === 'P') alternarPresentar();
    else if (k === 'f' || k === 'F') { try { document.fullscreenElement ? document.exitFullscreen() : document.documentElement.requestFullscreen(); } catch (_) { /* sin pantalla completa */ } }
  });

  /* ---------- portada: cifras ---------- */
  const c = D.cifras;
  const tiles = [[c.leidos, 'artículos leídos'], [c.evidencia, 'con evidencia'], [c.micrografias, 'micrografías'], [c.descriptores, 'filas de medidas'], [c.espectros, 'espectros']];
  const cont = $('#cifras-portada');
  tiles.forEach(([n, t]) => { const d = el('div', { className: 'cifra' }); d.innerHTML = `<b data-n="${n}">${miles(n)}</b><span>${esc(t)}</span>`; cont.append(d); });
  if (!reducido) {
    $$('b[data-n]', cont).forEach(b => {
      const fin = +b.dataset.n, t0 = performance.now();
      const paso = t => { const p = Math.min(1, (t - t0) / 900); b.textContent = miles(fin * (1 - Math.pow(1 - p, 3))); if (p < 1) requestAnimationFrame(paso); };
      requestAnimationFrame(paso);
    });
  }
  $('#sello-datos').textContent = `${miles(c.imagenes_descargadas)} figuras descargadas · ${D.decisiones.filas.length} decisiones registradas`;

  /* ---------- extractor: un dato real con su cita ---------- */
  const VARIANTES = { TEM_prep_not_declared: 'TEM (preparación no declarada)', TEM_negstain: 'TEM (tinción negativa)', TEM_dried_unstained: 'TEM (seca, sin teñir)', cryoTEM: 'cryo-TEM' };
  let exIdx = 0, exFalso = false;
  const pestanasEx = $('#extractor-pestanas');
  const etiquetasEx = ['Lípidos (NLC)', 'Plata (AgNP)', 'Liposomas', 'Polímero (quitosano)'];
  D.ejemplos.forEach((e, i) => {
    const b = el('button', { type: 'button', textContent: etiquetasEx[i] || e.portador });
    b.setAttribute('role', 'tab'); b.addEventListener('click', () => { exIdx = i; exFalso = false; pintarExtractor(); });
    pestanasEx.append(b);
  });
  const escRe = s => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const falsear = (valor, cita) => {
    const dec1 = (valor.split('.')[1] || '').length;
    for (const f of [1.18, 1.31, 0.77, 1.52]) {
      const v = (Number(valor) * f).toFixed(dec1);
      if (!cita.includes(v)) return v;
    }
    return String(Number(valor) + 37);
  };
  function pintarExtractor() {
    const e = D.ejemplos[exIdx];
    $$('button', pestanasEx).forEach((b, i) => b.setAttribute('aria-selected', i === exIdx));
    const tam = exFalso ? falsear(e.size_nm, e.cita) : e.size_nm;
    const fichas = [
      ['Tamaño (nm)', tam, 'tam'], ['PDI', e.pdi, 'pdi'], ['Potencial zeta (mV)', e.zeta_mV.replace('-', '−'), 'zeta'],
      ['Medio', e.medio.replace('_', ' '), ''], ['Dónde está', e.fuente, ''], ['Muestra', e.muestra, ''],
    ];
    const tokens = { tam, pdi: e.pdi, zeta: e.zeta_mV.replace(/^[-−]/, '') };
    const res = {};
    const rangos = [];
    for (const [k, tok] of Object.entries(tokens)) {
      const re = new RegExp('(?<![\\d.])' + escRe(tok) + '(?!\\d)', 'g');
      const m = re.exec(e.cita);
      res[k] = !!m;
      if (m) rangos.push([m.index, m.index + tok.length]);
    }
    rangos.sort((a, b) => a[0] - b[0]);
    let html = '', pos = 0;
    for (const [a, b] of rangos) { if (a < pos) continue; html += esc(e.cita.slice(pos, a)) + '<mark>' + esc(e.cita.slice(a, b)) + '</mark>'; pos = b; }
    html += esc(e.cita.slice(pos));
    $('#ex-campos').innerHTML = fichas.map(([t, v, k]) => `<div class="${k && exFalso && k === 'tam' ? 'mal' : k && res[k] ? 'bien' : ''}"${t === 'Muestra' ? ' style="grid-column:1/-1"' : ''}><dt>${esc(t)}</dt><dd${t === 'Muestra' || t === 'Dónde está' || t === 'Medio' ? ' style="font:500 14px var(--sans)"' : ''}>${esc(v)}</dd></div>`).join('');
    $('#ex-cita').innerHTML = '«' + html + '»';
    const items = [['tam', 'Tamaño', tam + ' nm'], ['pdi', 'PDI', e.pdi], ['zeta', 'Zeta', tokens.zeta + ' mV (valor absoluto)']];
    $('#ex-verif').innerHTML = items.map(([k, n, v]) => `<li class="${res[k] ? 'ok' : 'falla'}">${res[k] ? '✓' : '✗'} ${esc(n)} ${esc(v)} ${res[k] ? 'aparece en la cita' : 'NO aparece en la cita'}</li>`).join('')
      + `<li class="veredicto" style="color:var(${res.tam && res.pdi && res.zeta ? '--verde' : '--rojo'})">${res.tam && res.pdi && res.zeta ? 'Verificado: el dato se conserva con su cita.' : 'Rechazado por el código: el dato no entra a la base.'}</li>`;
    const img = $('#ex-imagen');
    img.src = e.imagen; img.alt = `Figura del artículo con micrografía ${e.microscopia}, muestra ${e.muestra}`;
    const v = VARIANTES[e.microscopia] || e.microscopia;
    $('#ex-pie').innerHTML = `${esc(v)} · ${esc(e.figura.replace(/\.$/, ''))}. <em>«${esc(e.cita_panel)}»</em><br>Crédito: ${esc(e.titulo.replace(/\.$/, ''))} (${esc(e.anio)}). Licencia ${esc(e.licencia.toUpperCase())}.`;
    const doi = $('#ex-doi'); doi.href = e.doi; doi.textContent = 'Abrir el artículo (' + e.doi.replace('https://doi.org/', 'doi:') + ') ↗';
    const btn = $('#ex-falso'); btn.setAttribute('aria-pressed', exFalso); btn.textContent = exFalso ? '↩ Volver al dato real' : '¿Y si la IA inventa el tamaño?';
  }
  $('#ex-falso').addEventListener('click', () => { exFalso = !exFalso; pintarExtractor(); });
  pintarExtractor();

  /* ---------- control de calidad ---------- */
  $('#calidad-barras').innerHTML = D.qc.filas.map(f => {
    const t = f.si + f.no + f.no_comprobable, comp = f.si + f.no;
    const seg = (n, cl, txt) => n ? `<span class="${cl}" style="width:${100 * n / t}%" title="${txt}">${n}</span>` : '';
    return `<div class="cb-fila" role="listitem"><b>${esc(f.campo)}: ${f.si} de ${comp} comprobables correctos (${Math.round(100 * f.si / comp)} %)</b>
      <div class="cb-barra" aria-hidden="true">${seg(f.si, 'cb-si', 'sí')}${seg(f.no, 'cb-no', 'no')}${seg(f.no_comprobable, 'cb-nc', 'no comprobable')}</div>
      <div class="cb-leyenda">${f.si} sí · ${f.no} no · ${f.no_comprobable} no comprobable (de ${t})</div></div>`;
  }).join('') + '<div class="cb-leyenda"><span style="color:var(--verde)">■</span> sí &nbsp; <span style="color:var(--rojo)">■</span> no &nbsp; <span style="color:#7d8b93">■</span> no comprobable</div>';

  /* ---------- línea de tiempo ---------- */
  const hitos = [
    ['9 oct', 'Preregistro y búsqueda', 'Se registran 10 hipótesis antes de leer ningún artículo y se consulta Europe PMC: 2.025 artículos de acceso abierto en alcance, 7 familias de portadores. Fuente: PREREGISTRATION.md y REPORT.md.'],
    ['12–20 oct', 'Repositorio estricto', 'De 86 a 87 artículos con micrografía, DLS y zeta de una misma muestra, leídos con dos pasadas de IA y auditados. Es el patrón de calidad con el que se mide lo demás. Fuente: curation/ESTADO.md.'],
    ['21 oct', 'Base ampliada', 'Una regla de dos niveles (E1: micrografía + medidas + espectro; E2: micrografía + medidas o espectro) permite pasar a 1.824 artículos leídos, 1.707 con evidencia. Fuente: DECISIONES.md, D4.'],
    ['22 oct', 'v0.1 congelada', 'La base se congela con sumas de verificación para que todo el equipo trabaje sobre los mismos bytes. Se descargan 2.149 figuras de artículos CC BY. Fuente: curation/v0.1, D21.'],
    ['23 oct', 'Modelos y decisiones', 'Rondas 1 y 2 de modelos tabulares, auditadas. Vectores de imagen (ResNet50 y DINOv2) calculados en Kabré. Sesión con el profesor y registro de las 22 decisiones. Fuente: equipo/PANORAMA_23OCT.md.'],
    ['24 oct', 'Congelación', 'Plan: resultados de modelos congelados a las 3 pm, Atlas congelado a las 5 pm, grabación de la demo y de la narración.', true],
    ['25 oct', 'Entrega', 'Plan: montaje y subida del video antes de las 2 pm. Entrega del hackatón a las 5:45 pm (hora de Costa Rica).', true],
  ];
  const linea = $('#linea'), detalle = $('#linea-detalle');
  hitos.forEach((h, i) => {
    const b = el('button', { type: 'button', className: 'hito' + (h[3] ? ' plan' : '') }, `<i></i><b>${esc(h[0])}</b><span>${esc(h[1])}</span>`);
    b.setAttribute('role', 'listitem'); b.addEventListener('click', () => mostrar(i)); linea.append(b);
  });
  function mostrar(i) {
    const h = hitos[i];
    $$('.hito', linea).forEach((b, k) => b.setAttribute('aria-pressed', k === i));
    detalle.innerHTML = `<h3>${esc(h[0])} · ${esc(h[1])}${h[3] ? '<span class="etiqueta-plan">PLAN</span>' : ''}</h3><p>${esc(h[2])}</p>`;
  }
  mostrar(3);

  /* ---------- galería ---------- */
  const galImg = $('#gal-img'), galPie = $('#gal-pie'), galMini = $('#gal-mini');
  const ordenGal = D.figuras;
  function verFigura(i) {
    const f = ordenGal[i];
    galImg.src = f.archivo; galImg.alt = `Figura ${f.n}. ${f.pie}`;
    galPie.innerHTML = `<strong>Figura ${f.n}.</strong> ${esc(f.pie)}`;
    $$('button', galMini).forEach((b, k) => b.setAttribute('aria-selected', k === i));
  }
  ordenGal.forEach((f, i) => {
    const b = el('button', { type: 'button' }, `<img src="${f.archivo}" alt="" loading="lazy"><span>${f.n}</span>`);
    b.setAttribute('role', 'tab'); b.setAttribute('aria-label', `Figura ${f.n}: ${f.pie}`); b.addEventListener('click', () => verFigura(i)); galMini.append(b);
  });
  verFigura(2);

  /* ---------- vista previa del Atlas ---------- */
  $('#btn-vista').addEventListener('click', () => {
    $('#vista').innerHTML = '<iframe src="../web/" title="Vista previa del Atlas de Nano2Predict" loading="lazy"></iframe>';
    $('#btn-vista').disabled = true;
  });

  /* ---------- modelos: escalera ---------- */
  const M = D.modelos;
  const TABS = {
    tamano: {
      datos: M.tamano, dominio: [-0.02, 0.32], marcas: [0, 0.1, 0.2, 0.3],
      titulo: 'El mejor modelo explica ≈ 24 % de la variación del tamaño',
      texto: 'Predecir siempre el promedio no explica nada (R² = 0). Predecir el promedio de cada tipo de portador explica 18 %. La regresión Ridge con técnicas y medidas llega a <strong>0,24</strong> [0,19–0,29]. El <strong>error relativo mediano sigue en ≈ 44 %</strong>. Random Forest y boosting no la mejoraron: la base no trae proporciones ni condiciones de preparación.',
      aviso: 'La mejora sobre la línea base es real pero pequeña. El modelo usa zeta y PDI ya medidos: describe la base, no predice una formulación antes de prepararla.',
    },
    clase: {
      datos: M.clase, dominio: [0, 0.62], marcas: [0, 0.2, 0.4, 0.6],
      titulo: 'Con las medidas, F1 de 0,51 frente a 0,12',
      texto: 'Cuatro clases: lipídico, polimérico, inorgánico y nanomaterial. Responder siempre la clase más común da F1 = 0,12. La regresión logística con las mediciones llega a <strong>0,51</strong> [0,48–0,54], y los modelos más complejos no la superan. Se prohíbe usar el tipo de portador, la familia o el título como entradas: serían la respuesta disfrazada.',
      aviso: '«Nanomaterial» se solapa con «inorgánico» (mezcla composición y uso): el F1 es el de esta definición de clases.',
    },
    imagen: {
      datos: M.imagen, dominio: [0, 0.7], marcas: [0, 0.2, 0.4, 0.6],
      titulo: M.imagen.titulo, texto: M.imagen.texto, aviso: M.imagen.aviso, // textos y cifras: construir_datos.py
    },
  };
  let tab = 'tamano';
  const claseBarra = (id, base) => base ? 'base' : id === 'atlas' ? 'imagen' : id === 'fusion' ? 'fusion' : 'b';
  function pintarModelo() {
    const T = TABS[tab], d = T.datos, ic = $('#chk-ic').checked;
    $$('#modelo-pestanas button').forEach(b => b.setAttribute('aria-selected', b.dataset.tab === tab));
    $('#lectura-titulo').textContent = T.titulo;
    $('#lectura-texto').innerHTML = T.texto;
    $('#lectura-aviso').innerHTML = esc(T.aviso);
    const W = 760, x0 = 215, x1 = 560, fila = 46, top = 14, alto = top + d.items.length * fila + 52;
    const [lo, hi] = T.dominio, X = v => x0 + (v - lo) / (hi - lo) * (x1 - x0);
    let s = `<svg viewBox="0 0 ${W} ${alto}" aria-hidden="true">`;
    T.marcas.forEach(m => { s += `<line class="rejilla" x1="${X(m)}" x2="${X(m)}" y1="${top - 6}" y2="${alto - 46}"/><text class="eje" x="${X(m)}" y="${alto - 28}" text-anchor="middle">${dec(m, 1)}</text>`; });
    s += `<line class="cero" x1="${X(Math.max(0, lo))}" x2="${X(Math.max(0, lo))}" y1="${top - 6}" y2="${alto - 46}"/>`;
    d.items.forEach((it, i) => {
      const y = top + i * fila, v = it.valor, a = X(Math.min(0, v)), b = X(Math.max(0, v));
      const tieneIc = ic && it.lo !== undefined;
      const fin = tieneIc ? X(it.hi) : b;
      const txt = tieneIc ? `${dec(v, 3)} [${dec(it.lo, 3)}–${dec(it.hi, 3)}]` : (it.nota || dec(v, 3));
      s += `<g class="fila" tabindex="0" aria-label="${esc(it.nombre)}: ${txt}"><title>${esc(it.nombre)}: ${txt}</title>
        <text class="etq" x="${x0 - 12}" y="${y + 20}" text-anchor="end">${esc(it.nombre)}</text>
        <rect class="${claseBarra(it.id, it.base)}" x="${a}" y="${y + 4}" width="${Math.max(2, b - a)}" height="24" rx="3"/>`;
      if (tieneIc) s += `<line class="ic" x1="${X(it.lo)}" x2="${X(it.hi)}" y1="${y + 16}" y2="${y + 16}"/><line class="ic" x1="${X(it.lo)}" x2="${X(it.lo)}" y1="${y + 10}" y2="${y + 22}"/><line class="ic" x1="${X(it.hi)}" x2="${X(it.hi)}" y1="${y + 10}" y2="${y + 22}"/>`;
      s += `<text class="valor" x="${fin + 10}" y="${y + 21}">${esc(txt)}</text>${it.destacado ? `<text class="eje" x="${fin + 10}" y="${y + 38}">mejor combinación</text>` : ''}</g>`;
    });
    s += `<text class="eje" x="${(x0 + x1) / 2}" y="${alto - 8}" text-anchor="middle">${esc(d.metrica)}</text></svg>`;
    const hayImagen = d.items.some(i => i.id === 'atlas'), hayFusion = d.items.some(i => i.id === 'fusion');
    const ley = `<div class="leyenda"><span><i style="background:var(--base)"></i>línea base</span><span><i style="background:var(--accent)"></i>modelo con medidas</span>${hayImagen ? '<span><i style="background:var(--azul)"></i>solo imagen</span>' : ''}${hayFusion ? '<span><i style="background:var(--fusion)"></i>imagen + medidas</span>' : ''}<span>n = ${miles(d.n_filas)} ${tab === 'imagen' ? 'figuras' : 'filas'} · ${miles(d.n_articulos)} artículos · fuente: ${esc(d.fuente)}</span></div>`;
    const g = $('#grafica');
    g.innerHTML = s + ley;
    g.setAttribute('aria-label', `${T.titulo}. ` + d.items.map(i => `${i.nombre} ${dec(i.valor, 2)}`).join('; '));
  }
  $$('#modelo-pestanas button').forEach(b => b.addEventListener('click', () => { tab = b.dataset.tab; pintarModelo(); }));
  $('#chk-ic').addEventListener('change', pintarModelo);
  pintarModelo();

  /* ---------- decisiones ---------- */
  const filas = D.decisiones.filas, secciones = D.decisiones.secciones;
  let secSel = '';
  const chips = $('#dec-chips');
  [['', 'Todas'], ...secciones.map(s => [s, s])].forEach(([v, t]) => {
    const b = el('button', { type: 'button', textContent: t }); b.dataset.sec = v; b.setAttribute('aria-pressed', v === '');
    b.addEventListener('click', () => { secSel = v; pintarDecisiones(); }); chips.append(b);
  });
  const claseEstado = t => { const x = t.toLowerCase(); return x.startsWith('cerrada') ? ['Cerrada', 'cerrada'] : x.startsWith('abierta') ? ['Abierta', 'abierta'] : x.startsWith('en curso') ? ['En curso', 'en-curso'] : ['Pendiente', 'pendiente']; };
  function pintarDecisiones() {
    const est = $('#dec-estado').value, q = $('#dec-buscar').value.trim().toLowerCase();
    $$('button', chips).forEach(b => b.setAttribute('aria-pressed', b.dataset.sec === secSel));
    const vis = filas.filter(f => (!secSel || f.seccion === secSel) && (!est || claseEstado(f.estado)[0] === est)
      && (!q || (f.decision + ' ' + f.porque + ' ' + f.evidencia + ' ' + f.id).toLowerCase().includes(q)));
    $('#dec-conteo').textContent = `${vis.length} de ${filas.length} decisiones`;
    $('#dec-tabla tbody').innerHTML = vis.map(f => {
      const [lab, cl] = claseEstado(f.estado.replace(/\*\*/g, '')), extra = f.estado.replace(/\*\*/g, '').replace(/^[^;:]+[;:]\s*/, '');
      return `<tr><td>${esc(f.id)}</td><td>${md(f.decision)}</td><td>${md(f.porque)}</td><td>${md(f.evidencia || '—')}</td><td><span class="estado ${cl}">${lab}</span>${extra !== f.estado.replace(/\*\*/g, '') ? `<span class="estado-extra">${md(extra)}</span>` : ''}</td></tr>`;
    }).join('') || '<tr><td colspan="5">Ninguna decisión coincide con el filtro.</td></tr>';
  }
  $('#dec-estado').addEventListener('change', pintarDecisiones);
  $('#dec-buscar').addEventListener('input', pintarDecisiones);
  pintarDecisiones();

  /* ---------- limitaciones ---------- */
  const limites = [
    ['La unidad es el artículo, no el experimento', 'Ningún artículo está en entrenamiento y prueba a la vez, pero eso no descarta datos reutilizados entre artículos distintos.'],
    ['Figura completa, no panel', 'Muchas figuras mezclan varias micrografías, espectros y texto. No verificamos visualmente que cada imagen sea una micrografía pura. Es la principal limitación del modelo de imágenes.'],
    ['Una mención no prueba un método', 'En una muestra auditada, 9 de 30 banderas de formulación fueron dudosas. Son proxies ruidosos: no las usamos como resultado principal.'],
    ['Variables que no existen antes del experimento', 'Los modelos usan zeta y PDI ya medidos: explican la base, no predicen una formulación antes de prepararla. Faltan proporciones y condiciones.'],
    ['Las clases mezclan composición y uso', '«Nanomaterial» se solapa con «inorgánico». Un F1 mayor con otras clases no prueba mejor capacidad sobre los mismos artículos.'],
    ['Intervalos condicionales', 'El bootstrap remuestrea predicciones ya hechas, no todos los reentrenamientos ni la búsqueda entre modelos: puede dar una impresión excesiva de certeza.'],
    ['Control de calidad asistido por IA', 'Fue una muestra de 20 artículos, revisada con ayuda de una IA. Falta una auditoría humana a ciegas.'],
    ['Alcance y validación', 'Se excluyen vectores virales (AAV). Se probaron varias variantes del modelo de imágenes sobre las mismas particiones, y no hay validación externa.'],
  ];
  $('#limites').innerHTML = limites.map(([t, x]) => `<article class="tarjeta"><h3>${esc(t)}</h3><p>${esc(x)}</p></article>`).join('');

  /* ---------- siguientes pasos ---------- */
  const ex = D.decisiones.experimentos.slice(0, 4);
  $('#lista-siguientes').innerHTML = ex.map(t => `<li>${md(t)}</li>`).join('')
    + '<li><strong>Extraer las condiciones de preparación</strong> (proporciones, métodos) que hoy faltan en la base.</li>'
    + '<li><strong>Revisión humana a ciegas</strong> de una muestra de extracciones.</li>';
})();
