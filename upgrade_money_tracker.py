from pathlib import Path
import re

path = Path('app/src/main/assets/index.html')
if not path.exists():
    raise SystemExit('ERROR: Run this from the repository root. index.html not found.')
s = path.read_text()
if 'personGroupKey(' in s:
    raise SystemExit('Already upgraded; no changes made.')
backup = path.with_suffix('.html.before-person-groups')
backup.write_text(s)

def replace_once(pattern, replacement, flags=re.S):
    global s
    s2, count = re.subn(pattern, lambda m: replacement, s, count=1, flags=flags)
    if count != 1:
        raise SystemExit(f'ERROR: Could not locate {pattern[:70]!r}. Original backup at {backup}')
    s = s2

css = '''
.person-card{border:1px solid #e1e7e9;border-radius:14px;margin-bottom:12px;padding:14px;background:#fff}
.person-card.done{background:#eaf9f1;border-color:#b7ebcd}
.person-card h3{margin:0 0 4px;font-size:18px}
.person-card small,.history-item small{color:#72808b}
.person-card .actions{flex-wrap:wrap}
.person-card .actions button{min-width:110px}
.history-item{display:flex;justify-content:space-between;gap:10px;border-bottom:1px solid #e8eef0;padding:13px 0}
.history-item:last-child{border-bottom:0}
.history-item b{white-space:nowrap}
.history-item .actions{margin-top:7px}
.history-item .actions button{padding:7px 10px;min-width:0;flex:0}
.section-label{font-size:13px;color:#687a88;margin:20px 0 6px;text-transform:uppercase;letter-spacing:.04em}
.detail-total{padding:13px;border-radius:12px;background:#f2f7f5;margin:14px 0}
'''
replace_once(r'</style>', css + '</style>', flags=0)
replace_once(r"let section='gave',screen='home',tab='active',search='',editId=null,repayId=null;", "let section='gave',screen='home',tab='active',search='',editId=null,repayId=null,personKey=null;", flags=0)

helpers = r'''
function personGroupKey(name){return String(name||'').trim().replace(/\s+/g,' ').toLocaleLowerCase()}
function personRecords(key){return records.filter(r=>r.section===section&&personGroupKey(r.name)===key).sort((a,b)=>a.date.localeCompare(b.date)||String(a.id).localeCompare(String(b.id)))}
function groupsForSection(){const map=new Map();for(const r of records.filter(r=>r.section===section)){const key=personGroupKey(r.name);if(!map.has(key))map.set(key,{key,name:r.name,items:[]});map.get(key).items.push(r)}return [...map.values()].map(g=>({...g,total:g.items.reduce((a,r)=>a+Number(r.amount),0),returned:g.items.reduce((a,r)=>a+paid(r),0),latest:g.items.reduce((a,r)=>r.date>a?r.date:a,'')}))}
function groupPending(g){return Math.max(0,Math.round((g.total-g.returned)*100)/100)}
function openPerson(key){personKey=key;nav('person')}
function openAddForPerson(){editId=null;nav('form')}
function closeToPerson(){nav('person')}
function historyFor(items){const history=[];const byId=new Map();for(const r of items){history.push({type:'given',date:r.date,id:r.id,amount:Number(r.amount),notes:r.notes||'',record:r});for(const p of r.payments){const id=p.id||('legacy-'+r.id+'-'+p.date+'-'+p.amount);if(byId.has(id)){byId.get(id).amount+=Number(p.amount)}else{const h={type:'repay',date:p.date,id,amount:Number(p.amount),notes:p.notes||''};byId.set(id,h);history.push(h)}}}return history.sort((a,b)=>b.date.localeCompare(a.date)||(a.type==='repay'?-1:1))}
function deletePersonTransaction(id){removeRecord(id)}
'''
replace_once(r'function persist\(\)', helpers + '\nfunction persist()', flags=0)

