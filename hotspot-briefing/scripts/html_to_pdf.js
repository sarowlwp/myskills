#!/usr/bin/env node
/**
 * HTML to PDF Converter using Playwright
 * 支持跨平台运行
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

/**
 * 动态查找 Playwright 模块路径
 */
function findPlaywright() {
    // 尝试路径列表（按优先级）
    const tryPaths = [
        // 环境变量指定
        process.env.PLAYWRIGHT_PATH,
        // 全局安装（openclaw 环境）
        '/usr/lib/node_modules/openclaw/node_modules/playwright-core',
        '/usr/local/lib/node_modules/playwright-core',
        // Homebrew + playwright-mcp 路径 (macOS)
        '/opt/homebrew/lib/node_modules/playwright-mcp/node_modules/playwright-core',
        '/usr/local/lib/node_modules/playwright-mcp/node_modules/playwright-core',
        // Homebrew 独立 playwright
        '/opt/homebrew/lib/node_modules/playwright-core',
        // 项目本地安装
        path.join(__dirname, '..', '..', '..', 'node_modules', 'playwright-core'),
        // npm 全局安装
        path.join(process.env.NPM_CONFIG_PREFIX || '/usr/local', 'lib', 'node_modules', 'playwright-core'),
        // 使用 require 解析
        'playwright-core'
    ].filter(Boolean);

    for (const tryPath of tryPaths) {
        try {
            if (tryPath === 'playwright-core') {
                return require('playwright-core');
            }
            if (fs.existsSync(tryPath)) {
                return require(tryPath);
            }
        } catch (e) {
            continue;
        }
    }
    throw new Error('无法找到 playwright-core 模块，请设置 PLAYWRIGHT_PATH 环境变量');
}

/**
 * 动态查找 Chrome/Chromium 可执行文件
 */
function findChromeExecutable() {
    // 如果环境变量指定，直接使用
    if (process.env.CHROME_PATH || process.env.CHROMIUM_PATH) {
        return process.env.CHROME_PATH || process.env.CHROMIUM_PATH;
    }

    // 各平台常见路径
    const platformPaths = {
        darwin: [ // macOS
            '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
            '/Applications/Chromium.app/Contents/MacOS/Chromium',
            '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
            '/opt/homebrew/bin/chromium',
            '/usr/local/bin/chromium'
        ],
        linux: [ // Linux
            '/usr/bin/google-chrome',
            '/usr/bin/google-chrome-stable',
            '/usr/bin/chromium',
            '/usr/bin/chromium-browser',
            '/snap/bin/chromium',
            '/usr/bin/microsoft-edge'
        ],
        win32: [ // Windows
            'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
            'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
            process.env.LOCALAPPDATA + '\\Google\\Chrome\\Application\\chrome.exe'
        ].filter(Boolean)
    };

    const currentPlatform = process.platform;
    const pathsToTry = platformPaths[currentPlatform] || [];

    for (const chromePath of pathsToTry) {
        try {
            if (fs.existsSync(chromePath)) {
                return chromePath;
            }
        } catch (e) {
            continue;
        }
    }

    // 尝试使用 which/where 命令查找
    try {
        const whichCmd = currentPlatform === 'win32' ? 'where' : 'which';
        const chromeName = currentPlatform === 'win32' ? 'chrome.exe' : 'google-chrome';
        const found = execSync(`${whichCmd} ${chromeName}`, { encoding: 'utf-8' }).trim().split('\n')[0];
        if (found && fs.existsSync(found)) {
            return found;
        }
    } catch (e) {
        // 命令失败，继续
    }

    // 如果找不到，返回 null 让 Playwright 使用内置 Chromium
    console.warn('警告: 未找到系统 Chrome，将尝试使用 Playwright 内置 Chromium');
    return null;
}

async function htmlToPdf(inputFile, outputFile) {
    if (!fs.existsSync(inputFile)) {
        console.error(`Error: File not found ${inputFile}`);
        process.exit(1);
    }

    const inputPath = path.resolve(inputFile);
    const outputPath = outputFile ? path.resolve(outputFile) : inputPath.replace('.html', '.pdf');

    console.log(`Converting ${inputPath} to PDF...`);

    // 动态加载 Playwright
    const { chromium } = findPlaywright();

    // 构建启动选项
    const launchOptions = {
        headless: true
    };

    const chromePath = findChromeExecutable();
    if (chromePath) {
        launchOptions.executablePath = chromePath;
        console.log(`Using Chrome: ${chromePath}`);
    }

    const browser = await chromium.launch(launchOptions);
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
    console.log('');
    console.log('Environment variables:');
    console.log('  PLAYWRIGHT_PATH    - Path to playwright-core module');
    console.log('  CHROME_PATH        - Path to Chrome/Chromium executable');
    process.exit(1);
}

htmlToPdf(args[0], args[1]).catch(err => {
    console.error('Error:', err.message);
    process.exit(1);
});
