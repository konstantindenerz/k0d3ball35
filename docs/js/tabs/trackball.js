// SPDX-License-Identifier: MIT
// Trackball tab: the cradle of each variant in section, with the ball and its three bearings drawn
// from stack.json and the optional retainer.
// Data: docs/data/parts.json (docs/gen/parts.py). Route: #trackball/<variant>, e.g. #trackball/25mm-pocket.
//
// Frame: the cradle STLs are in the print frame (mm, z = 0 on the main PCB top, ball centre on the
// z axis, x outward, +y away from the user, i.e. towards the keys), so the ball goes to
// (0, 0, ball_centre_z). The bearings sit 35 degrees below the equator at 60, 180 and 300 degrees
// from +x; the angle is derived from bearing_contact_z so the drawing follows the model.

import * as THREE from 'three';
import { ModelViewer, parseSTL } from '../viewer.js';
import { loadData, fetchBuffer, assetUrl, githubUrl, downloadFile, fmt, esc } from '../assets.js';
import { t } from '../i18n.js';

const BEARING_D = 2.0;                 // ZrO2 balls, hardware/trackball-cradle/README.md "Bearings"
const BEARING_AZ = [60, 180, 300];
const views = () => [['iso', t('Iso')], ['front', t('Front')], ['top', t('Top')], ['bottom', t('Bottom')], ['side', t('Side')]];
const css = (v, fb) => getComputedStyle(document.documentElement).getPropertyValue(v).trim() || fb;
const signed = (v, d = 2) => (v == null ? '-' : `${v >= 0 ? '+' : '−'}${fmt(Math.abs(v), d)}`);

let root, viewer, data, ctx;
let variant = null;
const objs = { cradle: null, ball: null, retainer: null, sensor: null };
const geomCache = new Map();
let token = 0;
const state = { view: 'iso', ball: true, retainer: false, sensor: true, clip: true, at: 0, flip: false };

const variantById = (id) => data.trackball.variants.find((v) => v.id === id);
const part = (id) => data.parts.find((p) => p.id === id);

// ------------------------------------------------------------------ scene objects
/** Unlit back faces: where the section plane opens a closed mesh, its inside shows as a flat
 *  filled area, like the hatched cut of a drawing. */
const cutMaterial = (color) => new THREE.MeshBasicMaterial({
  color, side: THREE.BackSide, clippingPlanes: viewer.clip.on ? [viewer.clipPlane] : [],
});

function solid(geom, colourVar, fallback, cutVar = '--tb-cut', cutFallback = '#1E5A3E') {
  const g = new THREE.Group();
  const outer = new THREE.Mesh(geom, viewer.material(css(colourVar, fallback)));
  outer.material.side = THREE.FrontSide;
  outer.userData.colour = [colourVar, fallback];
  const inner = new THREE.Mesh(geom, cutMaterial(css(cutVar, cutFallback)));
  inner.userData.colour = [cutVar, cutFallback];
  g.add(outer, inner);
  return g;
}

/** viewer.fit fits the narrower field of view itself, portrait stages included. */
function frame(dir) { viewer.fit(dir); }

async function stlGeometry(path) {
  if (!geomCache.has(path)) {
    const name = path.split('/').pop();
    geomCache.set(path, fetchBuffer(path, (f) => viewer.showStatus(t('Loading {name}', { name }), f)).then((buf) => parseSTL(buf)));
  }
  try {
    return await geomCache.get(path);
  } catch (e) {
    geomCache.delete(path);
    throw e;
  }
}