render = r'''function render(){const app=$('app');if(screen==='home'){app.innerHTML=`<div class="page"><div class="hero"><h1>My Money Tracker</h1><p>Private • Offline • Just for you</p></div><button class="choice green" onclick="openSection('gave')">↗ &nbsp; Money I Gave <span>›</span></button><button class="choice bluebg" onclick="openSection('took')">↙ &nbsp; Money I Took <span>›</span></button><div class="more"><button onclick="exportData()">⬇ Export backup</button><button onclick="window.AndroidBackup?window.chooseBackup():$('importFile').click()">⬆ Restore backup</button><input class="hidden" id="importFile" type="file" accept="application/json,.json" onchange="importData(event)"></div><div class="notice">Records stay on this device. Back up regularly: clearing app data or uninstalling can erase them.</div></div>`;return}
if(screen==='list'){const groups=groupsForSection(),shown=groups.filter(g=>(tab==='active'?groupPending(g)>0:groupPending(g)===0)&&g.name.toLowerCase().includes(search.toLowerCase())).sort((a,b)=>b.latest.localeCompare(a.latest));const total=groups.reduce((a,g)=>a+g.total,0),returned=groups.reduce((a,g)=>a+g.returned,0);app.innerHTML=head(title())+`<div class="page"><div class="summary"><div class="stat"><small>${section==='gave'?'Given':'Taken'}</small><strong>${fmt(total)}</strong></div><div class="stat"><small>Returned</small><strong class="ok">${fmt(returned)}</strong></div><div class="stat"><small>Pending</small><strong class="red">${fmt(total-returned)}</strong></div></div><div class="tabs"><button class="${tab==='active'?'active':''}" onclick="setTab('active')">Active (${groups.filter(g=>groupPending(g)>0).length})</button><button class="${tab==='returned'?'active':''}" onclick="setTab('returned')">Returned (${groups.filter(g=>groupPending(g)===0).length})</button></div><input class="search" placeholder="Search by name" value="${esc(search)}" oninput="setSearch(this.value)"><div id="entries">${shown.length?shown.map(g=>`<div class="person-card ${groupPending(g)===0?'done':''}"><div class="entryTop"><div><h3>${esc(g.name)}</h3><small>${g.items.length} transaction${g.items.length===1?'':'s'}</small></div>${groupPending(g)===0?'<span class="badge">✓ Returned</span>':''}</div><div class="amounts"><div><small>${section==='gave'?'Given':'Taken'}</small><b>${fmt(g.total)}</b></div><div><small>Returned</small><b class="ok">${fmt(g.returned)}</b></div><div><small>Pending</small><b class="${groupPending(g)?'red':'ok'}">${fmt(groupPending(g))}</b></div></div><div class="actions"><button onclick="openPerson(decodeURIComponent('${encodeURIComponent(g.key)}'))">View History ›</button></div></div>`).join(''):'<div class="empty">No records here yet.</div>'}</div></div><div class="bottom"><button class="primary ${section==='took'?'bluebg':''}" onclick="openAdd()">＋ Add New Record</button></div>`;return}
if(screen==='person'){const items=personRecords(personKey);if(!items.length){nav('list');return}const name=items[items.length-1].name,total=items.reduce((a,r)=>a+Number(r.amount),0),returned=items.reduce((a,r)=>a+paid(r),0),pending=Math.max(0,Math.round((total-returned)*100)/100),history=historyFor(items);app.innerHTML=head(esc(name))+`<div class="page"><div class="summary"><div class="stat"><small>${section==='gave'?'Given':'Taken'}</small><strong>${fmt(total)}</strong></div><div class="stat"><small>Returned</small><strong class="ok">${fmt(returned)}</strong></div><div class="stat"><small>Pending</small><strong class="${pending?'red':'ok'}">${fmt(pending)}</strong></div></div>${pending===0?'<p class="badge">✓ Fully returned</p>':''}<div class="actions"><button onclick="openAddForPerson()">＋ Add Money</button>${pending>0?'<button onclick="openGroupRepay()">＋ Repayment</button>':''}</div><h3 class="section-label">Transaction history</h3>${history.map(h=>`<div class="history-item"><div><strong>${h.type==='given'?(section==='gave'?'Money given':'Money taken'):'Repayment'}</strong><br><small>${date(h.date)}${h.notes?' · '+esc(h.notes):''}</small>${h.type==='given'?`<div class="actions"><button onclick="openEdit('${h.id}')">Edit</button><button class="danger" onclick="deletePersonTransaction('${h.id}')">Delete</button></div>`:''}</div><b class="${h.type==='repay'?'ok':''}">${h.type==='repay'?'−':'+'}${fmt(h.amount)}</b></div>`).join('')}</div><div class="bottom"><button class="primary ${section==='took'?'bluebg':''}" onclick="openAddForPerson()">＋ Add Money</button></div>`;return}
if(screen==='form'){let r=records.find(x=>x.id===editId);let items=personKey?personRecords(personKey):[],defaultName=!r&&items.length?items[items.length-1].name:'';app.innerHTML=head(r?'Edit Record':'Add New Record')+`<form id="recordForm" class="page" onsubmit="saveRecord(event)"><label for="name">Person Name</label><input id="name" required maxlength="100" placeholder="Enter name" value="${esc(r?.name||defaultName)}"><label for="amount">Amount ${section==='gave'?'Given':'Taken'} (₹)</label><input id="amount" type="number" min="0.01" step="0.01" required inputmode="decimal" value="${r?.amount||''}"><label for="date">Date</label><input id="date" type="date" required value="${r?.date||today()}"><label for="notes">Notes (optional)</label><textarea id="notes" placeholder="Reason, UPI, etc.">${esc(r?.notes||'')}</textarea><div class="bottom"><button class="primary ${section==='took'?'bluebg':''}" type="submit">Save Record</button></div></form>`;return}
if(screen==='repay'){const items=personRecords(personKey);if(!items.length){nav('list');return}const total=items.reduce((a,r)=>a+Number(r.amount),0),returned=items.reduce((a,r)=>a+paid(r),0),pending=Math.max(0,Math.round((total-returned)*100)/100);app.innerHTML=head('Record Repayment')+`<div class="page"><h2>${esc(items[items.length-1].name)}</h2><p class="muted">Total: ${fmt(total)} · Returned: ${fmt(returned)}</p><h3 class="red">Pending: ${fmt(pending)}</h3><div class="notice">Repayment is automatically applied to the oldest unpaid transaction first.</div><form onsubmit="saveRepayment(event)"><label for="repayAmount">Amount Returned (₹)</label><input id="repayAmount" type="number" min="0.01" max="${pending}" step="0.01" required inputmode="decimal"><label for="repayDate">Date</label><input id="repayDate" type="date" required value="${today()}"><label for="repayNotes">Notes (optional)</label><textarea id="repayNotes" placeholder="Cash, UPI, etc."></textarea><div class="bottom"><button class="primary ${section==='took'?'bluebg':''}" type="submit">Save Repayment</button></div></form></div>`;return}}
'''
replace_once(r'function render\(\).*?(?=function openSection\()', render, flags=re.S)

