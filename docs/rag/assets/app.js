(function(){
  'use strict';
  const data=window.COURSE_DATA, $=(s,r=document)=>r.querySelector(s), $$=(s,r=document)=>[...r.querySelectorAll(s)];
  const key='ai-engineering-lab:rag:progress:v1';
  const known=new Set(data.sessions.map(s=>s.id));
  let storageAvailable=true, state={completed:[],last:null}, toastTimer;
  try{const raw=JSON.parse(localStorage.getItem(key)||'null');if(raw)state=cleanState(raw);}catch(e){storageAvailable=false;}
  function cleanState(raw){return {completed:[...new Set((Array.isArray(raw.completed)?raw.completed:[]).filter(x=>known.has(x)))],last:known.has(raw.last)?raw.last:null};}
  function save(){try{localStorage.setItem(key,JSON.stringify(state));}catch(e){storageAvailable=false;toast('Progress is temporary. Export a backup before leaving.');}updateProgress();}
  function toast(text){const box=$('#toast');box.textContent=text;box.classList.add('visible');clearTimeout(toastTimer);toastTimer=setTimeout(()=>box.classList.remove('visible'),3000);}
  const page=document.body.dataset.page;
  const rootPrefix='../'.repeat((page.match(/\//g)||[]).length);
  function localHref(path){return rootPrefix+path;}
  function updateProgress(){
    const done=new Set(state.completed);
    $$('[data-progress-count]').forEach(e=>e.textContent=`${done.size} / 144`);
    $$('[data-global-progress]').forEach(e=>e.value=done.size);
    for(let m=1;m<=8;m++){
      const count=data.sessions.filter(s=>s.module===m&&done.has(s.id)).length;
      $$(`[data-module-progress="${m}"]`).forEach(e=>e.textContent=count?`${count}/18`:'');
      $$(`[data-card-progress="${m}"]`).forEach(e=>e.value=count);
    }
    $$('[data-session-id]').forEach(e=>{
      const checked=done.has(e.dataset.sessionId);e.dataset.complete=String(checked);
      const input=$('input[type=checkbox]',e);if(input)input.checked=checked;
    });
    const resume=data.sessions.find(s=>s.id===state.last&&!done.has(s.id))||data.sessions.find(s=>!done.has(s.id));
    if(state.completed.length||state.last){
      $$('[data-resume]').forEach(e=>{e.href=localHref(resume?resume.href:'resources/assessment.html');e.innerHTML=resume?'Continue learning <span>↗</span>':'Review practical checkpoints <span>↗</span>';});
      $$('[data-resume-title]').forEach(e=>e.textContent=resume?`Week ${resume.week} · Session ${resume.letter} — ${data.modules.find(m=>m.id===resume.module).title}`:'All learning sessions marked complete');
    }
    $$('.storage-status').forEach(e=>e.textContent=storageAvailable?'Stored on this browser. No account or analytics required.':'Browser storage is unavailable. Export a backup to keep this session’s progress.');
  }
  function sessionize(){
    const article=$('article.lesson-content');if(!article)return;
    const moduleNumber=Number(document.body.dataset.module);
    if(moduleNumber){
      const nodes=[...article.childNodes];let section=null,session=null,sessionBody=null,currentWeek=null;
      for(const node of nodes){
        if(node.nodeType===1&&node.tagName==='H2'&&/^Week \d+/.test(node.textContent)){
          section=document.createElement('section');section.className='week-section';section.id=node.id;node.removeAttribute('id');node.before(section);section.append(node);session=null;sessionBody=null;
          currentWeek=Number(node.textContent.match(/^Week (\d+)/)[1]);
        }else if(section&&node.nodeType===1&&node.tagName==='H2'){
          section=null;session=null;sessionBody=null;
        }else if(section&&node.nodeType===1&&node.tagName==='H3'&&/^Session [ABC]/.test(node.textContent)){
          const letter=node.textContent.match(/^Session ([ABC])/)[1];
          const sid=`m${String(moduleNumber).padStart(2,'0')}-w${String(currentWeek).padStart(2,'0')}-${letter.toLowerCase()}`;
          session=document.createElement('details');session.className='session';session.id=node.id;session.dataset.sessionId=sid;
          const summary=document.createElement('summary');const span=document.createElement('span');span.textContent=node.textContent;summary.append(span);
          const tag=document.createElement('span');tag.className='session-tag';tag.textContent='60 MIN';summary.append(tag);session.append(summary);
          sessionBody=document.createElement('div');sessionBody.className='session-body';session.append(sessionBody);section.append(session);node.remove();
          summary.addEventListener('click',()=>{state.last=sid;save();});
        }else if(section){
          const isDeliverable=node.nodeType===1&&node.tagName==='P'&&/^((Save|Move on when):)/.test(node.textContent);
          if(isDeliverable){node.classList.add('week-deliverable');section.append(node);session=null;sessionBody=null;}
          else if(sessionBody)sessionBody.append(node);else section.append(node);
        }
      }
      $$('.session',article).forEach((entry)=>{
        const sid=entry.dataset.sessionId, target=$('.session-body',entry);
        const footer=document.createElement('div');footer.className='session-complete';
        const label=document.createElement('label');label.className='complete-label';const input=document.createElement('input');input.type='checkbox';label.append(input,document.createTextNode('Mark this session complete'));
        input.addEventListener('change',()=>{state.completed=state.completed.filter(x=>x!==sid);if(input.checked)state.completed.push(sid);state.last=sid;save();});
        footer.append(label);
        const next=data.sessions[data.sessions.findIndex(s=>s.id===sid)+1];
        if(next){const a=document.createElement('a');a.className='next-session';a.href=localHref(next.href);a.textContent=`Next: week ${next.week}, session ${next.letter} →`;a.dataset.nextSession=next.id;a.addEventListener('click',(event)=>{state.last=next.id;save();if(next.module===moduleNumber){event.preventDefault();location.hash=next.href.split('#')[1];const nextEntry=$('[data-session-id="'+next.id+'"]',article);if(nextEntry){$$('.session',article).forEach(e=>e.open=e===nextEntry);nextEntry.scrollIntoView({block:'start'});}}});footer.append(a);}
        target.append(footer);
      });
      const first=$$('.session',article).find(e=>e.dataset.sessionId===state.last&&!state.completed.includes(e.dataset.sessionId))||$$('.session',article).find(e=>!state.completed.includes(e.dataset.sessionId))||$('.session',article);if(first)first.open=true;
    }
    const ref=$$('h2',article).find(e=>e.textContent.startsWith('Reference —'));
    if(ref){const detail=document.createElement('details');detail.className='reference-section';const summary=document.createElement('summary');summary.textContent=ref.textContent;const sub=document.createElement('small');sub.textContent='Open the original explanations and worked examples when you need them.';summary.append(sub);detail.append(summary);const body=document.createElement('div');body.className='reference-body';detail.append(body);ref.before(detail);let node=ref;while(node){const next=node.nextSibling;body.append(node);node=next;}}
    $$('pre',article).forEach(pre=>{
      const code=$('code',pre);if(!code)return;
      pre.dataset.language=(code.className.match(/language-([\w-]+)/)||[])[1]||'code';
      const button=document.createElement('button');button.className='copy-button';button.textContent='Copy';button.type='button';button.setAttribute('aria-label','Copy code block');
      button.addEventListener('click',async()=>{try{await navigator.clipboard.writeText(code.textContent);button.textContent='Copied';setTimeout(()=>button.textContent='Copy',1500);}catch(e){const range=document.createRange();range.selectNodeContents(code);const selection=getSelection();selection.removeAllRanges();selection.addRange(range);toast('Code selected. Use your browser’s copy shortcut.');}});pre.append(button);
    });
    $$('table',article).forEach(table=>{const wrapper=document.createElement('div');wrapper.className='table-scroll';wrapper.tabIndex=0;wrapper.setAttribute('aria-label','Scrollable lesson table');table.before(wrapper);wrapper.append(table);});
    if(moduleNumber===7||moduleNumber===8)addArchitecture(article);
    if(page==='lessons/introduction.html')addPipeline(article);
  }
  function openAnchor(){
    if(!location.hash)return;
    let id;try{id=decodeURIComponent(location.hash.slice(1));}catch(e){return;}
    const target=document.getElementById(id);if(!target)return;
    let parent=target.closest('details');while(parent){parent.open=true;parent=parent.parentElement.closest('details');}
    if(target.classList.contains('week-section')){
      const wanted=data.sessions.find(s=>s.id===state.last),entries=$$('.session',target);
      (entries.find(e=>wanted&&e.dataset.sessionId===wanted.id)||entries.find(e=>!state.completed.includes(e.dataset.sessionId))||entries[0])?.setAttribute('open','');
    }
    setTimeout(()=>target.scrollIntoView({block:'start'}),40);
  }
  function addPipeline(article){
    const headings=$$('h3',article);const labels=['Ingestion: prepare sources for search','Query time: find evidence and answer'];
    const intro=labels.map(label=>headings.find(h=>h.textContent===label)).filter(Boolean);
    if(intro.length!==2)return;
    const box=document.createElement('section');box.className='pipeline-visual';box.setAttribute('aria-label','Explore the two RAG workflows');
    const h=document.createElement('h2');h.textContent='Two workflows, one system';box.append(h);
    const tabs=document.createElement('div');tabs.className='pipeline-steps';const detail=document.createElement('div');detail.className='pipeline-detail';detail.setAttribute('aria-live','polite');
    intro.forEach((heading,i)=>{const b=document.createElement('button');b.textContent=labels[i];b.type='button';b.setAttribute('aria-pressed',String(i===0));b.addEventListener('click',()=>{select(i);});tabs.append(b);});
    function select(i){$$('button',tabs).forEach((b,j)=>b.setAttribute('aria-pressed',String(i===j)));detail.replaceChildren();let next=intro[i].nextElementSibling;while(next&&next.tagName!=='H2'&&next.tagName!=='H3'){if(next.tagName==='OL'){const clone=next.cloneNode(true);detail.append(clone);break;}next=next.nextElementSibling;}}
    box.append(tabs,detail);intro[0].parentNode.insertBefore(box,intro[0]);select(0);
  }
  function addArchitecture(article){
    const box=document.createElement('figure');box.className='architecture';box.innerHTML=`<svg viewBox="0 0 780 250" role="img" aria-label="Authenticated HTTPS traffic flows through ALB and API to pgvector and Bedrock. An ingestion task builds versioned snapshots from S3."><defs><marker id="arrow" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto"><path d="M0 0L6 3L0 6" fill="#83a58f"/></marker></defs><g class="map-arrow" marker-end="url(#arrow)"><path d="M150 62H235"/><path d="M375 62H465"/><path d="M600 62H660"/><path d="M530 85V153"/><path d="M320 192H465"/></g><rect class="map-node" x="10" y="35" width="140" height="55" rx="8"/><rect class="map-node" x="235" y="35" width="140" height="55" rx="8"/><rect class="map-node" x="465" y="35" width="135" height="55" rx="8"/><rect class="map-node" x="660" y="35" width="110" height="55" rx="8"/><rect class="map-node" x="465" y="155" width="135" height="65" rx="8"/><rect class="map-node" x="150" y="165" width="170" height="55" rx="8"/><g text-anchor="middle"><text x="80" y="66">HTTPS + identity</text><text x="305" y="66">ALB → API</text><text x="532" y="59">Authorized</text><text x="532" y="76">pgvector retrieval</text><text x="715" y="66">Bedrock</text><text x="532" y="182">Approved index</text><text x="532" y="200">snapshot</text><text x="235" y="187">S3 sources</text><text x="235" y="205">→ ingestion job</text></g></svg><figcaption>Map of the existing AWS route. The lesson below contains the full provisioning and access-control instructions.</figcaption>`;
    const start=$('h2',article);if(start)start.before(box);
  }
  sessionize();updateProgress();openAnchor();window.addEventListener('hashchange',openAnchor);
  $$('[data-expand-all]').forEach(b=>b.addEventListener('click',()=>$$('.session,.reference-section').forEach(e=>e.open=true)));
  $$('[data-collapse-all]').forEach(b=>b.addEventListener('click',()=>{$$('.session,.reference-section').forEach(e=>e.open=false);const target=$('.session:not([data-complete=true])')||$('.session');if(target)target.open=true;}));
  $$('[data-print]').forEach(b=>b.addEventListener('click',()=>window.print()));
  let printState=[];window.addEventListener('beforeprint',()=>{printState=$$('details').map(e=>[e,e.open]);printState.forEach(([e])=>e.open=true);});window.addEventListener('afterprint',()=>printState.forEach(([e,open])=>e.open=open));
  $('#menu-toggle')?.addEventListener('click',e=>{const open=$('#sidebar').classList.toggle('open');e.currentTarget.setAttribute('aria-expanded',String(open));});
  document.addEventListener('click',e=>{if(!e.target.closest('#sidebar,#menu-toggle')){$('#sidebar').classList.remove('open');$('#menu-toggle')?.setAttribute('aria-expanded','false');}});
  const searchDialog=$('#search-dialog'),progressDialog=$('#progress-dialog');
  $$('[data-search-open]').forEach(b=>b.addEventListener('click',()=>{searchDialog.showModal();$('#search-input').focus();}));
  $$('[data-open-progress]').forEach(b=>b.addEventListener('click',()=>{updateProgress();progressDialog.showModal();}));
  $$('[data-close-dialog]').forEach(b=>b.addEventListener('click',()=>b.closest('dialog').close()));
  $$('dialog').forEach(d=>d.addEventListener('click',e=>{if(e.target===d){const r=d.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)d.close();}}));
  document.addEventListener('keydown',e=>{if(e.key==='/'&&!e.metaKey&&!e.ctrlKey&&!/INPUT|TEXTAREA|SELECT/.test(e.target.tagName)&&!document.querySelector('dialog[open]')){e.preventDefault();searchDialog.showModal();$('#search-input').focus();}if(e.key==='Escape'){$('#sidebar').classList.remove('open');$('#menu-toggle')?.setAttribute('aria-expanded','false');}});
  // Search reads the editable HTML pages directly. There is no generated content index.
  let searchPagesPromise,searchSequence=0;
  function searchPages(){
    if(!searchPagesPromise)searchPagesPromise=(async()=>{
      if(location.protocol==='file:')return data.search.map(p=>({...p,text:p.title,localOnly:true}));
      return Promise.all(data.search.map(async p=>{
        try{
          const response=await fetch(localHref(p.href));
          if(!response.ok)throw new Error('Page unavailable');
          const document=new DOMParser().parseFromString(await response.text(),'text/html');
          return {...p,title:document.querySelector('h1')?.textContent||p.title,text:(document.querySelector('article')||document.querySelector('main')).textContent.replace(/\s+/g,' ')};
        }catch(error){return {...p,text:p.title,localOnly:true};}
      }));
    })();
    return searchPagesPromise;
  }
  $('#search-input').addEventListener('input',async e=>{
    const sequence=++searchSequence,query=e.target.value.trim().toLowerCase(),result=$('#search-results');
    result.replaceChildren();
    if(query.length<2){result.textContent='Type at least two characters to search all course material.';return;}
    result.textContent='Searching course pages…';
    const pages=await searchPages();
    if(sequence!==searchSequence)return;
    result.replaceChildren();
    const normalized=s=>s.toLowerCase().replace(/\bweek\s+0*(\d+)\b/g,'week $1'),needle=normalized(query);
    const score=p=>(normalized(p.title).includes(needle)?30:0)+normalized(p.text).split(needle).length-1;
    const matches=pages.filter(p=>normalized(p.title+' '+p.text).includes(needle)).sort((a,b)=>score(b)-score(a)).slice(0,12);
    matches.forEach(p=>{
      const a=document.createElement('a');a.className='search-hit';a.href=localHref(p.href);
      const title=document.createElement('strong');title.textContent=p.title;
      const snippet=document.createElement('p'),at=normalized(p.text).indexOf(needle);
      snippet.textContent=(at>60?'…':'')+p.text.slice(Math.max(0,at-60),Math.max(0,at-60)+190)+'…';
      a.append(title,snippet);result.append(a);
    });
    if(!matches.length)result.textContent='No matching lesson text.';
    if(pages.some(p=>p.localOnly)){const note=document.createElement('p');note.className='muted';note.textContent='Some pages are searchable by title only. Full-text search needs this folder served over HTTP/HTTPS.';result.append(note);}
  });
  $('#export-progress').addEventListener('click',()=>{const blob=new Blob([JSON.stringify({version:1,exported_at:new Date().toISOString(),...state},null,2)],{type:'application/json'});const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='rag-course-progress.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
  $('#import-progress').addEventListener('change',async e=>{const file=e.target.files[0];if(!file)return;try{if(file.size>100000)throw new Error('Backup is too large.');const raw=JSON.parse(await file.text());if(raw.version!==1||!Array.isArray(raw.completed)||raw.completed.some(x=>!known.has(x)))throw new Error('Use an exported RAG course backup.');state=cleanState(raw);save();$('#import-status').textContent=`Imported ${state.completed.length} completed sessions.`;}catch(error){$('#import-status').textContent=error.message;}e.target.value='';});
  $('#reset-progress').addEventListener('click',()=>{state={completed:[],last:null};save();$('#import-status').textContent='Saved session progress reset.';});
  if(page==='explore.html')setupExplorer();if(page==='metrics.html')setupMetrics();
  function setupExplorer(){
    const select=$('#question-select');data.questions.forEach(q=>{const o=document.createElement('option');o.value=q.id;o.textContent=`${q.id} — ${q.query}`;select.append(o);});select.value='q02';let revealed=false;
    function showSource(id){const d=data.corpus.find(x=>x.id===id),q=data.questions.find(x=>x.id===select.value);$('#source-title').textContent=d.title;$('#source-text').textContent=d.text;$('#source-meta').replaceChildren();[d.id,`v${d.version}`,d.status,d.roles.join(' / ')].forEach(t=>{const b=document.createElement('span');b.className='badge';b.textContent=t;$('#source-meta').append(b,document.createTextNode(' '));});const warnings=[];if(!d.roles.includes(q.role))warnings.push('This reader is not authorized for this source.');if(q.current_only&&d.status!=='current')warnings.push('Archived evidence does not satisfy this current-only request.');$('#source-warning').textContent=warnings.join(' ');$$('.result-card').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.id===id)));}
    function render(){const q=data.questions.find(x=>x.id===select.value),mode=$('#mode-select').value,k=Number($('#k-select').value);const hits=Learning.retrieve(q,data.corpus,mode,k);$('#question-text').textContent=q.query;$('#question-meta').textContent=`${q.id} / ${q.role.toUpperCase()} / ${q.current_only?'CURRENT SOURCES ONLY':'HISTORICAL SOURCES ALLOWED'}`;$('#retrieval-count').textContent=`${hits.length} result${hits.length===1?'':'s'}`;const results=$('#retrieval-results');results.replaceChildren();hits.forEach((h,i)=>{const d=data.corpus.find(x=>x.id===h.id),button=document.createElement('button');button.className='result-card';button.dataset.id=d.id;button.setAttribute('aria-pressed','false');const head=document.createElement('span');head.className='result-head';const rank=document.createElement('span');rank.className='rank-number';rank.textContent=String(i+1).padStart(2,'0');const name=document.createElement('span');name.textContent=d.title;const score=document.createElement('span');score.className='result-score';score.textContent=h.score.toFixed(3);head.append(rank,name,score);const badges=document.createElement('span');badges.className='result-badges';[d.id,d.status,...(!d.roles.includes(q.role)?['unauthorized']:[])].forEach(t=>{const b=document.createElement('span');b.className='badge'+(t==='unauthorized'||(t==='archived'&&q.current_only)?' bad':'');b.textContent=t;badges.append(b);});button.append(head,badges);button.addEventListener('click',()=>showSource(d.id));results.append(button);});if(!hits.length)results.textContent='No positive-scoring eligible candidates. The local starter would abstain without a model call.';if(hits.length)showSource(hits[0].id);else{$('#source-title').textContent='No source selected';$('#source-meta').replaceChildren();$('#source-text').textContent='Search returned no candidates.';$('#source-warning').textContent='';}const refs=$('#reference-labels');refs.hidden=!revealed;refs.textContent=`Reference evidence: ${q.relevant.length?q.relevant.join(', '):'none authorized in this corpus'}. Expected behavior: ${q.expected}.`;$('#reveal-labels').setAttribute('aria-expanded',String(revealed));}
    select.addEventListener('change',()=>{revealed=false;render();});$('#mode-select').addEventListener('change',render);$('#k-select').addEventListener('change',render);$('#reveal-labels').addEventListener('click',()=>{revealed=!revealed;render();});
    function corpus(){const needle=$('#corpus-search').value.toLowerCase(),list=$('#corpus-list');list.replaceChildren();data.corpus.filter(d=>(d.title+' '+d.text).toLowerCase().includes(needle)).forEach(d=>{const b=document.createElement('button');b.className='corpus-row';b.textContent=`${d.id} · ${d.title} · ${d.status}`;b.addEventListener('click',()=>{showSource(d.id);$('#source-title').scrollIntoView({block:'center'});});list.append(b);});}$('#corpus-search').addEventListener('input',corpus);corpus();render();
  }
  function setupMetrics(){let ranked=['X','A','Y','B'];const labels={A:'Staging procedure · relevant',B:'Production procedure · relevant',X:'Irrelevant source',Y:'Irrelevant source'};
    function draw(){const k=Number($('#metric-k').value),list=$('#ranked-list');list.replaceChildren();ranked.forEach((id,i)=>{const li=document.createElement('li');li.className='ranked-item'+(i>=k?' outside-k':'');const letter=document.createElement('span');letter.className='doc-letter'+('AB'.includes(id)?' relevant':'');letter.textContent=id;const text=document.createElement('div');const p=document.createElement('p');p.textContent=`Rank ${i+1}${i>=k?' · outside top-k':''}`;const name=document.createElement('strong');name.style.fontSize='12px';name.textContent=labels[id];text.append(p,name);const buttons=document.createElement('div');buttons.className='ranked-controls';[-1,1].forEach(direction=>{const b=document.createElement('button');b.textContent=direction<0?'↑':'↓';b.disabled=i+direction<0||i+direction>=ranked.length;b.setAttribute('aria-label',`Move ${id} ${direction<0?'up':'down'}`);b.addEventListener('click',()=>{[ranked[i],ranked[i+direction]]=[ranked[i+direction],ranked[i]];draw();const nextButtons=$$('.ranked-item',list)[i+direction]?.querySelectorAll('button');nextButtons?.[direction<0?0:1]?.focus();});buttons.append(b);});li.append(letter,text,buttons);list.append(li);});const m=Learning.metrics(ranked,['A','B'],k);const cards=$('#metric-cards');cards.replaceChildren();[['Recall',m.recall,'Relevant IDs found / 2'],['Hit',m.hit,'At least one relevant ID'],['RR',m.rr,'1 / first relevant rank'],['Complete',m.complete,'All labeled IDs found']].forEach(([label,value,formula])=>{const div=document.createElement('div');div.className='metric-card';const a=document.createElement('span');a.textContent=`${label}@${k}`;const b=document.createElement('strong');b.textContent=Number.isInteger(value)?value.toFixed(0):value.toFixed(3).replace(/0+$/,'');const c=document.createElement('small');c.textContent=formula;div.append(a,b,c);cards.append(div);});const explanation=$('#metric-explanation');const h=document.createElement('h3');h.textContent=m.complete?'Both required procedures are present':m.hit?'Some evidence is present; the answer is still incomplete':'Neither required source is in the selected context';const p=document.createElement('p');p.textContent=`Top-${k}: ${ranked.slice(0,k).join(', ')}. ${m.complete?'Retrieval found A and B. Generation can still omit or invent a claim.':m.hit?'A hit only confirms that at least one relevant source was found.':'Move A or B into the selected results to see the metrics respond.'}`;explanation.replaceChildren(h,p);}
    $('#metric-k').addEventListener('change',draw);$('#reset-ranking').addEventListener('click',()=>{ranked=['X','A','Y','B'];$('#metric-k').value='3';draw();});draw();
  }
})();
