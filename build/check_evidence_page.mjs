/* Drive the built evidence.html and check it behaves, in light and dark.
 *
 *   npm i -D playwright && node build/check_evidence_page.mjs
 *
 * Every check here is a promise the page makes to a student, not a detail of the
 * code: the landing view is the coverage grid, the tree walks and climbs, each of
 * the three ways in returns evidence, a summary renders as markup rather than as
 * markdown source, ticking builds a sheet and an evidence map, Start again really
 * does start again (and can be undone), colour says both what a piece is about and
 * what form it takes, the first-visit tour appears and can be skipped, there is no
 * in-page composer (evidence arrives through the Drive inbox), and nothing scrolls
 * sideways on a phone.
 */
import { chromium } from 'playwright';
import { pathToFileURL } from 'node:url';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const FILE = pathToFileURL(resolve(process.argv[2] || resolve(HERE, '..', 'evidence.html'))).href;
const POINTS = Number(process.argv[3] || 147);

const fails = [];
const ok = (c, m) => { if (!c) fails.push(m); };
const browser = await chromium.launch({ executablePath: process.env.PW_CHROMIUM });

for (const scheme of ['light', 'dark']) {
  const ctx = await browser.newContext({ colorScheme: scheme, viewport: { width: 1280, height: 900 } });
  /* The tour is a first-visit thing and would sit over everything else; it gets a
     context of its own at the end. */
  await ctx.addInitScript(() => {
    try { localStorage.setItem('hsc-ls-ev-tour', '1'); } catch (e) {}
  });
  const page = await ctx.newPage();
  const errs = [];
  page.on('pageerror', e => errs.push(scheme + ': ' + e.message));
  page.on('console', m => {
    // the only network request the page makes is the webfont, and it is allowed to fail
    if (m.type() === 'error' && !/fonts\.googleapis|ERR_/.test(m.text()))
      errs.push(scheme + ' console: ' + m.text());
  });
  await page.goto(FILE, { waitUntil: 'load' });

  ok(errs.length === 0, 'page errors in ' + scheme + ': ' + errs.join(' | '));
  ok(await page.locator('#cov').isVisible(), scheme + ': coverage grid missing on landing');
  ok((await page.locator('#list .ev').count()) === 0, scheme + ': results shown on landing');
  ok((await page.locator('#rhead').isVisible()) === false, scheme + ': results header shown on landing');
  const cells = await page.locator('.cell[data-act="point"]').count();
  ok(cells === POINTS, scheme + ': ' + cells + ' coverage cells, expected ' + POINTS);

  await page.locator('button.row[data-id="crime"]').click();
  await page.locator('button.row[data-id="crime.4"]').click();
  await page.locator('button.row[data-id="crime.4.8"]').click();
  ok((await page.locator('#list .ev').count()) > 0, scheme + ': no evidence for crime.4.8');
  ok(/post-sentencing/i.test(await page.locator('#rtitle').textContent()), scheme + ': wrong results title');
  await page.locator('.trail button[data-act="topic"]').click();
  ok((await page.locator('button.row[data-id="crime.1"]').count()) === 1, scheme + ': the trail did not climb');

  await page.locator('#tab-themes').click();
  await page.locator('button.row[data-id="crime.t.discretion"]').click();
  ok((await page.locator('#list .ev').count()) > 0, scheme + ': no evidence for the discretion theme');
  await page.locator('#tab-kinds').click();
  await page.locator('button.row[data-id="enforceability"]').click();
  ok((await page.locator('#list .ev').count()) > 0, scheme + ': no evidence for enforceability');

  await page.locator('#q').fill('coercive control');
  ok((await page.locator('#list .ev').count()) > 0, scheme + ': search returned nothing');
  await page.locator('#homeBtn').click();
  ok(await page.locator('#cov').isVisible(), scheme + ': home did not return to the landing view');

  await page.locator('.cell[data-act="point"][data-id="fam.2.4"]').click();
  await page.locator('.ev-more').first().click();
  const open = page.locator('.ev-full.open').first();
  ok(await open.isVisible(), scheme + ': the summary did not open');
  ok((await open.locator('h3, p, table, ul').count()) > 0, scheme + ': the summary rendered no markup');

  await page.locator('.ev-tick').first().click();
  await page.locator('.ev-tick').nth(1).click();
  ok(await page.locator('#selbar').isVisible(), scheme + ': the selection bar did not appear');
  ok((await page.locator('#selN').textContent()) === '2', scheme + ': selection count wrong');
  ok((await page.locator('#sheet .sheet-i').count()) === 2, scheme + ': the sheet did not build');

  /* --------------------------------------------------- colour says two things */
  const edge = await page.locator('#list .ev').first().evaluate(
    el => getComputedStyle(el).getPropertyValue('--edge').trim());
  ok(edge.length > 0, scheme + ': a card carries no topic colour on its edge');
  ok((await page.locator('#list .ev-topics i').count()) > 0,
     scheme + ': cards do not name the topic they belong to');
  ok(await page.locator('#cardkey').isVisible(), scheme + ': the colour key is missing from results');
  const labels = await page.locator('#list .ev').first().locator('.chiplab').allTextContents();
  ok(labels.length >= 2 && labels[0] === 'About',
     scheme + ': a card does not label what its tags claim (' + labels.join('/') + ')');
  ok(labels.every(l => ['About', 'Also useful for', 'Themes and challenges',
                        'Effectiveness criteria'].indexOf(l) >= 0),
     scheme + ': an unexpected tag-row label: ' + labels.join('/'));

  /* ------------------------------------------------------- the evidence map */
  ok((await page.locator('#map .map-pt').count()) > 0, scheme + ': the evidence map has no dot points');
  ok((await page.locator('#map .map-pt .map-type').count()) > 0,
     scheme + ': the map does not group by form of evidence');
  const mt = await page.evaluate(() => mapText());
  ok(/^EVIDENCE MAP/.test(mt) && mt.split('\n').length > 6, scheme + ': the copyable map is empty');

  /* ----------------------------------------- start again, and undoing it */
  await page.locator('#courseswitch button[data-course="hsc"]').click();
  await page.locator('#q').fill('coercive');
  await page.waitForTimeout(120);
  await page.locator('#startBtn').click();
  await page.waitForTimeout(150);
  ok(await page.locator('#cov').isVisible(), scheme + ': Start again did not return to the landing view');
  ok((await page.locator('#courseswitch button[aria-checked="true"]').getAttribute('data-course')) === 'all',
     scheme + ': Start again left the course scoped');
  ok((await page.locator('#q').inputValue()) === '', scheme + ': Start again left the search box filled');
  ok((await page.locator('#selbar').isVisible()) === false, scheme + ': ticked evidence survived Start again');
  await page.locator('#toastUndo').click();
  await page.waitForTimeout(120);
  ok((await page.locator('#selN').textContent()) === '2', scheme + ': Undo did not bring the ticked evidence back');

  ok((await page.locator('#addBtn, #compose').count()) === 0,
     scheme + ': the retired Add evidence composer is back on the page');

  /* ---------------------------------------------- the documents behind a point */
  await page.locator('#homeBtn').click();
  await page.locator('.cell[data-act="point"][data-id="shel.3.1"]').click();
  await page.waitForTimeout(120);
  const libN = await page.locator('#libwrap .libf').count();
  ok(libN > 0, scheme + ': no library files under shel.3.1');
  /* A document opens from Drive when the id map has it and from the local folder
     when it does not, so either form is valid — which one shows depends on
     whether data/drive-links.json existed at build time. */
  const href = await page.locator('#libwrap .libf').first().getAttribute('href');
  ok(href.startsWith('file:///') || href.startsWith('https://drive.google.com/file/d/'),
     scheme + ': a library link is neither a local file nor a Drive link: ' + href);

  /* ------------------------------------------------------ the course switch */
  await page.locator('#homeBtn').click();
  await page.locator('#q').fill('');
  await page.waitForTimeout(120);
  ok((await page.locator('.covband').count()) === 2, scheme + ': expected a band per course on "Both"');
  const allRecords = Number(await page.locator('#m-records').textContent());

  await page.locator('#courseswitch button[data-course="preliminary"]').click();
  await page.waitForTimeout(150);
  const prelimCells = await page.locator('.cell[data-act="point"]').count();
  ok(prelimCells === 55, scheme + ': Preliminary shows ' + prelimCells + ' cells, expected 55');
  ok((await page.locator('.covband').count()) === 0, scheme + ': bands should go when scoped');
  ok(await page.locator('#covnote').isVisible(), scheme + ': the scope note is missing');
  ok(Number(await page.locator('#m-records').textContent()) < allRecords,
     scheme + ': the record count did not shrink when scoped');
  ok((await page.locator('.row[data-id="crime"]').count()) === 0, scheme + ': an HSC topic is still in the tree');
  ok((await page.locator('.row[data-id="legalsystem"]').count()) === 1, scheme + ': a Preliminary topic is missing');

  /* cross-course evidence stays, and says which course it is really about */
  await page.locator('.cell[data-act="point"][data-id="ls.2.7"]').click();
  await page.waitForTimeout(120);
  ok((await page.locator('#list .ev').count()) > 0, scheme + ': no evidence at ls.2.7 in Preliminary');
  ok((await page.locator('#list .chip.xcourse').count()) > 0, scheme + ': no cross-course mark');
  ok(/HSC evidence/.test(await page.locator('#list .chip.xcourse').first().textContent()),
     scheme + ': the cross-course mark names the wrong course');

  /* leaving a course drops a selection that belongs to it */
  await page.locator('#courseswitch button[data-course="hsc"]').click();
  await page.waitForTimeout(150);
  ok(await page.locator('#cov').isVisible(), scheme + ': did not fall back to the grid');
  const hscCells = await page.locator('.cell[data-act="point"]').count();
  ok(hscCells === 92, scheme + ': HSC shows ' + hscCells + ' cells, expected 92');
  await page.locator('#courseswitch button[data-course="all"]').click();
  await page.waitForTimeout(120);
  ok((await page.locator('.cell[data-act="point"]').count()) === 147, scheme + ': "Both" is not 147 cells');

  await page.setViewportSize({ width: 390, height: 844 });
  await page.waitForTimeout(150);
  const over = await page.evaluate(() =>
    document.documentElement.scrollWidth - document.documentElement.clientWidth);
  ok(over === 0, scheme + ': ' + over + 'px of horizontal scroll at 390px');
  ok((await page.evaluate(() => getComputedStyle(document.body).backgroundColor)) !== 'rgba(0, 0, 0, 0)',
     scheme + ': body has no background');

  await ctx.close();
}

/* --------------------------------------------------- the first-visit tour -- */
{
  const ctx = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  const page = await ctx.newPage();
  await page.goto(FILE, { waitUntil: 'load' });
  await page.waitForTimeout(1100);
  ok(await page.locator('#tour').isVisible(), 'the tour did not appear on a first visit');
  ok((await page.locator('#tourTitle').textContent()).length > 0, 'the tour has no first step');
  await page.locator('#tourNext').click();
  ok(/2 of/.test(await page.locator('#tourN').textContent()), 'the tour did not advance');
  await page.locator('#tourSkip').click();
  ok((await page.locator('#tour').isVisible()) === false, 'the tour could not be skipped');
  await page.reload({ waitUntil: 'load' });
  await page.waitForTimeout(1100);
  ok((await page.locator('#tour').isVisible()) === false, 'the tour came back after being skipped');
  await ctx.close();
}
await browser.close();
if (fails.length) { console.log('FAILED:'); fails.forEach(f => console.log('  ' + f)); process.exit(1); }
console.log('all page checks passed');
