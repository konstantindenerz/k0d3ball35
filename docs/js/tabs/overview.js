// SPDX-License-Identifier: MIT
// Overview tab: what the keyboard is, in a few facts, where it stands in one line, and links to the
// documents in the repository (the licences are in the page footer). The page shows the 3D files; the markdown keeps the details, so this
// sheet does not repeat it. Everything comes from data/site.json.

import { assetUrl, esc, githubUrl } from '../assets.js';

const HERO = 'spec/images/concept-render.png';
// the sheets that show the repository's files (STL, GLB, layer plots, the keymap)
const VIEWS = [['explorer', 'Explorer'], ['case', 'Case'], ['trackball', 'Trackball'], ['pcbs', 'PCBs'], ['keymap', 'Keymap']];

const ext = (path, text) => `<a href="${githubUrl(path)}" target="_blank" rel="noopener">${text}</a>`;

export async function mount(section, ctx) {
  const site = ctx.site;
  const st = site.status;
  const repo = `https://github.com/${site.github}`;

  const facts = site.facts.map((f) => `<dt>${esc(f.label)}</dt><dd>${esc(f.text)}</dd>`).join('');
  const docs = site.docs.map((d) => `
    <li>${ext(d.path, `<b>${esc(d.title)}</b>`)}<span>${esc(d.text)}${d.path === 'spec/03-bom.md' ? ` About ${esc(st.cost.replace(/^about /, ''))} in total.` : ''}</span></li>`).join('');
  const views = VIEWS.map(([id, t]) => `<a href="#${id}">${t}</a>`).join('');
  const status = st.pcbs_ordered
    ? `PCBs ordered, not built yet.`
    : `Design stage: nothing ordered or built yet.`;

  section.innerHTML = `
  <div class="page ov">
    <header class="ov-hero">
      <div class="ov-intro">
        <p class="eyebrow">Revision ${esc(site.revision)}</p>
        <h1 class="display ov-name">${esc(site.name)}</h1>
        <p class="ov-what">A wireless split keyboard with ${site.facts[0].value} low-profile keys and a trackball under the right thumb, designed in the open.</p>
        <p class="ov-status"><span class="ov-dot" aria-hidden="true"></span>${esc(status)} ${ext(site.status.order_ticket, 'Order ticket')} · ${ext('spec/09-roadmap.md', 'Roadmap')}</p>
        <div class="actions"><a class="btn primary" href="#explorer">Open the 3D explorer</a><a class="btn" href="${repo}" target="_blank" rel="noopener">Repository on GitHub</a></div>
        <p class="ov-views">From the repository files: ${views}</p>
      </div>
      <figure class="ov-fig">
        <img src="${assetUrl(HERO)}" alt="Both halves of the keyboard on a desk: light grey keys, orange thumb keys, a white ball in a pocket on the right half" width="1536" height="1024" decoding="async">
        <figcaption>Concept render, not a photo.</figcaption>
      </figure>
    </header>

    <div class="ov-grid">
      <section aria-labelledby="ovFactsH">
        <h2 class="ov-bh" id="ovFactsH">At a glance</h2>
        <dl class="ov-facts">${facts}</dl>
      </section>
      <section aria-labelledby="ovDocsH">
        <h2 class="ov-bh" id="ovDocsH">In the repository</h2>
        <ul class="ov-docs">${docs}</ul>
      </section>
    </div>
  </div>`;
}
