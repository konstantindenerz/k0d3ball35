// SPDX-License-Identifier: MIT
// ModelViewer: the one 3D viewer the Case, Trackball and PCBs tabs share.
//
// World frame = the repository's CAD frame: millimetres, Z up (OpenSCAD and KiCad). glTF files
// (KiCad GLB export) are Y up and in metres, so loadGLB turns them into this frame.
// Renders on demand: a frame is drawn when the camera moves, a model loads or a setting changes,
// and nothing runs while the tab is hidden (setActive(false)).

import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { STLLoader } from 'three/addons/loaders/STLLoader.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { fetchBuffer } from './assets.js';

const css = (v) => getComputedStyle(document.documentElement).getPropertyValue(v).trim();
const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;

/** Apply a 4x4 matrix to a geometry in place and keep it outward facing: a reflection
 *  (negative determinant) reverses the triangle winding, so the winding is reversed back. */
export function transformGeometry(geom, matrix) {
  geom.applyMatrix4(matrix);
  if (matrix.determinant() < 0) {
    if (geom.index) {
      const a = geom.index.array;
      for (let i = 0; i < a.length; i += 3) { const t = a[i + 1]; a[i + 1] = a[i + 2]; a[i + 2] = t; }
      geom.index.needsUpdate = true;
    } else {
      for (const name of Object.keys(geom.attributes)) {
        const attr = geom.attributes[name];
        const n = attr.itemSize;
        const arr = attr.array;
        for (let i = 0; i < attr.count; i += 3) {
          for (let k = 0; k < n; k++) {
            const b = (i + 1) * n + k, c = (i + 2) * n + k;
            const t = arr[b]; arr[b] = arr[c]; arr[c] = t;
          }
        }
        attr.needsUpdate = true;
      }
    }
  }
  return geom;
}

/** Parse an STL ArrayBuffer into a BufferGeometry (mm, as written by OpenSCAD). */
export function parseSTL(buffer) {
  return new STLLoader().parse(buffer);
}

