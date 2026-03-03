/**
 * convert-slides.js - Convert all HTML slides in a directory to PPTX
 * 
 * Usage: node convert-slides.js <input-dir> <output.pptx>
 */

const path = require('path');
const fs = require('fs');
const pptxgen = require('pptxgenjs');
const html2pptx = require('./html2pptx.js');

async function main() {
  const args = process.argv.slice(2);
  
  if (args.length < 2) {
    console.log('Usage: node convert-slides.js <input-dir> <output.pptx>');
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
  
  console.log('Found', htmlFiles.length, 'slides:');
  htmlFiles.forEach((f, i) => console.log('  ' + (i + 1) + '.', path.basename(f)));
  
  // Create presentation
  const pptx = new pptxgen();
  pptx.layout = 'LAYOUT_16x9';
  pptx.title = 'AI Tools Sharing';
  
  // Convert each HTML to slide
  for (let i = 0; i < htmlFiles.length; i++) {
    const htmlFile = htmlFiles[i];
    console.log('\nProcessing [' + (i + 1) + '/' + htmlFiles.length + ']:', path.basename(htmlFile));
    
    try {
      await html2pptx(htmlFile, pptx);
      console.log('  Done');
    } catch (error) {
      console.error('  Error:', error.message);
      // Continue with other slides
    }
  }
  
  // Save PPTX
  console.log('\nSaving to:', outputFile);
  await pptx.writeFile(outputFile);
  console.log('Done! Created PPTX with', pptx.slides.length, 'slides.');
}

main().catch(err => {
  console.error('Fatal error:', err);
  process.exit(1);
});