function ballObject(s) {
  const R = s.ball_d / 2;
  const g = new THREE.Group();
  g.name = 'ball';
  const ball = solid(new THREE.SphereGeometry(R, 96, 64), '--tb-ball', '#B8862B', '--tb-ball-cut', '#8A6418');
  ball.position.set(0, 0, s.ball_centre_z);
  g.add(ball);
  // bearing centres: on the line from the ball centre through the contact point, one bearing radius further out
  const phi = Math.asin((s.ball_centre_z - s.bearing_contact_z) / R);
  const r = BEARING_D / 2;
  const bgeom = new THREE.SphereGeometry(r, 32, 24);
  for (const az of BEARING_AZ) {
    const a = THREE.MathUtils.degToRad(az);
    const b = solid(bgeom, '--tb-bearing', '#EEECE4', '--tb-bearing', '#EEECE4');
    // bearing_az is measured in the layout frame (y towards the user); the STLs are in the print
    // frame (y away from the user), hence -sin
    b.position.set((R + r) * Math.cos(phi) * Math.cos(a), -(R + r) * Math.cos(phi) * Math.sin(a), s.ball_centre_z - (R + r) * Math.sin(phi));
    g.add(b);
  }
  g.userData.phiDeg = THREE.MathUtils.radToDeg(phi);
  return g;
}

function detach(key) {
  const o = objs[key];
  if (!o) return;
  viewer.remove(o);
  objs[key] = null;
}

function attach(key, obj) {
  detach(key);
  objs[key] = obj;
  if (obj) viewer.add(obj);
}

async function sync({ refit = false } = {}) {
  const v = variantById(variant);
  const s = v.stack;
  const my = ++token;
  try {
    const cg = await stlGeometry(part(v.cradle).path);
    if (my !== token) return;
    if (!objs.cradle || objs.cradle.userData.variant !== v.id) {
      const o = solid(cg, '--tb-cradle', '#C9CFC4');
      o.userData.variant = v.id;
      attach('cradle', o);
    }
    if (state.ball && (!objs.ball || objs.ball.userData.variant !== v.id)) {
      const b = ballObject(s);
      b.userData.variant = v.id;
      attach('ball', b);
    } else if (!state.ball) detach('ball');

    if (state.retainer && v.retainer) {
      const rp = part(v.retainer).path;
      const rg = await stlGeometry(rp);
      if (my !== token) return;
      if (!objs.retainer || objs.retainer.userData.path !== rp) {
        const o = solid(rg, '--tb-retainer', '#7E8C83');
        o.userData.path = rp;
        attach('retainer', o);
      }
    } else detach('retainer');
    // the bought module's envelope in the sleeve, same frame as the cradle
    if (state.sensor && v.sensor) {
      const sg = await stlGeometry(v.sensor);
      if (my !== token) return;
      if (!objs.sensor || objs.sensor.userData.path !== v.sensor) {
        const o = solid(sg, '--tb-sensor', '#3C6E4A', '--tb-sensor-cut', '#2B5136');
        o.userData.path = v.sensor;
        attach('sensor', o);
      }
    } else detach('sensor');
    viewer.hideStatus();
  } catch (e) {
    if (my === token) viewer.showError(e.message);
    return;
  }

  if (refit) frame(state.view);
  applyClip();
  updateHud();
}

function recolour() {
  viewer.content.traverse((o) => { if (o.isMesh && o.userData.colour) o.material.color.set(css(...o.userData.colour)); });
  viewer.requestRender();
}

// ------------------------------------------------------------------ section through the ball centre
function applyClip() {
  // the viewer takes the plane as a fraction across the content bounds; the content changes with
  // the toggles, so the fraction is recomputed from the plane position in mm every time
  const box = viewer.bounds();
  let frac = 0.5;
  if (!box.isEmpty() && box.max.y > box.min.y) frac = (state.at - box.min.y) / (box.max.y - box.min.y);
  // keep the +y half: the iso and front cameras look from -y, straight at the cut
  viewer.setClip({ on: state.clip, axis: 'y', t: Math.min(1, Math.max(0, frac)), flip: !state.flip });
  const out = root.querySelector('.tb-clip-at');
  out.textContent = Math.abs(state.at) < 0.05 ? t('y = 0, through the ball centre') : `y = ${signed(state.at, 1)} mm`;
  root.querySelector('.tb-clip-row').hidden = !state.clip;
}

