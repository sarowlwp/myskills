#!/usr/bin/env node
/**
 * HTML to PDF Converter using Playwright
 */

const { chromium } = require('/usr/lib/node_modules/openclaw/node_modules/playwright-core');
const fs = require('fs');
const path = require('path');

async function htmlToPdf(inputFile, outputFile) {
    if (!fs.existsSync(inputFile)) {
        console.error(`Error: File not found ${inputFile}`);
        process.exit(1);
    }

    const inputPath = path.resolve(inputFile);
    const outputPath = outputFile ? path.resolve(outputFile) : inputPath.replace('.html', '.pdf');

    console.log(`Converting ${inputPath} to PDF...`);

    const browser = await chromium.launch({ 
        headless: true,
        executablePath: '/usr/bin/google-chrome'
    });
    const page = await browser.newPage();

    // Load HTML file
    await page.goto('file://' + inputPath, { waitUntil: 'networkidle' });

    // Generate PDF
    await page.pdf({
        path: outputPath,
        format: 'A4',
        printBackground: true,
        margin: {
            top: '20mm',
            right: '20mm',
            bottom: '20mm',
            left: '20mm'
        }
    });

    await browser.close();

    console.log(`PDF saved to: ${outputPath}`);
}

// Main
const args = process.argv.slice(2);
if (args.length < 1) {
    console.log('Usage: node html_to_pdf.js <input.html> [output.pdf]');
    process.exit(1);
}

htmlToPdf(args[0], args[1]).catch(err => {
    console.error('Error:', err.message);
    process.exit(1);
});
