// SPDX-License-Identifier: MIT
// Explorer tab: exploded view of one half, layer by layer, at true heights.
//
// World frame here is three.js Y up (unlike viewer.js, which keeps the CAD frame): world X = layout x,
// world Y = height above the PCB top, world Z = layout y. The procedural parts are drawn from
// data/layout.json; the printed case parts (tray, controller box cap, lid, folded lid) are the real
// STLs from hardware/case, fetched per half on first use and turned into this frame here.
// The left half is drawn mirrored (root.scale.x = -1), matching the mirrored left board files.
// Sub routes: #explorer/right, #explorer/left.

import * as THREE from 'three';
import { fetchBuffer, loadData } from '../assets.js';
import { parseSTL, transformGeometry } from '../viewer.js';

const css = (v) => getComputedStyle(document.documentElement).getPropertyValue(v).trim();
const col = (hex) => new THREE.Color(hex);
const reducedMq = matchMedia('(prefers-reduced-motion: reduce)');
const reduced = () => reducedMq.matches;
const HALVES = ['right', 'left'];
const CASE_KEYS = ['tray', 'cap', 'lid', 'lid_folded'];

// ---------- geometry helpers ----------
function outlineShape(points, holes = []) {
  const s = new THREE.Shape();
  points.forEach(([x, y], i) => (i ? s.lineTo(x, y) : s.moveTo(x, y)));
  s.closePath();
  for (const h of holes) {
    const p = new THREE.Path();
    if (h.points) { h.points.forEach(([x, y], i) => (i ? p.lineTo(x, y) : p.moveTo(x, y))); p.closePath(); }
    else p.absarc(h.x, h.y, h.r, 0, Math.PI * 2, true);
    s.holes.push(p);
  }
  return s;
}
// Extrude a layout-plane shape down by depth, starting at height top (layout y -> world Z, height -> world Y)
function slab(shape, depth, top, mat) {
  const g = new THREE.ExtrudeGeometry(shape, { depth, bevelEnabled: false });
  const m = new THREE.Mesh(g, mat);
  m.rotation.x = Math.PI / 2;
  m.position.y = top;
  return m;
}
function box(w, h, d, mat, x, y, z, rotDeg = 0) {   // w along X, h along Y (height), d along Z
  const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat);
  m.position.set(x, y, z);
  m.rotation.y = THREE.MathUtils.degToRad(rotDeg);
  return m;
}
function cyl(r, h, mat, x, y, z, rt = r, open = false) {
  const m = new THREE.Mesh(new THREE.CylinderGeometry(rt, r, h, 64, 1, open), mat);
  m.position.set(x, y, z);
  return m;
}
// local key offset (lx, ly) rotated by the KiCad rotation (positive = counter-clockwise on screen)
function keyLocal(k, lx, ly) {
  const t = THREE.MathUtils.degToRad(k.rot);
  return { x: k.x + lx * Math.cos(t) + ly * Math.sin(t), z: k.y - lx * Math.sin(t) + ly * Math.cos(t) };
}

// Case STL (CAD frame, Z up) -> this page's frame: swap Y and Z; the left STLs are physically
// mirrored boards, so they are mirrored back first (the whole left half is mirrored for display).
// transformGeometry restores the outward winding the reflections reverse.
const SWAP = new THREE.Matrix4().set(1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1);
const UNMIRROR = new THREE.Matrix4().makeScale(-1, 1, 1);
const caseMatrix = (half) => (half === 'left' ? SWAP.clone().multiply(UNMIRROR) : SWAP.clone());

// ---------- materials ----------
const M = {
  tray: new THREE.MeshStandardMaterial({ color: col('#CFC3AE'), roughness: .85 }),
  boxCap: new THREE.MeshStandardMaterial({ color: col('#B9A98E'), roughness: .85, transparent: true, opacity: .8 }),
  lid: new THREE.MeshStandardMaterial({ color: col('#E8762E'), roughness: .8, transparent: true, opacity: .3 }),
  pcb: new THREE.MeshStandardMaterial({ color: col('#2E5A3B'), roughness: .6 }),
  pcbEdge: new THREE.MeshStandardMaterial({ color: col('#C9A24A'), roughness: .5, metalness: .4 }),
  black: new THREE.MeshStandardMaterial({ color: col('#2A2A2C'), roughness: .7 }),
  socket: new THREE.MeshStandardMaterial({ color: col('#3B3B3F'), roughness: .8 }),
  diode: new THREE.MeshStandardMaterial({ color: col('#1B1B1D'), roughness: .5 }),
  metal: new THREE.MeshStandardMaterial({ color: col('#B9BCC2'), roughness: .35, metalness: .8 }),
  ctrl: new THREE.MeshStandardMaterial({ color: col('#1C2538'), roughness: .5 }),
  battery: new THREE.MeshStandardMaterial({ color: col('#8E9CB0'), roughness: .5 }),
  switchBody: new THREE.MeshStandardMaterial({ color: col('#EDE8DF'), roughness: .8 }),
  stem: new THREE.MeshStandardMaterial({ color: col('#C8402C'), roughness: .6 }),
  cap: new THREE.MeshStandardMaterial({ color: col('#F4F0E7'), roughness: .75 }),
  capGrey: new THREE.MeshStandardMaterial({ color: col('#CFCAC0'), roughness: .75 }),
  capThumb: new THREE.MeshStandardMaterial({ color: col('#EF7F3A'), roughness: .7 }),
  cradle: new THREE.MeshStandardMaterial({ color: col('#CFC5B3'), roughness: .85 }),
  ball: new THREE.MeshStandardMaterial({ color: col('#FFFFFF'), roughness: .25 }),
  sensor: new THREE.MeshStandardMaterial({ color: col('#1E4A6B'), roughness: .5 }),
  lens: new THREE.MeshStandardMaterial({ color: col('#9FB9C9'), roughness: .2, transparent: true, opacity: .8 }),
  bumper: new THREE.MeshStandardMaterial({ color: col('#2A2A2C'), roughness: 1 }),
  bearing: new THREE.MeshStandardMaterial({ color: col('#F2F2F2'), roughness: .2 }),
};
for (const m of Object.values(M)) m.side = THREE.DoubleSide;

