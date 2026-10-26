/* The browser workbenches use the existing course examples and retrieval rules. */
(function(root){
  'use strict';
  const unique = ids => [...new Set(ids)];
  const tokens = s => (s.toLowerCase().match(/[a-z0-9]+/g) || []);
  const eligible = (d,q) => d.roles.includes(q.role) && (q.current_only === false || d.status === 'current');
  function retrieve(q,docs,mode='bm25',k=3){
    if(!['faulty','keyword','bm25'].includes(mode)) throw new Error('Unknown mode');
    const candidates=mode==='faulty'?docs:docs.filter(d=>eligible(d,q));
    const termCounts=candidates.map(d=>{
      const terms=tokens(d.title+' '+d.text), counts={};
      terms.forEach(t=>counts[t]=(counts[t]||0)+1);
      return {doc:d,counts,length:terms.length};
    });
    const avg=termCounts.reduce((s,d)=>s+d.length,0)/(termCounts.length||1);
    const queryTerms=unique(tokens(q.query));
    return termCounts.map(d=>{
      let score=0;
      queryTerms.forEach(t=>{
        const f=d.counts[t]||0;
        if(!f)return;
        if(mode==='bm25'){
          const df=termCounts.filter(x=>x.counts[t]).length;
          const idf=Math.log(1+(termCounts.length-df+.5)/(df+.5));
          score+=idf*f*2.5/(f+1.5*(.25+.75*d.length/avg));
        }else score+=1;
      });
      return {id:d.doc.id,score};
    }).filter(d=>d.score>0).sort((a,b)=>b.score-a.score||(a.id<b.id?-1:a.id>b.id?1:0)).slice(0,k);
  }
  function metrics(ranked,relevant,k=3){
    const gold=new Set(relevant),found=unique(ranked).slice(0,k);
    if(!gold.size)return {recall:null,hit:null,rr:null,complete:null};
    const overlap=found.filter(x=>gold.has(x)),first=found.findIndex(x=>gold.has(x));
    return {recall:overlap.length/gold.size,hit:overlap.length?1:0,rr:first<0?0:1/(first+1),complete:overlap.length===gold.size?1:0};
  }
  const api={tokens,eligible,retrieve,metrics};
  if(typeof module!=='undefined'&&module.exports)module.exports=api;
  else root.Learning=api;
})(typeof window!=='undefined'?window:globalThis);
