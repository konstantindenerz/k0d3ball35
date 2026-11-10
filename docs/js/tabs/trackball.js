// SPDX-License-Identifier: MIT
// Trackball tab: the cradle of each variant in section, with the ball and its three bearings drawn
// from stack.json, the optional retainer and the sensor board GLB in place.
// Data: docs/data/parts.json (docs/gen/parts.py). Route: #trackball/<variant>, e.g. #trackball/25mm-pocket.
//
// Frame: the cradle STLs are in the stack frame of hardware/trackball-cradle/README.md (mm, z = 0 on
// the main PCB top, ball centre on the z axis, -y towards the keys), so the ball goes to
// (0, 0, ball_centre_z). The bearings sit 35 degrees below the equator at 60, 180 and 300 degrees
// from +x; the angle is derived from bearing_contact_z so the drawing follows the model.

import * as THREE from 'three';
import { ModelViewer, parseSTL } from '../viewer.js';
import { loadData, fetchBuffer, assetUrl, githubUrl, downloadFile, fmt, esc } from '../assets.js';

const SENSOR_GLB = 'hardware/sensor-pcb/renders/k0d3ball35-sensor.glb';
const BEARING_D = 2.0;                 // ZrO2 balls, hardware/trackball-cradle/README.md "Bearings"
const BEARING_AZ = [60, 180, 300];
const VIEWS = [['iso', 'Iso'], ['front', 'Front'], ['top', 'Top'], ['bottom', 'Bottom'], ['side', 'Side']];
const css = (v, fb) => getComputedStyle(document.documentElement).getPropertyValue(v).trim() || fb;
const signed = (v, d = 2) => (v == null ? '-' : `${v >= 0 ? '+' : '−'}${fmt(Math.abs(v), d)}`);

let root, viewer, data, ctx;
let variant = null;
const objs = { cradle: null, ball: null, retainer: null, sensor: null };
const geomCache = new Map();
let sensorState = 'idle';               // idle | loading | ok | missing | error
let sensorRoot = null;                  // the placed GLB (kept across variants, the board is the same)
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

async function stlGeometry(path) {
  if (!geomCache.has(path)) {
    const name = path.split('/').pop();
    geomCache.set(path, fetchBuffer(path, (f) => viewer.showStatus(`Loading ${name}`, f)).then((buf) => parseSTL(buf)));
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
    b.position.set((R + r) * Math.cos(phi) * Math.cos(a), (R + r) * Math.cos(phi) * Math.sin(a), s.ball_centre_z - (R + r) * Math.sin(phi));
    g.add(b);
  }
  g.userData.phiDeg = THREE.MathUtils.radToDeg(phi);
  return g;
}

/** Sensor board GLB (KiCad export) placed in the cradle frame. loadGLB turns it into KiCad's 3D
 *  frame (x right, y = -pcb y, z up from the B face). The cradle frame is the layout frame
 *  (y = pcb y, towards the user), and the board hangs component side down with its lens ("BALL
 *  SIDE", B face) against the housing face at sensor_pcb_plane_z. Together that is x -> -x,
 *  y -> -y, z -> -z about the board centre, which puts J1 at local x = -7.6 in front of the cable
 *  channel (cable_channel_x in stack.json; tests/test_sensor_pcb_vs_cradle.py checks the same). */
function placeSensor(glbRoot, planeZ) {
  // the board substrate: the thinnest mesh that spans more than 20 mm on x and y and is over 1 mm
  // thick (copper and soldermask layers span the board too, but are thicker or flat)
  glbRoot.updateMatrixWorld(true);
  let box = null;
  glbRoot.traverse((o) => {
    if (!o.isMesh) return;
    const b = new THREE.Box3().setFromObject(o);
    const sz = b.getSize(new THREE.Vector3());
    if (sz.x > 20 && sz.y > 20 && sz.z > 1 && (!box || sz.z < box.getSize(new THREE.Vector3()).z)) box = b;
  });
  if (!box) box = new THREE.Box3().setFromObject(glbRoot);
  const c = box.getCenter(new THREE.Vector3());
  const wrap = new THREE.Group();
  wrap.name = 'sensor';
  wrap.add(glbRoot);
  wrap.scale.set(-1, -1, -1);
  wrap.position.set(c.x, c.y, planeZ + box.min.z);
  return wrap;
}