// ---------- DOM ----------
const TEMPLATE = `
<div class="split explorer">
  <div class="stage xp-stage">
    <svg class="xp-leaders" aria-hidden="true"></svg>
    <div class="xp-labels" aria-hidden="true"></div>
    <div class="xp-hud">
      <h1 class="xp-title">k0d3ball35</h1>
      <p>Drag to orbit, also from underneath; scroll or pinch to zoom. With the view focused, arrow keys orbit and + / - zoom. Heights are true to the CAD.</p>
      <span class="xp-tag" aria-live="polite">assembled</span>
    </div>
    <div class="viewer-status" role="status" hidden></div>
  </div>
  <aside class="panel" aria-label="Explorer controls">
    <div>
      <h2 id="xpHalfH">Half</h2>
      <div class="seg" role="radiogroup" aria-labelledby="xpHalfH">
        <label><input type="radio" name="xpHalf" value="right" checked><span>Right · 17 keys, ball</span></label>
        <label><input type="radio" name="xpHalf" value="left"><span>Left · 18 keys</span></label>
      </div>
    </div>
    <div class="xp-slider">
      <h2><label for="xpExplode">Explode</label></h2>
      <div class="xp-row"><span>assembled</span><output for="xpExplode">0.00</output><span>exploded</span></div>
      <input type="range" id="xpExplode" min="0" max="1" step="0.01" value="0">
      <div class="actions">
        <button class="btn primary" type="button" data-act="play">Animate</button>
        <button class="btn" type="button" data-act="under">From below</button>
        <button class="btn" type="button" data-act="reset">Reset view</button>
      </div>
    </div>
    <div>
      <h2>View</h2>
      <div class="toggles">
        <label><input type="checkbox" name="rotate" checked> Auto-rotate</label>
        <label><input type="checkbox" name="section"> Section through the ball centre</label>
        <label><input type="checkbox" name="labels" checked> Labels</label>
      </div>
    </div>
    <div>
      <h2 id="xpLidH">Lid</h2>
      <div class="seg" role="radiogroup" aria-labelledby="xpLidH">
        <label><input type="radio" name="xpLid" value="off" checked><span>Off</span></label>
        <label><input type="radio" name="xpLid" value="on"><span>On top</span></label>
        <label><input type="radio" name="xpLid" value="foot"><span>As foot</span></label>
      </div>
      <p class="xp-hint">The lid is two plates on a pin hinge: it holds on top by an inner lip and folds into a tenting foot under the half (magnets in the floor and the outer plate).</p>
    </div>
    <div>
      <h2>Layers</h2>
      <div class="xp-layers"></div>
    </div>
    <div>
      <h2>Dimensions</h2>
      <dl class="dims"></dl>
    </div>
    <p class="note"></p>
  </aside>
</div>`;

// ---------- state ----------
let D = null;            // data/layout.json
let H = null;            // D.halves[half]
let half = null;
let ctxRef = null;
let el = {};
let renderer, scene, camera, root;
let layers = [];
let lidLayer = null;
let labelNodes = [];
let caseMeshes = {};     // key -> Mesh (geometry filled in once the STL is loaded)
const caseCache = new Map();   // half -> Promise<{tray, cap, lid, lid_folded}: BufferGeometry>
const target = new THREE.Vector3();
const clipPlane = new THREE.Plane(new THREE.Vector3(0, 0, -1), 0);
let explode = 0, anim = null;
let active = false, raf = 0, last = 0;
let drag = null, pinch = null;
const pointers = new Set();
const sph = { r: 230, theta: 0.55, phi: 1.05 };
const home = { ...sph };
let stageW = 0, stageH = 0;

function layer(name, explodeY, color, anchor, hidden = false) {
  const g = new THREE.Group();
  g.visible = !hidden;
  root.add(g);
  const l = { name, group: g, explode: explodeY, color, anchor, hidden, baseY: 0 };
  layers.push(l);
  return g;
}

