// SPDX-License-Identifier: MIT
// Case tab: every printed part (case, cradle, retainer) one at a time in the 3D viewer, with its
// measured facts, print notes and downloads. Data: docs/data/parts.json (docs/gen/parts.py).
// Route: #case/<file stem>, e.g. #case/lid-outer-right.

import * as THREE from 'three';
import { ModelViewer, parseSTL } from '../viewer.js';
import { loadData, fetchBuffer, assetUrl, githubUrl, downloadFile, fmt, esc } from '../assets.js';
import { t } from '../i18n.js';

const DEFAULT = 'tray-right';
const VIEWS = [['iso', t('Iso')], ['top', t('Top')], ['bottom', t('Bottom')], ['front', t('Front')]];
const css = (v, fb) => getComputedStyle(document.documentElement).getPropertyValue(v).trim() || fb;

let root, viewer, data, ctx;
let current = null;          // part id shown
let shown = null;            // THREE.Group in the viewer
let loadToken = 0;
let abort = null;
const geomCache = new Map(); // repo path -> BufferGeometry (parsed once per visit)
const state = { view: 'iso', wire: false, clip: false, axis: 'y', t: 0.5, flip: false };

const byId = (id) => data.parts.find((p) => p.id === id);
const stemOf = (p) => p.path.split('/').pop();

/** Unlit back faces: where the section plane opens a closed mesh, its inside shows as a flat
 *  filled area, like the hatched cut of a drawing. */
const cutMaterial = (color) => new THREE.MeshBasicMaterial({
  color, side: THREE.BackSide, clippingPlanes: viewer.clip.on ? [viewer.clipPlane] : [],
});

/** A closed mesh drawn twice: the outside in the part colour, the inside (only visible where the
 *  section plane opens it) in the cut colour, so a section reads like a hatched drawing. */
function partObject(geom) {
  const g = new THREE.Group();
  const outer = new THREE.Mesh(geom, viewer.material(css('--case-part', '#C9CFC4')));
  outer.material.side = THREE.FrontSide;
  const inner = new THREE.Mesh(geom, cutMaterial(css('--case-cut', '#1E5A3E')));
  inner.userData.cut = true;
  inner.visible = !state.wire;
  g.add(outer, inner);
  return g;
}

function recolour() {
  if (!shown) return;
  shown.traverse((o) => {
    if (o.isMesh) o.material.color.set(o.userData.cut ? css('--case-cut', '#1E5A3E') : css('--case-part', '#C9CFC4'));
  });
  viewer.requestRender();
}

/** viewer.fit fits the narrower field of view itself, portrait stages included. */
function frame(dir) { viewer.fit(dir); }

async function geometry(path, signal) {
  if (geomCache.has(path)) return geomCache.get(path);
  const name = path.split('/').pop();
  viewer.showStatus(t('Loading {name}', { name }), 0);
  const buf = await fetchBuffer(path, (f) => viewer.showStatus(t('Loading {name}', { name }), f), signal);
  const geom = parseSTL(buf);
  geom.computeBoundingBox();
  geomCache.set(path, geom);
  return geom;
}

async function select(id, { push = true } = {}) {
  const part = byId(id) || byId(DEFAULT);
  if (push) ctx.navigate(part.id);
  if (current === part.id && shown) return;
  current = part.id;
  renderPanel(part);
  const token = ++loadToken;
  abort?.abort();
  abort = new AbortController();
  try {
    const geom = await geometry(part.path, abort.signal);
    if (token !== loadToken) return;
    viewer.hideStatus();
    if (shown) viewer.remove(shown);
    shown = viewer.add(partObject(geom));
    if (state.wire) viewer.setWireframe(true);
    frame(state.view);
    applyClip();
    root.querySelector('.case-stage').setAttribute('aria-busy', 'false');
  } catch (e) {
    if (e.name === 'AbortError' || token !== loadToken) return;
    if (shown) { viewer.remove(shown); shown = null; }
    viewer.showError(e.message);
  }
}

// ------------------------------------------------------------------ panel
const HALVES = ['right', 'left'];
const halfOf = (p) => (HALVES.includes(p.group) ? p.group : null);

function groupList(g, hidden = false) {
  const parts = data.parts.filter((p) => p.group === g.id);
  if (!parts.length) return '';
  return `<div class="case-group" data-group="${esc(g.id)}"${hidden ? ' hidden' : ''}><h3>${esc(t(g.label))}</h3><ul class="picklist">${parts.map((p) => `
    <li><button type="button" data-part="${esc(p.id)}" aria-pressed="false">
      <span>${esc(t(p.name.replace(/, (left|right)$/, '')))}</span>
      ${p.printed ? '' : `<small>${t('display')}</small>`}
    </button></li>`).join('')}</ul></div>`;
}

/** The two halves are mirror images with the same parts, so they share one list with a switch;
 *  switching shows the same part of the other half. */
