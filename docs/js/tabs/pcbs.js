// SPDX-License-Identifier: MIT
// PCBs tab: the three boards, in 3D (the GLB written by make pcb-3d) or as a layer plot.
//
// Route: #pcbs/<board>/<mode>, board = left | right | sensor, mode = 3d | layers.
// The layer plot stacks the per-layer SVGs of a board (all share one viewBox, in mm). They are
// fetched as text and inlined, because raw.githubusercontent.com serves SVG as text/plain, which an
// <img> refuses. Each layer is drawn in currentColor, so the colour is set here; drill holes use
// var(--hole). Solder mask is drawn the way the fab makes it: the board shape in green with the
// mask layer (the openings) cut out of it.

import { assetUrl, downloadFile, esc, fetchText, githubTreeUrl, githubUrl, loadData } from '../assets.js';

const SVGNS = 'http://www.w3.org/2000/svg';
const MODES = ['3d', 'layers'];
const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;

let data, ctx, root, els;
let state = { board: 'right', mode: '3d' };
let viewer = null;          // ModelViewer, created on the first 3D visit
let viewerMod = null;
const glbRoots = new Map(); // board id -> THREE.Group (kept, so switching back does not refetch)
let glbShown = null;
let loadToken = 0;
const plots = new Map();    // board id -> Promise<{svg, view}>
let plot = null;            // { board, svg, view, cam: {x, y, s} }
const flipped = new Map();  // board id -> viewing the back
const layerOn = new Map();  // `${board}:${layer}` -> bool

const kib = (n) => (n >= 1 << 20 ? `${(n / (1 << 20)).toFixed(1)} MB` : `${Math.max(1, Math.round(n / 1024))} KB`);
const boardById = (id) => data.boards.find((b) => b.id === id) || data.boards[0];

function parseSub(sub) {
  const [b, m] = (sub || '').split('/');
  return {
    board: data.boards.some((x) => x.id === b) ? b : state.board,
    mode: MODES.includes(m) ? m : state.mode,
  };
}

