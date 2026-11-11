// SPDX-License-Identifier: MIT
// Overview tab: what the keyboard is, in a few facts, where it stands in one line, and links to the
// documents in the repository (the licences are in the page footer). The page shows the 3D files; the markdown keeps the details, so this
// sheet does not repeat it. Everything comes from data/site.json.

import { assetUrl, esc, githubUrl } from '../assets.js';
import { t } from '../i18n.js';

const HERO = 'spec/images/concept-render.png';
// the sheets that show the repository's files (STL, GLB, layer plots, the keymap)
const VIEWS = [['explorer', 'Explorer'], ['case', 'Case'], ['trackball', 'Trackball'], ['pcbs', 'PCBs'], ['keymap', 'Keymap']];

const ext = (path, text) => `<a href="${githubUrl(path)}" target="_blank" rel="noopener">${text}</a>`;

export async function mount(section, ctx) {
  const site = ctx.site;
  const st = site.status;
  const repo = `https://github.com/${site.github}`;

  const facts = site.facts.map((f) => `<dt>${esc(t(f.label))}</dt><dd>${esc(f.tpl ? t(f.tpl, f.params) : t(f.text))}</dd>`).join('');
  const docs = site.docs.map((d) => `
    <li>${ext(d.path, `<b>${esc(t(d.title))}</b>`)}<span>${esc(t(d.text))}${d.path === 'spec/03-bom.md' ? ` ${esc(t('About {cost} in total.', { cost: st.cost.replace(/^about /, '') }))}` : ''}</span></li>`).join('');
  const views = VIEWS.map(([id, title]) => `<a href="#${id}">${t(title)}</a>`).join('');
  const status = st.pcbs_ordered
    ? t('PCBs ordered, not built yet.')
    : t('Design stage: nothing ordered or built yet.');

  section.innerHTML = `
  <div class="page ov">
    <header class="ov-hero">
      <div class="ov-intro">
        <p class="eyebrow">${esc(t('Revision {rev}', { rev: site.revision }))}</p>
        <h1 class="display ov-name">${esc(site.name)}</h1>
        <p class="ov-alias">${esc(t('Read: {alias}', { alias: site.alias }))}</p>
        <p class="ov-what">${esc(t('A wireless split keyboard with {n} low-profile keys and a trackball under the right thumb, designed in the open.', { n: site.facts[0].value }))}</p>
        <p class="ov-status"><span class="ov-dot" aria-hidden="true"></span>${esc(status)} ${ext(site.status.order_ticket, t('Order ticket'))} · ${ext('spec/09-roadmap.md', t('Roadmap'))}</p>
        <div class="actions"><a class="btn primary" href="#explorer">${t('Open the 3D explorer')}</a><a class="btn" href="${repo}" target="_blank" rel="noopener">${t('Repository on GitHub')}</a></div>
        <p class="ov-views">${t('From the repository files:')} ${views}</p>
      </div>
      <figure class="ov-fig">
        <img src="${assetUrl(HERO)}" alt="${esc(t('Both halves of the keyboard on a desk: light grey keys, orange thumb keys, a white ball in a pocket on the right half'))}" width="1536" height="1024" decoding="async">
        <figcaption>${t('Concept render, not a photo.')}</figcaption>
      </figure>
    </header>

    <div class="ov-grid">
      <section aria-labelledby="ovFactsH">
        <h2 class="ov-bh" id="ovFactsH">${t('At a glance')}</h2>
        <dl class="ov-facts">${facts}</dl>
      </section>
      <section aria-labelledby="ovDocsH">
        <h2 class="ov-bh" id="ovDocsH">${t('In the repository')}</h2>
        <ul class="ov-docs">${docs}</ul>
      </section>
    </div>
  </div>`;
}
