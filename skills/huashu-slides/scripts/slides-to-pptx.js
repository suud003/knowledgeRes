/**
 * slides-to-pptx.js - Convert HTML slides to PPTX via screenshot
 * 
 * This approach captures each HTML slide as an image and embeds into PPTX.
 * Simpler and more compatible than element-by-element conversion.
 * 
 * Usage: node slides-to-pptx.js <input-dir> <output.pptx>
 */

const path = require('path');
const fs = require('fs');
const { chromium } = require('playwright');
const pptxgen = require('pptxgenjs');

async function main() {
  const args = process.argv.slice(2);
  
  if (args.length < 2) {
    console.log('Usage: node slides-to-pptx.js <input-dir> <output.pptx>');
    process.exit(1);
  }
  
  const inputDir = args[0];
  const outputFile = args[1];
  
  // Get all HTML files, sorted by name
  const htmlFiles = fs.readdirSync(inputDir)
    .filter(f => f.endsWith('.html'))
    .sort()
    .map(f => path.join(inputDir, f));
  
  if (htmlFiles.length === 0) {
    console.error('No HTML files found in', inputDir);
    process.exit(1);
  }
  
  console.log('Found', htmlFiles.length, 'slides');
  
  // Create temp dir for screenshots
  const tempDir = path.join(inputDir, 'temp_screenshots');
  if (!fs.existsSync(tempDir)) {
    fs.mkdirSync(tempDir);
  }
  
  // Launch browser
  console.log('Launching browser...');
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  // Create presentation
  const pptx = new pptxgen();
  pptx.layout = 'LAYOUT_16x9';
  pptx.title = 'AI Tools Sharing';
  
  // Process each slide
  for (let i = 0; i < htmlFiles.length; i++) {
    const htmlFile = htmlFiles[i];
    const baseName = path.basename(htmlFile, '.html');
    const screenshotPath = path.join(tempDir, baseName + '.png');
    
    console.log('[' + (i + 1) + '/' + htmlFiles.length + ']', baseName);
    
    try {
      // Navigate to HTML file
      await page.goto('file://' + htmlFile);
      
      // Get body dimensions
      const dimensions = await page.evaluate(() => {
        const body = document.body;
        const style = window.getComputedStyle(body);
        return {
          width: parseInt(style.width),
          height: parseInt(style.height)
        };
      });
      
      // Set viewport to match slide dimensions
      await page.setViewportSize({
        width: dimensions.width,
        height: dimensions.height
      });
      
      // Take screenshot
      await page.screenshot({
        path: screenshotPath,
        type: 'png',
        scale: 'device'  // Higher quality
      });
      
      // Add slide with image
      const slide = pptx.addSlide();
      slide.addImage({
        path: screenshotPath,
        x: 0,
        y: 0,
        w: '100%',
        h: '100%'
      });
      
      console.log('  Done');
      
    } catch (error) {
      console.error('  Error:', error.message);
    }
  }
  
  await browser.close();
  
  // Save PPTX
  console.log('\nSaving to:', outputFile);
  await pptx.writeFile({ fileName: outputFile });
  console.log('Done! Created PPTX with', pptx.slides.length, 'slides.');
  
  // Clean up temp screenshots
  console.log('Cleaning up temp files...');
  fs.readdirSync(tempDir).forEach(f => fs.unlinkSync(path.join(tempDir, f)));
  fs.rmdirSync(tempDir);
}

main().catch(err => {
  console.error('Fatal error:', err);
  process.exit(1);
});
