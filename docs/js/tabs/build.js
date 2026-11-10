// SPDX-License-Identifier: MIT
// Build & BOM tab: the parts list of spec/03-bom.md, the roadmap steps before ordering, the open
// tickets and the guides. Everything comes from data/bom.json and data/status.json.
// Sub route: #build/<parts|before|tickets|guides> scrolls to that section.

import { esc, githubUrl, loadData } from '../assets.js';

const GUIDES = [
  ['spec/04-build-guide.md', 'Build guide', 'Step by step assembly of both halves and the trackball module.'],
  ['spec/12-order-checklist.md', 'Order checklist', 'Shop by shop: what to buy, what is already ordered, the JLCPCB and LCSC lines.'],
  ['spec/05-firmware.md', 'Firmware', 'Building and flashing ZMK, pairing, the layer table, trackball tuning.'],
];
const PRIORITY = { P0: 'blocker', P1: 'must', P2: 'should', P3: 'nice to have' };
const STATE = { done: 'Done', partly: 'Partly done', open: 'Open' };

let root;

function runHtml(cell) {
  return cell.map((r) => {
    if (typeof r === 'string') return esc(r);
    const href = typeof r.href === 'string' ? r.href : githubUrl(r.href.repo);
    return `<a href="${esc(href)}" target="_blank" rel="noopener"${typeof r.href === 'string' ? ` title="${esc(r.href)}"` : ''}>${esc(r.text)}</a>`;
  }).join('');
}
const runText = (cell) => cell.map((r) => (typeof r === 'string' ? r : r.text)).join('');
const NUMERIC = /^(qty|eur|lcsc)$/i;

function tableHtml(t) {
  const numCols = t.header.map((h) => NUMERIC.test(h));
  const head = t.header.map((h) => `<th scope="col">${esc(h)}</th>`).join('');
  const rows = t.rows.map((r) => {
    const total = /^total$/i.test(runText(r[0]).trim());
    return `<tr${total ? ' class="bom-total"' : ''} data-text="${esc(r.map(runText).join(' ').toLowerCase())}">${
      r.map((c, i) => `<td${numCols[i] ? ' class="num"' : ''}>${runHtml(c)}</td>`).join('')}</tr>`;
  }).join('');
  return `<div class="table-wrap"><table class="data bom-table"><thead><tr>${head}</tr></thead><tbody>${rows}</tbody></table></div>`;
}

function partsHtml(bom) {
  const secs = bom.sections.map((s) => {
    const blocks = s.blocks.map((b) => (b.table ? tableHtml(b.table) : `<p class="bom-text">${runHtml(b.text)}</p>`)).join('');
    return `<section class="bom-sec" aria-labelledby="bom-s${s.number}"><h3 id="bom-s${s.number}"><span class="bom-n">${s.number ?? ''}</span>${esc(s.title)}</h3>${blocks}</section>`;
  }).join('');
  const rows = bom.sections.reduce((a, s) => a + s.blocks.reduce((b, x) => b + (x.table ? x.table.rows.length : 0), 0), 0);
  return `
    <div class="bom-intro prose">${bom.intro.map((b) => `<p>${runHtml(b.text)}</p>`).join('')}</div>
    <div class="bom-filter">
      <label for="bomQ">Filter parts</label>
      <input id="bomQ" type="search" placeholder="e.g. FFC, LCSC, M2, keycapsss" autocomplete="off" spellcheck="false">
      <span id="bomCount" aria-live="polite">${rows} rows</span>
    </div>
    <div class="bom-secs">${secs}</div>
    <p class="note">Source: <a href="${githubUrl(bom.source)}" target="_blank" rel="noopener">${esc(bom.source)}</a>. Prices as written there, not checked again by this page.</p>`;
}

function stepsHtml(st) {
  const b = st.before_ordering;
  const items = b.steps.map((s) => `
    <li class="step step-${s.state}">
      <span class="step-box" aria-hidden="true">${s.state === 'done' ? '✓' : s.state === 'partly' ? '◐' : ''}</span>
      <div>
        <p class="step-head"><span class="step-n">${s.number}</span> <span class="step-state">${STATE[s.state]}</span>${s.label && !/^done|^mostly done/i.test(s.label) ? ` <b>${esc(s.label)}</b>` : ''}</p>
        <p class="step-sum">${esc(s.summary)}.</p>
        ${s.open ? `<p class="step-open"><b>Still open:</b> ${esc(s.open)}.</p>` : ''}
        ${s.tickets.length ? `<p class="step-t">${s.tickets.map((t) => `<a href="${githubUrl(t.path)}" target="_blank" rel="noopener">${esc(t.slug)}</a> <small>${esc(t.status)}</small>`).join(' · ')}</p>` : ''}
      </div>
    </li>`).join('');
  const done = b.steps.filter((s) => s.state === 'done').length;
  const o = st.order;
  const orderRows = o.sections.map((s) => `<tr><td>${s.number}. ${esc(s.title)}</td><td class="num">${s.done} of ${s.total}</td></tr>`).join('');
  return `
    <p class="lede">From <a href="${githubUrl(b.source)}" target="_blank" rel="noopener">${esc(b.source)}</a>, “${esc(b.title)}”: ${done} of ${b.steps.length} steps done.</p>
    <ol class="steps">${items}</ol>
    <h3 class="sub">Order checklist, lines ticked</h3>
    <div class="table-wrap order-wrap"><table class="data"><thead><tr><th scope="col">Section of ${esc(o.source.split('/').pop())}</th><th scope="col">Ordered</th></tr></thead>
      <tbody>${orderRows}<tr class="bom-total"><td>All lines</td><td class="num">${o.done} of ${o.total}</td></tr></tbody></table></div>
    <p class="note">The PCB order is ticket <a href="${githubUrl(o.pcb_ticket.path)}" target="_blank" rel="noopener">${esc(o.pcb_ticket.slug)}</a>, status <b>${esc(o.pcb_ticket.status)}</b>.</p>`;
}

