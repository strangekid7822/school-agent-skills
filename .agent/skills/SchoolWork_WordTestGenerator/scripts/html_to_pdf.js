#!/usr/bin/env node
/**
 * HTML to PDF Converter
 * Usage: node html_to_pdf.js <input.html> [output.pdf]
 * 
 * Requires: npm install puppeteer (one-time setup)
 */

const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

async function htmlToPdf(inputHtml, outputPdf) {
    // Resolve absolute paths
    const htmlPath = path.resolve(inputHtml);
    const pdfPath = outputPdf 
        ? path.resolve(outputPdf) 
        : htmlPath.replace(/\.html$/i, '.pdf');
    
    // Check input exists
    if (!fs.existsSync(htmlPath)) {
        console.error(`Error: File not found: ${htmlPath}`);
        process.exit(1);
    }
    
    console.log(`Converting: ${htmlPath}`);
    console.log(`Output: ${pdfPath}`);
    
    const browser = await puppeteer.launch({
        headless: 'new',
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    const page = await browser.newPage();
    
    // Load HTML file
    await page.goto(`file://${htmlPath}`, { waitUntil: 'networkidle0' });
    
    // Generate PDF with A4 settings
    await page.pdf({
        path: pdfPath,
        format: 'A4',
        printBackground: true,
        margin: {
            top: '12mm',
            right: '12mm',
            bottom: '5mm',
            left: '12mm'
        }
    });
    
    await browser.close();
    console.log(`✅ PDF created: ${pdfPath}`);
}

// CLI entry point
const args = process.argv.slice(2);
if (args.length === 0) {
    console.log('Usage: node html_to_pdf.js <input.html> [output.pdf]');
    process.exit(1);
}

htmlToPdf(args[0], args[1]).catch(err => {
    console.error('Error:', err.message);
    process.exit(1);
});