async function ensureSensor(planeZ) {
  if (sensorRoot) { sensorRoot.position.z = planeZ + sensorRoot.userData.faceZ; return sensorRoot; }
  if (sensorState === 'loading' || sensorState === 'missing') return null;
  sensorState = 'loading';
  renderSensorNote();
  try {
    const glb = await viewer.loadGLB(SENSOR_GLB, { add: false, status: false });
    sensorRoot = placeSensor(glb, planeZ);
    sensorRoot.userData.faceZ = sensorRoot.position.z - planeZ;
    sensorState = 'ok';
  } catch (e) {
    sensorState = e.status === 404 ? 'missing' : 'error';
    if (sensorState === 'error') console.warn(e);
  }
  renderSensorNote();
  return sensorRoot;
}

function detach(key) {
  const o = objs[key];
  if (!o) return;
  if (key === 'sensor') {           // keep the GLB: same board for every variant
    viewer.content.remove(o);
    viewer.requestRender();
  } else {
    viewer.remove(o);
  }
  objs[key] = null;
}

function attach(key, obj) {
  detach(key);
  objs[key] = obj;
  if (obj) {
    if (key === 'sensor') {
      // materials were made when the GLB loaded: give them the current section plane
      obj.traverse((o) => { if (o.isMesh) [].concat(o.material).forEach((m) => { m.clippingPlanes = viewer.clip.on ? [viewer.clipPlane] : []; m.needsUpdate = true; }); });
    }
    viewer.add(obj);
  }
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
    viewer.hideStatus();
  } catch (e) {
    if (my === token) viewer.showError(e.message);
    return;
  }

  if (state.sensor) {
    const sr = await ensureSensor(s.sensor_pcb_plane_z);
    if (my !== token) return;
    if (sr && state.sensor && objs.sensor !== sr) attach('sensor', sr);
  } else detach('sensor');

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
  let t = 0.5;
  if (!box.isEmpty() && box.max.y > box.min.y) t = (state.at - box.min.y) / (box.max.y - box.min.y);
  // keep the +y half: the iso and front cameras look from -y, straight at the cut
  viewer.setClip({ on: state.clip, axis: 'y', t: Math.min(1, Math.max(0, t)), flip: !state.flip });
  const out = root.querySelector('.tb-clip-at');
  out.textContent = Math.abs(state.at) < 0.05 ? 'y = 0, through the ball centre' : `y = ${signed(state.at, 1)} mm`;
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
  root.querySelector('.tb-variant-role').textContent = cradle.role;
  const ret = root.querySelector('input[data-toggle="retainer"]');
  ret.disabled = !retainer;
  ret.closest('label').classList.toggle('tb-off', !retainer);

  const floorRow = v.mount === 'pocket'
    ? ['Case floor, housing stands on it', `${signed(s.floor_z)} mm`]
    : ['Lowest plastic, flange under the PCB', `${signed(s.lowest_plastic_z)} mm`];
  root.querySelector('.tb-stack').innerHTML = `
    <h2>Stack heights</h2>
    <p class="tb-hint">z = 0 is the top face of the main PCB; + is up.</p>
    ${dims([
      ['Ball diameter', `${fmt(s.ball_d, 2)} mm`],
      ['Ball top', `${signed(s.ball_top_above_pcb_top)} mm`],
      ['Ball centre', `${signed(s.ball_centre_z)} mm`],
      ['Cup rim', `${signed(s.rim_z)} mm`, 'The rim stays below the equator, so the ball lifts straight out'],
      ['Rim below the ball equator', `${fmt(s.rim_below_equator, 2)} mm`],
      ['Bearing contact', `${signed(s.bearing_contact_z)} mm`, 'Where the ball touches the three 2 mm ceramic bearings, 35° below the equator'],
      ['Ball bottom', `${signed(s.ball_bottom_z)} mm`],
      ['Ball surface to lens reference plane', `${fmt(s.lens_reference_plane_dist, 2)} mm`, 'PMW3610 datasheet: 2.4 mm, 2.2 to 2.6'],
      ['Sensor board, lens-side face', `${signed(s.sensor_pcb_plane_z)} mm`],
      floorRow,
    ])}
    <h2 class="tb-sub">Footprint</h2>
    ${dims([
      ['Cup outer diameter', `${fmt(s.cup_outer_d, 2)} mm`],
      ['Widest part above the PCB', `${fmt(s.envelope_d_above_pcb, 2)} mm`],
      ['PCB notch apothem it needs', `${fmt(s.notch_apothem, 1)} mm`],
      [v.mount === 'pocket' ? 'Housing on the case floor' : 'Flange under the PCB', `${fmt(s.footprint_x, 1)} × ${fmt(s.footprint_y, 1)} mm`],
    ])}`;

  root.querySelector('.tb-retention').innerHTML = retainer ? `
    <h2>Ball retention</h2>
    <p class="tb-text">Without the retainer the ball rests in the cup by gravity and ${r.without_retainer_trapped ? 'still cannot fall out' : 'falls out when the half is turned over'}.
    With <span class="mono">${esc(retainer.id)}.stl</span> clipped on, two claws over the ball's shoulders ${r.trapped ? 'keep it in' : 'do <b>not</b> keep it in'};
    the thumb side stays open. Checked by <span class="mono">retention.py</span> (configuration-space flood fill).</p>
    ${dims([
      ['Ball trapped with retainer', r.trapped ? 'yes' : 'no'],
      ['Looseness it still tolerates', `${fmt(r.guaranteed_margin, 2)} mm`, 'Combined print error, undersized ball and claw flex before the ball could escape'],
      ['Lift before a claw touches', `${fmt(r.ball_lift_play, 2)} mm`],
      ['Claw gap to the ball at rest', `${fmt(r.rest_gap, 2)} mm`],
      ['Open sector for the thumb', `${fmt(r.open_sector_deg, 0)}°`],
      r.boss_clearance != null && ['Arch clearance over the bearing bosses', `${fmt(r.boss_clearance, 2)} mm`],
    ])}` : '<h2>Ball retention</h2><p class="tb-text">No retainer for this variant.</p>';

  const dl = (p) => `<div class="tb-file"><span class="mono">${esc(p.path.split('/').pop())}</span>
      <span class="tb-file-meta">${fmt(p.size[0], 1)} × ${fmt(p.size[1], 1)} × ${fmt(p.size[2], 1)} mm · ${fmt(p.mass_g_solid, 1)} g solid</span>
      <span class="actions"><button class="btn primary" type="button" data-download="${esc(p.path)}">Download STL</button>
      <a class="btn" href="${esc(githubUrl(p.path))}" rel="noopener">GitHub</a>
      <a class="btn" href="#case/${esc(p.id)}">Facts</a></span></div>`;
  root.querySelector('.tb-downloads').innerHTML = `<h2>Files</h2>${dl(cradle)}${retainer ? dl(retainer) : ''}
    <p class="note">${esc(cradle.print_notes)}${retainer ? ` Retainer: ${esc(retainer.print_notes)}` : ''}</p>`;

  const previews = v.previews.map((path) => {
    const pv = data.previews.find((x) => x.path === path);
    return `<li><a href="${esc(assetUrl(path))}" target="_blank" rel="noopener"><img src="${esc(assetUrl(path))}" alt="${esc(pv?.caption || '')}" loading="lazy" width="1200" height="900"><span>${esc(pv?.caption || '')}</span></a></li>`;
  }).join('');
  root.querySelector('.tb-previews').innerHTML = previews ? `<h2>OpenSCAD renders</h2><ul>${previews}</ul>` : '';
  root.querySelector('.tb-previews').hidden = !previews;
}

