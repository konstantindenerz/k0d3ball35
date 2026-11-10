// SPDX-License-Identifier: MIT
// Case tab: every printed part (case, cradle, retainer) one at a time in the 3D viewer, with its
// measured facts, print notes and downloads. Data: docs/data/parts.json (docs/gen/parts.py).
// Route: #case/<file stem>, e.g. #case/lid-outer-right.

import * as THREE from 'three';
import { ModelViewer, parseSTL } from '../viewer.js';
import { loadData, fetchBuffer, assetUrl, githubUrl, downloadFile, fmt, esc } from '../assets.js';

const DEFAULT = 'tray-right';
const VIEWS = [['iso', 'Iso'], ['top', 'Top'], ['bottom', 'Bottom'], ['front', 'Front']];
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

/** viewer.fit frames the bounding sphere in the vertical field of view; on a stage narrower than
 *  it is tall the sides would be cut, so the camera backs off by the aspect ratio. */
function frame(dir) {
  viewer.fit(dir);
  const a = viewer.camera.aspect;
  if (a < 1) {
    const t = viewer.controls.target;
    viewer.camera.position.sub(t).multiplyScalar(1 / a).add(t);
    viewer.camera.far /= a;
    viewer.camera.updateProjectionMatrix();
    viewer.controls.update();
    viewer.requestRender();
  }
}

async function geometry(path, signal) {
  if (geomCache.has(path)) return geomCache.get(path);
  const name = path.split('/').pop();
  viewer.showStatus(`Loading ${name}`, 0);
  const buf = await fetchBuffer(path, (f) => viewer.showStatus(`Loading ${name}`, f), signal);
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
  return `<div class="case-group" data-group="${esc(g.id)}"${hidden ? ' hidden' : ''}><h3>${esc(g.label)}</h3><ul class="picklist">${parts.map((p) => `
    <li><button type="button" data-part="${esc(p.id)}" aria-pressed="false">
      <span>${esc(p.name.replace(/, (left|right)$/, ''))}</span>
      <small>${p.printed ? fmt(p.mass_g_solid, p.mass_g_solid < 10 ? 1 : 0) + ' g' : 'display'}</small>
    </button></li>`).join('')}</ul></div>`;
}

/** The two halves are mirror images with the same parts, so they share one list with a switch;
 *  switching shows the same part of the other half. */
function partList() {
  const halves = data.groups.filter((g) => HALVES.includes(g.id));
  const others = data.groups.filter((g) => !HALVES.includes(g.id));
  return `<div class="case-halfswitch">${seg('case-half', halves.map((g) => [g.id, g.label]), 'right', 'Case half')}</div>
    ${halves.map((g, i) => groupList(g, i > 0)).join('')}
    ${others.map((g) => groupList(g)).join('')}`;
}

function showHalf(half) {
  root.querySelectorAll('.case-group[data-group]').forEach((el) => { if (HALVES.includes(el.dataset.group)) el.hidden = el.dataset.group !== half; });
  root.querySelectorAll('input[name="case-half"]').forEach((i) => { i.checked = i.value === half; });
}

function meshFact(p) {
  if (p.watertight) return 'closed';
  if (p.non_manifold_edges) return `closed, ${p.non_manifold_edges} edge${p.non_manifold_edges > 1 ? 's' : ''} shared by 4 faces`;
  return 'open';
}

