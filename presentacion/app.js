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
  /* ---------- visor para ampliar imágenes (clic, Enter; Esc cierra) ---------- */
  const visor = $('#visor'), visorImg = $('#visor-img'), visorPie = $('#visor-pie');
  let focoPrevio = null;
  const abrirVisor = img => {
    focoPrevio = document.activeElement;
    visorImg.src = img.currentSrc || img.src; visorImg.alt = img.alt; visorPie.textContent = img.alt;
    visor.hidden = false; document.body.style.overflow = 'hidden'; $('#visor-cerrar').focus();
  };
  const cerrarVisor = () => { visor.hidden = true; document.body.style.overflow = ''; if (focoPrevio && focoPrevio.focus) focoPrevio.focus(); };
  document.addEventListener('click', e => {
    const im = e.target.closest('img.zoom');
    if (im && visor.hidden) abrirVisor(im);
    else if (!visor.hidden && (e.target === visor || e.target.closest('#visor-cerrar') || e.target === visorImg)) cerrarVisor();
  });
  const prepararZoom = () => $$('img.zoom').forEach(i => { i.tabIndex = 0; i.setAttribute('role', 'button'); i.title = 'Clic para ampliar'; });
  prepararZoom();
  new MutationObserver(prepararZoom).observe(document.body, { childList: true, subtree: true });

  document.addEventListener('keydown', e => {
    if (!visor.hidden) { if (e.key === 'Escape') { e.preventDefault(); cerrarVisor(); } return; }
    if ((e.key === 'Enter' || e.key === ' ') && e.target.matches && e.target.matches('img.zoom')) { e.preventDefault(); abrirVisor(e.target); return; }
    if (e.ctrlKey || e.metaKey || e.altKey || /^(INPUT|SELECT|TEXTAREA)$/.test(e.target.tagName)) return;
    const k = e.key;
    if (k === 'ArrowRight' || k === 'PageDown') { e.preventDefault(); ir(actual + 1); }
    else if (k === 'ArrowLeft' || k === 'PageUp') { e.preventDefault(); ir(actual - 1); }
    else if (k === 'Home') { e.preventDefault(); ir(0); }
    else if (k === 'End') { e.preventDefault(); ir(dias.length - 1); }
    else if (k === 'p' || k === 'P') alternarPresentar();
    else if (k === 'f' || k === 'F') { try { (document.fullscreenElement ? document.exitFullscreen() : document.documentElement.requestFullscreen()).catch(() => { /* el navegador no la permite aquí */ }); } catch (_) { /* sin pantalla completa */ } }
  });

  /* ---------- portada: cifras ---------- */
  const c = D.cifras;
  const DV = D.descriptores_v03, CF = D.calidad_figuras;
  const tiles = [[c.leidos, 'artículos leídos'], [c.evidencia, 'con evidencia'], [c.micrografias, 'micrografías'],
    [c.descriptores, 'filas de medidas', `${miles(DV.usables)} utilizables tras la auditoría v03`], [c.espectros, 'espectros']];
  const cont = $('#cifras-portada');
  tiles.forEach(([n, t, sub]) => { const d = el('div', { className: 'cifra' }); d.innerHTML = `<b data-n="${n}">${miles(n)}</b><span>${esc(t)}</span>${sub ? `<small>${esc(sub)}</small>` : ''}`; cont.append(d); });
  if (!reducido) {
    $$('b[data-n]', cont).forEach(b => {
      const fin = +b.dataset.n, t0 = performance.now();
      const paso = t => { const p = Math.min(1, (t - t0) / 900); b.textContent = miles(fin * (1 - Math.pow(1 - p, 3))); if (p < 1) requestAnimationFrame(paso); };
      requestAnimationFrame(paso);
      setTimeout(() => { b.textContent = miles(fin); }, 1200);
    });
  }
  $('#sello-datos').textContent = `${miles(D.calidad_figuras.n_figuras)} figuras clasificadas · ${D.decisiones.filas.length} decisiones registradas`;

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

  /* ---------- contadores que suben al entrar en pantalla ---------- */
  const alEntrar = (nodos, fn) => {
    const o = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { o.unobserve(e.target); fn(e.target); } }), { threshold: 0.35 });
    nodos.forEach(n => o.observe(n));
  };
  const contar = b => {
    const fin = +b.dataset.contar;
    if (reducido) { b.textContent = miles(fin); return; }
    const t0 = performance.now();
    const paso = t => { const p = Math.min(1, (t - t0) / 1000); b.textContent = miles(fin * (1 - Math.pow(1 - p, 3))); if (p < 1) requestAnimationFrame(paso); };
    requestAnimationFrame(paso);
    setTimeout(() => { b.textContent = miles(fin); }, 1200); // por si el navegador pausa la animación (pestaña oculta)
  };
  const tarjetas = (arr, extra = '') => arr.map(([n, t, sub]) =>
    `<div class="cifra" role="listitem"><b data-contar="${n}">${miles(n)}</b><span>${esc(t)}</span>${sub ? `<small>${esc(sub)}</small>` : ''}</div>`).join('') + extra;
  const activarContadores = raiz => alEntrar($$('[data-contar]', raiz), contar);

  /* ---------- línea de proceso ---------- */
  const proceso = [
    ['Búsqueda', c.leidos, 'artículos leídos en Europe PMC, solo acceso abierto (CC BY)'],
    ['Extracción con IA', c.descriptores, `filas de medidas, y ${miles(c.espectros)} espectros: un modelo de lenguaje lee el texto completo`],
    ['Verificación por código', null, 'cada cita y cada número deben estar en el artículo; si no, se rechazan (solo 2 artículos con citas rechazadas)'],
    ['Figuras', CF.n_figuras, 'figuras clasificadas una por una, mirando la imagen'],
    ['Recortes', CF.n_recortes, `recortes de panel; ${miles(CF.n_recortes_clase)} son micrografías de partículas con clase`],
    ['Modelo', null, 'clase de portador y tamaño, evaluados por artículo'],
  ];
  const ol = $('#proceso');
  ol.innerHTML = proceso.map(([t, n, x], i) => `<li style="--i:${i}"><span class="nodo-n">${String(i + 1).padStart(2, '0')}</span><h3>${esc(t)}</h3>${n ? `<b class="nodo-cifra" data-contar="${n}">${miles(n)}</b>` : '<b class="nodo-cifra">✓</b>'}<p>${esc(x)}</p></li>`).join('');
  alEntrar([ol], o => { o.classList.add('animado'); activarContadores(o); });

  /* ---------- De la figura al recorte ---------- */
  const FR = D.figuras_recortes;
  const pn = FR.paneles;
  $('#cifras-panel').innerHTML = [
    [dec(pn.media, 2), 'paneles por figura, en promedio'],
    [dec(pn.pct1, 1) + ' %', 'de las figuras tiene un solo panel'],
    [dec(pn.pct3, 1) + ' %', 'tiene tres o más paneles'],
  ].map(([n, t]) => `<div class="cifra" role="listitem"><b>${n}</b><span>${esc(t)}</span></div>`).join('');

  // barras apiladas: cinco destinos × (aceptada automática / aceptada por arbitraje / cola de revisión)
  (() => {
    const max = Math.max(...FR.destinos.map(d => d.n)), W = 640, x0 = 130, ancho = 400, alto = 50;
    const seg = [['aceptada_auto', 'aceptadas automáticamente', 'var(--accent)'], ['aceptada_arbitrada', 'aceptadas por arbitraje', 'var(--azul)'], ['cola_revision', 'en cola de revisión', 'var(--base)']];
    let s = `<svg viewBox="0 0 ${W} ${FR.destinos.length * alto + 54}">`;
    FR.destinos.forEach((d, i) => {
      const y = 8 + i * alto; let x = x0;
      s += `<text class="etq" x="${x0 - 10}" y="${y + 21}" text-anchor="end">${esc(d.nombre)}</text><text class="eje" x="${x0 - 10}" y="${y + 38}" text-anchor="end">${dec(d.pct, 1)} %</text>`;
      seg.forEach(([k, nom, col]) => {
        const w = ancho * d[k] / max;
        if (!w) return;
        s += `<rect x="${x}" y="${y + 4}" width="${w}" height="30" rx="2" fill="${col}"><title>${esc(d.nombre)} · ${nom}: ${miles(d[k])}</title></rect>`;
        x += w;
      });
      s += `<text class="valor" x="${x + 8}" y="${y + 24}">${miles(d.n)}</text>`;
    });
    const yl = FR.destinos.length * alto + 18;
    s += seg.map(([, nom, col], i) => `<rect x="${x0 + i * 170}" y="${yl}" width="12" height="12" fill="${col}"/><text class="eje" x="${x0 + i * 170 + 18}" y="${yl + 11}">${nom}</text>`).join('') + '</svg>';
    $('#barras-destinos').innerHTML = s;
  })();

  // selector de tipos de figura
  const pest = $('#destino-pestanas');
  let tipoIdx = 2, ejIdx = 0, modo = 'cajas';
  FR.destinos.forEach((d, i) => {
    const b = el('button', { type: 'button', textContent: `${d.nombre} · ${dec(d.pct, 1)} %` });
    b.setAttribute('role', 'tab'); b.addEventListener('click', () => { tipoIdx = i; ejIdx = 0; pintarTipo(); }); pest.append(b);
  });
  const creditoHtml = cr => `Figura de «${esc(cr.titulo.replace(/\.$/, ''))}» ${cr.anio ? ` (${esc(cr.anio)})` : ''}. <a href="${esc(cr.doi)}" target="_blank" rel="noopener">${esc(cr.doi.replace('https://doi.org/', 'doi:'))}</a> · licencia ${esc(cr.licencia)}.`;
  function pintarTipo() {
    const d = FR.destinos[tipoIdx], ej = d.ejemplos[ejIdx];
    $$('button', pest).forEach((b, i) => b.setAttribute('aria-selected', i === tipoIdx));
    $('#tipo-nombre').textContent = d.nombre;
    $('#tipo-frase').textContent = d.frase;
    $('#tipo-cifras').innerHTML = `<strong>${miles(d.n)}</strong> figuras (${dec(d.pct, 1)} %): ${miles(d.aceptada_auto)} aceptadas automáticamente, ${miles(d.aceptada_arbitrada)} por arbitraje y ${miles(d.cola_revision)} en la cola de revisión.`;
    $$('.ver-modo button').forEach(b => {
      if (b.dataset.modo) { b.hidden = !(ej && ej.original); b.setAttribute('aria-pressed', b.dataset.modo === modo); }
      if (b.dataset.ej !== undefined) { b.hidden = d.ejemplos.length < 2; b.setAttribute('aria-pressed', +b.dataset.ej === ejIdx); }
    });
    const img = $('#tipo-img'), pend = $('#tipo-pendiente');
    if (!ej) { img.hidden = true; pend.hidden = false; $('#tipo-credito').innerHTML = ''; return; }
    img.hidden = false; pend.hidden = true;
    img.src = modo === 'cajas' || !ej.original ? ej.cajas : ej.original;
    img.alt = `Figura ejemplo de destino ${d.nombre.toLowerCase()}, con ${ej.n_paneles} ${ej.n_paneles === 1 ? 'panel' : 'paneles'}${ej.original === null ? ' y las cajas de panel dibujadas' : ''}`;
    $('#tipo-credito').innerHTML = creditoHtml(ej.credito) + ` Figura con ${ej.n_paneles} ${ej.n_paneles === 1 ? 'panel' : 'paneles'}.`;
  }
  $$('.ver-modo button').forEach(b => b.addEventListener('click', () => { if (b.dataset.modo) modo = b.dataset.modo; if (b.dataset.ej !== undefined) ejIdx = +b.dataset.ej; pintarTipo(); }));
  pintarTipo();

  // de la figura a los recortes, en tres pasos
  const demo = FR.compuesta_demo;
  let paso = 1;
  const PASOS = {
    1: ['1 · La figura original', 'Así llega del artículo: varios paneles en una sola imagen, con letras, rótulos y escalas.'],
    2: ['2 · Una caja por panel', `Un modelo dibuja una caja normalizada (0–1) sobre cada panel y le asigna un tipo: micrografía (verde), espectro (azul) u otro (naranja). Aquí hay ${demo.n_paneles} paneles de nivel superior.`],
    3: ['3 · Los recortes', 'Cada caja se recorta de la figura original. Solo los de micrografía de partículas entran al modelo; el recorte hereda la clase de portador del artículo.'],
  };
  function pintarPaso() {
    $$('#paso-pestanas button').forEach(b => b.setAttribute('aria-selected', +b.dataset.paso === paso));
    $('#paso-titulo').textContent = PASOS[paso][0]; $('#paso-texto').textContent = PASOS[paso][1];
    const img = $('#recorte-img'), rej = $('#recorte-rejilla');
    img.hidden = paso === 3; rej.hidden = paso !== 3;
    img.src = paso === 1 ? demo.original : demo.cajas;
    img.alt = paso === 1 ? 'Figura compuesta original, con varios paneles de micrografías' : `La misma figura con ${demo.n_cajas} cajas de panel dibujadas`;
    rej.innerHTML = demo.recortes.map(r => `<figure><img class="zoom" src="${r.img}" alt="Recorte del panel ${esc(r.panel)} (${esc(r.tipo)})" tabindex="0" role="button"><figcaption>panel ${esc(r.panel)} · ${esc(r.tipo)}</figcaption></figure>`).join('');
    $('#recorte-credito').innerHTML = creditoHtml(demo.credito);
  }
  $$('#paso-pestanas button').forEach(b => b.addEventListener('click', () => { paso = +b.dataset.paso; pintarPaso(); }));
  pintarPaso();

  // qué recortes entran al modelo (cifras leídas de paneles.csv e indice_recortes.csv)
  const RC = FR.recortes;
  $('#cifras-recortes').innerHTML = tarjetas([
    [RC.total, 'recortes de panel en total'], [RC.micro, 'son micrografías'], [RC.espectro, 'son espectros'], [RC.otro, 'son otro (fotos, esquemas, histogramas, biología…)'],
    [RC.elegibles_con_clase, 'micrografías de partículas con clase de portador', `de ${miles(RC.articulos_elegibles)} artículos`],
  ]);
  $('#aviso-recortes').innerHTML = `<strong>Cómo leerlo:</strong> solo ${miles(RC.elegibles_con_clase)} de los ${miles(RC.total)} recortes cumplen todas las reglas y tienen clase. Los demás se conservan en la base pero no se usan para entrenar. Fuente: <code>${esc(FR.fuentes)}</code>.`;
  activarContadores($('#fig-reglas'));

  // muestra sin retoques
  const MU = FR.muestra;
  const mi = $('#muestra-img');
  mi.src = MU.imagen;
  $('#muestra-creditos').innerHTML = MU.creditos.map(m => `<li><strong>${esc(m.clase)}</strong>: ${creditoHtml(m.credito)}</li>`).join('');
  $('#aviso-muestra').innerHTML = '<strong>Sin retoques:</strong> tres recortes al azar por clase del artículo; no se eligieron los mejores. <strong>La clase es la del artículo, no la del recorte</strong>, y «nanomaterial» es una categoría general. Algunos recortes incluyen una franja del panel vecino o márgenes, y alguno trae un gráfico inserto: se ve en la rejilla.';

  /* ---------- calidad de figuras y descriptores ---------- */
  $('#cifras-figuras').innerHTML = tarjetas([
    [CF.n_figuras, 'figuras clasificadas una por una'],
    [CF.n_recortes, 'recortes de panel'],
    [CF.n_recortes_clase, 'recortes de micrografías de partículas, con clase'],
    [DV.usables, `descriptores utilizables, de ${miles(DV.filas)} filas (auditoría v03)`],
  ]);
  activarContadores($('#fig-calidad'));
  $('#hechos-figuras').innerHTML = [
    `<strong>Auditoría a ciegas:</strong> ${CF.auditoria.bien} de ${CF.auditoria.total} figuras con el número de paneles exacto.`,
    `<strong>Cajas del modelo contra cajas humanas:</strong> IoU ${CF.iou.valor} en ${CF.iou.n_figuras} figuras (${CF.iou.n_paneles} paneles dibujados a mano).`,
    `<strong>Arbitraje y cola:</strong> dos revisores independientes miran cada figura; ${miles(FR.acuerdo.arbitradas)} desacuerdos se resolvieron por arbitraje y ${miles(FR.acuerdo.cola)} figuras quedan en la cola de revisión. Imagen y pie de figura coinciden en el ${dec(FR.acuerdo.coinciden_pie_imagen, 1)} %.`,
    `<strong>Descriptores:</strong> se auditaron ${DV.auditadas} filas dudosas; ${miles(DV.usables)} de ${miles(DV.filas)} quedan utilizables.`,
  ].map(t => `<li>${t}</li>`).join('');
  $('#aviso-figuras').innerHTML = `<strong>Cómo leerlo:</strong> son muestras pequeñas (${CF.auditoria.total} figuras, ${CF.iou.n_figuras} figuras) y estimaciones preliminares. La clasificación la hacen modelos de IA; los recortes y las cajas no se han revisado todos a mano. Los recortes con clase vienen de ${miles(CF.n_articulos_recortes_clase)} artículos.`;
  // idioma de las figuras (ES/EN): un solo interruptor para el diagrama, el flujo y las figuras de modelos
  const FM = D.figuras_modelos;
  let idioma = 'es';
  const imgFlujo = $('#img-flujo-figuras');
  imgFlujo.dataset.es = CF.imagen.es; imgFlujo.dataset.en = CF.imagen.en;
  const hero = $('#fig-hero');
  hero.dataset.es = FM.hero.es; hero.dataset.en = FM.hero.en;
  const setIdioma = i => {
    idioma = i;
    $$('img.fig-i18n').forEach(im => { im.src = im.dataset[i]; });
    $$('.pie-i18n').forEach(p => { p.textContent = FM[p.dataset.pie].pie[i]; });
    $$('.idioma-fig button').forEach(b => b.setAttribute('aria-pressed', b.dataset.idioma === i));
  };
  document.addEventListener('click', e => { const b = e.target.closest('.idioma-fig button'); if (b) setIdioma(b.dataset.idioma); });
  setIdioma('es');

  /* ---------- línea de tiempo ---------- */
  const hitos = [
    ['9 oct', 'Preregistro y búsqueda', 'Se registran 10 hipótesis antes de leer ningún artículo y se consulta Europe PMC: 2.025 artículos de acceso abierto en alcance, 7 familias de portadores. Fuente: PREREGISTRATION.md y REPORT.md.'],
    ['12–20 oct', 'Repositorio estricto', 'De 86 a 87 artículos con micrografía, DLS y zeta de una misma muestra, leídos con dos pasadas de IA y auditados. Es el patrón de calidad con el que se mide lo demás. Fuente: curation/ESTADO.md.'],
    ['21 oct', 'Base ampliada', 'Una regla de dos niveles (E1: micrografía + medidas + espectro; E2: micrografía + medidas o espectro) permite pasar a 1.824 artículos leídos, 1.707 con evidencia. Fuente: DECISIONES.md, D4.'],
    ['22 oct', 'v0.1 congelada', 'La base se congela con sumas de verificación para que todo el equipo trabaje sobre los mismos bytes. Se descargan 2.149 figuras de artículos CC BY. Fuente: curation/v0.1, D21.'],
    ['23 oct', 'Modelos y decisiones', 'Rondas 1 y 2 de modelos tabulares, auditadas. Vectores de imagen (ResNet50 y DINOv2) y ajuste fino en GPU, en Kabré. Sesión con el profesor y registro de las 22 decisiones. Fuente: equipo/PANORAMA_23OCT.md.'],
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
    const b = el('button', { type: 'button' }, `<img src="${f.archivo}" alt="Miniatura de la Figura ${f.n}: ${esc(f.pie)}" loading="lazy"><span>${f.n}</span>`);
    b.setAttribute('role', 'tab'); b.setAttribute('aria-label', `Figura ${f.n}: ${f.pie}`); b.addEventListener('click', () => verFigura(i)); galMini.append(b);
  });
  verFigura(2);

  /* ---------- vista previa del Atlas ---------- */
  $('#btn-vista').addEventListener('click', () => {
    $('#vista').innerHTML = '<iframe src="../web/" title="Vista previa del Atlas de Nano2Predict"></iframe>';
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
  const claseBarra = (id, base) => base ? 'base' : id === 'atlas' || id === 'ajuste' ? 'imagen' : /^fusion/.test(id) ? 'fusion' : 'b';
  const sg = (v, d = 3) => (v >= 0 ? '+' : '−') + dec(Math.abs(v), d);
  const rango = (a, b) => `[${sg(a)}, ${sg(b)}]`;
  const figTarjeta = (clave, alt, clara = true) => `<figure class="fig-tarjeta ${clara ? 'clara' : 'oscura'}">${toggleIdioma()}<img class="zoom fig-i18n" data-es="${FM[clave].es}" data-en="${FM[clave].en}" src="${FM[clave][idioma]}" alt="${esc(alt)}"><figcaption class="pie-i18n" data-pie="${clave}">${esc(FM[clave].pie[idioma])}</figcaption></figure>`;
  const toggleIdioma = () => `<div class="idioma-fig" role="group" aria-label="Idioma de la figura"><button type="button" data-idioma="es" aria-pressed="${idioma === 'es'}">ES</button><button type="button" data-idioma="en" aria-pressed="${idioma === 'en'}">EN</button></div>`;
  const filaT = (cels, cls = '') => `<tr class="${cls}">${cels.map((x, i) => i ? `<td class="num">${x}</td>` : `<th scope="row">${esc(x)}</th>`).join('')}</tr>`;
  function pintarRecortes() {
    const R = D.recortes, I = R.imagen, F = R.fusion, P = I.promedio;
    $('#lectura-titulo').textContent = 'Con recortes de panel (preliminar): otra muestra, otra tabla';
    $('#lectura-texto').innerHTML = `Los recortes de panel mejoran un poco la imagen, y la fusión con medidas llega a F1 ${dec(F.filas[4].f1, 2)} <em>(n = ${miles(F.n_articulos)} artículos)</em>. Pero <strong>la ventaja se debe en buena parte a que los recortes aportan más vistas por artículo</strong> (${dec(I.vistas_04, 2)} frente a ${dec(I.vistas_03, 2)}): con el mismo número de vistas baja a ${sg(I.filas[0].dif_mismas_vistas_acc)} de exactitud en ResNet50 y ${sg(I.filas[1].dif_mismas_vistas_acc)} en DINOv2 (en F1, ${sg(I.filas[0].dif_mismas_vistas_f1)} y ${sg(I.filas[1].dif_mismas_vistas_f1)}). Y <strong>el intervalo de «fusión con recortes − fusión con figura completa» incluye el cero</strong>: ${sg(F.difs[1].f1)} ${rango(F.difs[1].ic[0], F.difs[1].ic[1])}.`;
    $('#lectura-aviso').innerHTML = `Resultados preliminares; evaluación por artículo. Son otras muestras (${miles(I.n_articulos)} y ${miles(F.n_articulos)} artículos, no ${miles(D.modelos.imagen.n_articulos)} figuras): <strong>no se comparan con las cifras de las otras pestañas</strong> y las dos tablas de abajo tampoco se mezclan. Fuente: ${esc(R.fuente)}.`;
    const tablaA = `<table class="tabla-mini"><caption>A · Imagen sola, por artículo · n = ${miles(I.n_articulos)} artículos · F1 macro</caption>
      <thead><tr><th></th><th>Figura completa</th><th>Recortes</th><th>Recortes, mismas vistas</th><th>Recortes − completa [IC 95 %]</th></tr></thead><tbody>
      ${I.filas.map(f => filaT([f.nombre, dec(f.completa_f1, 3), dec(f.recortes_f1, 3), dec(f.mismas_vistas_f1, 3), `${sg(f.dif_f1)} ${rango(f.dif_f1_ic[0], f.dif_f1_ic[1])}`])).join('')}
      ${filaT(['Promedio ResNet50 + DINOv2', dec(P.completa_f1, 3), dec(P.recortes_f1, 3), '—', `${sg(P.dif_f1)} ${rango(P.dif_ic[0], P.dif_ic[1])}`])}</tbody></table>`;
    const tablaB = `<table class="tabla-mini"><caption>B · Fusión con medidas, por artículo · n = ${miles(F.n_articulos)} artículos · línea base (clase mayoritaria): exactitud ${dec(F.linea_base_acc, 3)}</caption>
      <thead><tr><th></th><th>Exactitud</th><th>Exactitud balanceada</th><th>F1 macro</th></tr></thead><tbody>
      ${F.filas.map(f => filaT([f.nombre, dec(f.acc, 3), dec(f.acc_bal, 3), dec(f.f1, 3)], /recortes/.test(f.nombre) ? 'dest' : '')).join('')}</tbody></table>
      <table class="tabla-mini"><caption>Diferencias pareadas en F1 macro [IC 95 %] · n = ${miles(F.n_articulos)}</caption><tbody>
      ${F.difs.map(x => filaT([x.nombre, `${sg(x.f1)} ${rango(x.ic[0], x.ic[1])}`, x.ic[0] < 0 && x.ic[1] > 0 ? 'incluye el cero' : ''], x.ic[0] < 0 && x.ic[1] > 0 ? 'cero' : '')).join('')}</tbody></table>`;
    const g = $('#grafica');
    g.innerHTML = figTarjeta('recortes', 'De la figura completa a los recortes de panel, por artículo: F1 macro y diferencias pareadas con su intervalo de confianza') + tablaA + tablaB;
    g.setAttribute('aria-label', 'Resultados preliminares con recortes de panel: figura, tabla A (imagen sola, n = 1.112) y tabla B (fusión con medidas, n = 786).');
  }
  function pintarFinal() {
    const MF = D.modelo_final;
    $('#lectura-titulo').textContent = 'Modelo final: DINOv2, ensamble de 3 semillas';
    $('#lectura-texto').innerHTML = `Clasifica un <strong>recorte de micrografía de partículas</strong> en cuatro clases de portador. DINOv2 ViT-S/14 con ajuste fino completo y ensamble de 3 semillas, entrenado con ${miles(MF.n_recortes)} recortes de ${miles(MF.n_articulos_entrenamiento)} artículos. El ensamble mejora ≈ +${D.nffa.ens_acc} de exactitud y +${D.nffa.ens_f1} de F1 macro frente a una semilla (D34). <strong>El modelo final se entrenó con todos los datos: no se puede evaluar</strong>; la única estimación honesta es la validación cruzada por artículo.`;
    $('#lectura-aviso').innerHTML = 'Exploratorio. Las probabilidades no están calibradas. Solo tiene sentido con micrografías de partículas; la etiqueta es la clase del artículo, no la del recorte; «nanomaterial» es una categoría general. Sin validación externa.';
    $('#grafica').innerHTML = `<div class="kpis" role="list">
      <div class="kpi" role="listitem"><b>${dec(MF.exactitud, 3)}</b><span>exactitud</span></div>
      <div class="kpi" role="listitem"><b>${dec(MF.f1, 3)}</b><span>F1 macro</span></div>
      <div class="kpi" role="listitem"><b>${dec(MF.exactitud_bal, 3)}</b><span>exactitud balanceada</span></div>
      <div class="kpi base" role="listitem"><b>${dec(MF.linea_base, 3)}</b><span>exactitud de la clase mayoritaria</span></div></div>
      <p class="nota-tabla"><strong>Desempeño de referencia:</strong> validación cruzada por artículo, ${esc(MF.validacion)}, n = ${miles(MF.n_articulos)} artículos. La línea base (${dec(MF.linea_base, 3)}) es la de la clase mayoritaria con los mismos artículos: ${miles(MF.mayoritaria_n)} de ${miles(MF.n_linea_base)} («nanomaterial»).</p>
      <p class="nota-tabla"><strong>Demo «sube tu micrografía»:</strong> corre en el navegador con ONNX (la hizo Carlos; verificada con 20 de 20 entradas de prueba). Úsala solo con micrografías de partículas: con espectros, gráficas o fotos la salida no significa nada.</p>
      <p class="nota-tabla">Fuente: <code>${esc(MF.fuente)}</code>.</p>`;
    $('#grafica').setAttribute('aria-label', `Modelo final: exactitud ${dec(MF.exactitud, 3)} y F1 macro ${dec(MF.f1, 3)} por validación cruzada por artículo, n = ${MF.n_articulos}.`);
  }
  function pintarNffa() {
    const N = D.nffa;
    $('#lectura-titulo').textContent = 'Lo que probamos y no funcionó: preentrenar con NFFA-EUROPE';
    $('#lectura-texto').innerHTML = `Preentrenar con imágenes SEM de NFFA-EUROPE (7 morfologías) antes de ajustar con nuestros recortes <strong>no mejora</strong>: B − A = ${sg(N.difs[0].f1)} ${rango(N.difs[0].ic[0], N.difs[0].ic[1])}, un intervalo que incluye el cero. Mezclar las etiquetas de NFFA daña el modelo de forma clara (C − A = ${sg(N.difs[2].f1)} ${rango(N.difs[2].ic[0], N.difs[2].ic[1])}). Por semilla, B − A = ${esc(N.por_semilla_BA)}. Es un resultado negativo, y lo presentamos como tal.`;
    $('#lectura-aviso').innerHTML = `${miles(N.n_articulos)} artículos, 3 semillas por brazo, criterio fijado antes de ver los resultados. La etapa 1 corrió una vez y se probó una sola configuración. Fuente: ${esc(N.fuente)}.`;
    const tabla = `<table class="tabla-mini"><caption>Brazos · n = ${miles(N.n_articulos)} artículos · media ± desviación entre semillas</caption>
      <thead><tr><th></th><th>Exactitud</th><th>F1 macro</th><th>F1 macro, ensamble</th></tr></thead><tbody>
      ${N.brazos.map(a => filaT([a.nombre, `${dec(a.acc, 3)} ± ${dec(a.acc_sd, 3)}`, `${dec(a.f1, 3)} ± ${dec(a.f1_sd, 3)}`, dec(a.f1_ens, 3)])).join('')}</tbody></table>
      <table class="tabla-mini"><caption>Diferencias en F1 macro (ensamble) [IC 95 %]</caption><tbody>
      ${N.difs.map(x => filaT([x.nombre.replace('-', '−'), `${sg(x.f1)} ${rango(x.ic[0], x.ic[1])}`, x.ic[0] < 0 && x.ic[1] > 0 ? 'incluye el cero' : ''], x.ic[0] < 0 && x.ic[1] > 0 ? 'cero' : '')).join('')}</tbody></table>`;
    $('#grafica').innerHTML = figTarjeta('nffa', 'Preentrenar con NFFA-EUROPE antes de ajustar con los recortes: F1 macro por semilla y diferencias entre brazos') + tabla;
    $('#grafica').setAttribute('aria-label', 'Experimento NFFA: figura y tablas de los tres brazos y sus diferencias.');
  }
  function pintarModelo() {
    $$('#modelo-pestanas button').forEach(b => b.setAttribute('aria-selected', b.dataset.tab === tab));
    const especial = { recortes: pintarRecortes, final: pintarFinal, nffa: pintarNffa }[tab];
    if (especial) { $('.interruptor').hidden = true; especial(); return; }
    $('.interruptor').hidden = false;
    const T = TABS[tab], d = T.datos, ic = $('#chk-ic').checked;
    $('#lectura-titulo').textContent = T.titulo;
    $('#lectura-texto').innerHTML = T.texto;
    $('#lectura-aviso').innerHTML = esc(T.aviso);
    const x0 = Math.max(215, Math.round(Math.max(...d.items.map(i => i.nombre.length)) * 8.3) + 16), x1 = x0 + 345, W = x1 + 205, fila = 46, top = 14, alto = top + d.items.length * fila + 52;
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
    const hayImagen = d.items.some(i => i.id === 'atlas'), hayFusion = d.items.some(i => /^fusion/.test(i.id));
    const ley = `<div class="leyenda"><span><i style="background:var(--base)"></i>línea base</span><span><i style="background:var(--accent)"></i>modelo con medidas</span>${hayImagen ? '<span><i style="background:var(--azul)"></i>solo imagen</span>' : ''}${hayFusion ? '<span><i style="background:var(--fusion)"></i>imagen + medidas</span>' : ''}<span>n = ${miles(d.n_filas)} ${tab === 'imagen' ? 'figuras' : 'filas'} · ${miles(d.n_articulos)} artículos · fuente: ${esc(d.fuente)}</span></div>`;
    const g = $('#grafica');
    g.innerHTML = s + ley;
    g.setAttribute('aria-label', `${T.titulo}. ` + d.items.map(i => `${i.nombre} ${dec(i.valor, 2)}`).join('; '));
  }
  $$('#modelo-pestanas button').forEach(b => b.addEventListener('click', () => { tab = b.dataset.tab; pintarModelo(); }));
  $('#chk-ic').addEventListener('change', pintarModelo);
  pintarModelo();

  /* ---------- decisiones ---------- */
  const filas = D.decisiones.filas, grupos = D.decisiones.grupos;
  let secSel = '';
  const chips = $('#dec-chips');
  [['', 'Todas'], ...grupos.map(s => [s, s])].forEach(([v, t]) => {
    const b = el('button', { type: 'button', textContent: t }); b.dataset.sec = v; b.setAttribute('aria-pressed', v === '');
    b.addEventListener('click', () => { secSel = v; pintarDecisiones(); }); chips.append(b);
  });
  const claseEstado = t => { const x = t.toLowerCase(); return x.startsWith('cerrada') ? ['Cerrada', 'cerrada'] : x.startsWith('abierta') ? ['Abierta', 'abierta'] : x.startsWith('en curso') ? ['En curso', 'en-curso'] : x.startsWith('propuesta') ? ['Propuesta', 'propuesta'] : x.startsWith('superada') ? ['Superada', 'superada'] : ['Pendiente', 'pendiente']; };
  function pintarDecisiones() {
    const est = $('#dec-estado').value, q = $('#dec-buscar').value.trim().toLowerCase();
    $$('button', chips).forEach(b => b.setAttribute('aria-pressed', b.dataset.sec === secSel));
    const vis = filas.filter(f => (!secSel || f.grupo === secSel) && (!est || claseEstado(f.estado)[0] === est)
      && (!q || (f.decision + ' ' + f.porque + ' ' + f.evidencia + ' ' + f.id).toLowerCase().includes(q)));
    $('#dec-conteo').textContent = `${vis.length} de ${filas.length} decisiones`;
    $('#dec-tabla tbody').innerHTML = vis.map(f => {
      const [lab, cl] = claseEstado(f.estado.replace(/\*\*/g, '')), extra = f.estado.replace(/\*\*/g, '').replace(/^(Cerrada|Abierta|En curso|Pendiente|Propuesta|Superada)[;:,.]?\s*/i, '');
      return `<tr><td>${esc(f.id)}</td><td>${md(f.decision)}</td><td>${md(f.porque)}</td><td>${md(f.evidencia || '—')}</td><td><span class="estado ${cl}">${lab}</span>${extra ? `<span class="estado-extra">${md(extra)}</span>` : ''}</td></tr>`;
    }).join('') || '<tr><td colspan="5">Ninguna decisión coincide con el filtro.</td></tr>';
  }
  $('#dec-estado').addEventListener('change', pintarDecisiones);
  $('#dec-buscar').addEventListener('input', pintarDecisiones);
  pintarDecisiones();

  /* ---------- limitaciones ---------- */
  const limites = [
    ['La unidad es el artículo, no el experimento', 'Ningún artículo está en entrenamiento y prueba a la vez, pero eso no descarta datos reutilizados entre artículos distintos.'],
    ['Figura completa, no panel', 'Muchas figuras mezclan varias micrografías, espectros y texto: es la principal limitación del modelo de imágenes. Los recortes de panel mejoran un poco la imagen (pestaña «Con recortes de panel»), pero la ventaja se debe en buena parte a que aportan más vistas por artículo.'],
    ['Una micrografía es solo parte de la información', 'No dice cómo se preparó la muestra ni sus proporciones, que hoy faltan en la base.'],
    ['Una mención no prueba un método', 'En una muestra auditada, 9 de 30 banderas de formulación fueron dudosas. Son proxies ruidosos: no las usamos como resultado principal.'],
    ['Variables que no existen antes del experimento', 'Los modelos usan zeta y PDI ya medidos: explican la base, no predicen una formulación antes de prepararla. Faltan proporciones y condiciones.'],
    ['Las clases mezclan composición y uso', '«Nanomaterial» es una categoría general y se solapa con «inorgánico». Un F1 mayor con otras clases no prueba mejor capacidad sobre los mismos artículos.'],
    ['Intervalos condicionales', 'El bootstrap remuestrea predicciones ya hechas, no todos los reentrenamientos ni la búsqueda entre modelos: puede dar una impresión excesiva de certeza.'],
    ['Control de calidad asistido por IA', 'Una muestra de 20 artículos se revisó con ayuda de IA; falta una auditoría humana a ciegas amplia.'],
    ['Alcance y validación', 'Se excluyen vectores virales (AAV). Se probaron varias variantes del modelo de imágenes sobre las mismas particiones, y no hay validación externa.'],
    ['Demo «sube tu micrografía»', 'Corre en el navegador con ONNX (la hizo Carlos; 20 de 20 entradas de prueba verificadas contra PyTorch). Solo para micrografías de partículas: con espectros, gráficas o fotos la salida no significa nada. Las probabilidades no están calibradas y la etiqueta es la clase del artículo, no la del recorte.'],
  ];
  $('#limites').innerHTML = limites.map(([t, x]) => `<article class="tarjeta"><h3>${esc(t)}</h3><p>${esc(x)}</p></article>`).join('');

  /* ---------- siguientes pasos ---------- */
  $('#lista-siguientes').innerHTML = D.siguientes.map(t => `<li>${md(t)}</li>`).join('');
  $('#lista-siguientes').insertAdjacentHTML('afterend', `<div class="hecho"><strong>Ya hecho</strong><ul>${D.siguientes_hecho.map(t => `<li>${md(t)}</li>`).join('')}</ul></div>`);
})();