function caseMesh(key, mat) {
  const m = new THREE.Mesh(new THREE.BufferGeometry(), mat);
  m.userData.cached = true;     // geometry belongs to caseCache; not disposed on rebuild
  caseMeshes[key] = m;
  return m;
}

// ---------- building one half ----------
function build(which) {
  half = which;
  H = D.halves[which];
  while (root.children.length) {
    const c = root.children.pop();
    c.traverse((o) => { if (o.geometry && !o.userData.cached) o.geometry.dispose(); });
  }
  layers = [];
  caseMeshes = {};
  root.scale.x = which === 'left' ? -1 : 1;
  const B = H.bounds, ball = H.ball, S = H.stack, c = D.controller, PCB_T = D.pcb_thickness;
  const bx = ball ? ball.x : 0, bz = ball ? ball.y : 0;
  const ol = outlineShape(H.outline);
  target.set((B.min_x + B.max_x) / 2, 4, (B.min_y + B.max_y) / 2 + 2);
  clipPlane.constant = ball ? bz : 60;

  // --- case tray: the printed part from hardware/case (key floor -4.6, well and pocket floor -11.6, rim +5) ---
  layer('Case tray', -34, '#CFC3AE', { x: B.min_x + 10, y: -14, z: B.max_y - 10 }).add(caseMesh('tray', M.tray));
  // --- battery: one cell per half, under the PCB in the bay below the controller (case well) ---
  {
    const bt = H.battery, bay = bt.bay, cell = bt.size;
    const g = layer(`Battery ${bt.cell} (bay under the controller)`, -16, '#7B8BA3', { x: bay.center.x - 14, y: -8, z: bay.center.y + 6 });
    g.add(slab(outlineShape(bt.bay_polygon), 0.05, -PCB_T - 0.02, M.pcbEdge));          // bay outline, back silkscreen
    g.add(box(cell.x, 0.5, cell.y, M.bumper, bay.center.x, -PCB_T - 1.0 - 0.25, bay.center.y));   // 0.5 mm foam pad
    g.add(box(cell.x, cell.z, cell.y, M.battery, bay.center.x, -PCB_T - 1.5 - cell.z / 2, bay.center.y));
    g.add(box(cell.x - 2, 1.0, 2.0, M.black, bay.center.x, -PCB_T - 1.5 - cell.z / 2, bay.center.y + cell.y / 2 - 1.0));   // PCM / lead end
  }
  // --- sensor board + lens (on the case floor in the pocket) ---
  if (ball) {
    const g = layer('Sensor board PMW3610', -16, '#1E4A6B', { x: bx + 16, y: -11, z: bz });
    const sb = ball.sensor_board;
    g.add(box(sb.width, 1.6, sb.height, M.sensor, bx, S.sensor_pcb_plane_z - 0.8, bz));       // board, lens side up at the housing face
    g.add(box(21.5, 3.4, 11.4, M.lens, bx, S.sensor_pcb_plane_z + 1.7, bz));                  // LM18-LSI lens block above the board
    g.add(box(8.6, 2.0, 4.8, M.metal, bx + 6, S.sensor_pcb_plane_z - 1.6 - 1.0, bz - 9));     // FPC connector on the floor side
  }
  // --- cradle (pocket mount) ---
  if (ball) {
    const g = layer('Trackball cradle (pocket mount)', -8, '#CFC5B3', { x: bx - 18, y: 4, z: bz });
    const housing = new THREE.Mesh(new THREE.BoxGeometry(S.housing_x, S.housing_top_z - S.floor_z, S.housing_y), M.cradle);
    housing.position.set(bx, (S.housing_top_z + S.floor_z) / 2, bz); g.add(housing);
    // M2 x 10 flat heads in the 90 degree countersinks: the flat face sits below the tray underside
    const CS = H.case_stack, headK = (CS.case_screw_head_d - 2.0) / 2;
    for (const [sx, sz] of ball.case_screws) g.add(cyl(CS.case_screw_head_d / 2, headK, M.metal, sx, CS.case_screw_head_z + headK / 2, sz, 1.0));
    g.add(cyl(S.cup_outer_d / 2, S.rim_z - S.housing_top_z, M.cradle, bx, (S.rim_z + S.housing_top_z) / 2, bz));         // cup skirt
    const bowl = new THREE.Mesh(new THREE.SphereGeometry(ball.d / 2 + 1.2, 48, 24, 0, Math.PI * 2, Math.PI / 2 + 0.25, Math.PI / 2 - 0.25), M.cradle);
    bowl.position.set(bx, S.ball_centre_z, bz); g.add(bowl);
    // open cup: the rim stays 1 mm below the equator; the optional clip-on retainer is not drawn here
    for (const a of [60, 180, 300]) {                                                     // 2 mm ZrO2 bearings, 35 deg below the equator
      const t = THREE.MathUtils.degToRad(a), r = (ball.d / 2 + 1) * Math.cos(THREE.MathUtils.degToRad(35));
      const m = new THREE.Mesh(new THREE.SphereGeometry(1, 16, 12), M.bearing);
      m.position.set(bx + r * Math.cos(t), S.bearing_contact_z - 0.5, bz + r * Math.sin(t)); g.add(m);
    }
  }
  // --- bottom-side parts ---
  {
    const g = layer('Bottom-side parts', -5, '#3B3B3F', { x: 20, y: -3, z: 28 });
    for (const k of H.keys) {
      const p = keyLocal(k, 2.5, -5.4);
      g.add(box(14.8, 1.8, 6.6, M.socket, p.x, -PCB_T - 0.9, p.z, k.rot));
      const d = keyLocal(k, 0, 6);
      g.add(box(2.8, 1.1, 1.7, M.diode, d.x, -PCB_T - 0.55, d.z, k.rot));
    }
    if (H.fpc) g.add(box(8.6, 2.0, 4.8, M.metal, H.fpc.x, -PCB_T - 1.0, H.fpc.y + 0.6));
    g.add(box(3.0, 1.5, 7.0, M.black, D.power_switch.x, -PCB_T - 0.75, D.power_switch.y));
    g.add(box(2.0, 1.5, 1.5, M.metal, D.power_switch.x - 2.5, -PCB_T - 0.75, D.power_switch.y));  // actuator at the inner edge
    g.add(box(3.5, 1.7, 2.9, M.metal, D.reset.x, -PCB_T - 0.85, D.reset.y));
    g.add(box(8.0, 6.0, 6.0, M.black, D.jst.x, -PCB_T - 3.0, D.jst.y + 0.5));   // optional JST, 6 mm tall
  }
  // --- PCB ---
  {
    const g = layer(`${which === 'left' ? 'Left' : 'Right'} PCB (1.6 mm)`, 0, '#2E5A3B', { x: B.max_x - 6, y: 0, z: B.min_y + 30 });
    g.add(slab(ol, PCB_T, 0, M.pcb));
    for (const h of H.holes) g.add(cyl(1.6, PCB_T + 0.2, M.metal, h.x, -PCB_T / 2, h.y));
    const tp = H.test_pads;
    for (let i = 0; i < tp.labels.length; i++) g.add(cyl(0.75, 0.1, M.pcbEdge, tp.start.x + i * tp.pitch, 0.05, tp.start.y));
    g.add(box(1.7, 0.1, 4.6, M.pcbEdge, D.battery_pads.x, 0.05, D.battery_pads.y));
  }
  // --- controller ---
  {
    const g = layer('Controller nice!nano v2', 14, '#1C2538', { x: c.x - 16, y: 6, z: c.y - 12 });
    const sh = c.socket;                                                   // low-profile sockets, nothing underneath
    for (const sx of [-7.62, 7.62]) g.add(box(2.6, sh, 30.5, M.black, c.x + sx, sh / 2, c.y));
    g.add(box(c.w, 1.6, c.l, M.ctrl, c.x, sh + 0.8, c.y - 0.6));             // nice!nano PCB 1.6 mm
    g.add(box(6, 1.2, 6, M.black, c.x, sh + 1.6 + 0.6, c.y + 2));            // nRF52840 module
    g.add(box(9, 3.2, 7.3, M.metal, c.x, sh + 0.8 + 0.8, c.y - c.l / 2 + 2.5));   // mid-mount USB-C shell
    g.add(box(1.2, 0.6, 1.6, M.stem, c.x + 5, sh + 1.6 + 0.3, c.y - 8));     // status LED spot
  }
  // --- switches ---
  {
    const g = layer('Choc V1 switches', 24, '#EDE8DF', { x: 36, y: 4, z: -4 });
    for (const k of H.keys) {
      g.add(box(D.switch_body, 2.2, D.switch_body, M.switchBody, k.x, 1.1, k.y, k.rot));
      g.add(box(11.5, 2.8, 11.5, M.switchBody, k.x, 3.6, k.y, k.rot));
      g.add(box(4.5, 1.5, 3.0, M.stem, k.x, 5.75, k.y, k.rot));
    }
  }
  // --- keycaps ---
  {
    const g = layer('Keycaps (MBK 1u)', 34, '#F4F0E7', { x: 36, y: 10, z: 44 });
    for (const k of H.keys) {
      const mat = k.kind === 'thumb' ? M.capThumb : (k.ref.endsWith('0') ? M.capGrey : M.cap);
      g.add(box(D.keycap.width, 3.0, D.keycap.height, mat, k.x, 7.0, k.y, k.rot));
      g.add(box(D.keycap.width - 3, 0.6, D.keycap.height - 3, mat, k.x, 8.6, k.y, k.rot));
    }
  }
  // --- ball ---
  if (ball) {
    const g = layer(`Trackball ${ball.d} mm`, 28, '#FFFFFF', { x: bx + 20, y: S.ball_centre_z + 6, z: bz - 6 });
    const m = new THREE.Mesh(new THREE.SphereGeometry(ball.d / 2, 64, 48), M.ball);
    m.position.set(bx, S.ball_centre_z, bz); g.add(m);
  }
  // --- controller box cap: separate printed roof over the controller block, roof underside +6.7 ---
  layer('Controller box cap', 44, '#B9A98E', { x: c.x, y: H.case_stack.box_top_z + 2, z: B.min_y + 4 }).add(caseMesh('cap', M.boxCap));
  // --- lid: cover on top (inner lip, no magnets) or foot under the tray (magnets in floor and roof) ---
  {
    const g = layer('Lid', 60, '#E8762E', { x: B.max_x - 20, y: H.case_stack.lid_top_z + 2, z: B.min_y + 10 }, true);
    g.add(caseMesh('lid', M.lid), caseMesh('lid_folded', M.lid));
    lidLayer = layers[layers.length - 1];
    lidLayer.nolist = true;   // driven by the Lid control, not the layer list
  }

  buildLabels();
  buildDims();
  el.title.textContent = `${D.name} ${D.revision}, ${which} half (${H.keys.length} keys${ball ? `, ${ball.d} mm ball` : ''})`;
  el.section.disabled = !ball;
  el.section.closest('label').classList.toggle('xp-disabled', !ball);
  if (!ball && el.section.checked) { el.section.checked = false; setSection(false); }
  applyLidMode();
  attachCase(which);
}