navigation = r'''function openSection(s){section=s;tab='active';search='';personKey=null;nav('list')}function setTab(t){tab=t;render()}function setSearch(v){search=v;render();const inp=document.querySelector('.search');if(inp){inp.focus();inp.setSelectionRange(v.length,v.length)}}function openAdd(){personKey=null;editId=null;nav('form')}function openEdit(id){editId=id;const r=records.find(x=>x.id===id);if(r)personKey=personGroupKey(r.name);nav('form')}function openGroupRepay(){nav('repay')}
'''
replace_once(r'function openSection\(s\).*?(?=function saveRecord\()', navigation, flags=re.S)

save_record = r'''function saveRecord(e){e.preventDefault();const name=$('name').value.trim(),amount=Number($('amount').value),dt=$('date').value,notes=$('notes').value.trim();if(!name||!Number.isFinite(amount)||amount<=0||!dt)return alert('Please enter valid details.');let r=records.find(x=>x.id===editId);if(r){if(amount+0.000001<paid(r))return alert('Amount cannot be less than already returned.');Object.assign(r,{name,amount,date:dt,notes})}else records.push({id:crypto.randomUUID(),section,name,amount,date:dt,notes,payments:[]});personKey=personGroupKey(name);persist();nav('person')}
function saveRepayment(e){e.preventDefault();const items=personRecords(personKey);const amount=Number($('repayAmount').value);const pending=Math.round(items.reduce((a,r)=>a+balance(r),0)*100)/100;const dt=$('repayDate').value;if(!items.length||!Number.isFinite(amount)||amount<=0||Math.round(amount*100)!==amount*100||amount>pending+0.000001||!dt)return alert('Enter a valid repayment up to the pending balance.');let remaining=Math.round(amount*100);const paymentId=crypto.randomUUID();for(const r of items){const available=Math.round(balance(r)*100);const used=Math.min(available,remaining);if(used>0){r.payments.push({id:paymentId,amount:used/100,date:dt,notes:$('repayNotes').value.trim()});remaining-=used}if(remaining===0)break}if(remaining!==0)return alert('Unable to allocate repayment. No changes saved.');persist();nav('person')}
'''
replace_once(r'function saveRecord\(e\).*?(?=function removeRecord\()', save_record, flags=re.S)

# Return from confirmation to person screen if the person has more transactions.
s=s.replace("    render();\n  };\n}\nfunction exportData", "    if(screen==='person' && personRecords(personKey).length===0){nav('list');}else{render();}\n  };\n}\nfunction exportData",1)
# Change header back behavior for detail screen.
s=s.replace("screen==='list'?'home':'list'", "screen==='list'?'home':(screen==='person'?'list':(personKey?'person':'list'))",1)
path.write_text(s)
print('SUCCESS: Grouped people, Add Money, oldest-first repayments, and history installed.')
print('Original backed up at:', backup)