// ------------------------------------------------------------------ DOM
export async function mount(section, c) {
  ctx = c;
  data = await loadData('pcbs');
  state = { ...state, ...parseSub(ctx.sub) };
  section.innerHTML = `
  <div class="split pcbs">
    <div class="stage pcb-stage" data-mode="3d">
      <div class="pcb-3d" aria-label="3D view of the board"></div>
      <div class="pcb-plot" tabindex="0" role="img" aria-roledescription="layer plot" hidden></div>
      <div class="viewer-status pcb-plot-status" hidden></div>
      <div class="viewer-hud">
        <p class="eyebrow pcb-hud-title"></p>
        <p class="eyebrow pcb-hud-read" aria-live="off"></p>
      </div>
      <div class="pcb-scale" aria-hidden="true" hidden><span class="pcb-scale-bar"></span><span class="pcb-scale-label"></span></div>
      <div class="viewer-tools pcb-tools-3d">
        <button class="btn" type="button" data-view="top">Top</button>
        <button class="btn" type="button" data-view="bottom">Bottom</button>
        <button class="btn" type="button" data-view="iso">Iso</button>
      </div>
      <div class="viewer-tools pcb-tools-plot" hidden>
        <button class="btn" type="button" data-zoom="out" aria-label="Zoom out">&minus;</button>
        <button class="btn" type="button" data-zoom="in" aria-label="Zoom in">+</button>
        <button class="btn" type="button" data-zoom="fit">Fit</button>
        <button class="btn" type="button" data-flip aria-pressed="false">View back</button>
      </div>
    </div>
    <aside class="panel pcb-panel" aria-label="Board">
      <section>
        <h2>Board</h2>
        <ul class="picklist pcb-boards"></ul>
      </section>
      <section>
        <h2 id="pcbModeLabel">View</h2>
        <div class="seg pcb-mode" role="radiogroup" aria-labelledby="pcbModeLabel">
          <label><input type="radio" name="pcbMode" value="3d"><span>3D</span></label>
          <label><input type="radio" name="pcbMode" value="layers"><span>Layers</span></label>
        </div>
        <div class="pcb-3d-opts">
          <label class="pcb-check"><input type="checkbox" class="pcb-clip"> Section through the board</label>
          <input type="range" class="pcb-clip-t" min="0.02" max="0.98" step="0.01" value="0.5" aria-label="Section position, left to right" disabled>
          <p class="pcb-hint">Drag to orbit, right-drag or two fingers to pan, scroll or pinch to zoom.</p>
        </div>
        <div class="pcb-layer-opts" hidden>
          <ul class="pcb-layers" aria-label="Layers"></ul>
          <p class="pcb-hint">Drag to pan, scroll or pinch to zoom, arrow keys and + / - on the plot. The far side shows through, dimmed.</p>
        </div>
      </section>
      <section>
        <h2>Facts</h2>
        <dl class="dims pcb-facts"></dl>
      </section>
      <section>
        <h2>Parts worth knowing</h2>
        <ul class="pcb-parts"></ul>
      </section>
      <section>
        <h2>Files</h2>
        <div class="pcb-files"></div>
        <div class="pcb-renders"></div>
      </section>
      <p class="note pcb-note"></p>
    </aside>
  </div>`;
  root = section.querySelector('.pcbs');
  const q = (s) => root.querySelector(s);
  els = {
    stage: q('.pcb-stage'), host3d: q('.pcb-3d'), plot: q('.pcb-plot'), plotStatus: q('.pcb-plot-status'),
    title: q('.pcb-hud-title'), read: q('.pcb-hud-read'), scale: q('.pcb-scale'),
    tools3d: q('.pcb-tools-3d'), toolsPlot: q('.pcb-tools-plot'), flip: q('[data-flip]'),
    boards: q('.pcb-boards'), opts3d: q('.pcb-3d-opts'), optsLayers: q('.pcb-layer-opts'), layers: q('.pcb-layers'),
    clip: q('.pcb-clip'), clipT: q('.pcb-clip-t'),
    facts: q('.pcb-facts'), parts: q('.pcb-parts'), files: q('.pcb-files'), renders: q('.pcb-renders'), note: q('.pcb-note'),
  };

  els.boards.innerHTML = data.boards.map((b) => `
    <li><button type="button" data-board="${b.id}" aria-pressed="false">${esc(b.name)}<small>${b.size_mm[0].toFixed(0)} x ${b.size_mm[1].toFixed(0)} mm</small></button></li>`).join('');
  els.boards.addEventListener('click', (e) => {
    const btn = e.target.closest('[data-board]');
    if (btn) go({ board: btn.dataset.board });
  });
  root.querySelectorAll('input[name=pcbMode]').forEach((r) => r.addEventListener('change', () => go({ mode: r.value })));
  els.tools3d.addEventListener('click', (e) => {
    const v = e.target.closest('[data-view]')?.dataset.view;
    if (v && viewer && glbShown) viewer.fit(v, glbShown);
  });
  els.clip.addEventListener('change', () => {
    els.clipT.disabled = !els.clip.checked;
    viewer?.setClip({ on: els.clip.checked, axis: 'x', t: Number(els.clipT.value) });
  });
  els.clipT.addEventListener('input', () => viewer?.setClip({ t: Number(els.clipT.value) }));
  els.toolsPlot.addEventListener('click', (e) => {
    const z = e.target.closest('[data-zoom]')?.dataset.zoom;
    if (z === 'fit') fitPlot(true);
    else if (z) zoomBy(z === 'in' ? 1.5 : 1 / 1.5);
    if (e.target.closest('[data-flip]')) setFlip(!flipped.get(state.board));
  });
  els.layers.addEventListener('change', (e) => {
    const id = e.target.closest('input')?.dataset.layer;
    if (!id) return;
    layerOn.set(`${state.board}:${id}`, e.target.checked);
    applyLayers();
  });
  bindPlotInput();
  new ResizeObserver(() => { if (plot && state.mode === 'layers') { if (!plot.cam) fitPlot(); else drawCam(); } }).observe(els.plot);

  render();
}

export function show(sub) {
  const next = parseSub(sub);
  if (next.board !== state.board || next.mode !== state.mode) {
    state = { ...state, ...next };
    render();
  } else {
    viewer?.setActive(state.mode === '3d');
  }
}

export function hide() {
  viewer?.setActive(false);
}

function go(patch) {
  state = { ...state, ...patch };
  ctx.navigate(`${state.board}/${state.mode}`);
  render();
}

