(function(){
  'use strict';
  const data=window.COURSE_DATA, Lab=window.AgentLab, $=(s,r=document)=>r.querySelector(s), $$=(s,r=document)=>[...r.querySelectorAll(s)];
  const key='ai-engineering-lab:agents:progress:v1', TOTAL=data.sessions.length, PER_MODULE=12;
  const known=new Set(data.sessions.map(s=>s.id));
  let storageAvailable=true, state={completed:[],last:null,checks:{}}, toastTimer;
  try{const raw=JSON.parse(localStorage.getItem(key)||'null');if(raw)state=cleanState(raw);}catch(e){storageAvailable=false;}
  function cleanState(raw){
    const checks={};
    if(raw.checks&&typeof raw.checks==='object')Object.entries(raw.checks).slice(0,300).forEach(([k,v])=>{if(/^[a-z0-9-]{1,40}$/.test(k)&&Number.isInteger(v)&&v>=0&&v<10)checks[k]=v;});
    return {completed:[...new Set((Array.isArray(raw.completed)?raw.completed:[]).filter(x=>known.has(x)))],last:known.has(raw.last)?raw.last:null,checks};
  }
  function save(){try{localStorage.setItem(key,JSON.stringify(state));}catch(e){storageAvailable=false;toast('Progress is temporary. Export a backup before leaving.');}updateProgress();}
  function toast(text){const box=$('#toast');box.textContent=text;box.classList.add('visible');clearTimeout(toastTimer);toastTimer=setTimeout(()=>box.classList.remove('visible'),3000);}
  function el(tag,attrs={},...children){const e=document.createElement(tag);Object.entries(attrs).forEach(([k,v])=>{if(v===null||v===undefined||v===false)return;if(k==='class')e.className=v;else if(k==='text')e.textContent=v;else if(k.startsWith('on'))e.addEventListener(k.slice(2),v);else e.setAttribute(k,v===true?'':v);});children.flat().forEach(c=>{if(c!==null&&c!==undefined&&c!==false)e.append(c instanceof Node?c:document.createTextNode(String(c)));});return e;}
  const page=document.body.dataset.page;
  const rootPrefix='../'.repeat((page.match(/\//g)||[]).length);
  const localHref=path=>rootPrefix+path;
  function updateProgress(){
    const done=new Set(state.completed);
    $$('[data-progress-count]').forEach(e=>e.textContent=`${done.size} / ${TOTAL}`);
    $$('[data-global-progress]').forEach(e=>e.value=done.size);
    data.modules.forEach(m=>{
      const count=data.sessions.filter(s=>s.module===m.id&&done.has(s.id)).length;
      $$(`[data-module-progress="${m.id}"]`).forEach(e=>e.textContent=count?`${count}/${PER_MODULE}`:'');
      $$(`[data-card-progress="${m.id}"]`).forEach(e=>e.value=count);
    });
    $$('[data-session-id]').forEach(e=>{const checked=done.has(e.dataset.sessionId);e.dataset.complete=String(checked);const input=$('input[type=checkbox]',e);if(input)input.checked=checked;});
    const resume=data.sessions.find(s=>s.id===state.last&&!done.has(s.id))||data.sessions.find(s=>!done.has(s.id));
    if(state.completed.length||state.last){
      $$('[data-resume]').forEach(e=>{e.href=localHref(resume?resume.href:'resources/assessment.html');e.innerHTML=resume?'Continue learning <span>↗</span>':'Review practical checkpoints <span>↗</span>';});
      $$('[data-resume-title]').forEach(e=>e.textContent=resume?`Week ${resume.week} · Session ${resume.letter} — ${data.modules.find(m=>m.id===resume.module).title}`:'All learning sessions marked complete');
    }
    const answered=Object.keys(state.checks).length;
    $$('[data-checks-count]').forEach(e=>e.textContent=String(answered));
    $$('.storage-status').forEach(e=>e.textContent=storageAvailable?'Stored on this browser. No account or analytics required.':'Browser storage is unavailable. Export a backup to keep this session’s progress.');
  }
  // ------------------------------------------------------------------ lesson structure
  function sessionize(){
    const article=$('article.lesson-content');if(!article)return;
    const moduleNumber=Number(document.body.dataset.module);
    if(moduleNumber){
      let section=null,sessionBody=null,currentWeek=null;
      for(const node of [...article.childNodes]){
        if(node.nodeType===1&&node.tagName==='H2'&&/^Week \d+/.test(node.textContent)){
          section=document.createElement('section');section.className='week-section';section.id=node.id;node.removeAttribute('id');node.before(section);section.append(node);sessionBody=null;
          currentWeek=Number(node.textContent.match(/^Week (\d+)/)[1]);
        }else if(section&&node.nodeType===1&&node.tagName==='H2'){section=null;sessionBody=null;}
        else if(section&&node.nodeType===1&&node.tagName==='H3'&&/^Session [ABC]/.test(node.textContent)){
          const letter=node.textContent.match(/^Session ([ABC])/)[1];
          const sid=`m${String(moduleNumber).padStart(2,'0')}-w${String(currentWeek).padStart(2,'0')}-${letter.toLowerCase()}`;
          const session=document.createElement('details');session.className='session';session.id=node.id;session.dataset.sessionId=sid;
          const summary=document.createElement('summary');summary.append(el('span',{text:node.textContent}),el('span',{class:'session-tag',text:'60 MIN'}));session.append(summary);
          sessionBody=document.createElement('div');sessionBody.className='session-body';session.append(sessionBody);section.append(session);node.remove();
          summary.addEventListener('click',()=>{state.last=sid;save();});
        }else if(section){
          const isDeliverable=node.nodeType===1&&node.tagName==='P'&&/^((Save|Move on when):)/.test(node.textContent);
          const isCheck=node.nodeType===1&&node.classList&&node.classList.contains('quick-check');
          if(isDeliverable||isCheck){if(isDeliverable)node.classList.add('week-deliverable');section.append(node);sessionBody=null;}
          else if(sessionBody)sessionBody.append(node);else section.append(node);
        }
      }
      $$('.session',article).forEach(entry=>{
        const sid=entry.dataset.sessionId,target=$('.session-body',entry);
        const input=el('input',{type:'checkbox'});
        input.addEventListener('change',()=>{state.completed=state.completed.filter(x=>x!==sid);if(input.checked)state.completed.push(sid);state.last=sid;save();});
        const footer=el('div',{class:'session-complete'},el('label',{class:'complete-label'},input,'Mark this session complete'));
        const next=data.sessions[data.sessions.findIndex(s=>s.id===sid)+1];
        if(next){const a=el('a',{class:'next-session',href:localHref(next.href),text:`Next: week ${next.week}, session ${next.letter} →`});a.addEventListener('click',event=>{state.last=next.id;save();if(next.module===moduleNumber){event.preventDefault();location.hash=next.href.split('#')[1];const nextEntry=$('[data-session-id="'+next.id+'"]',article);if(nextEntry){$$('.session',article).forEach(e=>e.open=e===nextEntry);nextEntry.scrollIntoView({block:'start'});}}});footer.append(a);}
        target.append(footer);
      });
      const first=$$('.session',article).find(e=>e.dataset.sessionId===state.last&&!state.completed.includes(e.dataset.sessionId))||$$('.session',article).find(e=>!state.completed.includes(e.dataset.sessionId))||$('.session',article);if(first)first.open=true;
    }
    const ref=$$('h2',article).find(e=>e.textContent.startsWith('Reference —'));
    if(ref){const detail=el('details',{class:'reference-section'});const summary=el('summary',{text:ref.textContent},el('small',{text:'Open the explanations, worked example and primary references when a step points to them.'}));detail.append(summary);const body=el('div',{class:'reference-body'});detail.append(body);ref.before(detail);let node=ref;while(node){const n=node.nextSibling;body.append(node);node=n;}}
    $$('pre',article).forEach(pre=>{
      const code=$('code',pre);if(!code)return;
      pre.dataset.language=(code.className.match(/language-([\w-]+)/)||[])[1]||'code';
      const button=el('button',{class:'copy-button',type:'button','aria-label':'Copy code block',text:'Copy'});
      button.addEventListener('click',async()=>{try{await navigator.clipboard.writeText(code.textContent);button.textContent='Copied';setTimeout(()=>button.textContent='Copy',1500);}catch(e){const range=document.createRange();range.selectNodeContents(code);const sel=getSelection();sel.removeAllRanges();sel.addRange(range);toast('Code selected. Use your browser’s copy shortcut.');}});pre.append(button);
    });
    $$('table',article).forEach(table=>{if(table.parentElement.classList.contains('table-scroll'))return;const wrapper=el('div',{class:'table-scroll',tabindex:'0','aria-label':'Scrollable lesson table'});table.before(wrapper);wrapper.append(table);});
  }
  // Quick checks: self-checks with immediate feedback. Saved locally; never graded.
  function setupChecks(){
    $$('.quick-check').forEach(box=>{
      const id=box.dataset.checkId,options=$$('.check-options > li',box),explanation=$('.check-explanation',box);
      if(!id||!options.length)return;
      box.classList.add('ready');
      const list=$('.check-options',box);list.setAttribute('role','list');
      const label=el('p',{class:'check-label'},el('span',{class:'check-icon','aria-hidden':'true',text:'?'}),' Quick check');
      box.prepend(label);
      const feedback=el('p',{class:'check-feedback',role:'status','aria-live':'polite'});explanation.before(feedback);
      const buttons=options.map((li,i)=>{const b=el('button',{type:'button',class:'check-option'});while(li.firstChild)b.append(li.firstChild);li.append(b);b.addEventListener('click',()=>{state.checks[id]=i;save();render();});return b;});
      const retry=el('button',{type:'button',class:'text-button check-retry',text:'Try again'});retry.addEventListener('click',()=>{delete state.checks[id];save();render();buttons[0].focus();});explanation.after(retry);
      function render(){
        const chosen=state.checks[id],answered=chosen!==undefined;
        buttons.forEach((b,i)=>{const correct=options[i].hasAttribute('data-correct');b.disabled=answered;b.classList.toggle('chosen',answered&&i===chosen);b.classList.toggle('correct',answered&&correct);b.classList.toggle('wrong',answered&&i===chosen&&!correct);b.setAttribute('aria-pressed',String(answered&&i===chosen));});
        const right=answered&&options[chosen]&&options[chosen].hasAttribute('data-correct');
        feedback.textContent=answered?(right?'Correct.':'Not quite — the highlighted option is the better answer.'):'';feedback.className='check-feedback'+(answered?(right?' good':' bad'):'');
        explanation.hidden=!answered;retry.hidden=!answered;
      }
      render();
    });
  }
  function openAnchor(){
    if(!location.hash)return;
    let id;try{id=decodeURIComponent(location.hash.slice(1));}catch(e){return;}
    const target=document.getElementById(id);if(!target)return;
    let parent=target.closest('details');while(parent){parent.open=true;parent=parent.parentElement.closest('details');}
    if(target.classList.contains('week-section')){const wanted=data.sessions.find(s=>s.id===state.last),entries=$$('.session',target);(entries.find(e=>wanted&&e.dataset.sessionId===wanted.id)||entries.find(e=>!state.completed.includes(e.dataset.sessionId))||entries[0])?.setAttribute('open','');}
    setTimeout(()=>target.scrollIntoView({block:'start'}),40);
  }
  sessionize();setupChecks();updateProgress();openAnchor();window.addEventListener('hashchange',openAnchor);
  $$('[data-expand-all]').forEach(b=>b.addEventListener('click',()=>$$('.session,.reference-section').forEach(e=>e.open=true)));
  $$('[data-collapse-all]').forEach(b=>b.addEventListener('click',()=>{$$('.session,.reference-section').forEach(e=>e.open=false);const t=$('.session:not([data-complete=true])')||$('.session');if(t)t.open=true;}));
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
      return Promise.all(data.search.map(async p=>{try{const response=await fetch(localHref(p.href));if(!response.ok)throw new Error('Page unavailable');const doc=new DOMParser().parseFromString(await response.text(),'text/html');return {...p,title:doc.querySelector('h1')?.textContent||p.title,text:(doc.querySelector('article')||doc.querySelector('main')).textContent.replace(/\s+/g,' ')};}catch(error){return {...p,text:p.title,localOnly:true};}}));
    })();
    return searchPagesPromise;
  }
  $('#search-input').addEventListener('input',async e=>{
    const sequence=++searchSequence,query=e.target.value.trim().toLowerCase(),result=$('#search-results');
    result.replaceChildren();
    if(query.length<2){result.textContent='Type at least two characters to search all course material.';return;}
    result.textContent='Searching course pages…';
    const pages=await searchPages();if(sequence!==searchSequence)return;result.replaceChildren();
    const normalized=s=>s.toLowerCase().replace(/\bweek\s+0*(\d+)\b/g,'week $1'),needle=normalized(query);
    const score=p=>(normalized(p.title).includes(needle)?30:0)+normalized(p.text).split(needle).length-1;
    const matches=pages.filter(p=>normalized(p.title+' '+p.text).includes(needle)).sort((a,b)=>score(b)-score(a)).slice(0,12);
    matches.forEach(p=>{const at=normalized(p.text).indexOf(needle);result.append(el('a',{class:'search-hit',href:localHref(p.href)},el('strong',{text:p.title}),el('p',{text:(at>60?'…':'')+p.text.slice(Math.max(0,at-60),Math.max(0,at-60)+190)+'…'})));});
    if(!matches.length)result.textContent='No matching lesson text.';
    if(pages.some(p=>p.localOnly))result.append(el('p',{class:'muted',text:'Some pages are searchable by title only. Full-text search needs this folder served over HTTP/HTTPS.'}));
  });
  $('#export-progress').addEventListener('click',()=>{const blob=new Blob([JSON.stringify({version:1,course:'agents',exported_at:new Date().toISOString(),...state},null,2)],{type:'application/json'});const url=URL.createObjectURL(blob),a=el('a',{href:url,download:'agents-course-progress.json'});a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
  $('#import-progress').addEventListener('change',async e=>{const file=e.target.files[0];if(!file)return;try{if(file.size>100000)throw new Error('Backup is too large.');const raw=JSON.parse(await file.text());if(raw.version!==1||raw.course!=='agents'||!Array.isArray(raw.completed)||raw.completed.some(x=>!known.has(x)))throw new Error('Use an exported agents course backup.');state=cleanState(raw);save();$('#import-status').textContent=`Imported ${state.completed.length} completed sessions.`;}catch(error){$('#import-status').textContent=error.message;}e.target.value='';});
  $('#reset-progress').addEventListener('click',()=>{state={completed:[],last:null,checks:{}};save();$('#import-status').textContent='Saved progress reset.';});

  // ------------------------------------------------------------------ shared rendering helpers
  const pretty=o=>JSON.stringify(o,null,2);
  const fmt=(n,d=3)=>n===null||n===undefined?'—':Number(n).toFixed(d).replace(/\.?0+$/,'')||'0';
  const money=n=>n===null||n===undefined?'—':n<0.01?'$'+n.toFixed(4):'$'+n.toFixed(3);
  function stepCard(step,opts={}){
    if('final' in step)return el('li',{class:'trace-step final'},el('div',{class:'trace-head'},el('span',{class:'trace-n',text:String(step.n).padStart(2,'0')}),el('strong',{text:'Final answer'}),el('span',{class:'trace-ctx',text:`~${step.context_tokens} tokens in context`})),el('p',{class:'trace-final',text:step.final}));
    const err=step.result&&step.result.error;
    const li=el('li',{class:'trace-step'+(err?' has-error':'')},
      el('div',{class:'trace-head'},el('span',{class:'trace-n',text:String(step.n).padStart(2,'0')}),el('code',{class:'trace-call',text:`${step.tool}(${Lab.compact(step.args)})`}),el('span',{class:'trace-ctx',text:`~${step.context_tokens} tokens in context`})),
      step.note?el('p',{class:'trace-note',text:step.note}):null,
      err?el('p',{class:'trace-error'},el('strong',{text:err}),' — ',step.result.message||''):null,
      el('details',{class:'trace-result',open:opts.open?true:null},el('summary',{text:err?'Tool result returned to the model':'Tool result'}),el('pre',{},el('code',{text:pretty(step.result)}))));
    return li;
  }
  function checkList(checks){return el('ul',{class:'check-list'},Object.entries(checks).map(([name,ok])=>el('li',{class:ok?'ok':'fail'},el('span',{'aria-hidden':'true',text:ok?'✓':'✗'}),' ',name,el('span',{class:'sr-only',text:ok?' passed':' failed'}))));}
  function contextBars(steps,total){
    const max=Math.max(total,...steps.map(s=>s.context_tokens),1);
    return el('div',{class:'ctx-bars','aria-label':'Context size at each step'},steps.map(s=>el('div',{class:'ctx-bar'},el('span',{text:String(s.n).padStart(2,'0')}),el('div',{class:'ctx-track'},el('div',{class:'ctx-fill'+('final' in s?' final':''),style:`width:${Math.max(2,100*s.context_tokens/max)}%`})),el('small',{text:String(s.context_tokens)}))));
  }

  // ------------------------------------------------------------------ workbench: agent loop
  if(page==='loop.html')setupLoop();
  function setupLoop(){
    const taskSel=$('#loop-task'),modelSel=$('#loop-model'),budget=$('#loop-budget'),fault=$('#loop-fault');
    data.tasks.forEach(t=>taskSel.append(el('option',{value:t.id,text:`${t.title} — ${t.id}`})));
    const params=new URLSearchParams(location.search);
    if(params.get('task')&&data.tasks.some(t=>t.id===params.get('task')))taskSel.value=params.get('task');
    if(['careful','eager'].includes(params.get('model')))modelSel.value=params.get('model');
    let record,cursor=0;
    function options(){return {model:modelSel.value,max_steps:Number(budget.value),fault:fault.value,retry_transient:$('#loop-retry').checked,detect_repeats:$('#loop-repeats').checked,action_gate:$('#loop-gate').checked};}
    function compute(resetCursor){record=Lab.runAgent(data,taskSel.value,options());cursor=resetCursor?0:record.steps.length;$('#loop-budget-value').textContent=budget.value;render();}
    function render(){
      const task=data.tasks.find(t=>t.id===taskSel.value);
      $('#loop-prompt').textContent=task.prompt;
      const list=$('#loop-steps');list.replaceChildren(...record.steps.slice(0,cursor).map(s=>stepCard(s)));
      if(!cursor)list.append(el('li',{class:'trace-empty',text:'Press “Next step” to let the model choose its first action, or “Run to the end”.'}));
      const finished=cursor>=record.steps.length;
      $('#loop-next').disabled=finished;$('#loop-run').disabled=finished;
      const status=$('#loop-status');status.replaceChildren();
      const shown=record.steps.slice(0,cursor),ctx=shown.length?(cursor<record.steps.length?record.steps[cursor].context_tokens:record.context_tokens):record.steps[0]?.context_tokens||0;
      status.append(el('div',{class:'state-row'},el('span',{text:'Model turns used'}),el('strong',{text:`${cursor} / ${record.options.max_steps}`})));
      status.append(el('div',{class:'state-row'},el('span',{text:'Context now'}),el('strong',{text:`~${ctx} tokens`})));
      if(finished){
        status.append(el('div',{class:'state-row'},el('span',{text:'Stop reason'}),el('strong',{class:record.stop_reason==='final_answer'?'':'warn',text:record.stop_reason.replace('_',' ')})));
        status.append(el('div',{class:'state-row'},el('span',{text:'External side effects'}),el('strong',{class:record.side_effects.length?'bad':'',text:record.side_effects.length?record.side_effects.map(e=>e.tool).join(', '):'none'})));
        status.append(el('h3',{text:'End-state checks'}),checkList(record.checks));
        status.append(el('p',{class:'verdict '+(record.success?'good':'bad'),text:record.success?'Task succeeded.':'Task did not succeed.'}));
      }else status.append(el('p',{class:'muted',text:'Checks appear when the run stops.'}));
      $('#loop-context').replaceChildren(shown.length?contextBars(shown,record.context_tokens):el('p',{class:'muted',text:'Nothing has entered the context yet beyond the system prompt and task.'}));
      const messages=[{role:'system',content:data.world.system_prompt},{role:'user',content:task.prompt}];
      shown.forEach(s=>{if('final' in s)messages.push({role:'assistant',content:s.final});else{messages.push({role:'assistant',tool_call:{tool:s.tool,args:s.args}});messages.push({role:'tool',name:s.tool,content:Lab.compact(s.result)});}});
      $('#loop-messages').textContent=pretty(messages);
    }
    $('#loop-next').addEventListener('click',()=>{cursor=Math.min(cursor+1,record.steps.length);render();$('#loop-steps').lastElementChild?.scrollIntoView({block:'nearest'});});
    $('#loop-run').addEventListener('click',()=>{cursor=record.steps.length;render();});
    $('#loop-reset').addEventListener('click',()=>{cursor=0;render();});
    taskSel.addEventListener('change',()=>compute(true));
    [modelSel,budget,fault,$('#loop-retry'),$('#loop-repeats'),$('#loop-gate')].forEach(c=>c.addEventListener(c.type==='range'?'input':'change',()=>compute(false)));
    $$('[data-loop-preset]').forEach(b=>b.addEventListener('click',()=>{const p=JSON.parse(b.dataset.loopPreset);taskSel.value=p.task;modelSel.value=p.model||'careful';budget.value=p.max_steps||6;fault.value=p.fault||'none';$('#loop-retry').checked=p.retry!==false;$('#loop-repeats').checked=p.repeats!==false;$('#loop-gate').checked=p.gate!==false;compute(false);$('#loop-steps').scrollIntoView({block:'start'});}));
    compute(true);
  }
  // Mini loop on the introduction page.
  $$('[data-mini-loop]').forEach(box=>{
    const record=Lab.runAgent(data,box.dataset.miniLoop||'rollback-check',{});let cursor=0;
    const list=el('ol',{class:'trace-list mini'}),next=el('button',{class:'button primary',type:'button',text:'Next step'}),restart=el('button',{class:'button',type:'button',text:'Restart'}),phase=el('p',{class:'mini-phase','aria-live':'polite'});
    function render(){list.replaceChildren(...record.steps.slice(0,cursor).map(s=>stepCard(s)));next.disabled=cursor>=record.steps.length;const s=record.steps[cursor-1];phase.textContent=!s?'The model has the system prompt, the task and the tool list. Nothing else.':('final' in s)?'The model decided it had enough evidence and stopped. The loop ends on a final answer.':`The model chose ${s.tool}. The harness validated the arguments, ran the tool and appended the result to the context.`;}
    next.addEventListener('click',()=>{cursor++;render();});restart.addEventListener('click',()=>{cursor=0;render();});
    box.append(el('p',{class:'mini-task'},el('strong',{text:'Task: '}),data.tasks.find(t=>t.id===record.task).prompt),phase,list,el('div',{class:'mini-actions'},next,restart,el('a',{href:localHref('loop.html'),text:'Open the full loop workbench ↗'})));render();
  });

  // ------------------------------------------------------------------ workbench: tool contracts
  if(page==='tools.html')setupTools();
  function setupTools(){
    const toolSel=$('#tool-select'),presetSel=$('#preset-select'),defBox=$('#tool-definition'),argBox=$('#tool-args');
    data.tools.forEach(t=>toolSel.append(el('option',{value:t.name,text:t.name+(t.side_effect?' — side effect':'')})));
    function currentTool(){try{return {tool:JSON.parse(defBox.value),error:null};}catch(e){return {tool:null,error:e.message};}}
    function loadTool(){const t=data.tools.find(x=>x.name===toolSel.value);defBox.value=pretty(t);presetSel.replaceChildren(...data.arg_presets[t.name].map((p,i)=>el('option',{value:i,text:p.label})));loadPreset();}
    function loadPreset(){argBox.value=pretty(data.arg_presets[toolSel.value][Number(presetSel.value)].args);render();}
    function render(){
      const lint=$('#tool-lint'),out=$('#tool-result'),verdict=$('#tool-verdict');lint.replaceChildren();out.textContent='';
      const {tool,error}=currentTool();
      if(error){lint.append(el('li',{class:'fail',text:'Tool definition is not valid JSON: '+error}));verdict.textContent='';return;}
      const notes=Lab.lintTool(tool);
      if(notes.length)notes.forEach(n=>lint.append(el('li',{class:'warn',text:n})));else lint.append(el('li',{class:'ok',text:'No issues found by the heuristic review.'}));
      let args;try{args=JSON.parse(argBox.value);}catch(e){verdict.className='verdict bad';verdict.textContent='The model produced text that is not JSON. Most providers reject this before your tool runs; record it as a malformed call.';return;}
      const problems=Lab.validate(tool.input_schema||{},args);
      if(problems.length){verdict.className='verdict bad';verdict.textContent=`${problems.length} problem${problems.length>1?'s':''}: the tool does not run. This structured error goes back to the model:`;out.textContent=pretty({error:'invalid_arguments',details:problems,message:'Fix the listed fields and call again.',retryable:false});return;}
      const known=data.tools.find(x=>x.name===tool.name);
      if(!known){verdict.className='verdict good';verdict.textContent='Arguments are valid for this definition. (No fictional implementation exists for a renamed tool, so nothing runs.)';return;}
      const env=Lab.makeEnv(data,'none');const result=env.call(tool.name,args,$('#tool-gate').checked);
      verdict.className='verdict '+(result.error?'warn':'good');
      verdict.textContent=result.error?'Arguments are valid, but the action gate stopped the call:':(known.side_effect?'Arguments are valid and the gate is off: the fictional side effect ran.':'Arguments are valid. The fictional tool ran and returned:');
      out.textContent=pretty(result);
    }
    toolSel.addEventListener('change',loadTool);presetSel.addEventListener('change',loadPreset);
    defBox.addEventListener('input',render);argBox.addEventListener('input',render);$('#tool-gate').addEventListener('change',render);
    $('#reset-tool').addEventListener('click',loadTool);
    loadTool();
  }

  // ------------------------------------------------------------------ workbench: guardrails
  if(page==='guardrails.html')setupGuard();
  function setupGuard(){
    const boxes=$$('[data-defense]');
    const presets={none:[],approval:['require_approval'],all:Lab.DEFENSES};
    function render(){
      const on=boxes.filter(b=>b.checked).map(b=>b.dataset.defense);
      const results=data.scenarios.map(s=>Lab.gate(s,on)),sum=Lab.summarize(data.scenarios,results);
      const harmful=data.scenarios.filter(s=>s.harmful).length,legit=data.scenarios.length-harmful;
      $('#guard-harm').textContent=`${sum.harmful_executed} / ${harmful}`;$('#guard-harm').closest('.metric-card').classList.toggle('alarm',sum.harmful_executed>0);
      $('#guard-friction').textContent=`${sum.legitimate_stopped} / ${legit}`;
      $('#guard-held').textContent=String(sum.held_for_person);
      const grid=$('#guard-grid');grid.replaceChildren();
      data.scenarios.forEach((s,i)=>{
        const r=results[i],cls=r.harm?'harm':(!s.harmful&&(r.outcome==='blocked'||r.outcome==='held'))?'friction':'safe';
        const ap=s.approval?`approval: ${s.approval.by} (${s.approval.role})`:'no approval';
        grid.append(el('article',{class:'scenario '+cls},
          el('div',{class:'scenario-top'},el('code',{text:s.tool}),el('span',{class:'outcome '+r.outcome,text:r.outcome})),
          el('h3',{text:s.title}),el('p',{text:s.story}),
          el('div',{class:'result-badges'},el('span',{class:'badge',text:ap}),s.tainted?el('span',{class:'badge bad',text:'untrusted content in context'}):null,s.egress?el('span',{class:'badge',text:'to '+s.egress}):null,el('span',{class:'badge '+(s.harmful?'bad':'good'),text:s.harmful?'should not happen':'legitimate'})),
          el('p',{class:'scenario-reason'},el('strong',{text:r.by?r.by.replace(/_/g,' ')+': ':'Result: '}),r.reason),
          r.harm?el('p',{class:'scenario-harm',text:'Harm: '+s.harm}):null));
      });
    }
    boxes.forEach(b=>b.addEventListener('change',render));
    $$('[data-guard-preset]').forEach(b=>b.addEventListener('click',()=>{const p=presets[b.dataset.guardPreset];boxes.forEach(x=>x.checked=p.includes(x.dataset.defense));render();}));
    render();
  }

  // ------------------------------------------------------------------ workbench: evals
  if(page==='evals.html')setupEvals();
  function setupEvals(){
    const kSel=$('#eval-k'),steps=$('#eval-steps'),price=$('#eval-price');let selected=null;
    function graders(){return {end_state:$('#g-end').checked,no_forbidden_attempt:$('#g-forbidden').checked,cites_required:$('#g-cite').checked,max_steps:Number(steps.value)||0};}
    function render(){
      const k=Number(kSel.value),r=Lab.report(data.trials,graders(),k,Number(price.value)||0);
      $('#eval-at').textContent=fmt(r.mean_pass_at_k);$('#eval-hat').textContent=fmt(r.mean_pass_hat_k);$('#eval-cost').textContent=money(r.cost_per_success);
      $$('[data-k-label]').forEach(e=>e.textContent=String(k));
      const body=$('#eval-table tbody');body.replaceChildren();
      r.tasks.forEach(t=>body.append(el('tr',{},el('td',{},el('code',{text:t.task})),el('td',{text:`${t.passed} / ${t.n}`}),el('td',{},bar(t.pass_at_k)),el('td',{},bar(t.pass_hat_k)))));
      const matrix=$('#eval-matrix');matrix.replaceChildren();
      Object.entries(data.trials.tasks).forEach(([task,meta])=>{
        const row=el('div',{class:'matrix-row'},el('code',{text:task}));
        data.trials.trials.filter(t=>t.task===task).forEach(t=>{const [ok,reasons]=Lab.gradeTrial(t,r.graders,meta.must_cite);const b=el('button',{type:'button',class:'trial '+(ok?'pass':'fail'),'aria-pressed':String(selected===t),'aria-label':`${task} trial ${t.trial}: ${ok?'pass':'fail'}`,text:String(t.trial)});b.addEventListener('click',()=>{selected=t;render();});row.append(b);if(selected===t)showTrial(t,ok,reasons);});
        matrix.append(row);
      });
      if(!selected)$('#eval-detail').replaceChildren(el('p',{class:'muted',text:'Select a trial to read what happened and which graders it failed.'}));
      const best=r.tasks.find(t=>t.task==='rollback-check');
      $('#eval-explain').textContent=k===1?'With k = 1 both metrics equal the plain pass rate. Increase k to see them separate.':`For rollback-check, pass@${k} = ${fmt(best.pass_at_k)}: if you may try ${k} times and keep any success, you almost always get one. pass^${k} = ${fmt(best.pass_hat_k)}: the chance that ${k} runs in a row all succeed — what a user who runs the agent every day experiences.`;
    }
    function bar(v){return el('span',{class:'mini-bar'},el('span',{class:'track'},el('span',{class:'fill',style:`width:${Math.round(v*100)}%`})),el('b',{text:fmt(v)}));}
    function showTrial(t,ok,reasons){$('#eval-detail').replaceChildren(el('h3',{text:`${t.task} · trial ${t.trial}`}),el('p',{text:t.summary}),el('div',{class:'result-badges'},el('span',{class:'badge',text:`${t.steps} steps`}),el('span',{class:'badge',text:`${t.tokens} tokens`}),el('span',{class:'badge '+(t.end_state_ok?'good':'bad'),text:t.end_state_ok?'end state ok':'end state wrong'}),t.forbidden_attempt?el('span',{class:'badge bad',text:'forbidden attempt'}):null,t.cited_required?null:el('span',{class:'badge bad',text:'no citation'})),el('p',{class:'verdict '+(ok?'good':'bad'),text:ok?'Passes every enabled grader.':'Fails: '+reasons.join('; ')+'.'}));}
    [kSel,steps,price,$('#g-end'),$('#g-forbidden'),$('#g-cite')].forEach(c=>c.addEventListener('input',render));
    render();
  }

  // ------------------------------------------------------------------ workbench: cost
  if(page==='cost.html')setupCost();
  function setupCost(){
    const ids=['steps','base','toolOut','outTokens','keepLast','summaryTokens','cacheHit','cacheMultiplier','shareSmall','smallIn','smallOut','smallSuccess','largeIn','largeOut','largeSuccess'];
    const inputs=Object.fromEntries(ids.map(id=>[id,$('#c-'+id)]));
    function params(){const v=Object.fromEntries(ids.map(id=>[id,Number(inputs[id].value)]));
      return {steps:v.steps,base:v.base,toolOut:v.toolOut,outTokens:v.outTokens,keepLast:v.keepLast||0,summaryTokens:v.summaryTokens,cacheHit:v.cacheHit/100,cacheMultiplier:v.cacheMultiplier,shareSmall:v.shareSmall/100,escalate:$('#c-escalate').checked,
        small:{in:v.smallIn,out:v.smallOut,success:v.smallSuccess/100},large:{in:v.largeIn,out:v.largeOut,success:v.largeSuccess/100}};}
    function render(){
      ids.forEach(id=>{const o=$(`[data-out="${id}"]`);if(o)o.textContent=inputs[id].value;});
      const p=params(),r=Lab.routing(p),noCompact=Lab.contextSeries({...p,keepLast:0});
      $('#c-tokens').textContent=Math.round(r.large.input+r.large.output).toLocaleString();
      $('#c-large').textContent=money(r.large.cost);$('#c-routed').textContent=money(r.cost);
      $('#c-success').textContent=Math.round(r.success*100)+'%';$('#c-cps').textContent=money(r.costPerSuccess);
      const max=Math.max(...noCompact),w=560,h=180,bw=w/p.steps;
      const svg=document.createElementNS('http://www.w3.org/2000/svg','svg');svg.setAttribute('viewBox',`0 0 ${w} ${h+24}`);svg.setAttribute('role','img');
      svg.setAttribute('aria-label',`Input tokens per step: from ${r.large.series[0]} at step 1 to ${r.large.series[p.steps-1]} at step ${p.steps}${p.keepLast?' with compaction':''}.`);
      const ns='http://www.w3.org/2000/svg';
      noCompact.forEach((v,i)=>{const full=document.createElementNS(ns,'rect');full.setAttribute('x',i*bw+1);full.setAttribute('width',Math.max(1,bw-2));full.setAttribute('y',h-h*v/max);full.setAttribute('height',h*v/max);full.setAttribute('class','bar-ghost');svg.append(full);
        const actual=r.large.series[i],bar=document.createElementNS(ns,'rect');bar.setAttribute('x',i*bw+1);bar.setAttribute('width',Math.max(1,bw-2));bar.setAttribute('y',h-h*actual/max);bar.setAttribute('height',h*actual/max);bar.setAttribute('class','bar-real');svg.append(bar);});
      [[0,'step 1'],[p.steps-1,'step '+p.steps]].forEach(([i,t])=>{const tx=document.createElementNS(ns,'text');tx.setAttribute('x',i===0?0:w);tx.setAttribute('y',h+18);tx.setAttribute('text-anchor',i===0?'start':'end');tx.textContent=t;svg.append(tx);});
      const top=document.createElementNS(ns,'text');top.setAttribute('x',0);top.setAttribute('y',12);top.textContent=Math.round(max).toLocaleString()+' tokens';svg.append(top);
      $('#c-chart').replaceChildren(svg);
      const total=noCompact.reduce((s,x)=>s+x,0);
      $('#c-note').textContent=p.keepLast?`Compaction keeps the last ${p.keepLast} turns plus a ${p.summaryTokens}-token summary: ${Math.round(100*(1-r.large.input/total))}% fewer input tokens than without it. Check with your task suite that the summary keeps the facts later steps need.`:`Without compaction every step re-reads all earlier tool results, so input tokens grow with each step and the total grows roughly with the square of the step count.`;
    }
    ids.forEach(id=>inputs[id].addEventListener('input',render));$('#c-escalate').addEventListener('change',render);render();
  }
})();