function partList() {
  const halves = data.groups.filter((g) => HALVES.includes(g.id));
  const others = data.groups.filter((g) => !HALVES.includes(g.id));
  return `<div class="case-halfswitch">${seg('case-half', halves.map((g) => [g.id, esc(t(g.label))]), 'right', t('Case half'))}</div>
    ${halves.map((g, i) => groupList(g, i > 0)).join('')}
    ${others.map((g) => groupList(g)).join('')}`;
}

function showHalf(half) {
  root.querySelectorAll('.case-group[data-group]').forEach((el) => { if (HALVES.includes(el.dataset.group)) el.hidden = el.dataset.group !== half; });
  root.querySelectorAll('input[name="case-half"]').forEach((i) => { i.checked = i.value === half; });
}

function renderPanel(p) {
  if (halfOf(p)) showHalf(halfOf(p));
  root.querySelectorAll('[data-part]').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.part === p.id)));
  const [sx, sy, sz] = p.size;
  const previews = p.previews.map((path) => {
    const pv = data.previews.find((x) => x.path === path);
    return `<li><a href="${esc(assetUrl(path))}" target="_blank" rel="noopener">
      <img src="${esc(assetUrl(path))}" alt="${esc(pv?.caption ? t(pv.caption) : '')}" loading="lazy" width="320" height="240">
      <span>${esc(pv?.caption ? t(pv.caption) : path.split('/').pop())}</span></a></li>`;
  }).join('');
  const crossLink = p.group === 'cradle' || p.group === 'retainer'
    ? `<p class="note">${t('The {link} shows the cradle with the ball, the retainer and the sensor board in place.', { link: `<a href="#trackball/${esc(p.group === 'cradle' ? p.id.replace(/^cradle-/, '') : '19mm-pocket')}">${t('Trackball sheet')}</a>` })}</p>` : '';
  const docLink = `<a href="${esc(githubUrl(p.doc))}" target="_blank" rel="noopener">${esc(p.doc)}</a>`;
  root.querySelector('.case-detail').innerHTML = `
    <h2>${t('Selected part')}</h2>
    <h3 class="case-name">${esc(t(p.name))}</h3>
    <p class="case-kind ${p.printed ? 'print' : 'show'}">${p.printed ? t('Print this part') : t('Display only, not for printing')}</p>
    <p class="case-role">${esc(t(p.role))}</p>
    <dl class="dims">
      <dt>${t('Size x · y · z')}</dt><dd>${fmt(sx, 2)} × ${fmt(sy, 2)} × ${fmt(sz, 2)} mm</dd>
    </dl>
    ${p.printed ? `<p class="untested">${t('Untested: not printed or fit-checked yet. Print the pocket test first.')}</p>` : ''}
    <p class="note">${p.printed ? t('Print settings, inserts and assembly: {link}', { link: docLink }) : t('What it shows and which plates to print: {link}', { link: docLink })}</p>
    <div class="actions">
      <button class="btn primary" type="button" data-act="download">${esc(t('Download {name}', { name: stemOf(p) }))}</button>
      <a class="btn" href="${esc(githubUrl(p.path))}" rel="noopener">${t('View on GitHub')}</a>
    </div>
    ${previews ? `<div><h2>${t('Renders')}</h2><ul class="case-previews">${previews}</ul></div>` : ''}
    ${crossLink}`;
  root.querySelector('.case-file').textContent = stemOf(p);
  root.querySelector('.case-file-kind').textContent = p.printed ? t('print') : t('display only');
  root.querySelector('.case-file-kind').className = `case-file-kind ${p.printed ? 'print' : 'show'}`;
  root.querySelector('.case-stage').setAttribute('aria-busy', 'true');
  viewer.canvas.setAttribute('aria-label', t('3D model of {name}, {x} by {y} by {z} mm. Drag to rotate, scroll to zoom.', { name: t(p.name), x: fmt(sx, 1), y: fmt(sy, 1), z: fmt(sz, 1) }));
}

// ------------------------------------------------------------------ section
function applyClip() {
  // the iso and front cameras look from -y: on the y axis keep the far side so the cut faces them
  viewer.setClip({ on: state.clip, axis: state.axis, t: state.t, flip: (state.axis === 'y') !== state.flip });
  const out = root.querySelector('.case-clip-at');
  const box = viewer.bounds();
  if (!box.isEmpty()) {
    const i = { x: 0, y: 1, z: 2 }[state.axis];
    const at = box.min.getComponent(i) + (box.max.getComponent(i) - box.min.getComponent(i)) * state.t;
    out.textContent = `${state.axis} = ${fmt(at, 1)} mm`;
  }
  root.querySelector('.case-clip-row').hidden = !state.clip;
}

function seg(name, items, value, label) {
  return `<div class="seg" role="radiogroup" aria-label="${esc(label)}">${items.map(([v, t]) => `
    <label><input type="radio" name="${name}" value="${v}"${v === value ? ' checked' : ''}><span>${t}</span></label>`).join('')}</div>`;
}

