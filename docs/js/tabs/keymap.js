// SPDX-License-Identifier: MIT
// Keymap tab: the ZMK keymap drawn on the real key positions of both halves.
//
// data/keymap.json gives the layers (bindings in matrix-transform order, each with the half and
// switch reference it lands on), the combos and the trackball listener; data/layout.json gives
// each switch's position and rotation per half in the layout frame (x outward to the pinky,
// y towards the user). The right half is drawn as is; the left half with x negated, so both
// pinkies point outward like on a desk. Sub route: #keymap/<layer id>.

import { esc, githubUrl, loadData } from '../assets.js';

const SVGNS = 'http://www.w3.org/2000/svg';
const GAP = 22;          // mm between the inner edges of the two halves when drawn side by side
const PAD = 6;           // mm around the drawing

let km, layout, root, board, detail, seg, info, current = null, stacked = null, ctx;
const keyEls = new Map(); // pos -> <g>

const kindNote = {
  'mod-tap': 'tap for the key, hold for the modifier',
  'layer-tap': 'tap for the key, hold for the layer',
  layer: 'hold for the layer',
  trans: 'transparent: falls through to the layer below',
  none: 'does nothing',
};

function el(tag, attrs = {}, parent) {
  const n = document.createElementNS(SVGNS, tag);
  for (const [k, v] of Object.entries(attrs)) if (v != null) n.setAttribute(k, v);
  if (parent) parent.append(n);
  return n;
}

/** Physical key: position in the drawing for a half (mirrors the left). */
function place(half, k, offset) {
  const s = half === 'left' ? -1 : 1;
  // the right half's thumbs fan counter-clockwise on the page (inner key lower), the mirrored
  // left half clockwise: rotation in the frame is negated for the right half
  return { x: offset + s * k.x, y: k.y, rot: -s * k.rot };
}

function halfBounds(half) {
  const b = layout.halves[half].bounds;
  return { min: b.min_x, max: b.max_x, minY: b.min_y, maxY: b.max_y };
}

function geometry(isStacked) {
  // returns per half: {dx, dy} where page x = dx + s*x, page y = dy + y
  const L = halfBounds('left');
  const R = halfBounds('right');
  const h = Math.max(L.maxY, R.maxY) - Math.min(L.minY, R.minY);
  if (isStacked) {
    // each half on its own row, left above right, both starting at x = 0
    const left = { dx: L.max, dy: -L.minY };              // -x + L.max >= 0
    const right = { dx: -R.min, dy: -R.minY + h + 14 };
    const w = Math.max(L.max - L.min, R.max - R.min);
    return { left, right, w, h: 2 * h + 14 };
  }
  const left = { dx: L.max, dy: -L.minY };                 // left half: x from 0 to L.max-L.min
  const right = { dx: (L.max - L.min) + GAP - R.min, dy: -R.minY };
  return { left, right, w: (L.max - L.min) + GAP + (R.max - R.min), h };
}

function outlinePath(half, g) {
  const s = half === 'left' ? -1 : 1;
  const pts = layout.halves[half].outline.map(([x, y]) => `${(g.dx + s * x).toFixed(2)},${(g.dy + y).toFixed(2)}`);
  return `M${pts.join('L')}Z`;
}

function legendSize(text, base) {
  const n = [...String(text)].length;
  if (n <= 1) return base;
  if (n <= 2) return base * 0.82;
  if (n <= 4) return base * 0.62;
  if (n <= 6) return base * 0.5;
  return base * 0.42;
}

/** Long labels ("Left click", "Studio unlock") wrap to two lines. */
function lines(text) {
  const t = String(text);
  if (t.length <= 6 || !t.includes(' ')) return [t];
  const i = t.indexOf(' ');
  return [t.slice(0, i), t.slice(i + 1)];
}

