// Portable verification harness for the finite ASTRA browser demo.
// Run: node research/eth_repro/demo/check-demo.js
// Requires Node.js >=18; no network and no paid API.
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');

const nodes = {};
function el(id) {
  return nodes[id] || (nodes[id] = {
    value: id === 'point' ? '1' : '0',
    textContent: '',
    children: [],
    style: {},
    appendChild(item) { this.children.push(item); },
    getContext() { return { fillStyle: '', fillRect() {} }; },
  });
}
const sandbox = {
  document: {
    getElementById: el,
    createElement() { return { value:'', textContent:'', click(){} }; },
  },
  URL: { createObjectURL: () => 'blob:test', revokeObjectURL(){} },
  Blob: class { constructor(items,opts) {} },
  console,
};
const source = fs.readFileSync(path.join(__dirname, 'demo.js'), 'utf8');
const context = vm.createContext(sandbox);
vm.runInContext(source, context, { timeout: 10000 });
el('verify').onclick();
assert.match(el('verification').textContent, /PASS.*6144 exact off-group coefficient comparisons/);
assert.equal(el('rank').textContent, '10');
assert.equal(el('measurements').textContent, '10 / 64');
const proof = el('verification').textContent;
assert.throws(() => vm.runInContext('M[0][63]=1; verify()', context, { timeout: 10000 }), /Support violation/);
vm.runInContext('M[0][63]=0', context);
el('verify').onclick();
assert.equal(el('verification').textContent, proof);
console.log('PASS: 6,144 finite checks; rank=10; 10 measurement rows; corruption detected; restoration PASS');
