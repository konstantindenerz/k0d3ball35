// SPDX-License-Identifier: MIT
// Hash router for the sheet tabs.
//
// #<tab>[/<sub>]  e.g. #case/tray-right. A tab module is imported on its first visit and lives in
// js/tabs/<tab>.js (the importmap of index.html turns that into its hashed URL) with this contract:
//   export async function mount(section, ctx)  build the DOM once; ctx = { site, sub, navigate(sub) }
//   export function show(sub)                   the tab became visible (or its sub route changed)
//   export function hide()                      the tab was left: stop render loops
// Only mount is required.

import { assetBaseLabel, loadData, loadVersions } from './assets.js';

const chrome = document.getElementById('chrome');
const sections = new Map([...document.querySelectorAll('main > section.tab')].map((s) => [s.id.slice(4), s]));
const links = [...document.querySelectorAll('.sheets a[data-tab]')];
const ids = links.map((a) => a.dataset.tab);
const modules = new Map();     // id -> Promise<module>
let current = null;
let site = null;

function parseHash() {
  const [id, ...rest] = decodeURIComponent(location.hash.replace(/^#/, '')).split('/');
  return { id: ids.includes(id) ? id : ids[0], sub: rest.join('/') || '' };
}

function setChromeHeight() {
  document.documentElement.style.setProperty('--chrome-h', `${Math.ceil(chrome.getBoundingClientRect().height)}px`);
}

function load(id) {
  if (!modules.has(id)) {
    const section = sections.get(id);
    section.innerHTML = '<p class="loading-tab">Loading…</p>';
    const p = import(`./tabs/${id}.js`).then(async (mod) => {
      section.innerHTML = '';
      await mod.mount(section, {
        site,
        sub: parseHash().sub,
        navigate: (sub) => history.replaceState(null, '', `#${id}${sub ? `/${sub}` : ''}`),
      });
      return mod;
    }).catch((err) => {
      console.error(err);
      section.innerHTML = '';
      const box = document.createElement('div');
      box.className = 'tab-error';
      box.textContent = `This section did not load: ${err.message}`;
      section.append(box);
      return {};
    });
    modules.set(id, p);
  }
  return modules.get(id);
}

async function route() {
  const { id, sub } = parseHash();
  if (current && current !== id) {
    sections.get(current).hidden = true;
    modules.get(current)?.then((m) => m.hide?.());
  }
  const changedTab = current !== id;
  current = id;
  const section = sections.get(id);
  section.hidden = false;
  links.forEach((a) => (a.dataset.tab === id ? a.setAttribute('aria-current', 'page') : a.removeAttribute('aria-current')));
  const n = ids.indexOf(id) + 1;
  document.getElementById('tbSheet').innerHTML = `<b>${n}</b> of ${ids.length} · ${section.dataset.title}`;
  document.title = n === 1 ? 'k0d3ball35' : `${section.dataset.title} · k0d3ball35`;
  if (changedTab) {
    links[n - 1].scrollIntoView({ block: 'nearest', inline: 'nearest' });
    window.scrollTo({ top: 0 });
  }
  const mod = await load(id);
  if (current === id) mod.show?.(sub);
}

// ---------- theme: system -> light -> dark ----------
const THEMES = ['system', 'light', 'dark'];
const themeBtn = document.getElementById('themeBtn');
function readTheme() { try { return localStorage.getItem('k0d3-theme') || 'system'; } catch { return 'system'; } }
function applyTheme(t) {
  if (t === 'system') delete document.documentElement.dataset.theme;
  else document.documentElement.dataset.theme = t;
  themeBtn.textContent = `Theme: ${t}`;
  themeBtn.setAttribute('aria-label', `Colour theme: ${t}. Change`);
  document.dispatchEvent(new CustomEvent('themechange'));
}
themeBtn.addEventListener('click', () => {
  const t = THEMES[(THEMES.indexOf(readTheme()) + 1) % THEMES.length];
  try { localStorage.setItem('k0d3-theme', t); } catch { /* private mode */ }
  applyTheme(t);
});
matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => document.dispatchEvent(new CustomEvent('themechange')));
applyTheme(readTheme());

// ---------- start ----------
document.getElementById('assetBase').textContent = assetBaseLabel();
new ResizeObserver(setChromeHeight).observe(chrome);
setChromeHeight();
try { [site] = await Promise.all([loadData('site'), loadVersions()]); } catch (e) { console.error(e); site = {}; }
if (site.revision) document.getElementById('tbRev').textContent = site.revision;
// the release stamp follows the order ticket: preliminary until the PCBs are ordered
if (site.status?.pcbs_ordered) {
  const stamp = document.getElementById('wipBtn');
  stamp.querySelector('.stamp-stage').textContent = 'Prototype · ';
  stamp.setAttribute('aria-label', 'Status: prototype, untested. What that means');
}
addEventListener('hashchange', route);
route();