// ---------- case STLs, per half on first use ----------
function loadCase(which) {
  if (!caseCache.has(which)) {
    const files = D.halves[which].case_files;
    const frac = Object.fromEntries(CASE_KEYS.map((k) => [k, 0]));
    let failed = false;   // the other files keep reporting progress after one failed; keep the error on screen
    const report = () => {
      if (half !== which || failed) return;
      const f = CASE_KEYS.reduce((s, k) => s + frac[k], 0) / CASE_KEYS.length;
      showStatus(`Loading the ${which} case parts`, f);
    };
    report();
    const matrix = caseMatrix(which);
    const p = Promise.all(CASE_KEYS.map(async (k) => {
      const buf = await fetchBuffer(files[k], (f) => { frac[k] = f ?? 0.5; report(); });
      frac[k] = 1; report();
      const geom = transformGeometry(parseSTL(buf), matrix);
      geom.computeVertexNormals();
      geom.computeBoundingSphere();
      return [k, geom];
    })).then(Object.fromEntries);
    p.catch(() => { failed = true; caseCache.delete(which); });   // a later visit tries again
    caseCache.set(which, p);
  }
  return caseCache.get(which);
}

async function attachCase(which) {
  let geoms;
  try {
    geoms = await loadCase(which);
  } catch (e) {
    if (half === which) showError(e.message || String(e));
    return;
  }
  if (half !== which) return;      // switched halves while loading
  for (const k of CASE_KEYS) caseMeshes[k].geometry = geoms[k];
  hideStatus();
}