function drawBoard() {
  const isStacked = root.clientWidth < 720;
  if (isStacked === stacked && board.firstChild) return;
  stacked = isStacked;
  board.textContent = '';
  keyEls.clear();
  const g = geometry(isStacked);
  const svg = el('svg', {
    viewBox: `${-PAD} ${-PAD} ${g.w + 2 * PAD} ${g.h + 2 * PAD}`, class: 'km-svg',
    role: 'img', 'aria-labelledby': 'kmSvgTitle',
  }, board);
  el('title', { id: 'kmSvgTitle' }, svg).textContent = 'Both halves of the keyboard with the legends of the selected layer';
  const cap = layout.keycap;
  for (const half of ['left', 'right']) {
    const hg = g[half];
    const grp = el('g', { class: `km-half km-${half}` }, svg);
    el('path', { d: outlinePath(half, hg), class: 'km-outline' }, grp);
    const lbl = el('text', { x: half === 'left' ? 0 : hg.dx + layout.halves[half].bounds.max_x, y: -2, class: 'km-half-label',
                              'text-anchor': half === 'left' ? 'start' : 'end' }, grp);
    lbl.textContent = half === 'left' ? 'LEFT' : 'RIGHT';
    const ball = layout.halves[half].ball;
    if (ball) {
      const bx = hg.dx + ball.x, by = hg.dy + ball.y;
      el('circle', { cx: bx, cy: by, r: ball.pocket_d / 2 - 2, class: 'km-pocket' }, grp);
      el('circle', { cx: bx, cy: by, r: ball.d / 2, class: 'km-ball' }, grp);
      const t = el('text', { x: bx, y: by + 1.2, class: 'km-ball-label', 'text-anchor': 'middle' }, grp);
      t.textContent = `${ball.d} mm`;
    }
    const byRef = new Map(layout.halves[half].keys.map((k) => [k.ref, k]));
    for (const key of km.keys.filter((k) => k.half === half)) {
      const k = byRef.get(key.ref);
      if (!k) { console.warn(`keymap: ${half} ${key.ref} not in layout.json`); continue; }
      const p = place(half, k, 0);
      const kg = el('g', { class: 'km-key', transform: `translate(${(hg.dx + p.x).toFixed(2)} ${(hg.dy + p.y).toFixed(2)}) rotate(${p.rot})` }, grp);
      kg.dataset.pos = key.pos;
      el('rect', { x: -cap.width / 2, y: -cap.height / 2, width: cap.width, height: cap.height, rx: 1.6, class: 'km-cap' }, kg);
      el('title', {}, kg);
      el('g', { class: 'km-tap' }, kg);
      el('text', { x: 0, y: cap.height / 2 - 2.1, class: 'km-hold', 'text-anchor': 'middle' }, kg);
      el('text', { x: cap.width / 2 - 1.4, y: -cap.height / 2 + 3.2, class: 'km-flag', 'text-anchor': 'end' }, kg);
      keyEls.set(key.pos, kg);
      kg.addEventListener('pointerenter', () => describe(key.pos));
      kg.addEventListener('pointerleave', () => describe(null));
    }
  }
  if (current) paint(current);
}

function layerById(id) { return km.layers.find((l) => l.id === id) || km.layers[0]; }

function describe(pos) {
  if (pos == null) {
    detail.innerHTML = '<span class="km-detail-hint">Point at a key for its binding.</span>';
    return;
  }
  const L = layerById(current);
  const key = km.keys[pos];
  const b = L.bindings[pos];
  const base = km.layers[0].bindings[pos];
  const what = b.kind === 'trans'
    ? `transparent, falls through (base: ${esc(base.tap ?? '')}${base.hold ? ` / ${esc(base.hold)}` : ''})`
    : `${esc(b.tap ?? '')}${b.hold ? `, hold ${esc(b.hold)}` : ''}`;
  detail.innerHTML = `<b>${esc(key.half)} ${esc(key.name)}</b> <span class="km-mono">${esc(key.ref)} · position ${pos}</span>
    <span>${what}</span> <code>${esc(b.raw)}</code>`;
}

function heldKeysFor(L) {
  // keys on any layer whose hold (or press) opens L: those are the keys you hold to see L
  const out = new Set();
  for (const other of km.layers) {
    if (other === L) continue;
    for (const b of other.bindings) if (b.layer === L.name) out.add(b.pos);
  }
  return out;
}

