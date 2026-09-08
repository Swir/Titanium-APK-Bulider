(function(){
'use strict';
if(window.SWIR_PATCH&&window.SWIR_PATCH.version==='0.3.0')return;
const VERSION='0.3.0';
const $=(s,r=document)=>r.querySelector(s);
const $$=(s,r=document)=>[...r.querySelectorAll(s)];
const seenGif=new WeakSet();

function toast(msg){
 try{if(window.SwirAndroid&&typeof SwirAndroid.toast==='function'){SwirAndroid.toast(String(msg));return}}catch(e){}
 try{console.log('[SWIR]',msg)}catch(e){}
}
function copyText(text,label){
 const value=String(text||'');
 if(!value)return false;
 try{if(window.SwirAndroid&&typeof SwirAndroid.copyText==='function'){SwirAndroid.copyText(value);toast(label||'Skopiowano');return true}}catch(e){}
 try{navigator.clipboard.writeText(value).then(()=>toast(label||'Skopiowano'));return true}catch(e){}
 try{const ta=document.createElement('textarea');ta.value=value;ta.style.cssText='position:fixed;left:-9999px;top:-9999px';document.body.appendChild(ta);ta.select();document.execCommand('copy');ta.remove();toast(label||'Skopiowano');return true}catch(e){}
 return false;
}
function shareText(text){
 try{if(window.SwirAndroid&&typeof SwirAndroid.shareText==='function'){SwirAndroid.shareText(String(text||''));return true}}catch(e){}
 return false;
}

function installPolishTheme(){
 let st=$('#swir-v03-polish-style');
 if(!st){st=document.createElement('style');st.id='swir-v03-polish-style';document.head.appendChild(st)}
 st.textContent=`
 html,body{background:#071019!important;color:#dce8f3!important}
 [id^="m-messages_"],.m-messagesTextArea,.m-container,.m-textArea{background:#08111b!important;color:#dce8f3!important}
 .m-msg-item{background:#111c29!important;color:#dce8f3!important;border:1px solid #24384b!important;border-radius:10px!important;box-shadow:none!important}
 .m-msg-item *:not(img):not(svg):not(path):not(.m-msg-item-user-login):not(.info-user-login){color:#dce8f3!important;background-color:transparent!important}
 .m-msg-item-user-login,.info-user-login{color:var(--swir-app-a,#00e5ff)!important;font-weight:800!important;text-shadow:none!important}
 .m-msg-item a{color:#78caff!important;text-decoration:none!important}
 .m-topic-intro,.m-topic-message{background:#101a27!important;color:#dce8f3!important;border-color:#27384a!important}
 .m-topic-intro *,.m-topic-message *{color:#dce8f3!important}
 .m-usersList,[id^="m-users_"]{background:#0a1420!important;color:#dce8f3!important}
 .m-list-user-item{background:#0d1825!important;color:#dce8f3!important;border-color:#203246!important}
 .m-room,.m-category,.m-room-list,[id^="m-room-list-"]{background:#0a1420!important;color:#dce8f3!important}
 [id^="m-textMessage-"],input.text-input,textarea.text-input{background:#050b12!important;color:#f1f7fb!important;border:1px solid var(--swir-app-a,#00e5ff)!important;caret-color:var(--swir-app-a,#00e5ff)!important}
 [id^="m-textMessage-"]::placeholder,input.text-input::placeholder,textarea.text-input::placeholder{color:#8192a3!important;opacity:1!important}
 .button-send,[id^="m-sendMessage-button-"]{background:#ffd166!important;color:#071019!important;border-color:#ffc94f!important;font-weight:800!important}
 .swir-gif-wrap{position:relative!important;display:inline-block!important;max-width:100%!important}
 .swir-gif-tools{position:absolute!important;right:5px!important;top:5px!important;z-index:50!important;display:flex!important;gap:4px!important;opacity:.22!important;transition:opacity .15s!important}
 .swir-gif-wrap:hover .swir-gif-tools,.swir-gif-wrap:active .swir-gif-tools{opacity:1!important}
 .swir-gif-tool{min-width:30px!important;height:30px!important;padding:0 7px!important;border-radius:8px!important;border:1px solid rgba(255,255,255,.22)!important;background:rgba(4,12,20,.88)!important;color:#fff!important;font-size:15px!important;line-height:28px!important;text-align:center!important;box-shadow:0 2px 10px #0008!important}
 .swir-ad-hidden{display:none!important;visibility:hidden!important;height:0!important;min-height:0!important;max-height:0!important;margin:0!important;padding:0!important;border:0!important;overflow:hidden!important}
 `;
}

function looksLikeAd(el){
 if(!el||el===document.body||el===document.documentElement)return false;
 const id=String(el.id||'').toLowerCase();
 const cls=String(el.className||'').toLowerCase();
 const aria=String(el.getAttribute?.('aria-label')||'').toLowerCase();
 const marker=id+' '+cls+' '+aria;
 if(/(^|[\s_-])(reklama|advert|advertisement|adserver|adform|adslot|ad-slot|adsbygoogle)([\s_-]|$)/i.test(marker))return true;
 if(el.tagName==='IFRAME'){
  const src=String(el.getAttribute('src')||'').toLowerCase();
  if(/doubleclick|googlesyndication|adform|adserver|gemius|yieldlove|advert/.test(src))return true;
 }
 return false;
}
function hideAdElement(el){
 if(!el||el.dataset?.swirKeep==='1')return;
 let target=el;
 if(el.tagName==='IFRAME'){
  const p=el.parentElement;
  if(p&&p!==document.body&&p.getBoundingClientRect().height<500)target=p;
 }
 target.classList?.add('swir-ad-hidden');
 target.setAttribute?.('aria-hidden','true');
}
function hideAds(root=document){
 try{
  const all=[];
  if(root.nodeType===1)all.push(root);
  all.push(...$$('iframe,[id],[class],[aria-label]',root));
  all.forEach(el=>{if(looksLikeAd(el))hideAdElement(el)});
  $$('body *',root).slice(0,900).forEach(el=>{
   if(el.children.length>8)return;
   const txt=(el.textContent||'').replace(/\s+/g,' ').trim().toUpperCase();
   if(txt==='REKLAMA'||txt==='ADVERTISEMENT'){
    let p=el.parentElement;
    for(let i=0;i<3&&p&&p!==document.body;i++,p=p.parentElement){
     if(p.querySelector('iframe')||p.getBoundingClientRect().height>90){hideAdElement(p);break}
    }
   }
  });
 }catch(e){}
}

function gifUrl(img){
 return String(img.currentSrc||img.src||img.getAttribute('data-src')||img.getAttribute('data-original')||'');
}
function isGifLike(img){
 if(!img||img.tagName!=='IMG')return false;
 const u=gifUrl(img).toLowerCase();
 const cls=String(img.className||'').toLowerCase();
 const alt=String(img.alt||'').toLowerCase();
 return /\.gif(?:$|\?)/.test(u)||/giphy|tenor|gif/.test(u)||/gif/.test(cls)||/gif/.test(alt);
}
function decorateGif(img){
 if(!isGifLike(img)||seenGif.has(img))return;
 seenGif.add(img);
 let wrap=img.parentElement;
 if(!wrap||wrap.classList.contains('swir-gif-wrap')===false){
  const w=document.createElement('span');w.className='swir-gif-wrap';
  img.parentNode?.insertBefore(w,img);w.appendChild(img);wrap=w;
 }
 const tools=document.createElement('span');tools.className='swir-gif-tools';
 const cp=document.createElement('button');cp.type='button';cp.className='swir-gif-tool';cp.textContent='📋';cp.title='Kopiuj link GIF';
 cp.addEventListener('click',e=>{e.preventDefault();e.stopPropagation();copyText(gifUrl(img),'GIF skopiowany do schowka')});
 cp.addEventListener('touchend',e=>{e.stopPropagation()},{passive:true});
 const sh=document.createElement('button');sh.type='button';sh.className='swir-gif-tool';sh.textContent='↗';sh.title='Udostępnij GIF';
 sh.addEventListener('click',e=>{e.preventDefault();e.stopPropagation();if(!shareText(gifUrl(img)))copyText(gifUrl(img),'Link GIF skopiowany')});
 tools.appendChild(cp);tools.appendChild(sh);wrap.appendChild(tools);
 let pressTimer=0;
 img.addEventListener('touchstart',()=>{pressTimer=setTimeout(()=>copyText(gifUrl(img),'GIF skopiowany do schowka'),650)},{passive:true});
 img.addEventListener('touchend',()=>clearTimeout(pressTimer),{passive:true});
 img.addEventListener('touchmove',()=>clearTimeout(pressTimer),{passive:true});
}
function scanGifs(root=document){
 try{if(root.nodeType===1&&root.tagName==='IMG')decorateGif(root);$$('img',root).forEach(decorateGif)}catch(e){}
}

function installObserver(){
 if(window.__swirV03Observer)window.__swirV03Observer.disconnect();
 window.__swirV03Observer=new MutationObserver(ms=>{
  for(const m of ms){for(const n of m.addedNodes){if(n.nodeType===1){hideAds(n);scanGifs(n)}}}
 });
 window.__swirV03Observer.observe(document.documentElement||document.body,{childList:true,subtree:true});
}
function polishNow(){installPolishTheme();hideAds(document);scanGifs(document)}

polishNow();installObserver();
setTimeout(polishNow,800);setTimeout(polishNow,2200);setInterval(()=>{hideAds(document);scanGifs(document)},8000);
window.SWIR_PATCH={version:VERSION,polishNow,hideAds,scanGifs,copyText};
toast('SWIR v0.3: kolory + reklamy + kopiowanie GIF gotowe');
})();