function showStatus(text, progress) {
  const s = el.status;
  s.className = 'viewer-status';
  s.hidden = false;
  s.textContent = text;
  if (progress != null) {
    const bar = document.createElement('progress');
    bar.max = 1; bar.value = progress;
    s.append(bar);
  }
}
function showError(text) { el.status.className = 'viewer-status error'; el.status.hidden = false; el.status.textContent = text; }
function hideStatus() { el.status.hidden = true; }

// ---------- section view: clip everything in front of the ball centre ----------
function setSection(on) {
  for (const m of Object.values(M)) { m.clippingPlanes = on ? [clipPlane] : []; m.needsUpdate = true; }
  el.sectionLabel.hidden = !on;
}

// ---------- labels, layer list, dimensions ----------
function buildLabels() {
  el.labels.replaceChildren();
  el.leaders.replaceChildren();
  el.layers.replaceChildren();
  labelNodes = layers.map((l) => {
    const lab = document.createElement('div');
    lab.className = 'xp-label';
    lab.textContent = l.name;
    el.labels.append(lab);
    const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    el.leaders.append(line);
    if (!l.nolist) {
      const row = document.createElement('label');
      const cb = document.createElement('input'); cb.type = 'checkbox'; cb.checked = !l.hidden;
      cb.addEventListener('change', () => { l.group.visible = cb.checked; });
      const sw = document.createElement('span'); sw.className = 'xp-swatch'; sw.style.background = l.color;
      row.append(cb, sw, document.createTextNode(l.name));
      el.layers.append(row);
    }
    return { el: lab, line };
  });
  el.labels.append(el.sectionLabel);
  if (H.stack) el.sectionLabel.innerHTML = `lens gap <small>${H.stack.lens_reference_plane_dist.toFixed(1)} mm (2.2 to 2.6)</small>`;
}

