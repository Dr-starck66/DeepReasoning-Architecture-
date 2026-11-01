"use strict";
const r=2,Q=3,D=64;
const sequences=[...Array(8)].map((_,n)=>[(n>>2)&1,(n>>1)&1,n&1]);
const labels=sequences.flatMap(a=>sequences.map(d=>({a:[...a],d:[...d]})));
const key=u=>u.a.join('')+'|'+u.d.join('');
const byKey=new Map(labels.map((lab,i)=>[key(lab),i]));
function swap(u,axes){const a=[...u.a],d=[...u.d];for(const s of axes){[a[s],d[s]]=[d[s],a[s]];}return{a,d};}
const M=labels.map(u=>{const out=Array(D).fill(0);for(let s=0;s<Q;s++){out[byKey.get(key(swap(u,[0,1,2].filter(h=>h!==s))))]++;}out[byKey.get(key(swap(u,[0,1,2])))]-=2;return out});
const local=[[1,0,0,0],[0,0,0,1],[0,1,1,0],[0,1,-1,0]];
const C=[];
for(let i=0;i<4;i++)for(let j=0;j<4;j++)for(let k=0;k<4;k++){
 const bad=[i,j,k].filter(x=>x===3).length;if(bad<2)continue;
 C.push(labels.map(u=>local[i][2*u.a[0]+u.d[0]]*local[j][2*u.a[1]+u.d[1]]*local[k][2*u.a[2]+u.d[2]]));
}
function rank(matrix){const rows=matrix.map(a=>a.slice()), m=rows.length,n=rows[0].length;let pos=0;for(let j=0;j<n&&pos<m;j++){let pivot=pos;while(pivot<m&&Math.abs(rows[pivot][j])<1e-9)pivot++;if(pivot===m)continue;[rows[pivot],rows[pos]]=[rows[pos],rows[pivot]];const scale=rows[pos][j];for(let k=j;k<n;k++)rows[pos][k]/=scale;for(let k=pos+1;k<m;k++){if(Math.abs(rows[k][j])>1e-9){const a=rows[k][j];for(let h=j;h<n;h++)rows[k][h]-=a*rows[pos][h]}}pos++;}return pos;}
const diff=M.map((v,i)=>v.map((x,j)=>(i===j?1:0)-x));const rankC=rank(C),rankDiff=rank(diff);
function coeff(u,t,y){const v=labels[y],lab=labels[u];const mism=[];for(let s=0;s<3;s++)if(v.a[s]!==lab.d[s])mism.push(s);const slope=M[u][y]&&mism.length===1?-M[u][y]/(mism[0]+1):0;return (u===y?1:0)+t*slope;}
function verify(){if(rankC!==10||rankDiff!==10||C.length!==10)throw new Error('Incorrect rank or measurement count');let off=0;
 for(let u=0;u<64;u++){for(let y=0;y<64;y++){if(M[u][y]){let mism=0;for(let s=0;s<3;s++)if(labels[y].a[s]!==labels[u].d[s])mism++;if(mism>1)throw Error('Support violation u='+u+',y='+y);}}
 for(let t=1;t<=3;t++)for(let y=0;y<64;y++){const isOut=labels[y].a[t-1]!==labels[u].d[t-1];if(!isOut)continue;const v=coeff(u,t,y); if(v!==diff[u][y])throw Error('Polynomial off-group mismatch');off++;}}
 return off;
}
const c=document.getElementById('matrix'),ctx=c.getContext('2d');const color={0:'#11273a',1:'#68decf','-2':'#e8b25f','-1':'#bd70ea',2:'#bd70ea'};
for(let i=0;i<64;i++)for(let j=0;j<64;j++){ctx.fillStyle=color[M[i][j]]||'#ad6be1';ctx.fillRect(j*8,i*8,8,8)}
const row=document.getElementById('row');labels.forEach((u,i)=>{const x=document.createElement('option');x.value=i;x.textContent=String(i).padStart(2,'0')+'  '+key(u);row.appendChild(x)});
function update(){const u=Number(row.value),t=Number(document.getElementById('point').value),dest=labels[u].d[t-1],on=labels.reduce((sum,v,y)=>sum+(v.a[t-1]===dest&&coeff(u,t,y)!==0?1:0),0),off=labels.reduce((sum,v,y)=>sum+(v.a[t-1]!==dest&&coeff(u,t,y)!==0?1:0),0);document.getElementById('details').textContent='Label: '+key(labels[u])+'\nAssigned group: '+dest+'\nNonzero P_u(t) coefficients within group: '+on+'\nNonzero P_u(t) coefficients outside group: '+off+'\nEvery off-group coefficient is reconstructed from C.\nInteger measurement rows: '+C.length;}
row.onchange=update;document.getElementById('point').onchange=update;update();
document.getElementById('verify').onclick=()=>{try{const count=verify();document.getElementById('verification').textContent='PASS · '+count+' exact off-group coefficient comparisons · rank(I − M₀)='+rankDiff+' · rank(C)='+rankC;}catch(e){document.getElementById('verification').textContent='FAIL · '+String(e.message)}};
document.getElementById('dim').textContent=D+' × '+D;document.getElementById('rank').textContent=String(rankDiff);document.getElementById('measurements').textContent=C.length+' / '+D;
document.getElementById('download').onclick=()=>{const out={schema:'astra-prooflab/1',source:'OpenAI Oct 25 2026 Section 4',instance:{r:2,Q:3,R:2,interval:[0,1]},matrix:{D,rank_M0:rank(M),rank_I_minus_M0:rankDiff,rank_C:rankC,measurement_rows:C.length},verified_url:'https://github.com/Dr-starck66/DeepReasoning-Architecture-/actions/runs/41289001101',scope:'finite only; asymptotic and valuation unverified'};const url=URL.createObjectURL(new Blob([JSON.stringify(out,null,2)],{type:'application/json'}));const link=document.createElement('a');link.href=url;link.download='astra-prooflab-evidence.json';link.click();URL.revokeObjectURL(url)};