function renderSensorNote() {
  const n = root.querySelector('.tb-sensor-note');
  const t = {
    idle: '', ok: '',
    loading: 'Loading the sensor board model…',
    missing: 'The sensor board model (k0d3ball35-sensor.glb) is not in this branch yet; it appears once the board export is merged.',
    error: 'The sensor board model did not load. Reload the page to try again.',
  }[sensorState];
  n.textContent = t;
  n.hidden = !t;
  const box = root.querySelector('input[data-toggle="sensor"]');
  box.disabled = sensorState === 'missing';
  box.closest('label').classList.toggle('tb-off', sensorState === 'missing');
}

function updateHud() {
  const v = variantById(variant);
  const files = [part(v.cradle).path.split('/').pop()];
  if (objs.retainer) files.push(part(v.retainer).path.split('/').pop());
  if (objs.sensor) files.push('k0d3ball35-sensor.glb');
  root.querySelector('.tb-files').textContent = files.join(' + ');
  const shown = ['cradle', objs.ball && 'ball with its three bearings', objs.retainer && 'retainer', objs.sensor && 'sensor board'].filter(Boolean);
  viewer.canvas.setAttribute('aria-label', `3D model, ${v.label} variant: ${shown.join(', ')}${state.clip ? ', cut through the ball centre' : ''}. Drag to rotate, scroll to zoom.`);
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
  return `<div class="seg" role="radiogroup" aria-label="${esc(label)}">${items.map(([v, t]) => `
    <label><input type="radio" name="${name}" value="${v}"${v === value ? ' checked' : ''}><span>${esc(t)}</span></label>`).join('')}</div>`;
}