function buildDims() {
  const S = H.stack, B = H.bounds;
  const dims = [
    ['Board outline', `${B.width.toFixed(1)} x ${B.height.toFixed(1)} mm`],
    ['Keys', `${H.keys.length} (${H.keys.filter((k) => k.kind === 'thumb').length} thumb)`],
    ['PCB thickness', `${D.pcb_thickness.toFixed(1)} mm`],
    ['Controller top', `+${(D.controller.socket + 1.6 + 1.6).toFixed(1)} mm`],
    ['Lid over the controller block (concept)', `+${D.controller_lid_z.toFixed(1)} mm`],
    ['Battery', `${H.battery.cell}, ${H.battery.capacity_mah} mAh, bay ${H.battery.bay.size.x} x ${H.battery.bay.size.y} mm under the controller`],
    ['Battery well floor', `${H.battery.well_floor_z.toFixed(1)} mm`],
    ['Keycap top', '+8.9 mm'],
    ['Mounting holes', `${H.holes.length} x M2`],
    ['Test pads', H.test_pads.labels.join(' ')],
  ];
  if (S) dims.push(
    ['Ball top above PCB', `+${S.ball_top_above_pcb_top.toFixed(1)} mm`],
    ['Ball centre above PCB', `+${S.ball_centre_z.toFixed(1)} mm`],
    ['Cup rim', `+${S.rim_z.toFixed(1)} mm`],
    ['Case floor under the module', `${S.floor_z.toFixed(1)} mm`],
    ['Cup outer diameter', `${S.cup_outer_d.toFixed(1)} mm`],
    ['Cradle envelope above PCB', `${S.envelope_d_above_pcb.toFixed(1)} mm`],
    ['PCB notch', `octagon, apothem ${S.notch_apothem.toFixed(0)} mm`],
    ['Case pocket', `${H.ball.pocket_d.toFixed(0)} mm ring above the PCB`],
    ['Housing on the floor', `${S.housing_x.toFixed(0)} x ${S.housing_y.toFixed(0)} mm, 2 x M2 from below`],
  );
  el.dims.replaceChildren();
  for (const [k, v] of dims) {
    const dt = document.createElement('dt'); dt.textContent = k;
    const dd = document.createElement('dd'); dd.textContent = v;
    el.dims.append(dt, dd);
  }
  el.note.innerHTML = H.ball
    ? '<b>Reading the stack.</b> PCB top is the zero plane. Hot-swap sockets, diodes and connectors hang below the PCB; the controller sits on 2.5 mm low-profile sockets and the LP552035 cell lies under the PCB in the bay below it, in the 10 mm deep well of the printed tray, like on the left half. The trackball module stands on the tray floor in the pocket beside the PCB: its housing holds the sensor board, the cup rises through the octagonal notch and nothing touches the PCB. The tray, the controller box cap and the lid are the printed parts from hardware/case.'
    : '<b>Reading the stack.</b> PCB top is the zero plane. Hot-swap sockets, diodes and connectors hang below the PCB; the controller sits on 2.5 mm low-profile sockets and the LP552035 cell lies under the PCB in the bay below it, in the 10 mm deep well of the printed tray, identical to the right half. The left half has three thumb keys and no ball, no FPC connector and nine test pads.';
}

// ---------- camera: a small spherical orbit around the half ----------
function applyCamera() {
  const tx = target.x * root.scale.x;
  camera.position.set(
    tx + sph.r * Math.sin(sph.phi) * Math.sin(sph.theta),
    target.y + sph.r * Math.cos(sph.phi),
    target.z + sph.r * Math.sin(sph.phi) * Math.cos(sph.theta));
  camera.lookAt(tx, target.y, target.z);
}
const clampPhi = (p) => THREE.MathUtils.clamp(p, 0.15, Math.PI - 0.15);
const clampR = (r) => THREE.MathUtils.clamp(r, 90, 600);

function bindCamera(canvas) {
  canvas.addEventListener('pointerdown', (e) => {
    pointers.add(e.pointerId);
    if (pointers.size > 1) { drag = null; return; }     // second finger: pinch, not orbit
    drag = { x: e.clientX, y: e.clientY };
    canvas.setPointerCapture(e.pointerId);
    el.rotate.checked = false;
  });
  canvas.addEventListener('pointermove', (e) => {
    if (!drag || pointers.size > 1) return;
    sph.theta -= (e.clientX - drag.x) * 0.006;
    sph.phi = clampPhi(sph.phi - (e.clientY - drag.y) * 0.006);
    drag = { x: e.clientX, y: e.clientY };
  });
  const up = (e) => { pointers.delete(e.pointerId); drag = null; };
  canvas.addEventListener('pointerup', up);
  canvas.addEventListener('pointercancel', up);
  canvas.addEventListener('wheel', (e) => { e.preventDefault(); sph.r = clampR(sph.r * (1 + e.deltaY * 0.001)); }, { passive: false });
  const span = (t) => Math.hypot(t[0].clientX - t[1].clientX, t[0].clientY - t[1].clientY);
  canvas.addEventListener('touchstart', (e) => { if (e.touches.length === 2) pinch = span(e.touches); }, { passive: true });
  canvas.addEventListener('touchmove', (e) => {
    if (e.touches.length === 2 && pinch) { const d = span(e.touches); sph.r = clampR(sph.r * pinch / d); pinch = d; }
  }, { passive: true });
  canvas.addEventListener('touchend', (e) => { if (e.touches.length < 2) pinch = null; }, { passive: true });
  canvas.addEventListener('keydown', (e) => {
    const step = 0.08;
    const keys = {
      ArrowLeft: () => { sph.theta += step; }, ArrowRight: () => { sph.theta -= step; },
      ArrowUp: () => { sph.phi = clampPhi(sph.phi - step); }, ArrowDown: () => { sph.phi = clampPhi(sph.phi + step); },
      '+': () => { sph.r = clampR(sph.r * 0.9); }, '=': () => { sph.r = clampR(sph.r * 0.9); },
      '-': () => { sph.r = clampR(sph.r * 1.1); }, _: () => { sph.r = clampR(sph.r * 1.1); },
    };
    if (!keys[e.key]) return;
    e.preventDefault();
    el.rotate.checked = false;
    keys[e.key]();
  });
}