function renderPanel(p) {
  if (halfOf(p)) showHalf(halfOf(p));
  root.querySelectorAll('[data-part]').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.part === p.id)));
  const [sx, sy, sz] = p.size;
  const previews = p.previews.map((path) => {
    const pv = data.previews.find((x) => x.path === path);
    return `<li><a href="${esc(assetUrl(path))}" target="_blank" rel="noopener">
      <img src="${esc(assetUrl(path))}" alt="${esc(pv?.caption || '')}" loading="lazy" width="320" height="240">
      <span>${esc(pv?.caption || path.split('/').pop())}</span></a></li>`;
  }).join('');
  const crossLink = p.group === 'cradle' || p.group === 'retainer'
    ? `<p class="note">The <a href="#trackball/${esc(p.group === 'cradle' ? p.id.replace(/^cradle-/, '') : p.id.replace(/^retainer-(\d+mm)$/, '$1-pocket'))}">Trackball sheet</a> shows the cradle with the ball, the retainer and the sensor board in place.</p>` : '';
  root.querySelector('.case-detail').innerHTML = `
    <h2>Selected part</h2>
    <h3 class="case-name">${esc(p.name)}</h3>
    <p class="case-kind ${p.printed ? 'print' : 'show'}">${p.printed ? 'Print this part' : 'Display only, not for printing'}</p>
    <p class="case-role">${esc(p.role)}</p>
    <dl class="dims">
      <dt>Size x · y · z</dt><dd>${fmt(sx, 2)} × ${fmt(sy, 2)} × ${fmt(sz, 2)} mm</dd>
      <dt>Lowest · highest z</dt><dd>${fmt(p.bbox_min[2], 2)} · ${fmt(p.bbox_max[2], 2)} mm</dd>
      <dt>Volume</dt><dd>${fmt(p.volume_cm3, 2)} cm³</dd>
      <dt title="${esc(data.mass_note)}">Mass, solid PLA (upper bound)</dt><dd>${fmt(p.mass_g_solid, 1)} g</dd>
      <dt>Triangles</dt><dd>${p.triangles.toLocaleString('en-US')}</dd>
      <dt>Mesh</dt><dd>${esc(meshFact(p))}</dd>
    </dl>
    <p class="note"><b>Printing.</b> ${esc(p.print_notes)}</p>
    <div class="actions">
      <button class="btn primary" type="button" data-act="download">Download ${esc(stemOf(p))}</button>
      <a class="btn" href="${esc(githubUrl(p.path))}" rel="noopener">View on GitHub</a>
    </div>
    ${previews ? `<div><h2>Renders</h2><ul class="case-previews">${previews}</ul></div>` : ''}
    ${crossLink}`;
  root.querySelector('.case-file').textContent = stemOf(p);
  root.querySelector('.case-file-kind').textContent = p.printed ? 'print' : 'display only';
  root.querySelector('.case-file-kind').className = `case-file-kind ${p.printed ? 'print' : 'show'}`;
  root.querySelector('.case-stage').setAttribute('aria-busy', 'true');
  viewer.canvas.setAttribute('aria-label', `3D model of ${p.name}, ${fmt(sx, 1)} by ${fmt(sy, 1)} by ${fmt(sz, 1)} mm. Drag to rotate, scroll to zoom.`);
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
          ${seg('case-axis', [['x', 'x'], ['y', 'y'], ['z', 'z']], state.axis, 'Section plane normal')}
          <input type="range" min="0" max="1" step="0.005" value="${state.t}" aria-label="Section plane position" class="case-clip-t">
          <output class="case-clip-at" aria-live="polite"></output>
          <button class="btn" type="button" data-act="flip" aria-pressed="false" title="Keep the other side of the plane">Flip</button>
        </div>
        <div class="case-tool-row">
          ${seg('case-view', VIEWS, state.view, 'View direction')}
          <button class="btn" type="button" data-act="wire" aria-pressed="false" title="Show the triangle edges">Wireframe</button>
          <button class="btn" type="button" data-act="clip" aria-pressed="false" title="Cut the part open with a plane">Section</button>
        </div>
      </div>
    </div>
    <aside class="panel case-panel" aria-label="Case parts">
      <header>
        <p class="eyebrow">Sheet 3 · printed parts</p>
        <h1 class="display">Case</h1>
        <p class="case-lede">Each half is a tray with a screwed controller box cap and a two-plate lid that covers
        the keys for transport and folds under the half as a tenting foot. Pick a part to turn it, cut it open
        and download its STL. Sizes are measured from the files.</p>
      </header>
      <nav class="case-parts" aria-label="Parts">${partList()}</nav>
      <section class="case-detail" aria-live="polite"></section>
    </aside>
  </div>`;

  viewer = new ModelViewer(section.querySelector('.case-stage'), { label: '3D model of the selected part' });
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
    b.textContent = 'Downloading…';
    downloadFile(p.path).finally(() => { b.disabled = false; b.textContent = `Download ${stemOf(p)}`; });
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