function paint(id) {
  const L = layerById(id);
  const base = km.layers[0];
  const held = heldKeysFor(L);
  const comboKeys = new Set(km.combos.filter((c) => !c.layers.length || c.layers.includes(L.name)).flatMap((c) => c.positions));
  for (const [pos, kg] of keyEls) {
    const b = L.bindings[pos];
    const trans = b.kind === 'trans';
    const shown = trans ? base.bindings[pos] : b;
    kg.setAttribute('class', ['km-key', `k-${b.kind}`, b.layer ? 'k-switch' : '', held.has(pos) ? 'k-held' : '',
      comboKeys.has(pos) ? 'k-combo' : ''].filter(Boolean).join(' '));
    const tapG = kg.querySelector('.km-tap');
    tapG.textContent = '';
    const tap = shown.kind === 'none' ? '' : (shown.tap ?? '');
    const ls = lines(tap);
    const size = legendSize(ls.reduce((a, s) => (s.length > a.length ? s : a), ''), 7.2);
    const lh = size * 1.05;
    const y0 = (shown.hold ? -1.4 : 0) - ((ls.length - 1) * lh) / 2 + size * 0.36;
    ls.forEach((s, i) => {
      const t = el('text', { x: 0, y: (y0 + i * lh).toFixed(2), 'text-anchor': 'middle', class: 'km-tap-t', 'font-size': size.toFixed(2) }, tapG);
      t.textContent = s;
    });
    kg.querySelector('.km-hold').textContent = shown.hold ?? '';
    kg.querySelector('.km-flag').textContent = held.has(pos) ? 'HELD' : '';
    kg.querySelector('title').textContent = trans
      ? `${km.keys[pos].half} ${km.keys[pos].name}: transparent (${base.bindings[pos].tap ?? ''})`
      : `${km.keys[pos].half} ${km.keys[pos].name}: ${b.tap ?? 'nothing'}${b.hold ? `, hold ${b.hold}` : ''}`;
  }
  paintInfo(L, held);
  describe(null);
}

function posLabel(pos) {
  const b = km.layers[0].bindings[pos];
  return b.tap ?? b.raw;
}

function paintInfo(L, held) {
  const p = km.pointer;
  const mode = p.modes.find((m) => m.layer === L.name);
  const rows = [];
  rows.push(`<dt>Layer</dt><dd>${L.index} · ${esc(L.name)}</dd>`);
  if (L.access) rows.push(`<dt>Reached by</dt><dd>${esc(L.access)}</dd>`);
  else if (L.index === 0) rows.push('<dt>Reached by</dt><dd>always active</dd>');
  if (held.size) rows.push(`<dt>Held keys</dt><dd>${[...held].map((pos) => `${esc(km.keys[pos].half)} ${esc(km.keys[pos].name)} (${esc(posLabel(pos))})`).join(', ')}</dd>`);
  if (L.content) rows.push(`<dt>Holds</dt><dd>${esc(L.content)}</dd>`);
  if (L.name === p.auto_layer) {
    rows.push(`<dt>Trackball</dt><dd>opens by itself when the ${esc(p.sensor)} reports movement and stays ${p.auto_timeout_ms} ms after the last one; not within ${p.require_prior_idle_ms} ms of typing. Any key other than ${p.keep_positions.map((x) => `<kbd>${esc(posLabel(x))}</kbd>`).join(' ')} closes it.</dd>`);
  }
  if (mode) rows.push(`<dt>Trackball</dt><dd>${mode.effect.map(esc).join(', ')} <code>${mode.processors.map(esc).join(' ')}</code></dd>`);
  const counts = L.bindings.reduce((a, b) => ((a[b.kind] = (a[b.kind] || 0) + 1), a), {});
  rows.push(`<dt>Bindings</dt><dd>${L.bindings.length - (counts.trans || 0)} own, ${counts.trans || 0} transparent</dd>`);
  info.innerHTML = `<dl class="km-dl">${rows.join('')}</dl>`;
}

function select(id, push = true) {
  const L = layerById(id);
  current = L.id;
  const input = seg.querySelector(`input[value="${CSS.escape(L.id)}"]`);
  if (input && !input.checked) input.checked = true;
  paint(L.id);
  if (push) ctx.navigate(L.id === km.layers[0].id ? '' : L.id);
}

function comboHtml() {
  return km.combos.map((c, i) => {
    const keys = c.positions.map((pos) => `<kbd>${esc(posLabel(pos))}</kbd>`).join('<span class="km-plus">+</span>');
    const where = c.positions.map((pos) => `${km.keys[pos].half} ${km.keys[pos].name}`).join(', ');
    return `<li><button type="button" class="km-combo" data-i="${i}" aria-describedby="kmc${i}">
      <span class="km-combo-keys">${keys}</span><span class="km-arrow" aria-hidden="true">→</span>
      <b>${esc(c.binding.tap ?? c.binding.raw)}</b></button>
      <span class="km-combo-meta" id="kmc${i}">${esc(where)} · ${c.layers.length ? `on ${c.layers.map(esc).join(', ')}` : 'on every layer'} · within ${c.timeout_ms} ms · <code>${esc(c.binding.raw)}</code></span></li>`;
  }).join('');
}

