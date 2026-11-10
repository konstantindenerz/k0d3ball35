// SPDX-License-Identifier: MIT
// Overview tab: the landing sheet. What the keyboard is, its facts as a drawing's spec block
// (from site.json, generated from the layout, stack, shield and spec files), where the project
// stands (status.json), an index of the other sheets and the licences.

import { assetUrl, esc, githubUrl, loadData } from '../assets.js';

const HERO = 'spec/images/concept-render.png';

// what each sheet shows; counts are filled in from the data files
const SHEETS = {
  explorer: () => `Both halves in 3D, exploded layer by layer: case, PCB, controller, battery bay, cradle and ball. Section through the ball pocket.`,
  case: () => 'The printed parts as they come out of OpenSCAD: tray, controller cap and the hinged lid that folds under as a tenting foot.',
  trackball: (d) => `The cradle for the ${d.ball} mm ball on three ceramic bearings, the sensor board below it and the stack heights.`,
  pcbs: () => 'Left, right and sensor board in 3D and as copper, silkscreen and outline layers.',
  keymap: (d) => `The ZMK keymap on the real key positions: ${d.layers} layers, ${d.combos} combos, the automatic mouse layer.`,
  build: (d) => `${d.bomRows} lines of parts with sources and prices, the ${d.steps} checks before ordering, ${d.tickets} open tickets.`,
};

const fact = (site, id) => (site.facts || []).find((f) => f.id === id) || {};

export async function mount(section, ctx) {
  const site = ctx.site?.facts ? ctx.site : await loadData('site');
  const [status, keymap, bom] = await Promise.all([loadData('status'), loadData('keymap'), loadData('bom')]);
  const keys = fact(site, 'keys');
  const ball = fact(site, 'ball');
  const bo = status.before_ordering;
  const done = bo.steps.filter((s) => s.state === 'done').length;
  const partly = bo.steps.filter((s) => s.state === 'partly').length;
  const pcb = status.order.pcb_ticket;
  const openTickets = Object.values(status.tickets).reduce((a, g) => a + g.length, 0);
  const counts = {
    ball: ball.value, layers: keymap.layers.length, combos: keymap.combos.length, steps: bo.steps.length, tickets: openTickets,
    bomRows: bom.sections.reduce((a, s) => a + s.blocks.reduce((b, x) => b + (x.table ? x.table.rows.length : 0), 0), 0),
  };

  const specRows = (site.facts || []).map((f, i) => `
    <tr><td class="ov-n">${i + 1}</td><th scope="row">${esc(f.label)}</th><td>${esc(f.text)}</td>
      <td class="ov-src"><a href="${githubUrl(f.source)}" target="_blank" rel="noopener" title="${esc(f.source)}">${esc(f.source.split('/').pop())}</a></td></tr>`).join('');

  const sheetRows = site.tabs.filter((t) => t.id !== 'overview').map((t) => {
    const n = site.tabs.findIndex((x) => x.id === t.id) + 1;
    return `<a class="ov-sheet" href="#${esc(t.id)}">
      <span class="ov-sheet-n">${n}</span>
      <span class="ov-sheet-t">${esc(t.title)}</span>
      <span class="ov-sheet-d">${esc((SHEETS[t.id] || (() => ''))(counts))}</span>
      <span class="ov-sheet-go" aria-hidden="true">→</span></a>`;
  }).join('');

  const ordered = pcb.status === 'done';
  const statusLines = [
    `Revision <b>${esc(site.revision)}</b>: work in progress, the geometry still changes between revisions.`,
    ordered
      ? `The first PCBs are ordered (<a href="${githubUrl(pcb.path)}" target="_blank" rel="noopener">${esc(pcb.slug)}</a>).`
      : `<b>Not ordered yet.</b> No PCB has been fabricated; the order is ticket <a href="${githubUrl(pcb.path)}" target="_blank" rel="noopener">${esc(pcb.slug)}</a>, status ${esc(pcb.status)}.`,
    `Checks before ordering: ${done} of ${bo.steps.length} done${partly ? `, ${partly} partly done` : ''}. <a href="#build/before">See them</a>.`,
    `Parts: ${status.order.done} of ${status.order.total} lines of the order checklist bought.`,
    `${openTickets} tickets open or in progress, ${status.ticket_counts.P0 || 0} of them blockers. <a href="#build/tickets">List</a>.`,
  ];

  const lic = (site.licences || []).map((l) => `<li><b>${esc(l.id)}</b> for ${esc(l.scope)} <a href="${githubUrl(l.path)}" target="_blank" rel="noopener">${esc(l.path)}</a></li>`).join('');
  const repo = `https://github.com/${site.github}`;

  section.innerHTML = `
  <div class="page ov">
    <header class="ov-hero">
      <div class="ov-intro">
        <p class="eyebrow">Sheet 1 · Overview · ${esc(site.revision)}</p>
        <h1 class="display ov-name">${esc(site.name)}</h1>
        <p class="ov-what">A wireless split keyboard with ${keys.value} low-profile keys and a ${ball.value} mm trackball beside the right thumb, designed in the open.</p>
        <p class="ov-more">Two halves talk over Bluetooth, each with its own controller and battery. The column stagger and thumb arc follow the Keyball39, scaled to Choc spacing. Everything is generated from one layout file, and this page shows those files.</p>
        <div class="actions"><a class="btn primary" href="#explorer">Open the 3D explorer</a><a class="btn" href="${repo}" target="_blank" rel="noopener">Repository on GitHub</a></div>
      </div>
      <figure class="ov-fig">
        <img src="${assetUrl(HERO)}" alt="Both halves of the keyboard on a desk: light grey keys, orange thumb keys, a white ball in a pocket on the right half" width="1536" height="1024" decoding="async">
        <figcaption><span>Fig. 1</span> Concept render, not a photo: nothing has been built yet. <a href="${githubUrl('spec/images/PROMPTS.md')}" target="_blank" rel="noopener">Prompt</a></figcaption>
      </figure>
    </header>

    <div class="ov-grid">
      <section class="ov-block ov-spec" aria-labelledby="ovSpecH">
        <h2 class="ov-bh" id="ovSpecH">Specification</h2>
        <div class="table-wrap"><table class="data ov-table">
          <thead><tr><th scope="col">#</th><th scope="col">Item</th><th scope="col">Value</th><th scope="col">From</th></tr></thead>
          <tbody>${specRows}</tbody></table></div>
      </section>
      <section class="ov-block ov-status" aria-labelledby="ovStatusH">
        <h2 class="ov-bh" id="ovStatusH">Status</h2>
        <ol class="ov-notes">${statusLines.map((l) => `<li>${l}</li>`).join('')}</ol>
      </section>
    </div>

    <section class="ov-block" aria-labelledby="ovSheetsH">
      <h2 class="ov-bh" id="ovSheetsH">Sheets in this set</h2>
      <nav class="ov-sheets" aria-labelledby="ovSheetsH">${sheetRows}</nav>
    </section>

    <section class="ov-block ov-lic" aria-labelledby="ovLicH">
      <h2 class="ov-bh" id="ovLicH">Licences</h2>
      <ul>${lic}</ul>
      <p>Source, issues and history: <a href="${repo}" target="_blank" rel="noopener">github.com/${esc(site.github)}</a></p>
    </section>
  </div>`;
}
