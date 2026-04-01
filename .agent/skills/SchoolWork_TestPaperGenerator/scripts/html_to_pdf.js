#!/usr/bin/env node
/**
 * HTML to PDF Converter
 * Usage: node html_to_pdf.js <input.html> [output.pdf]
 *
 * Requires: npm install puppeteer (one-time setup in this directory)
 */

const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

async function htmlToPdf(inputHtml, outputPdf) {
    const htmlPath = path.resolve(inputHtml);
    const pdfPath = outputPdf
        ? path.resolve(outputPdf)
        : htmlPath.replace(/\.html$/i, '.pdf');

    if (!fs.existsSync(htmlPath)) {
        console.error(`Error: File not found: ${htmlPath}`);
        process.exit(1);
    }

    console.log(`Converting: ${path.basename(htmlPath)}`);

    const browser = await puppeteer.launch({
        headless: 'new',
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    const page = await browser.newPage();

    await page.goto(`file://${htmlPath}`, { waitUntil: 'networkidle0' });

    await page.pdf({
        path: pdfPath,
        format: 'A4',
        printBackground: true,
        margin: { top: '0', right: '0', bottom: '0', left: '0' }
    });

    await browser.close();
    console.log(`PDF created: ${pdfPath}`);
}

const args = process.argv.slice(2);
if (args.length === 0) {
    console.log('Usage: node html_to_pdf.js <input.html> [output.pdf]');
    process.exit(1);
}

htmlToPdf(args[0], args[1]).catch(err => {
    console.error('Error:', err.message);
    process.exit(1);
});
