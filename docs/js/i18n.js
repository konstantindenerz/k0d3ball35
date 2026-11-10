// SPDX-License-Identifier: MIT
// Page language: English is the source, Japanese, Simplified Chinese and Russian are catalogs in docs/i18n/.
//
// The English text is the key (gettext style): the code keeps `t('Download {name}', { name })`
// readable, a catalog maps that exact text to its translation, and a text the catalog lacks stays
// English. Data texts (part names, captions, ...) go through t() too, so they translate by exact match.
// tests/test_site.py fails when a catalog misses a key or keeps one nobody uses
// (`python docs/build.py --i18n` lists both).
//
// The language is picked once per page load: ?lang=, then the saved choice, then the browser
// languages, then English. Switching reloads the page: every tab builds its DOM once.

export const LANGS = ['en', 'ja', 'zh-CN', 'ru'];
/** short code in the title block button, full name in the menu */
export const LANG_LABELS = {
  en: ['EN', 'English'],
  ja: ['JA', '日本語'],
  'zh-CN': ['ZH', '简体中文'],
  ru: ['RU', 'Русский'],
};
const KEY = 'k0d3-lang';

function normalise(code) {
  const c = String(code || '').toLowerCase();
  if (c.startsWith('ja')) return 'ja';
  if (c.startsWith('zh')) return 'zh-CN';
  if (c.startsWith('ru')) return 'ru';
  if (c.startsWith('en')) return 'en';
  return null;
}

function pick() {
  const param = normalise(new URLSearchParams(location.search).get('lang'));
  if (param) return param;
  try { const saved = normalise(localStorage.getItem(KEY)); if (saved) return saved; } catch { /* private mode */ }
  for (const l of navigator.languages || [navigator.language]) {
    const n = normalise(l);
    if (n) return n;
  }
  return 'en';
}

export const lang = pick();
let catalog = {};

/** Fetch docs/i18n/<lang>.json (content-hashed like the data files). English needs none. */
export async function loadCatalog() {
  document.documentElement.lang = lang;
  if (lang === 'en') return;
  let v = '';
  try { v = JSON.parse(document.getElementById('dataVersions')?.textContent || '{}')[`i18n/${lang}`] || ''; } catch { /* unstamped */ }
  try {
    const r = await fetch(new URL(`i18n/${lang}.json${v ? `?v=${v}` : ''}`, document.baseURI).href);
    if (!r.ok) throw new Error(`i18n/${lang}.json: HTTP ${r.status}`);
    catalog = await r.json();
  } catch (e) {
    console.warn(e);   // the page stays English
  }
}

/** The text in the page language; {name} placeholders filled from params (inserted as given). */
export function t(text, params) {
  const s = catalog[text] ?? text;
  return params ? s.replace(/\{(\w+)\}/g, (m, k) => (k in params ? String(params[k]) : m)) : s;
}

/** Save the choice, keep it in the address (?lang= beats the saved one) and reload. */
export function setLang(l) {
  try { localStorage.setItem(KEY, l); } catch { /* private mode */ }
  const url = new URL(location.href);
  if (l === 'en') url.searchParams.delete('lang'); else url.searchParams.set('lang', l);
  if (url.href === location.href) location.reload(); else location.href = url.href;
}

/** Translate the static shell: data-i18n (text), data-i18n-aria / data-i18n-title / data-i18n-content (attributes).
 *  The English stays in index.html, so the key is the element's own text. */
export function translateStatic(root = document) {
  if (lang === 'en') return;
  root.querySelectorAll('[data-i18n]').forEach((el) => {
    el.dataset.i18n ||= el.textContent.trim();
    el.textContent = t(el.dataset.i18n);
  });
  for (const attr of ['aria-label', 'title', 'content']) {
    const ds = `i18n${attr === 'aria-label' ? 'Aria' : attr[0].toUpperCase() + attr.slice(1)}`;
    root.querySelectorAll(`[data-i18n-${attr === 'aria-label' ? 'aria' : attr}]`).forEach((el) => {
      el.dataset[ds] ||= el.getAttribute(attr) || '';
      el.setAttribute(attr, t(el.dataset[ds]));
    });
  }
}