// ------------------------------------------------------------------ tab contract
export async function mount(section, c) {
  ctx = c;
  root = section;
  section.classList.add('case');
  data = await loadData('parts');
  section.innerHTML = `
  <div class="split">
    <div class="stage case-stage" aria-busy="true">
      <div class="viewer-hud">
        <div class="case-hud">
          <p class="eyebrow">STL</p>
          <p class="case-file-line"><span class="case-file"></span> <span class="case-file-kind"></span></p>
        </div>
      </div>
      <div class="viewer-tools case-tools">
        <div class="case-clip-row" hidden>
          ${seg('case-axis', [['x', 'x'], ['y', 'y'], ['z', 'z']], state.axis, t('Section plane normal'))}
          <input type="range" min="0" max="1" step="0.005" value="${state.t}" aria-label="${t('Section plane position')}" class="case-clip-t">
          <output class="case-clip-at" aria-live="polite"></output>
          <button class="btn" type="button" data-act="flip" aria-pressed="false" title="${t('Keep the other side of the plane')}">${t('Flip')}</button>
        </div>
        <div class="case-tool-row">
          ${seg('case-view', VIEWS, state.view, t('View direction'))}
          <button class="btn" type="button" data-act="wire" aria-pressed="false" title="${t('Show the triangle edges')}">${t('Wireframe')}</button>
          <button class="btn" type="button" data-act="clip" aria-pressed="false" title="${t('Cut the part open with a plane')}">${t('Section')}</button>
        </div>
      </div>
    </div>
    <aside class="panel case-panel" aria-label="${t('Case parts')}">
      <header>
        <p class="eyebrow">${t('Sheet 3 · printed parts')}</p>
        <h1 class="display">${t('Case')}</h1>
        <p class="case-lede">${t('Each half is a tray with a screwed controller box cap and a two-plate lid that covers the keys for transport and folds under the half as a tenting foot. Pick a part to turn it, cut it open and download its STL.')}</p>
      </header>
      <nav class="case-parts" aria-label="${t('Parts')}">${partList()}</nav>
      <section class="case-detail" aria-live="polite"></section>
    </aside>
  </div>`;

  viewer = new ModelViewer(section.querySelector('.case-stage'), { label: t('3D model of the selected part') });
  document.addEventListener('themechange', recolour);

  section.querySelector('.case-parts').addEventListener('click', (e) => {
    const b = e.target.closest('[data-part]');
    if (b) select(b.dataset.part);
  });
  section.querySelector('.case-parts').addEventListener('change', (e) => {
    if (e.target.name !== 'case-half') return;
    const half = e.target.value;
    const cur = byId(current);
    const twin = cur && halfOf(cur) ? cur.id.replace(/(left|right)$/, half) : null;
    if (twin && byId(twin)) select(twin);
    else showHalf(half);
  });
  section.querySelector('.case-detail').addEventListener('click', (e) => {
    const b = e.target.closest('[data-act="download"]');
    if (!b) return;
    const p = byId(current);
    b.disabled = true;
    b.textContent = t('Downloading…');
    downloadFile(p.path).finally(() => { b.disabled = false; b.textContent = t('Download {name}', { name: stemOf(p) }); });
  });
  section.querySelector('.case-tools').addEventListener('change', (e) => {
    const t = e.target;
    if (t.name === 'case-view') { state.view = t.value; frame(state.view); }
    if (t.name === 'case-axis') { state.axis = t.value; applyClip(); }
  });
  section.querySelector('.case-clip-t').addEventListener('input', (e) => { state.t = Number(e.target.value); applyClip(); });
  section.querySelector('.case-tools').addEventListener('click', (e) => {
    const b = e.target.closest('button[data-act]');
    if (!b) return;
    if (b.dataset.act === 'wire') {
      state.wire = !state.wire;
      viewer.setWireframe(state.wire);
      shown?.traverse((o) => { if (o.userData.cut) o.visible = !state.wire; });
      b.setAttribute('aria-pressed', String(state.wire));
    } else if (b.dataset.act === 'clip') {
      state.clip = !state.clip;
      b.setAttribute('aria-pressed', String(state.clip));
      applyClip();
    } else if (b.dataset.act === 'flip') {
      state.flip = !state.flip;
      b.setAttribute('aria-pressed', String(state.flip));
      applyClip();
    }
  });
  // a plain click on a view preset that is already checked re-frames the part
  section.querySelectorAll('input[name="case-view"]').forEach((i) => i.addEventListener('click', () => { if (i.value === state.view) frame(state.view); }));

  await select(byId(c.sub) ? c.sub : DEFAULT, { push: false });
}

export function show(sub) {
  viewer?.setActive(true);
  const id = byId(sub) ? sub : DEFAULT;
  if (data && id !== current) select(id, { push: false });
}

export function hide() {
  viewer?.setActive(false);
}