// ------------------------------------------------------------------ panel
function render() {
  const b = boardById(state.board);
  els.boards.querySelectorAll('[data-board]').forEach((btn) => btn.setAttribute('aria-pressed', String(btn.dataset.board === b.id)));
  root.querySelectorAll('input[name=pcbMode]').forEach((r) => { r.checked = r.value === state.mode; });
  const is3d = state.mode === '3d';
  els.stage.dataset.mode = state.mode;
  els.host3d.hidden = !is3d;
  els.plot.hidden = is3d;
  els.tools3d.hidden = !is3d;
  els.toolsPlot.hidden = is3d;
  els.opts3d.hidden = !is3d;
  els.optsLayers.hidden = is3d;
  els.scale.hidden = true;   // shown once a plot is drawn
  els.plotStatus.hidden = true;
  els.read.textContent = '';
  els.title.textContent = `${b.name} · ${is3d ? '3D' : (flipped.get(b.id) ? 'Layers, seen from the back' : 'Layers, seen from the front')}`;

  els.facts.innerHTML = b.facts.map(([k, v]) => `<dt>${esc(k)}</dt><dd>${esc(v)}</dd>`).join('');
  els.parts.innerHTML = b.parts.map((p) => `
    <li><span class="pcb-ref">${esc(p.ref)}</span><span class="pcb-part"><b>${esc(p.role)}</b> ${esc(p.value)}<small>${esc(p.side)}</small></span></li>`).join('');
  const f = b.files, s = b.sizes;
  els.files.innerHTML = `
    <div class="pcb-dl">
      <button class="btn primary" type="button" data-dl="${esc(f.gerbers)}">Gerbers (zip)<small>${kib(s.gerbers)}</small></button>
      <button class="btn" type="button" data-dl="${esc(f.step)}">STEP model<small>${kib(s.step)}</small></button>
      <button class="btn" type="button" data-dl="${esc(f.kicad_pcb)}">KiCad board<small>${kib(s.kicad_pcb)}</small></button>
      <button class="btn" type="button" data-dl="${esc(f.glb)}">GLB (3D view)<small>${kib(s.glb)}</small></button>
    </div>
    <p class="untested">Untested: never fabricated. Do not order from these files yet.</p>
    <p class="pcb-gh"><a href="${githubTreeUrl(b.folder)}" rel="noopener">View ${esc(b.folder)}/ on GitHub</a></p>`;
  els.files.querySelectorAll('[data-dl]').forEach((btn) => btn.addEventListener('click', async () => {
    btn.disabled = true;
    try { await downloadFile(btn.dataset.dl); } finally { btn.disabled = false; }
  }));
  els.renders.innerHTML = ['render_top', 'render_bottom'].map((k) => `
    <a class="pcb-thumb" href="${githubUrl(f[k])}" rel="noopener">
      <img src="${assetUrl(f[k])}" alt="${esc(b.name)}, KiCad render of the ${k === 'render_top' ? 'front' : 'back'}" loading="lazy" width="160" height="${b.id === 'sensor' ? 160 : 107}">
      <span>${k === 'render_top' ? 'Front' : 'Back'} render</span>
    </a>`).join('');
  els.renders.querySelectorAll('img').forEach((img) => img.addEventListener('error', () => { img.closest('.pcb-thumb').classList.add('missing'); }, { once: true }));
  els.note.innerHTML = noteFor(b);

  renderLayerList(b);
  if (is3d) show3d(b); else showPlot(b);
  viewer?.setActive(is3d);
}

function noteFor(b) {
  const bits = [];
  if (b.notes) bits.push(esc(b.notes[0].toUpperCase() + b.notes.slice(1)) + '.');
  if (b.id === 'left') bits.push('The left board is the mirror image of the right one around the controller, with a third thumb key and no notch.');
  if (b.id === 'sensor') bits.push('The sensor and its lens sit on the back, facing the ball; the slot in the middle takes the sensor body.');
  bits.push('Exported from <b>' + esc(b.stem) + '.kicad_pcb</b> with <code>make pcb-3d</code>.');
  return bits.join(' ');
}

