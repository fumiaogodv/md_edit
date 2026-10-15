import fs from 'fs';
import katex from 'katex';

const katexOptions = { throwOnError: false, strict: false, trust: true };

function renderBlock(tex) {
  try { katex.renderToString(tex, { ...katexOptions, displayMode: true }); return 'OK'; }
  catch (e) { return 'ERR: ' + e.message.slice(0, 80); }
}
function renderInline(tex) {
  try { katex.renderToString(tex, { ...katexOptions, displayMode: false }); return 'OK'; }
  catch (e) { return 'ERR: ' + e.message.slice(0, 80); }
}

// 测试 IO 设备文件的 aligned 环境
const ioContent = fs.readFileSync('../examples/操作系统整理/a.5IO设备/总文件.md', 'utf-8');
const alignedMatch = ioContent.match(/\$\$([\s\S]*?)\$\$/);
if (alignedMatch) {
  console.log('IO设备 aligned 公式:', renderBlock(alignedMatch[1]));
}

// 测试行内 $...$
const inlineTests = ['E = mc^2', 'x_i', '\\frac{a}{b}'];
inlineTests.forEach(t => {
  console.log(`行内 $${t}$:`, renderInline(t));
});
