// SPDX-License-Identifier: MIT
// case tab (temporary viewer smoke test).
import { ModelViewer } from '../viewer.js';
let v;
export async function mount(section) {
  section.innerHTML = '<div class="split"><div class="stage"></div><aside class="panel"><h2>Smoke test</h2></aside></div>';
  v = new ModelViewer(section.querySelector('.stage'));
  await v.loadSTL('hardware/case/stl/tray-right.stl', { color: '#C9CFC4' });
  v.fit();
}
export const show = () => v?.setActive(true);
export const hide = () => v?.setActive(false);