// ------------------------------------------------------------------ 3D
async function show3d(b) {
  const token = ++loadToken;
  if (!viewer) {
    viewerMod = await import('../viewer.js');
    viewer = new viewerMod.ModelViewer(els.host3d, { grid: true, label: '3D model of the board' });
  }
  viewer.setActive(true);
  if (glbShown && glbShown.userData.board === b.id) return;
  if (glbShown) { viewer.content.remove(glbShown); glbShown = null; viewer.requestRender(); }
  let obj = glbRoots.get(b.id);
  if (!obj) {
    try {
      obj = await viewer.loadGLB(b.files.glb, { add: false, name: b.name });
    } catch (e) {
      console.warn(e.message);   // the viewer already shows the message in its status box
      return;
    }
    obj.userData.board = b.id;
    glbRoots.set(b.id, obj);
  } else {
    viewer.hideStatus();
  }
  if (token !== loadToken || state.mode !== '3d' || state.board !== b.id) return;
  glbShown = obj;
  viewer.add(obj);
  if (els.clip.checked) viewer.setClip({ on: true, axis: 'x', t: Number(els.clipT.value) });
  viewer.fit('iso', obj);
}

// ------------------------------------------------------------------ layer list
function isOn(b, l) {
  const key = `${b.id}:${l.id}`;
  if (!layerOn.has(key)) layerOn.set(key, l.side === 'both' || l.side === 'front');
  return layerOn.get(key);
}

function renderLayerList(b) {
  els.layers.innerHTML = b.layers.slice().reverse().map((l) => `
    <li><label>
      <input type="checkbox" data-layer="${l.id}" ${isOn(b, l) ? 'checked' : ''}>
      <span class="pcb-swatch kind-${l.kind}" style="${l.color ? `--sw:${l.color}` : ''}"></span>
      <span class="pcb-layer-name">${esc(l.label)}</span><small>${esc(l.id)}</small>
    </label></li>`).join('');
}

function setFlip(on) {
  const b = boardById(state.board);
  flipped.set(b.id, on);
  // turning the board over brings the other face's layers up: swap front and back visibility
  const pairs = [['F.Cu', 'B.Cu'], ['F.Mask', 'B.Mask'], ['F.Silkscreen', 'B.Silkscreen']];
  for (const [f, k] of pairs) {
    const a = layerOn.get(`${b.id}:${f}`), c = layerOn.get(`${b.id}:${k}`);
    layerOn.set(`${b.id}:${f}`, c);
    layerOn.set(`${b.id}:${k}`, a);
  }
  renderLayerList(b);
  els.title.textContent = `${b.name} · ${on ? 'Layers, seen from the back' : 'Layers, seen from the front'}`;
  applyLayers();
}

// ------------------------------------------------------------------ layer plot
function el(name, attrs = {}) {
  const n = document.createElementNS(SVGNS, name);
  for (const [k, v] of Object.entries(attrs)) n.setAttribute(k, v);
  return n;
}

/** Children of a fetched layer SVG, ready to append (the KiCad root and its <title>/<desc> are dropped). */
function layerContent(text) {
  const doc = new DOMParser().parseFromString(text, 'image/svg+xml');
  const g = el('g');
  for (const c of [...doc.documentElement.children]) {
    if (c.localName === 'title' || c.localName === 'desc') continue;
    g.append(document.importNode(c, true));
  }
  return g;
}

