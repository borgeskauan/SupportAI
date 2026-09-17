// Run against `python -m backend.demo` and the English `npm start` frontend.
// Requires Playwright + Chromium and sharp; see docs/developer-reference.md.
const { chromium } = require('playwright');
const sharp = require('sharp');
const assert = require('node:assert/strict');
const path = require('node:path');
const root = path.resolve(__dirname, '..');

(async () => {
  const browser = await chromium.launch({
    headless: true,
    ...(process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE ? {executablePath: process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE} : {}),
  });
  try {
    const context = await browser.newContext({viewport: {width: 1200, height: 1200}, deviceScaleFactor: 2, locale: 'en-US'});
    const page = await context.newPage();
    const errors = [];
    page.on('pageerror', e => errors.push(e.message));
    page.on('response', r => { if (r.status() >= 400) errors.push(`${r.status()} ${r.url()}`); });
    const get = async endpoint => {
      const response = await context.request.get(`http://127.0.0.1:8000${endpoint}`);
      assert(response.ok(), endpoint);
      return response.json();
    };
    assert.equal((await get('/health')).records_loaded, 6);
    const records = (await get('/records')).records;
    assert.equal(new Set(records.map(r => r.case_summary)).size, 6);
    const clusters = await get('/clusters');
    assert.equal(clusters.total, 1);
    assert.deepEqual([...clusters.clusters[0].supporting_case_ids].sort(), ['receipt_01', 'receipt_02', 'receipt_03']);

    await page.goto('http://localhost:4200');
    const response = page.waitForResponse(r => r.url().endsWith('/faqs/generate') && r.request().method() === 'POST');
    await page.getByRole('button', {name: 'Generate / Regenerate FAQs', exact: true}).click();
    const generated = await (await response).json();
    assert.equal(generated.total, 1);
    assert.deepEqual(generated.failures, []);
    const faq = generated.faqs[0];
    assert.equal(faq.faq.title, 'My payment went through. Where is my receipt?');
    assert(faq.confidence_score > 0.90 && faq.confidence_score < 0.99);
    await page.getByRole('link', {name: faq.faq.title}).click();
    await page.getByRole('heading', {name: faq.faq.title, exact: true}).waitFor();
    for (const record of records.slice(0, 3)) await page.getByText(record.case_summary, {exact: true}).waitFor();
    assert.equal(await page.locator('.evidence-card').count(), 3);
    assert(await page.getByRole('button', {name: 'Approve', exact: true}).isVisible());
    assert(await page.getByRole('button', {name: 'Reject', exact: true}).isVisible());
    await page.getByText('A missing receipt alone is not a reason to repeat a confirmed payment.', {exact: true}).waitFor();
    await page.evaluate(() => document.fonts.ready);
    const shell = await page.locator('.main-shell').boundingBox();
    const content = await page.locator('.canvas').boundingBox();
    const faqImage = await page.screenshot({clip: {x: shell.x, y: 0, width: shell.width, height: Math.ceil(content.y + content.height)}});

    const matrix = await get('/similarity-matrix');
    assert.equal(matrix.record_ids.length, 6);
    await page.setViewportSize({width: 1040, height: 980});
    await page.goto(`file://${path.join(root, 'backend/similarity_matrix_viewer.html')}`);
    await page.locator('#matrixFile').setInputFiles({name: 'demo-matrix.json', mimeType: 'application/json', buffer: Buffer.from(JSON.stringify(matrix))});
    await page.locator('#recordsFile').setInputFiles({name: 'demo-records.json', mimeType: 'application/json', buffer: Buffer.from(JSON.stringify(records))});
    await page.getByText('Records: 6', {exact: true}).waitFor();
    await page.locator('#cellSize').fill('48');
    assert.equal(await page.getByText('Data and display settings', {exact: true}).count(), 1);
    await page.getByText('Data and display settings', {exact: true}).click();
    const geometry = await page.evaluate(() => {
      const box = selector => document.querySelector(selector).getBoundingClientRect().toJSON();
      const labels = selector => Array.from(document.querySelectorAll(selector), element => {
        const range = document.createRange();
        range.selectNodeContents(element);
        return range.getBoundingClientRect().toJSON();
      });
      return {canvas: box('#matrixCanvas'), rows: labels('#axisLeft > div'), columns: labels('#axisTop > div'), wrap: box('#viewerWrap')};
    });
    for (const [index, row] of geometry.rows.entries()) {
      assert(Math.abs(row.y + row.height / 2 - geometry.canvas.y - (index + 0.5) * 48) < 2, 'Row labels must align with heatmap rows');
      assert(row.x >= geometry.wrap.x, 'Row labels must not clip at the left edge');
    }
    for (const column of geometry.columns) {
      assert(column.y >= geometry.wrap.y, 'Column labels must not clip above the viewer');
      assert(column.y + column.height <= geometry.canvas.y, 'Column labels must fit above the matrix');
      assert(column.x + column.width <= geometry.wrap.x + geometry.wrap.width, 'Column labels must not clip at the right edge');
    }
    assert(geometry.canvas.y + geometry.canvas.height <= geometry.wrap.y + geometry.wrap.height, 'Entire matrix must be visible');
    await page.locator('#matrixCanvas').click({position: {x: 72, y: 24}});
    await page.mouse.move(0, 0);
    assert.equal(await page.locator('#details .record-id').nth(0).innerText(), 'receipt_01');
    assert.equal(await page.locator('#details .record-id').nth(1).innerText(), 'receipt_02');
    const details = await page.locator('#details').evaluate(e => ({height: e.clientHeight, content: e.scrollHeight}));
    assert(details.content <= details.height, 'Both selected records must fit without clipping');
    const matrixImage = await page.screenshot({fullPage: true});
    assert.deepEqual(errors, []);
    // Only replace tracked assets once all UI and layout checks have passed.
    for (const [buffer, name] of [[faqImage, 'faq-detail.png'], [matrixImage, 'similarity-matrix.png']]) {
      const output = path.join(root, 'docs/images', name);
      const info = await sharp(buffer).png({compressionLevel: 9, effort: 10}).toFile(output);
      console.log(name, info.width, info.height, info.size, 'bytes');
    }
    console.log('Verified: six distinct cases, one receipt family, grounded FAQ, review controls, matrix comparison, no browser errors.');
    console.log('Synthetic cluster similarity:', faq.confidence_score);
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