// ------------------------------------------------------------------ panel
function dims(rows) {
  return `<dl class="dims">${rows.filter(Boolean).map(([k, v, title]) => `<dt${title ? ` title="${esc(title)}"` : ''}>${esc(k)}</dt><dd>${v}</dd>`).join('')}</dl>`;
}

function renderPanel() {
  const v = variantById(variant);
  const s = v.stack;
  const r = v.retention;
  const cradle = part(v.cradle);
  const retainer = v.retainer ? part(v.retainer) : null;
  root.querySelectorAll('input[name="tb-variant"]').forEach((i) => { i.checked = i.value === v.id; });
  root.querySelector('.tb-variant-role').textContent = t(cradle.role);
  const ret = root.querySelector('input[data-toggle="retainer"]');
  ret.disabled = !retainer;
  ret.closest('label').classList.toggle('tb-off', !retainer);

  const floorRow = v.mount === 'pocket'
    ? [t('Case floor, housing stands on it'), `${signed(s.floor_z)} mm`]
    : [t('Lowest plastic, flange under the PCB'), `${signed(s.lowest_plastic_z)} mm`];
  root.querySelector('.tb-stack').innerHTML = `
    <h2>${t('Stack heights')}</h2>
    <p class="tb-hint">${t('z = 0 is the top face of the main PCB; + is up.')}</p>
    ${dims([
      [t('Ball diameter'), `${fmt(s.ball_d, 2)} mm`],
      [t('Ball top'), `${signed(s.ball_top_above_pcb_top)} mm`],
      [t('Ball centre'), `${signed(s.ball_centre_z)} mm`],
      [t('Cup rim'), `${signed(s.rim_z)} mm`, t('The rim stays below the equator, so the ball lifts straight out')],
      [t('Rim below the ball equator'), `${fmt(s.rim_below_equator, 2)} mm`],
      [t('Bearing contact'), `${signed(s.bearing_contact_z)} mm`, t('Where the ball touches the three 2 mm ceramic bearings, 35° below the equator')],
      [t('Ball bottom'), `${signed(s.ball_bottom_z)} mm`],
      [t('Ball surface to lens reference plane'), `${fmt(s.lens_reference_plane_dist, 2)} mm`, t('Nominal, not yet measured on the PAW3222 module')],
      [t('Sensor board, lens-side face'), `${signed(s.sensor_pcb_plane_z)} mm`],
      floorRow,
    ])}
    <h2 class="tb-sub">${t('Footprint')}</h2>
    ${dims([
      [t('Cup outer diameter'), `${fmt(s.cup_outer_d, 2)} mm`],
      [t('Widest part above the PCB'), `${fmt(s.envelope_d_above_pcb, 2)} mm`],
      [t('PCB notch apothem it needs'), `${fmt(s.notch_apothem, 1)} mm`],
      [v.mount === 'pocket' ? t('Housing on the case floor') : t('Flange under the PCB'), `${fmt(s.footprint_x, 1)} × ${fmt(s.footprint_y, 1)} mm`],
    ])}`;

  root.querySelector('.tb-retention').innerHTML = retainer ? `
    <h2>${t('Ball retention')}</h2>
    ${dims([
      [t('Without the retainer'), r.without_clip_trapped ? t('ball stays in') : t('ball falls out upside down')],
      [t('With the retainer clipped on'), r.trapped ? t('ball stays in') : t('ball falls out')],
      [t('Print error it tolerates'), `${fmt(r.guaranteed_margin, 2)} mm`],
    ])}` : `<h2>${t('Ball retention')}</h2><p class="tb-text">${t('No retainer for this variant.')}</p>`;

  const dl = (p) => `<div class="tb-file"><span class="mono">${esc(p.path.split('/').pop())}</span>
      <span class="tb-file-meta">${fmt(p.size[0], 1)} × ${fmt(p.size[1], 1)} × ${fmt(p.size[2], 1)} mm</span>
      <span class="actions"><button class="btn primary" type="button" data-download="${esc(p.path)}">${t('Download STL')}</button>
      <a class="btn" href="${esc(githubUrl(p.path))}" rel="noopener">GitHub</a>
      <a class="btn" href="#case/${esc(p.id)}">${t('On its own')}</a></span></div>`;
  root.querySelector('.tb-downloads').innerHTML = `<h2>${t('Files')}</h2>${dl(cradle)}${retainer ? dl(retainer) : ''}
    <p class="untested">${t('Untested: not printed, no ball has run in it yet.')}</p>
    <p class="note">${t('Print settings and fitting the bearings: {link}', { link: `<a href="${esc(githubUrl(cradle.doc))}" target="_blank" rel="noopener">${esc(cradle.doc)}</a>` })}</p>`;

  const previews = v.previews.map((path) => {
    const pv = data.previews.find((x) => x.path === path);
    const cap = pv?.caption ? t(pv.caption) : '';
    return `<li><a href="${esc(assetUrl(path))}" target="_blank" rel="noopener"><img src="${esc(assetUrl(path))}" alt="${esc(cap)}" loading="lazy" width="1200" height="900"><span>${esc(cap)}</span></a></li>`;
  }).join('');
  root.querySelector('.tb-previews').innerHTML = previews ? `<h2>${t('OpenSCAD renders')}</h2><ul>${previews}</ul>` : '';
  root.querySelector('.tb-previews').hidden = !previews;
}