function buildPlot(b) {
  if (!plots.has(b.id)) {
    const p = (async () => {
      const [outlineText, ...layerTexts] = await Promise.all([fetchText(b.files.outline), ...b.layers.map((l) => fetchText(l.path))]);
      const [vx, vy, vw, vh] = b.viewbox;
      const svg = el('svg', { class: 'pcb-svg', xmlns: SVGNS, preserveAspectRatio: 'xMidYMid meet' });
      const defs = el('defs');
      const pre = `pcb-${b.id}`;
      // drafting grid in mm: fine every 1, strong every 10
      const pat1 = el('pattern', { id: `${pre}-g1`, width: 1, height: 1, patternUnits: 'userSpaceOnUse', x: 0, y: 0 });
      pat1.append(el('path', { d: 'M 1 0 L 0 0 0 1', class: 'grid-fine' }));
      const pat10 = el('pattern', { id: `${pre}-g10`, width: 10, height: 10, patternUnits: 'userSpaceOnUse', x: 0, y: 0 });
      pat10.append(el('rect', { width: 10, height: 10, fill: `url(#${pre}-g1)` }), el('path', { d: 'M 10 0 L 0 0 0 10', class: 'grid-major' }));
      defs.append(pat1, pat10);
      svg.append(defs);
      const big = Math.max(vw, vh) * 6;
      svg.append(el('rect', { class: 'pcb-grid', x: vx - big, y: vy - big, width: vw + 2 * big, height: vh + 2 * big, fill: `url(#${pre}-g10)` }));

      const outline = layerContent(outlineText);
      const outlineD = outline.querySelector('path').getAttribute('d');
      const board = el('g', { class: 'pcb-board' });
      board.append(el('path', { class: 'pcb-substrate', d: outlineD, 'fill-rule': 'evenodd' }));
      b.layers.forEach((l, i) => {
        const content = layerContent(layerTexts[i]);
        const g = el('g', { class: `pcb-layer kind-${l.kind}`, 'data-layer': l.id, 'data-side': l.side });
        if (l.color) g.style.color = l.color;
        if (l.kind === 'mask') {
          // the mask file holds the openings; the mask itself is the board minus those openings
          const id = `${pre}-mask-${l.id.replace('.', '')}`;
          const m = el('mask', { id, maskUnits: 'userSpaceOnUse', x: vx, y: vy, width: vw, height: vh });
          m.append(el('path', { d: outlineD, fill: '#fff', 'fill-rule': 'evenodd' }));
          content.setAttribute('style', 'color:#000');
          m.append(content);
          defs.append(m);
          g.append(el('path', { d: outlineD, 'fill-rule': 'evenodd', fill: 'currentColor', mask: `url(#${id})`, class: 'mask-fill' }));
        } else {
          g.append(content);
        }
        board.append(g);
      });
      const mirror = el('g', { class: 'pcb-mirror' });
      mirror.append(board);
      svg.append(mirror);
      svg.append(dimensions(b, vx, vy, vw, vh));
      return { svg, view: b.viewbox };
    })();
    plots.set(b.id, p);
    p.catch(() => plots.delete(b.id));   // let a later visit try again
  }
  return plots.get(b.id);
}

/** Overall width and height as drawing dimensions just outside the board. */
function dimensions(b, vx, vy, vw, vh) {
  const [w, h] = b.size_mm;
  const g = el('g', { class: 'pcb-dims', 'aria-hidden': 'true' });
  const off = Math.max(2.4, Math.min(w, h) * 0.06);
  const fs = Math.max(1.4, Math.min(w, h) * 0.035);
  const y = h + off, x = w + off;
  const tick = fs * 0.5;
  g.append(
    el('path', { d: `M0 ${h + 0.6} V${y + tick} M${w} ${h + 0.6} V${y + tick} M0 ${y} H${w}`, class: 'dim-line' }),
    el('path', { d: `M${w + 0.6} 0 H${x + tick} M${w + 0.6} ${h} H${x + tick} M${x} 0 V${h}`, class: 'dim-line' }),
  );
  const t1 = el('text', { x: w / 2, y: y - fs * 0.35, 'font-size': fs, 'text-anchor': 'middle' });
  t1.textContent = `${w.toFixed(1)}`;
  const t2 = el('text', { x: x - fs * 0.35, y: h / 2, 'font-size': fs, 'text-anchor': 'middle', transform: `rotate(-90 ${x - fs * 0.35} ${h / 2})` });
  t2.textContent = `${h.toFixed(1)}`;
  g.append(t1, t2);
  return g;
}

async function showPlot(b) {
  const token = ++loadToken;
  if (plot?.board === b.id) { applyLayers(); drawCam(); return; }
  els.plot.replaceChildren();
  els.plotStatus.className = 'viewer-status pcb-plot-status';
  els.plotStatus.textContent = `Loading the layers of ${b.name}`;
  els.plotStatus.hidden = false;
  let built;
  try {
    built = await buildPlot(b);
  } catch (e) {
    if (token !== loadToken) return;
    els.plotStatus.className = 'viewer-status pcb-plot-status error';
    els.plotStatus.textContent = e.message;
    plot = null;
    return;
  }
  if (token !== loadToken || state.mode !== 'layers' || state.board !== b.id) return;
  els.plotStatus.hidden = true;
  els.plot.replaceChildren(built.svg);
  els.plot.setAttribute('aria-label', `${b.name}, layer plot, ${b.size_mm[0].toFixed(1)} by ${b.size_mm[1].toFixed(1)} mm`);
  plot = { board: b.id, svg: built.svg, view: built.view, cam: null };
  applyLayers();
  fitPlot();
}