// ---------- controls ----------
function setExplode(v) {
  explode = v;
  el.explode.value = v.toFixed(2);
  el.explodeVal.textContent = v.toFixed(2);
  el.tag.textContent = v < 0.02 ? 'assembled' : v > 0.98 ? 'exploded' : 'exploding';
  for (const l of layers) l.group.position.y = l.baseY + l.explode * v;
}

function applyLidMode() {
  if (!lidLayer) return;
  const mode = el.panel.querySelector('input[name=xpLid]:checked').value;
  const cs = H.case_stack;
  lidLayer.group.visible = mode !== 'off';
  // foot: the plates folded by hinge_fold_deg and shifted inward by foot_dx, the outer plate
  // roof-up under the controller half, the inner plate as the kickstand beyond the inner edge
  // (the view keeps the half level; on the desk the kickstand tilts it by tent_deg)
  caseMeshes.lid.visible = mode !== 'foot';
  caseMeshes.lid_folded.visible = mode === 'foot';
  caseMeshes.lid_folded.position.x = cs.foot_dx ?? 0;
  if (mode === 'foot') {
    lidLayer.baseY = cs.base_z - cs.lid_top_z; lidLayer.explode = -60;
    lidLayer.anchor.y = cs.base_z - 4;
  } else {
    lidLayer.baseY = 0; lidLayer.explode = 60;
    lidLayer.anchor.y = cs.lid_top_z + 2;
  }
  lidLayer.name = mode === 'foot'
    ? `Lid folded as kickstand (hinge ${(cs.hinge_fold_deg ?? 34).toFixed(0)} deg, tilts the half by ${(cs.tent_deg ?? 15).toFixed(0)} deg)`
    : 'Lid (two hinged plates, inner lip)';
  const node = labelNodes[layers.indexOf(lidLayer)];
  if (node) node.el.textContent = lidLayer.name;
  setExplode(explode);
}

function bindPanel() {
  const p = el.panel;
  el.explode.addEventListener('input', () => { anim = null; setExplode(parseFloat(el.explode.value)); });
  p.querySelector('[data-act=play]').addEventListener('click', () => {
    const to = explode > 0.5 ? 0 : 1;
    if (reduced()) { setExplode(to); return; }
    anim = { from: explode, to, t0: performance.now(), dur: 1600 };
  });
  p.querySelector('[data-act=reset]').addEventListener('click', () => { Object.assign(sph, home); el.rotate.checked = !reduced(); });
  p.querySelector('[data-act=under]').addEventListener('click', () => {
    Object.assign(sph, { r: home.r, theta: 0.55, phi: Math.PI - 0.45 });
    el.rotate.checked = false;
  });
  for (const r of p.querySelectorAll('input[name=xpLid]')) r.addEventListener('change', () => { if (r.checked) applyLidMode(); });
  for (const r of p.querySelectorAll('input[name=xpHalf]')) {
    r.addEventListener('change', () => {
      if (!r.checked) return;
      build(r.value);
      ctxRef?.navigate(r.value);
    });
  }
  el.section.addEventListener('change', () => setSection(el.section.checked));
  el.showLabels.addEventListener('change', () => {
    el.labels.style.visibility = el.leaders.style.visibility = el.showLabels.checked ? 'visible' : 'hidden';
  });
}

// ---------- theme, size, render loop ----------
function applyTheme() { renderer?.setClearColor(new THREE.Color(css('--stage') || '#DCE1D8')); }

function resize() {
  const w = el.stage.clientWidth, h = el.stage.clientHeight;
  if (!w || !h) return;               // hidden tab
  stageW = w; stageH = h;
  renderer.setSize(w, h, false);
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
  el.leaders.setAttribute('viewBox', `0 0 ${w} ${h}`);
}

const v3 = new THREE.Vector3();
function project(x, y, z) {
  v3.set(x * root.scale.x, y, z).project(camera);
  return { x: (v3.x + 1) / 2 * stageW, y: (1 - v3.y) / 2 * stageH, behind: v3.z > 1 };
}

