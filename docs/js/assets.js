// SPDX-License-Identifier: MIT
// Where the page finds its files.
//
// The published page (GitHub Pages serves only docs/) loads the real repository files - STL, GLB,
// SVG, PNG - from raw.githubusercontent.com, so there are no copies to go stale. Served from
// localhost (`make site-serve`, repo root as document root) the same repo paths resolve against the
// working tree, which previews a branch before it is merged.
//   ?ref=<branch>  load the files of that branch from GitHub instead of main
//   ?remote        on localhost, load from GitHub anyway (how the published page behaves)

export const REPO = 'konstantindenerz/k0d3ball35';
const params = new URLSearchParams(location.search);
const LOCAL_HOSTS = ['localhost', '127.0.0.1', '[::1]', ''];
export const isLocal = LOCAL_HOSTS.includes(location.hostname) && !params.has('remote') && !params.has('ref');
export const ref = params.get('ref') || 'main';

/** URL of a file given by its path from the repository root, e.g. "hardware/case/stl/tray-right.stl". */
export function assetUrl(repoPath) {
  const p = repoPath.replace(/^\/+/, '');
  if (isLocal) return new URL(`../${p}`, document.baseURI).href;
  return `https://raw.githubusercontent.com/${REPO}/${encodeURIComponent(ref).replace(/%2F/g, '/')}/${p}`;
}

/** The file's page on GitHub (GitHub renders STL, SVG, PNG and markdown there). */
export const githubUrl = (repoPath) => `https://github.com/${REPO}/blob/${ref}/${repoPath.replace(/^\/+/, '')}`;
export const githubTreeUrl = (repoPath) => `https://github.com/${REPO}/tree/${ref}/${repoPath.replace(/^\/+/, '')}`;

export const assetBaseLabel = () => (isLocal ? 'the working tree (localhost)' : `github.com/${REPO} @ ${ref}`);

export class AssetError extends Error {
  constructor(repoPath, status) {
    super(status === 404
      ? `${repoPath} is not on ${isLocal ? 'disk' : ref} yet. It appears here once the branch that adds it is merged.`
      : `${repoPath} did not load (HTTP ${status}). Reload the page to try again.`);
    this.status = status;
    this.repoPath = repoPath;
  }
}

/** Fetch a repo file as an ArrayBuffer, reporting progress as a fraction 0..1 (or null when the size is unknown). */
export async function fetchBuffer(repoPath, onProgress = () => {}, signal) {
  const res = await fetch(assetUrl(repoPath), { signal });
  if (!res.ok) throw new AssetError(repoPath, res.status);
  const total = Number(res.headers.get('content-length')) || 0;
  if (!res.body || !total) {
    onProgress(null);
    return res.arrayBuffer();
  }
  const reader = res.body.getReader();
  const chunks = [];
  let got = 0;
  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    chunks.push(value);
    got += value.length;
    onProgress(Math.min(1, got / total));
  }
  const out = new Uint8Array(got);
  let o = 0;
  for (const c of chunks) { out.set(c, o); o += c.length; }
  return out.buffer;
}

export async function fetchText(repoPath) {
  const res = await fetch(assetUrl(repoPath));
  if (!res.ok) throw new AssetError(repoPath, res.status);
  return res.text();
}

/** Save a repo file under its own name. A plain <a download> is ignored for cross-origin URLs,
 *  so the file is fetched and handed over as an object URL. Falls back to opening the raw URL. */
export async function downloadFile(repoPath) {
  const name = repoPath.split('/').pop();
  try {
    const buf = await fetchBuffer(repoPath);
    const url = URL.createObjectURL(new Blob([buf]));
    const a = Object.assign(document.createElement('a'), { href: url, download: name });
    document.body.append(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 10_000);
  } catch (e) {
    window.open(assetUrl(repoPath), '_blank', 'noopener');
  }
}

const dataCache = new Map();
/** docs/data/<name>.json, fetched once per page load. */
export function loadData(name) {
  if (!dataCache.has(name)) {
    dataCache.set(name, fetch(new URL(`data/${name}.json`, document.baseURI)).then((r) => {
      if (!r.ok) throw new Error(`data/${name}.json is missing (HTTP ${r.status}); run \`make site\`.`);
      return r.json();
    }));
  }
  return dataCache.get(name);
}

export const fmt = (v, digits = 1) => (v == null || Number.isNaN(v) ? '-' : Number(v).toFixed(digits));
export const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