function tableHtml() {
  // the same data as a table: for screen readers and for reading every layer at once
  const head = km.layers.map((l) => `<th scope="col">${esc(l.name)}</th>`).join('');
  const body = km.keys.map((k) => `<tr><th scope="row">${esc(k.half)} ${esc(k.name)} <small>${k.pos}</small></th>${
    km.layers.map((l) => {
      const b = l.bindings[k.pos];
      if (b.kind === 'trans') return '<td class="km-t-trans">▽</td>';
      if (b.kind === 'none') return '<td class="km-t-trans">·</td>';
      return `<td>${esc(b.tap ?? '')}${b.hold ? ` <small>${esc(b.hold)}</small>` : ''}</td>`;
    }).join('')}</tr>`).join('');
  return `<div class="table-wrap"><table class="data km-table"><thead><tr><th scope="col">Key</th>${head}</tr></thead><tbody>${body}</tbody></table></div>`;
}

export async function mount(section, c) {
  ctx = c;
  [km, layout] = await Promise.all([loadData('keymap'), loadData('layout')]);
  const segHtml = km.layers.map((l, i) => `<label><input type="radio" name="kmLayer" value="${esc(l.id)}"${i === 0 ? ' checked' : ''}><span><small>${l.index}</small> ${esc(l.name)}</span></label>`).join('');
  section.innerHTML = `
  <div class="page km">
    <p class="eyebrow">Sheet 6 · ZMK keymap</p>
    <h1 class="display">Keymap</h1>
    <p class="lede">${km.layers.length} layers on ${km.keys.length} keys, drawn on the real switch positions. Big legend: tap. Small legend: hold.
      The trackball opens the ${esc(km.pointer.auto_layer)} layer by itself. Read from
      <a href="${githubUrl(km.source)}" rel="noopener" target="_blank">${esc(km.source.split('/').pop())}</a> and the shield's matrix transform.</p>
    <div class="km-bar">
      <div class="seg km-seg" role="radiogroup" aria-label="Layer">${segHtml}</div>
      <p class="km-keyhint">Arrow keys switch layers.</p>
    </div>
    <div class="km-board" id="kmBoard"></div>
    <p class="km-detail" id="kmDetail" aria-live="polite"></p>
    <ul class="km-legend" aria-label="Key styles">
      <li><i class="sw sw-switch"></i>switches a layer</li>
      <li><i class="sw sw-held"></i>held to reach this layer</li>
      <li><i class="sw sw-trans"></i>transparent, shows the base key</li>
      <li><i class="sw sw-mouse"></i>mouse button</li>
    </ul>
    <div class="km-cols">
      <section aria-labelledby="kmInfoH"><h2 class="eyebrow" id="kmInfoH">This layer</h2><div id="kmInfo"></div></section>
      <section aria-labelledby="kmComboH"><h2 class="eyebrow" id="kmComboH">Combos: press together</h2><ul class="km-combos">${comboHtml()}</ul>
        <p class="note">Trackball: ${esc(km.pointer.sensor)} at <b>${km.pointer.cpi} CPI</b>. ${km.pointer.modes.map((m) => `${esc(m.layer)}: ${m.effect.map(esc).join(', ')}`).join('. ')}.</p></section>
    </div>
    <details class="km-all"><summary>All layers as a table</summary>${tableHtml()}</details>
  </div>`;
  root = section.querySelector('.km');
  board = section.querySelector('#kmBoard');
  detail = section.querySelector('#kmDetail');
  seg = section.querySelector('.km-seg');
  info = section.querySelector('#kmInfo');
  seg.addEventListener('change', (e) => select(e.target.value));
  section.querySelectorAll('.km-combo').forEach((btn) => {
    const c2 = km.combos[Number(btn.dataset.i)];
    const on = (v) => c2.positions.forEach((pos) => keyEls.get(pos)?.classList.toggle('k-lit', v));
    btn.addEventListener('pointerenter', () => on(true));
    btn.addEventListener('pointerleave', () => on(false));
    btn.addEventListener('focus', () => on(true));
    btn.addEventListener('blur', () => on(false));
  });
  new ResizeObserver(() => drawBoard()).observe(root);
  current = layerById(c.sub).id;
  drawBoard();
  select(current, false);
}

export function show(sub) {
  if (!km) return;
  const id = layerById(sub).id;
  if (id !== current) select(id, false);
}