// ------------------------------------------------------------------ tab contract
export async function mount(section, c) {
  ctx = c;
  root = section;
  section.classList.add('trackball');
  data = await loadData('parts');
  const variants = data.trackball.variants.map((v) => [v.id, v.label]);
  section.innerHTML = `
  <div class="split">
    <div class="stage tb-stage" aria-busy="true">
      <div class="viewer-hud">
        <div class="tb-hud">
          <p class="eyebrow">Loaded</p>
          <p class="tb-files"></p>
        </div>
      </div>
      <div class="viewer-tools tb-tools">
        <div class="tb-clip-row">
          <input type="range" min="-20" max="20" step="0.1" value="0" class="tb-clip-y" aria-label="Section plane position along y, in mm from the ball centre">
          <output class="tb-clip-at" aria-live="polite"></output>
          <button class="btn" type="button" data-act="centre" title="Put the plane back through the ball centre">Centre</button>
          <button class="btn" type="button" data-act="flip" aria-pressed="false" title="Keep the other half">Flip</button>
        </div>
        <div class="tb-tool-row">
          ${seg('tb-view', VIEWS, state.view, 'View direction')}
          <button class="btn" type="button" data-act="clip" aria-pressed="true" title="Cut the module open on the plane through the ball centre">Section</button>
        </div>
      </div>
    </div>
    <aside class="panel tb-panel" aria-label="Trackball module">
      <header>
        <p class="eyebrow">Sheet 4 · trackball module</p>
        <h1 class="display">Trackball</h1>
        <p class="tb-lede">A printed cup on three ceramic bearings with the PMW3610 sensor board straight underneath,
        standing on the case floor beside the right PCB. The view is cut through the ball centre; the ball and the
        bearings are drawn from the stack numbers, the rest are the real files.</p>
      </header>
      <section>
        <h2 id="tb-variant-h">Variant</h2>
        ${seg('tb-variant', variants, data.trackball.default, 'Cradle variant').replace('class="seg"', 'class="seg tb-variants"')}
        <p class="tb-variant-role tb-text"></p>
      </section>
      <section>
        <h2>Show</h2>
        <div class="toggles">
          <label><input type="checkbox" data-toggle="ball" checked> Ball and its three bearings</label>
          <label><input type="checkbox" data-toggle="retainer"> Retainer (optional clip-on ring)</label>
          <label><input type="checkbox" data-toggle="sensor" checked> Sensor board under the cup</label>
        </div>
        <p class="tb-sensor-note tb-hint" hidden></p>
      </section>
      <section class="tb-stack"></section>
      <section class="tb-retention"></section>
      <section class="tb-downloads"></section>
      <section class="tb-previews" hidden></section>
    </aside>
  </div>`;

  viewer = new ModelViewer(section.querySelector('.tb-stage'), { label: '3D model of the trackball cradle' });
  document.addEventListener('themechange', recolour);

  section.querySelector('.tb-panel').addEventListener('change', (e) => {
    const t = e.target;
    if (t.name === 'tb-variant') setVariant(t.value);
    if (t.dataset.toggle) { state[t.dataset.toggle] = t.checked; sync(); }
  });
  section.querySelector('.tb-panel').addEventListener('click', (e) => {
    const b = e.target.closest('[data-download]');
    if (!b) return;
    const label = b.textContent;
    b.disabled = true;
    b.textContent = 'Downloading…';
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