function updateHud() {
  const v = variantById(variant);
  const files = [part(v.cradle).path.split('/').pop()];
  if (objs.retainer) files.push(part(v.retainer).path.split('/').pop());
  root.querySelector('.tb-files').textContent = files.join(' + ');
  const shown = [t('cradle'), objs.ball && t('ball with its three bearings'), objs.retainer && t('retainer')].filter(Boolean);
  const aria = { variant: t(v.label), parts: shown.join(', ') };
  viewer.canvas.setAttribute('aria-label', state.clip
    ? t('3D model, {variant} variant: {parts}, cut through the ball centre. Drag to rotate, scroll to zoom.', aria)
    : t('3D model, {variant} variant: {parts}. Drag to rotate, scroll to zoom.', aria));
}

function setVariant(id, { push = true } = {}) {
  const v = variantById(id) || variantById(data.trackball.default);
  if (push) ctx.navigate(v.id);
  if (v.id === variant) return;
  const first = variant == null;
  variant = v.id;
  renderPanel();
  sync({ refit: true }).then(() => { if (first) root.querySelector('.tb-stage').setAttribute('aria-busy', 'false'); });
}

function seg(name, items, value, label) {
  return `<div class="seg" role="radiogroup" aria-label="${esc(label)}">${items.map(([v, lbl]) => `
    <label><input type="radio" name="${name}" value="${v}"${v === value ? ' checked' : ''}><span>${esc(lbl)}</span></label>`).join('')}</div>`;
}