function ticketsHtml(st) {
  return Object.entries(st.tickets).filter(([, g]) => g.length).map(([p, g]) => {
    const list = g.map((t) => `<li><a href="${githubUrl(t.path)}" target="_blank" rel="noopener">${esc(t.title)}</a>
      <span class="tk-meta">${esc(t.area)} · ${esc(t.type)}${t.status === 'in-progress' ? ' · <b class="tk-prog">in progress</b>' : ''}</span></li>`).join('');
    const body = `<ul class="tk-list">${list}</ul>`;
    const head = `<span class="tk-p tk-${p}">${p}</span> ${PRIORITY[p] ?? ''} <small>${g.length}</small>`;
    return p === 'P3'
      ? `<details class="tk-group"><summary>${head}</summary>${body}</details>`
      : `<div class="tk-group"><h3>${head}</h3>${body}</div>`;
  }).join('');
}

function guidesHtml() {
  return `<div class="cards">${GUIDES.map(([path, title, text]) => `
    <a class="card guide" href="${githubUrl(path)}" target="_blank" rel="noopener">
      <span class="eyebrow">${esc(path)}</span><b>${esc(title)}</b><span>${esc(text)}</span></a>`).join('')}</div>`;
}

function applyFilter(q) {
  const needle = q.trim().toLowerCase();
  let shown = 0, total = 0;
  root.querySelectorAll('.bom-sec').forEach((sec) => {
    let any = false;
    sec.querySelectorAll('tbody tr').forEach((tr) => {
      total += 1;
      const hit = !needle || tr.dataset.text.includes(needle);
      tr.hidden = !hit;
      if (hit) { shown += 1; any = true; }
    });
    const hasTable = !!sec.querySelector('table');
    sec.hidden = needle ? !any : false;
    sec.querySelectorAll('.bom-text').forEach((p) => { p.hidden = !!needle; });
    if (!hasTable && needle) sec.hidden = true;
    sec.querySelectorAll('.table-wrap').forEach((w) => { w.hidden = needle && !w.querySelector('tbody tr:not([hidden])'); });
  });
  root.querySelector('#bomCount').textContent = needle ? `${shown} of ${total} rows` : `${total} rows`;
}

export async function mount(section) {
  const [bom, st] = await Promise.all([loadData('bom'), loadData('status')]);
  const open = Object.values(st.tickets).reduce((a, g) => a + g.length, 0);
  section.innerHTML = `
  <div class="page bld">
    <p class="eyebrow">Sheet 7 · Build and bill of materials</p>
    <h1 class="display">Build &amp; BOM</h1>
    <p class="lede">What one keyboard needs, what has to be checked before anything is ordered, and what is still open. Taken from the spec and the tickets in the repository.</p>
    <nav class="bld-toc" aria-label="On this sheet">
      <a href="#build/parts">Parts</a><a href="#build/before">Before ordering</a><a href="#build/tickets">Open tickets <small>${open}</small></a><a href="#build/guides">Guides</a>
    </nav>
    <section class="bld-sec" id="bld-parts" aria-labelledby="bldPartsH"><h2 class="bld-h" id="bldPartsH"><span>A</span>Parts</h2>${partsHtml(bom)}</section>
    <section class="bld-sec" id="bld-before" aria-labelledby="bldBeforeH"><h2 class="bld-h" id="bldBeforeH"><span>B</span>Before ordering</h2>${stepsHtml(st)}</section>
    <section class="bld-sec" id="bld-tickets" aria-labelledby="bldTicketsH"><h2 class="bld-h" id="bldTicketsH"><span>C</span>Open tickets</h2>
      <p class="lede">${open} tickets open or in progress in <a href="${githubUrl('issues/README.md')}" target="_blank" rel="noopener">issues/</a>, by priority.</p>
      <div class="tk">${ticketsHtml(st)}</div></section>
    <section class="bld-sec" id="bld-guides" aria-labelledby="bldGuidesH"><h2 class="bld-h" id="bldGuidesH"><span>D</span>Guides</h2>${guidesHtml()}</section>
  </div>`;
  root = section.querySelector('.bld');
  const q = root.querySelector('#bomQ');
  q.addEventListener('input', () => applyFilter(q.value));
}

export function show(sub) {
  if (!root || !sub) return;
  const target = root.querySelector(`#bld-${CSS.escape(sub)}`);
  if (target) {
    const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
    target.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'start' });
  }
}