export class ModelViewer {
  /**
   * @param {HTMLElement} host  positioned container (e.g. .stage); the canvas fills it
   * @param {{grid?: boolean, autoRotate?: boolean, label?: string}} opts
   */
  constructor(host, opts = {}) {
    this.host = host;
    this.opts = { grid: true, autoRotate: false, ...opts };
    this.active = true;
    this.needsRender = true;

    this.renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: false });
    this.renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
    this.renderer.outputColorSpace = THREE.SRGBColorSpace;
    this.renderer.localClippingEnabled = true;
    this.canvas = this.renderer.domElement;
    this.canvas.setAttribute('role', 'img');
    this.canvas.setAttribute('aria-label', this.opts.label || '3D model');
    host.prepend(this.canvas);

    this.scene = new THREE.Scene();
    this.camera = new THREE.PerspectiveCamera(32, 1, 0.5, 5000);
    this.camera.up.set(0, 0, 1);
    this.camera.position.set(120, -160, 120);

    this.scene.add(new THREE.HemisphereLight(0xffffff, 0x8a8f86, 1.6));
    const key = new THREE.DirectionalLight(0xffffff, 1.7);
    key.position.set(1, -1.2, 2);
    const rim = new THREE.DirectionalLight(0xffffff, 0.6);
    rim.position.set(-1.5, 1, 0.6);
    this.scene.add(key, rim);

    this.content = new THREE.Group();
    this.scene.add(this.content);

    this.controls = new OrbitControls(this.camera, this.canvas);
    this.controls.enableDamping = !reducedMotion;
    this.controls.dampingFactor = 0.12;
    this.controls.autoRotate = this.opts.autoRotate && !reducedMotion;
    this.controls.autoRotateSpeed = 0.8;
    this.controls.addEventListener('change', () => this.requestRender());
    this.controls.addEventListener('start', () => { this.controls.autoRotate = false; });

    this.clipPlane = new THREE.Plane(new THREE.Vector3(0, 0, -1), 0);
    this.clip = { on: false, axis: 'z', t: 0.5, flip: false };

    this.status = document.createElement('div');
    this.status.className = 'viewer-status';
    this.status.hidden = true;
    host.append(this.status);

    this._resize = () => this.resize();
    this._ro = new ResizeObserver(this._resize);
    this._ro.observe(host);
    this._theme = () => this.applyTheme();
    document.addEventListener('themechange', this._theme);
    this.applyTheme();
    this.resize();
    this._loop = this._loop.bind(this);
    requestAnimationFrame(this._loop);
  }

  // ---------------------------------------------------------------- loading
  /** Load a repo STL and add it. opts: color, matrix (THREE.Matrix4), name, opacity, add (default true). */
  async loadSTL(repoPath, opts = {}) {
    const buf = await this._fetch(repoPath, opts);
    const geom = parseSTL(buf);
    if (opts.matrix) transformGeometry(geom, opts.matrix);
    geom.computeBoundingBox();
    const mesh = new THREE.Mesh(geom, this.material(opts.color, opts.opacity));
    mesh.name = opts.name || repoPath;
    mesh.userData.repoPath = repoPath;
    mesh.userData.triangles = geom.index ? geom.index.count / 3 : geom.attributes.position.count / 3;
    if (opts.add !== false) this.add(mesh);
    return mesh;
  }

  /** Load a repo GLB (KiCad export: Y up, metres) into the Z-up millimetre frame and add it. */
  async loadGLB(repoPath, opts = {}) {
    const buf = await this._fetch(repoPath, opts);
    const gltf = await new Promise((resolve, reject) => new GLTFLoader().parse(buf, '', resolve, reject));
    const root = new THREE.Group();
    const scale = opts.scale ?? 1000;               // metres -> mm
    gltf.scene.rotation.x = Math.PI / 2;            // Y up -> Z up
    gltf.scene.scale.setScalar(scale);
    root.add(gltf.scene);
    root.name = opts.name || repoPath;
    root.userData.repoPath = repoPath;
    root.traverse((o) => {
      if (o.isMesh) {
        const mats = Array.isArray(o.material) ? o.material : [o.material];
        mats.forEach((m) => { m.side = THREE.DoubleSide; m.clippingPlanes = this._planes(); });
      }
    });
    if (opts.add !== false) this.add(root);
    return root;
  }

  async _fetch(repoPath, opts) {
    if (opts.status !== false) this.showStatus(`Loading ${repoPath.split('/').pop()}`, 0);
    try {
      const buf = await fetchBuffer(repoPath, (f) => { if (opts.status !== false) this.showStatus(`Loading ${repoPath.split('/').pop()}`, f); });
      if (opts.status !== false) this.hideStatus();
      return buf;
    } catch (e) {
      if (opts.status !== false) this.showError(e.message);
      throw e;
    }
  }

  material(color = '#C9CFC4', opacity = 1) {
    return new THREE.MeshStandardMaterial({
      color, roughness: 0.72, metalness: 0.02, side: THREE.DoubleSide,
      transparent: opacity < 1, opacity, clippingPlanes: this._planes(),
    });
  }

  _planes() { return this.clip.on ? [this.clipPlane] : []; }

  add(obj) { this.content.add(obj); this._refreshGrid(); this.requestRender(); return obj; }
  remove(obj) {
    this.content.remove(obj);
    obj.traverse?.((o) => { o.geometry?.dispose(); (Array.isArray(o.material) ? o.material : [o.material]).forEach((m) => m?.dispose?.()); });
    this._refreshGrid();
    this.requestRender();
  }
  clear() { [...this.content.children].forEach((c) => this.remove(c)); }

  // ---------------------------------------------------------------- view
  /** Box3 of everything shown, in mm. */
  bounds(obj = this.content) { return new THREE.Box3().setFromObject(obj); }

  /** Frame the content. dir: camera direction from the target ('iso', 'top', 'bottom', 'front', 'side'). */
  fit(dir = 'iso', obj = this.content) {
    const box = this.bounds(obj);
    if (box.isEmpty()) return;
    const c = box.getCenter(new THREE.Vector3());
    const r = box.getSize(new THREE.Vector3()).length() / 2;
    const dirs = { iso: [0.55, -0.85, 0.75], top: [0, -0.001, 1], bottom: [0, 0.001, -1], front: [0, -1, 0.12], side: [1, 0, 0.12] };
    const d = new THREE.Vector3(...(dirs[dir] || dirs.iso)).normalize();
    const dist = r / Math.sin(THREE.MathUtils.degToRad(this.camera.fov / 2)) * 1.08;
    this.camera.position.copy(c).addScaledVector(d, dist);
    this.camera.near = Math.max(0.1, dist / 200);
    this.camera.far = dist * 20;
    this.camera.updateProjectionMatrix();
    this.controls.target.copy(c);
    this.controls.update();
    this._applyClip();
    this.requestRender();
  }

  setWireframe(on) {
    this.content.traverse((o) => { if (o.isMesh) (Array.isArray(o.material) ? o.material : [o.material]).forEach((m) => { m.wireframe = on; }); });
    this.requestRender();
  }

  setAutoRotate(on) { this.controls.autoRotate = on && !reducedMotion; this.requestRender(); }

  /** Section plane. axis 'x'|'y'|'z', t 0..1 across the content's bounds; keeps the part below t (flip: above). */
  setClip({ on = this.clip.on, axis = this.clip.axis, t = this.clip.t, flip = this.clip.flip } = {}) {
    const was = this.clip.on;
    Object.assign(this.clip, { on, axis, t, flip });
    if (was !== on) {
      this.content.traverse((o) => { if (o.isMesh) (Array.isArray(o.material) ? o.material : [o.material]).forEach((m) => { m.clippingPlanes = this._planes(); m.needsUpdate = true; }); });
    }
    this._applyClip();
    this.requestRender();
  }

  _applyClip() {
    if (!this.clip.on) return;
    const box = this.bounds();
    if (box.isEmpty()) return;
    const i = { x: 0, y: 1, z: 2 }[this.clip.axis];
    const lo = box.min.getComponent(i), hi = box.max.getComponent(i);
    const at = lo + (hi - lo) * this.clip.t;
    const n = new THREE.Vector3(); n.setComponent(i, this.clip.flip ? 1 : -1);
    this.clipPlane.normal.copy(n);
    this.clipPlane.constant = this.clip.flip ? -at : at;
  }

  _refreshGrid() {
    if (this.grid) { this.scene.remove(this.grid); this.grid.geometry.dispose(); this.grid.material.dispose(); this.grid = null; }
    if (!this.opts.grid) return;
    const box = this.bounds();
    if (box.isEmpty()) return;
    const size = box.getSize(new THREE.Vector3());
    const span = Math.ceil(Math.max(size.x, size.y, 40) * 1.6 / 10) * 10;
    this.grid = new THREE.GridHelper(span, span / 5, css('--muted') || '#888', css('--line') || '#ccc');
    this.grid.rotation.x = Math.PI / 2;
    const c = box.getCenter(new THREE.Vector3());
    this.grid.position.set(Math.round(c.x / 5) * 5, Math.round(c.y / 5) * 5, box.min.z - 0.01);
    this.grid.material.transparent = true;
    this.grid.material.opacity = 0.55;
    this.scene.add(this.grid);
  }

  applyTheme() {
    this.renderer.setClearColor(new THREE.Color(css('--stage') || '#DCE1D8'));
    this._refreshGrid();
    this.requestRender();
  }

  // ---------------------------------------------------------------- status overlay
  showStatus(text, progress = null) {
    this.status.className = 'viewer-status';
    this.status.hidden = false;
    this.status.textContent = text;
    if (progress != null) {
      const bar = document.createElement('progress');
      bar.max = 1; bar.value = progress;
      this.status.append(bar);
    }
  }
  showError(text) { this.status.className = 'viewer-status error'; this.status.hidden = false; this.status.textContent = text; }
  hideStatus() { this.status.hidden = true; }

  // ---------------------------------------------------------------- lifecycle
  resize() {
    const w = this.host.clientWidth, h = this.host.clientHeight;
    if (!w || !h) return;
    this.renderer.setSize(w, h, false);
    this.camera.aspect = w / h;
    this.camera.updateProjectionMatrix();
    this.requestRender();
  }

  requestRender() { this.needsRender = true; }

  /** Pause (false) or resume (true) drawing, e.g. when the tab is hidden or shown. */
  setActive(on) { this.active = on; if (on) { this.resize(); this.requestRender(); } }

  _loop() {
    requestAnimationFrame(this._loop);
    if (!this.active) return;
    const moving = this.controls.update();   // true while damping or auto-rotating
    if (this.needsRender || moving || this.controls.autoRotate) {
      this.needsRender = false;
      this.renderer.render(this.scene, this.camera);
    }
  }

  dispose() {
    this.active = false;
    this._ro.disconnect();
    document.removeEventListener('themechange', this._theme);
    this.clear();
    this.controls.dispose();
    this.renderer.dispose();
    this.canvas.remove();
    this.status.remove();
  }
}