// ------------------------------------------------------------------ tab contract
export async function mount(section, c) {
  ctx = c;
  root = section;
  section.classList.add('trackball');
  data = await loadData('parts');
  const variants = data.trackball.variants.map((v) => [v.id, t(v.label)]);
  section.innerHTML = `
  <div class="split">
    <div class="stage tb-stage" aria-busy="true">
      <div class="viewer-hud">
        <div class="tb-hud">
          <p class="eyebrow">${t('Loaded')}</p>
          <p class="tb-files"></p>
        </div>
      </div>
      <div class="viewer-tools tb-tools">
        <div class="tb-clip-row">
          <input type="range" min="-20" max="20" step="0.1" value="0" class="tb-clip-y" aria-label="${t('Section plane position along y, in mm from the ball centre')}">
          <output class="tb-clip-at" aria-live="polite"></output>
          <button class="btn" type="button" data-act="centre" title="${t('Put the plane back through the ball centre')}">${t('Centre')}</button>
          <button class="btn" type="button" data-act="flip" aria-pressed="false" title="${t('Keep the other half')}">${t('Flip')}</button>
        </div>
        <div class="tb-tool-row">
          ${seg('tb-view', views(), state.view, t('View direction'))}
          <button class="btn" type="button" data-act="clip" aria-pressed="true" title="${t('Cut the module open on the plane through the ball centre')}">${t('Section')}</button>
        </div>
      </div>
    </div>
    <aside class="panel tb-panel" aria-label="${t('Trackball module')}">
      <header>
        <p class="eyebrow">${t('Sheet 4 · trackball module')}</p>
        <h1 class="display">${t('Trackball')}</h1>
        <p class="tb-lede">${t('A printed cup on three ceramic bearings for the 19.05 mm ball, with a bought PAW3222 sensor module tilted beside it, on the case floor beside the right PCB. The view is cut through the ball centre; ball and bearings are drawn from the stack numbers, the rest are the real files.')}</p>
      </header>
      <section>
        <h2 id="tb-variant-h">${t('Variant')}</h2>
        ${seg('tb-variant', variants, data.trackball.default, t('Cradle variant')).replace('class="seg"', 'class="seg tb-variants"')}
        <p class="tb-variant-role tb-text"></p>
      </section>
      <section>
        <h2>${t('Show')}</h2>
        <div class="toggles">
          <label><input type="checkbox" data-toggle="ball" checked> ${t('Ball and its three bearings')}</label>
          <label><input type="checkbox" data-toggle="retainer"> ${t('Retainer (optional clip-on ring)')}</label>
          <label><input type="checkbox" data-toggle="sensor" checked> ${t('Sensor module (envelope)')}</label>
        </div>
      </section>
      <section class="tb-stack"></section>
      <section class="tb-retention"></section>
      <section class="tb-downloads"></section>
      <section class="tb-previews" hidden></section>
    </aside>
  </div>`;

  viewer = new ModelViewer(section.querySelector('.tb-stage'), { label: t('3D model of the trackball cradle') });
  document.addEventListener('themechange', recolour);

  section.querySelector('.tb-panel').addEventListener('change', (e) => {
    const tg = e.target;
    if (tg.name === 'tb-variant') setVariant(tg.value);
    if (tg.dataset.toggle) { state[tg.dataset.toggle] = tg.checked; sync(); }
  });
  section.querySelector('.tb-panel').addEventListener('click', (e) => {
    const b = e.target.closest('[data-download]');
    if (!b) return;
    const label = b.textContent;
    b.disabled = true;
    b.textContent = t('Downloading…');
    downloadFile(b.dataset.download).finally(() => { b.disabled = false; b.textContent = label; });
  });
  section.querySelector('.tb-tools').addEventListener('change', (e) => {
    if (e.target.name === 'tb-view') { state.view = e.target.value; frame(state.view); }
  });
  section.querySelectorAll('input[name="tb-view"]').forEach((i) => i.addEventListener('click', () => { if (i.value === state.view) frame(state.view); }));
  const slider = section.querySelector('.tb-clip-y');
  slider.addEventListener('input', () => { state.at = Number(slider.value); applyClip(); });
  section.querySelector('.tb-tools').addEventListener('click', (e) => {
    const b = e.target.closest('button[data-act]');
    if (!b) return;
    if (b.dataset.act === 'clip') { state.clip = !state.clip; b.setAttribute('aria-pressed', String(state.clip)); }
    if (b.dataset.act === 'flip') { state.flip = !state.flip; b.setAttribute('aria-pressed', String(state.flip)); }
    if (b.dataset.act === 'centre') { state.at = 0; slider.value = '0'; }
    applyClip();
    updateHud();
  });

  setVariant(variantById(c.sub) ? c.sub : data.trackball.default, { push: false });
}

export function show(sub) {
  viewer?.setActive(true);
  if (!data) return;
  const id = variantById(sub) ? sub : data.trackball.default;
  if (id !== variant) setVariant(id, { push: false });
}

export function hide() {
  viewer?.setActive(false);
}