function applyLayers() {
  if (!plot) return;
  const b = boardById(plot.board);
  const back = !!flipped.get(b.id);
  const near = back ? 'back' : 'front';
  const [vx, , vw] = b.viewbox;
  const mirror = plot.svg.querySelector('.pcb-mirror');
  mirror.setAttribute('transform', back ? `translate(${2 * vx + vw} 0) scale(-1 1)` : '');
  const board = plot.svg.querySelector('.pcb-board');
  const groups = b.layers.map((l) => board.querySelector(`[data-layer="${l.id}"]`));
  // draw order: the far face first, the near face on top, the edge last
  const order = back ? [...groups].reverse() : groups;
  const edge = order.find((g) => g.dataset.side === 'both');
  [...order.filter((g) => g !== edge), edge].forEach((g) => board.append(g));
  b.layers.forEach((l, i) => {
    const g = groups[i];
    g.style.display = isOn(b, l) ? '' : 'none';
    g.classList.toggle('far', l.side !== 'both' && l.side !== near);
  });
  els.flip.setAttribute('aria-pressed', String(back));
  els.flip.textContent = back ? 'View front' : 'View back';
}

// camera: x, y = the plot point at the centre of the stage (mm), s = pixels per mm
function fitPlot(animate = false) {
  if (!plot) return;
  const [vx, vy, vw, vh] = plot.view;
  const r = els.plot.getBoundingClientRect();
  if (!r.width || !r.height) return;
  const pad = 56;
  const s = Math.min((r.width - pad * 2) / (vw + 8), (r.height - pad * 2) / (vh + 8));
  setCam({ x: vx + vw / 2 + 2, y: vy + vh / 2 + 2, s: Math.max(0.5, s) }, animate);
}