function frame(now) {
  raf = 0;
  if (!active) return;
  const dt = Math.min(0.05, (now - last) / 1000); last = now;
  if (el.rotate.checked && !drag && !reduced()) sph.theta += dt * 0.18;
  if (anim) {
    const k = Math.min(1, (now - anim.t0) / anim.dur), e = k < .5 ? 2 * k * k : 1 - Math.pow(-2 * k + 2, 2) / 2;
    setExplode(anim.from + (anim.to - anim.from) * e);
    if (k >= 1) anim = null;
  }
  applyCamera();
  renderer.render(scene, camera);
  const showLabels = explode > 0.35;
  const offset = Math.min(110, stageW * 0.2);   // leader length, shorter on narrow screens
  const widths = labelNodes.map((n) => n.el.offsetWidth);   // read before any write: one layout per frame
  layers.forEach((l, i) => {
    const { el: lab, line } = labelNodes[i];
    const on = showLabels && l.group.visible;
    lab.classList.toggle('on', on);
    if (!on) { line.setAttribute('opacity', 0); return; }
    const a = l.anchor, y = a.y + l.baseY + l.explode * explode;
    const p = project(a.x, y, a.z);
    const side = (a.x * root.scale.x) < (target.x * root.scale.x) ? -1 : 1;
    const half = widths[i] / 2 + 4;   // keep the label inside the stage on narrow screens
    const lx = THREE.MathUtils.clamp(p.x + side * offset, half, Math.max(half, stageW - half)), ly = p.y - 18;
    lab.style.left = `${lx}px`; lab.style.top = `${ly}px`;
    line.setAttribute('x1', p.x); line.setAttribute('y1', p.y);
    line.setAttribute('x2', lx - side * Math.min(48, offset * 0.44, half)); line.setAttribute('y2', ly);
    line.setAttribute('opacity', p.behind ? 0 : 1);
  });
  if (!el.sectionLabel.hidden && H.ball) {
    const p = project(H.ball.x, H.stack.ball_centre_z - H.ball.d / 2 - 1.2, H.ball.y + 0.1);
    el.sectionLabel.style.left = `${p.x + Math.min(90, stageW * 0.18)}px`; el.sectionLabel.style.top = `${p.y}px`;
  }
  raf = requestAnimationFrame(frame);
}

function start() {
  if (active || !renderer) return;
  active = true;
  resize();
  last = performance.now();
  if (!raf) raf = requestAnimationFrame(frame);
}
function stop() {
  active = false;
  if (raf) cancelAnimationFrame(raf);
  raf = 0;
  drag = null; pinch = null; pointers.clear();
  if (anim) { setExplode(anim.to); anim = null; }
}

// ---------- tab contract ----------
const pickHalf = (sub) => (HALVES.includes(sub) ? sub : null);

function selectHalf(which) {
  if (!D || which === half) return;
  el.panel.querySelector(`input[name=xpHalf][value=${which}]`).checked = true;
  build(which);
}

export async function mount(section, ctx) {
  ctxRef = ctx;
  section.innerHTML = TEMPLATE;
  const q = (s) => section.querySelector(s);
  el = {
    stage: q('.xp-stage'), leaders: q('.xp-leaders'), labels: q('.xp-labels'), title: q('.xp-title'), tag: q('.xp-tag'),
    status: q('.xp-stage .viewer-status'), panel: q('aside.panel'), explode: q('#xpExplode'), explodeVal: q('output[for=xpExplode]'),
    rotate: q('input[name=rotate]'), section: q('input[name=section]'), showLabels: q('input[name=labels]'),
    layers: q('.xp-layers'), dims: q('.dims'), note: q('.note'),
  };
  el.sectionLabel = document.createElement('div');
  el.sectionLabel.className = 'xp-label on';
  el.sectionLabel.hidden = true;
  if (reduced()) el.rotate.checked = false;

  try {
    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
  } catch (e) {
    showError('This view needs WebGL, which this browser did not provide.');
    return;
  }
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  renderer.localClippingEnabled = true;
  const canvas = renderer.domElement;
  canvas.tabIndex = 0;
  canvas.setAttribute('role', 'img');
  canvas.setAttribute('aria-label', '3D exploded view of one k0d3ball35 half. Arrow keys orbit, plus and minus zoom.');
  el.stage.prepend(canvas);

  scene = new THREE.Scene();
  camera = new THREE.PerspectiveCamera(38, 1, 1, 2000);
  scene.add(new THREE.HemisphereLight(0xffffff, 0x8a8370, 1.15));
  const sun = new THREE.DirectionalLight(0xffffff, 1.6); sun.position.set(80, 160, 120); scene.add(sun);
  const fill = new THREE.DirectionalLight(0xffffff, .5); fill.position.set(-120, 60, -80); scene.add(fill);
  // from below: the case underside carries the engraved wordmark and the magnet pockets
  const under = new THREE.DirectionalLight(0xffffff, .85); under.position.set(40, -140, 90); scene.add(under);
  root = new THREE.Group();      // mirrored (scale.x = -1) for the left half
  scene.add(root);

  bindCamera(canvas);
  bindPanel();
  applyTheme();
  document.addEventListener('themechange', applyTheme);
  new ResizeObserver(() => { if (active) resize(); }).observe(el.stage);

  try {
    D = await loadData('layout');
  } catch (e) {
    showError(e.message || String(e));
    return;
  }
  const first = pickHalf(ctx.sub) || 'right';
  el.panel.querySelector(`input[name=xpHalf][value=${first}]`).checked = true;
  build(first);
}

export function show(sub) {
  const which = pickHalf(sub);
  if (which) selectHalf(which);
  start();
}

export function hide() { stop(); }
