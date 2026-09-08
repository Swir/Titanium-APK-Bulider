(function(){
'use strict';
if(window.SWIR_APP&&window.SWIR_APP.version==='0.2.0')return;

const VERSION='0.2.0';
const LS={friends:'swir_app_friends',server:'swir_app_server_friends',seen:'swir_app_last_seen',chns:'swir_app_chns_text',theme:'swir_app_theme',sound:'swir_app_sound'};
const state={serverFresh:false,last159:0,wrapped:new WeakSet(),observer:null};
const $=(s,r=document)=>r.querySelector(s);
const $$=(s,r=document)=>[...r.querySelectorAll(s)];
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const key=v=>String(v||'').trim().toLocaleLowerCase('pl-PL');
const load=(k,d)=>{try{const v=localStorage.getItem(k);return v===null?d:JSON.parse(v)}catch(e){return d}};
const save=(k,v)=>{try{localStorage.setItem(k,JSON.stringify(v))}catch(e){}};

function accent(){const t=load(LS.theme,'cyber');return({cyber:'#00e5ff',matrix:'#00ff88',ocean:'#47a7ff',amber:'#ffd166'})[t]||'#00e5ff'}
function applyTheme(){
 const a=accent();document.documentElement.style.setProperty('--swir-app-a',a);
 let st=$('#swir-app-style');if(!st){st=document.createElement('style');st.id='swir-app-style';document.head.appendChild(st)}
 st.textContent=`:root{--swir-app-a:${a}}body{background:#08111b!important}[id^="m-messages_"],.m-messagesTextArea,.m-usersList,[id^="m-users_"]{background:#0b1420!important;color:#e9f3fc!important;border-color:var(--swir-app-a)!important}.m-msg-item,.m-msg-item *,.m-topic-message,.m-topic-intro{color:#e8f0f8!important}.m-msg-item-user-login,.info-user-login{color:var(--swir-app-a)!important;font-weight:700!important}[id^="m-textMessage-"],input.text-input,textarea.text-input{background:#050b12!important;color:#eef8ff!important;border:1px solid var(--swir-app-a)!important}.button-send,[id^="m-sendMessage-button-"]{background:var(--swir-app-a)!important;color:#041018!important}.m-room,.m-category,.m-room-list{background:#0b1420!important;color:#dceaf7!important}.swir-mentioned{border-left:3px solid var(--swir-app-a)!important;background:color-mix(in srgb,var(--swir-app-a) 10%,transparent)!important}`;
}

function modal(id,title,html,width='760px'){
 $('#'+id)?.remove();const wrap=document.createElement('div');wrap.id=id;
 wrap.style.cssText='position:fixed;inset:0;z-index:2147483000;background:#000b;backdrop-filter:blur(5px);display:flex;align-items:center;justify-content:center;padding:16px;font-family:Arial,sans-serif';
 const box=document.createElement('div');box.style.cssText=`width:min(${width},95vw);max-height:90vh;overflow:auto;background:#0b1420;color:#eaf5ff;border:1px solid var(--swir-app-a,#00e5ff);border-radius:16px;box-shadow:0 24px 80px #000;padding:14px`;
 box.innerHTML=`<div style="display:flex;align-items:center;gap:8px;margin-bottom:12px"><b style="color:var(--swir-app-a);font-size:17px;flex:1">${title}</b><button data-close style="background:#142235;color:white;border:1px solid #345;border-radius:8px;padding:6px 10px">✕</button></div>${html}`;
 wrap.appendChild(box);document.body.appendChild(wrap);$('[data-close]',box).onclick=()=>wrap.remove();wrap.onclick=e=>{if(e.target===wrap)wrap.remove()};return{wrap,box};
}

function scanChns(){
 if(typeof CHNS==='undefined')return'CHNS [niedostępny]';const out=[];
 Object.keys(CHNS).sort().forEach(n=>{let v;try{v=CHNS[n]}catch(e){return}const typ=typeof v;out.push(`CHNS.${n} [${typ}]`);if(v&&(typ==='object'||typ==='function')){const methods=new Set();try{Object.keys(v).forEach(m=>{try{if(typeof v[m]==='function')methods.add(m)}catch(e){}})}catch(e){}try{const p=typ==='function'?v.prototype:Object.getPrototypeOf(v);if(p)Object.getOwnPropertyNames(p).forEach(m=>{if(m!=='constructor'){try{if(typeof p[m]==='function')methods.add(m)}catch(e){}}})}catch(e){}[...methods].sort().forEach(m=>out.push(`  • CHNS.${n}.${m}()`))}});return out.join('\n');
}
function openChns(){
 const m=modal('swir-app-chns','🧩 CHNS LAB — autosave','<div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:8px"><button data-scan>🔄 Nowy skan</button><button data-append>➕ Dołącz skan</button><button data-copy>📋 Kopiuj</button><span data-state style="margin-left:auto;color:#79eab5;font-size:11px">● autosave</span></div><textarea data-text spellcheck="false" style="width:100%;height:60vh;box-sizing:border-box;background:#050b12;color:#e5f1fb;border:1px solid #294157;border-radius:10px;padding:10px;font:12px/1.45 Consolas,monospace;resize:none"></textarea><div style="font-size:10px;color:#7890a5;margin-top:7px">To lokalny edytowalny notatnik diagnostyczny. Nie wykonuje wpisanej treści i nie zmienia uprawnień serwera.</div>','900px');
 const ta=$('[data-text]',m.box),st=$('[data-state]',m.box);ta.value=localStorage.getItem(LS.chns)||scanChns();let tm=0;const persist=()=>{localStorage.setItem(LS.chns,ta.value);st.textContent='✅ zapisano '+new Date().toLocaleTimeString()};ta.oninput=()=>{st.textContent='● zapisuję…';clearTimeout(tm);tm=setTimeout(persist,450)};$('[data-scan]',m.box).onclick=()=>{if(confirm('Zastąpić edycję świeżym skanem?')){ta.value=scanChns();persist()}};$('[data-append]',m.box).onclick=()=>{ta.value+='\n\n===== SKAN '+new Date().toLocaleString()+' =====\n'+scanChns();persist()};$('[data-copy]',m.box).onclick=async()=>{try{await navigator.clipboard.writeText(ta.value)}catch(e){ta.select();document.execCommand('copy')}st.textContent='📋 skopiowano'};m.wrap.addEventListener('click',e=>{if(e.target===m.wrap)persist()});
}

function serverState(){const s=load(LS.server,{updatedAt:0,users:{}});if(!s.users)s.users={};return s}
function remember(name,rooms){if(!rooms.length)return;const s=load(LS.seen,{});s[key(name)]={name,rooms:[...new Set(rooms)],ts:Date.now()};save(LS.seen,s)}
function roomNames(v){return[...new Set((Array.isArray(v)?v:[]).map(r=>typeof r==='string'?r:r&&r.name).filter(Boolean).map(String))]}
function ingest159(p){
 if(!p||!Array.isArray(p.users))return;const s={updatedAt:Date.now(),users:{}};p.users.forEach(u=>{if(!u||!u.name)return;const rooms=roomNames(u.rooms);s.users[key(u.name)]={id:u.id??null,name:String(u.name),rooms,ts:Date.now()};remember(u.name,rooms)});save(LS.server,s);state.serverFresh=true;state.last159=Date.now();window.dispatchEvent(new CustomEvent('swir-app-friends',{detail:{count:Object.keys(s.users).length}}));
}
function handlePacket(p){if(!p||typeof p!=='object')return;const c=Number(p.code);if(c===159)ingest159(p);else if(c===163&&Array.isArray(p.users)){const s=serverState();p.users.forEach(u=>{if(u&&u.name){const rooms=roomNames(u.rooms);s.users[key(u.name)]={id:u.id??null,name:String(u.name),rooms,ts:Date.now()};remember(u.name,rooms)}});s.updatedAt=Date.now();save(LS.server,s)}}
function connections(){
 const set=new Set();try{if(!CHNS||!CHNS.connManager)return[];try{const c=CHNS.connManager.getCurrentConnection?.();if(c)set.add(c)}catch(e){}try{const c=CHNS.connManager.getFirstConnection?.();if(c)set.add(c)}catch(e){}try{const channels=CHNS.channelManager?.channels||{};Object.values(channels).forEach(ch=>{try{const id=ch?.getChannelId?.();if(id!==undefined&&id!==null){const c=CHNS.connManager.getConnectionRelatedWithId?.(id);if(c)set.add(c)}}catch(e){}})}catch(e){}}catch(e){}return[...set]
}
function wrapConn(c){
 try{if(!c||state.wrapped.has(c)||typeof c.processMessage!=='function')return;const orig=c.processMessage;c.processMessage=function(ev){try{const raw=typeof ev==='string'?ev:(ev&&typeof ev.data==='string'?ev.data:null);if(raw)handlePacket(JSON.parse(raw))}catch(e){}return orig.apply(this,arguments)};state.wrapped.add(c)}catch(e){}
}
function installProtocol(){connections().forEach(wrapConn)}
function requestFriends(show){
 try{installProtocol();const c=connections()[0];if(!c){if(show)alert('Brak aktywnego połączenia z CZATerią.');return false}c.send(JSON.stringify({code:85}));if(show)console.log('SWIR: wysłano code 85');return true}catch(e){if(show)alert('Nie udało się pobrać znajomych: '+e.message);return false}
}
function localFriends(){const a=load(LS.friends,[]);return Array.isArray(a)?a:[]}
function setLocalFriends(a){save(LS.friends,a)}
function serverRecord(n){return serverState().users[key(n)]||null}
function visibleRooms(n){
 const out=[];const r=serverRecord(n);if(state.serverFresh&&r)out.push(...(r.rooms||[]));try{$('[id^="m-users_"]')&&$$('[id^="m-users_"]').forEach(list=>{let found=false;$$('.m-list-user-item',list).forEach(row=>{if(key(row.textContent)===key(n))found=true});if(found){const hash=list.id.replace(/^m-users_/,'');let name='';try{name=CHNS.channelManager.getChannelRelatedWithNameHash(hash)?.getChannelName?.()||''}catch(e){}if(name)out.push(name)}})}catch(e){}const u=[...new Set(out)];remember(n,u);return u
}
function lastSeen(n){const x=load(LS.seen,{})[key(n)];if(!x)return'';return`🕘 ${x.rooms.join(', ')} • ${new Date(x.ts).toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'})}`}
function openFriends(){
 const m=modal('swir-app-friends','🧑‍🤝‍🧑 Znajomi — Mobile Radar 85→159','<div style="display:flex;gap:6px;margin-bottom:8px"><button data-refresh>📡 Pobierz z serwera</button><span data-info style="font-size:11px;color:#8ba2b8;align-self:center"></span></div><input data-search placeholder="Filtruj znajomych…" style="width:100%;box-sizing:border-box;padding:8px;background:#050b12;color:white;border:1px solid #294157;border-radius:8px;margin-bottom:8px"><div data-list></div><div style="display:flex;gap:6px;margin-top:10px"><input data-add placeholder="Dodaj nick do listy SWIR" style="flex:1;padding:8px;background:#050b12;color:white;border:1px solid #294157;border-radius:8px"><button data-plus>➕</button></div>','620px');
 const list=$('[data-list]',m.box),info=$('[data-info]',m.box),search=$('[data-search]',m.box);let locals=localFriends();
 const render=()=>{const ss=serverState(),map=new Map();locals.forEach(n=>map.set(key(n),{name:n,local:true,server:false}));Object.values(ss.users||{}).forEach(r=>{if(!r?.name)return;const k=key(r.name);if(map.has(k))map.get(k).server=true;else map.set(k,{name:r.name,local:false,server:true})});const q=key(search.value);const items=[...map.values()].filter(x=>!q||key(x.name).includes(q)).sort((a,b)=>a.name.localeCompare(b.name,'pl'));info.textContent=`159: ${state.last159?new Date(state.last159).toLocaleTimeString():'—'} • serwer: ${Object.keys(ss.users||{}).length}`;list.innerHTML=items.length?'':'<div style="padding:20px;text-align:center;color:#8499ad">Brak danych. Kliknij 📡.</div>';items.forEach(x=>{const rooms=visibleRooms(x.name);const row=document.createElement('div');row.style.cssText='display:flex;gap:8px;align-items:center;border-bottom:1px solid #ffffff12;padding:8px 2px';row.innerHTML=`<div style="flex:1;min-width:0"><b>${esc(x.name)}</b> ${x.server?'<small style="color:#79eab5">APP</small>':''} ${x.local?'<small style="color:#72cfff">SWIR</small>':''}<div style="font-size:10px;color:#849aaf;margin-top:3px">${esc(rooms.length?'📡 '+rooms.join(', '):(lastSeen(x.name)||'⚪ brak aktywnego pokoju'))}</div></div><button data-find>🔍</button>${x.local?'<button data-del>❌</button>':''}`;$('[data-find]',row).onclick=()=>{const r=visibleRooms(x.name);alert(r.length?`${x.name}: ${r.join(', ')}`:`Brak bieżącej lokalizacji dla ${x.name}. ${lastSeen(x.name)}`)};const d=$('[data-del]',row);if(d)d.onclick=()=>{locals=locals.filter(n=>key(n)!==key(x.name));setLocalFriends(locals);render()};list.appendChild(row)})};
 search.oninput=render;$('[data-refresh]',m.box).onclick=()=>{requestFriends(true);setTimeout(render,1000)};$('[data-plus]',m.box).onclick=()=>{const i=$('[data-add]',m.box),n=i.value.trim();if(n&&!locals.some(x=>key(x)===key(n))){locals.push(n);setLocalFriends(locals)}i.value='';render()};window.addEventListener('swir-app-friends',render,{once:false});render();requestFriends(false);setTimeout(render,1200)
}

function beep(){if(load(LS.sound,true)===false)return;try{const A=window.AudioContext||window.webkitAudioContext;if(!A)return;const a=new A(),o=a.createOscillator(),g=a.createGain();o.frequency.value=720;g.gain.value=.04;o.connect(g);g.connect(a.destination);o.start();o.stop(a.currentTime+.09)}catch(e){}}
function meNick(){try{return CHNS.connManager.getMeUser?.()?.getLogin?.()||''}catch(e){return''}}
function highlightNode(root,notify){const n=meNick();if(!n)return;const rows=[];if(root.matches?.('.m-msg-item'))rows.push(root);rows.push(...$$('.m-msg-item',root));rows.forEach(r=>{if(r.dataset.swirMention)return;r.dataset.swirMention='1';const t=r.textContent||'';if(key(t).includes(key(n))){r.classList.add('swir-mentioned');if(notify)beep()}})}
function installMentionObserver(){if(state.observer)state.observer.disconnect();state.observer=new MutationObserver(ms=>ms.forEach(m=>m.addedNodes.forEach(n=>{if(n.nodeType===1)highlightNode(n,true)})));state.observer.observe(document.body,{childList:true,subtree:true});highlightNode(document.body,false)}
function openPanel(){
 const t=load(LS.theme,'cyber'),snd=load(LS.sound,true)!==false;const m=modal('swir-app-panel','⚡ SWIR Czateria+ v'+VERSION,`<div style="display:grid;gap:10px"><div style="padding:10px;border:1px solid #ffffff15;border-radius:10px"><b>Motyw</b><div style="display:flex;gap:6px;margin-top:7px"><button data-theme="cyber">Cyber</button><button data-theme="matrix">Matrix</button><button data-theme="ocean">Ocean</button><button data-theme="amber">Amber</button></div></div><label style="padding:10px;border:1px solid #ffffff15;border-radius:10px"><input type="checkbox" data-sound ${snd?'checked':''}> Dźwięk przy wzmiance</label><button data-friends>🧑‍🤝‍🧑 Otwórz znajomych</button><button data-chns>🧩 CHNS LAB</button><button data-request>📡 Pobierz friends/rooms (85→159)</button><div style="font-size:11px;color:#8299ae">Aplikacja korzysta z normalnych funkcji klienta. Nie nadaje admin/honour i nie omija CAPTCHA ani uprawnień serwera.</div></div>`,'520px');$$('[data-theme]',m.box).forEach(b=>b.onclick=()=>{save(LS.theme,b.dataset.theme);applyTheme()});$('[data-sound]',m.box).onchange=e=>save(LS.sound,e.target.checked);$('[data-friends]',m.box).onclick=openFriends;$('[data-chns]',m.box).onclick=openChns;$('[data-request]',m.box).onclick=()=>requestFriends(true)
}

function boot(){applyTheme();installProtocol();installMentionObserver();setInterval(installProtocol,3000);setTimeout(()=>requestFriends(false),1800);setInterval(()=>requestFriends(false),60000);console.log('SWIR Czateria+ v'+VERSION+' ready')}
window.SWIR_APP={version:VERSION,openPanel,openFriends,openChns,requestFriends,scanChns,serverState,visibleRooms,applyTheme};
boot();
})();