function setCam(cam, animate = false) {
  if (!plot) return;
  const lim = plotLimits();
  cam.s = Math.min(lim.smax, Math.max(lim.smin, cam.s));
  if (!animate || reducedMotion || !plot.cam) { plot.cam = cam; drawCam(); return; }
  const from = { ...plot.cam }, t0 = performance.now();
  const step = (now) => {
    const k = Math.min(1, (now - t0) / 220), e = 1 - (1 - k) ** 3;
    plot.cam = { x: from.x + (cam.x - from.x) * e, y: from.y + (cam.y - from.y) * e, s: from.s * (cam.s / from.s) ** e };
    drawCam();
    if (k < 1) requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
}

function plotLimits() {
  const [, , vw, vh] = plot.view;
  const r = els.plot.getBoundingClientRect();
  return { smin: Math.min(r.width / (vw * 4), r.height / (vh * 4)), smax: 400 };
}

function drawCam() {
  if (!plot?.cam) return;
  const r = els.plot.getBoundingClientRect();
  if (!r.width || !r.height) return;
  const { x, y, s } = plot.cam;
  const w = r.width / s, h = r.height / s;
  plot.svg.setAttribute('viewBox', `${x - w / 2} ${y - h / 2} ${w} ${h}`);
  plot.svg.style.setProperty('--px', `${1 / s}`);   // one screen pixel in mm, for hairlines
  plot.svg.classList.toggle('zoomed', s > 9);
  els.scale.hidden = state.mode !== 'layers';
  // scale bar: the round length closest to 90 px
  const target = 90 / s;
  const nice = [0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50, 100].reduce((a, v) => (Math.abs(Math.log(v / target)) < Math.abs(Math.log(a / target)) ? v : a), 10);
  els.scale.querySelector('.pcb-scale-bar').style.width = `${nice * s}px`;
  els.scale.querySelector('.pcb-scale-label').textContent = `${nice} mm`;
}

function zoomBy(f, cx, cy) {
  if (!plot?.cam) return;
  const r = els.plot.getBoundingClientRect();
  const { x, y, s } = plot.cam;
  const lim = plotLimits();
  const ns = Math.min(lim.smax, Math.max(lim.smin, s * f));
  // keep the point under (cx, cy) in place; default: the centre
  const px = cx == null ? 0 : cx - r.left - r.width / 2;
  const py = cy == null ? 0 : cy - r.top - r.height / 2;
  const mx = x + px / s, my = y + py / s;
  setCam({ x: mx - px / ns, y: my - py / ns, s: ns }, cx == null);
}

function toPlot(clientX, clientY) {
  const r = els.plot.getBoundingClientRect();
  const { x, y, s } = plot.cam;
  return { x: x + (clientX - r.left - r.width / 2) / s, y: y + (clientY - r.top - r.height / 2) / s };
}

function bindPlotInput() {
  const pts = new Map();
  let pinch = null;
  const p = els.plot;
  p.addEventListener('pointerdown', (e) => {
    if (!plot?.cam) return;
    p.setPointerCapture(e.pointerId);
    pts.set(e.pointerId, { x: e.clientX, y: e.clientY });
    p.classList.add('dragging');
    if (pts.size === 2) {
      const [a, c] = [...pts.values()];
      pinch = { d: Math.hypot(a.x - c.x, a.y - c.y), s: plot.cam.s };
    }
  });
  p.addEventListener('pointermove', (e) => {
    if (plot?.cam) readout(e);
    const prev = pts.get(e.pointerId);
    if (!prev || !plot?.cam) return;
    const cur = { x: e.clientX, y: e.clientY };
    pts.set(e.pointerId, cur);
    if (pts.size === 1) {
      plot.cam = { ...plot.cam, x: plot.cam.x - (cur.x - prev.x) / plot.cam.s, y: plot.cam.y - (cur.y - prev.y) / plot.cam.s };
      drawCam();
    } else if (pts.size === 2 && pinch) {
      const [a, c] = [...pts.values()];
      const d = Math.hypot(a.x - c.x, a.y - c.y);
      const target = pinch.s * d / pinch.d;
      zoomBy(target / plot.cam.s, (a.x + c.x) / 2, (a.y + c.y) / 2);
      // pan with the midpoint as well
      const mid = { x: (a.x + c.x) / 2, y: (a.y + c.y) / 2 };
      const pmid = pinch.mid || mid;
      plot.cam = { ...plot.cam, x: plot.cam.x - (mid.x - pmid.x) / plot.cam.s, y: plot.cam.y - (mid.y - pmid.y) / plot.cam.s };
      pinch.mid = mid;
      drawCam();
    }
  });
  const up = (e) => {
    pts.delete(e.pointerId);
    if (pts.size < 2) pinch = null;
    if (!pts.size) p.classList.remove('dragging');
  };
  p.addEventListener('pointerup', up);
  p.addEventListener('pointercancel', up);
  p.addEventListener('pointerleave', () => { els.read.textContent = ''; });
  p.addEventListener('wheel', (e) => {
    if (!plot?.cam) return;
    e.preventDefault();
    const k = e.ctrlKey ? 0.01 : 0.0018;   // trackpad pinch arrives as ctrl+wheel
    zoomBy(Math.exp(-e.deltaY * k), e.clientX, e.clientY);
  }, { passive: false });
  p.addEventListener('dblclick', (e) => zoomBy(2, e.clientX, e.clientY));
  p.addEventListener('keydown', (e) => {
    if (!plot?.cam) return;
    const stepPx = e.shiftKey ? 160 : 40;
    const moves = { ArrowLeft: [-1, 0], ArrowRight: [1, 0], ArrowUp: [0, -1], ArrowDown: [0, 1] };
    if (moves[e.key]) {
      const [dx, dy] = moves[e.key];
      plot.cam = { ...plot.cam, x: plot.cam.x + dx * stepPx / plot.cam.s, y: plot.cam.y + dy * stepPx / plot.cam.s };
      drawCam();
    } else if (e.key === '+' || e.key === '=') zoomBy(1.5);
    else if (e.key === '-' || e.key === '_') zoomBy(1 / 1.5);
    else if (e.key === '0' || e.key === 'Home') fitPlot(true);
    else return;
    e.preventDefault();
  });
}

/** Cursor position in board millimetres (from the outline's top left corner, y down as in KiCad). */
function readout(e) {
  const b = boardById(plot.board);
  const pt = toPlot(e.clientX, e.clientY);
  const [vx, , vw] = b.viewbox;
  const x = flipped.get(b.id) ? 2 * vx + vw - pt.x : pt.x;
  els.read.textContent = `x ${x.toFixed(2)}  y ${pt.y.toFixed(2)} mm`;
}
