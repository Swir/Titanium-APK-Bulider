(function(){
'use strict';
if(window.SWIR_PATCH&&window.SWIR_PATCH.version==='0.5.0')return;
const VERSION='0.5.0';
const $=(s,r=document)=>r.querySelector(s);
const $$=(s,r=document)=>[...r.querySelectorAll(s)];

function toast(msg){
 try{if(window.SwirAndroid&&typeof SwirAndroid.toast==='function'){SwirAndroid.toast(String(msg));return}}catch(e){}
 try{console.log('[SWIR]',msg)}catch(e){}
}

function installPolishTheme(){
 let st=$('#swir-v03-polish-style');
 if(!st){st=document.createElement('style');st.id='swir-v03-polish-style';document.head.appendChild(st)}
 st.textContent=`
 html,body{background:#071019!important;color:#dce8f3!important}
 [id^="m-messages_"],.m-messagesTextArea,.m-container,.m-textArea{background:#08111b!important;color:#dce8f3!important}
 .m-msg-item{background:#111c29!important;color:#dce8f3!important;border:1px solid #24384b!important;border-radius:10px!important;box-shadow:none!important}
 .m-msg-item *:not(img):not(svg):not(path):not(.m-msg-item-user-login):not(.info-user-login){color:#dce8f3!important;background-color:transparent!important}
 .m-msg-item a{color:#78caff!important;text-decoration:none!important}
 .m-topic-intro,.m-topic-message{background:#101a27!important;color:#dce8f3!important;border-color:#27384a!important}
 .m-topic-intro *,.m-topic-message *{color:#dce8f3!important}
 .m-usersList,[id^="m-users_"]{background:#0a1420!important;color:#dce8f3!important}
 .m-list-user-item{background:#0d1825!important;color:#dce8f3!important;border-color:#203246!important}
 .m-room,.m-category,.m-room-list,[id^="m-room-list-"]{background:#0a1420!important;color:#dce8f3!important}
 [id^="m-textMessage-"],input.text-input,textarea.text-input{background:#050b12!important;color:#f1f7fb!important;border:1px solid var(--swir-app-a,#00e5ff)!important;caret-color:var(--swir-app-a,#00e5ff)!important}
 [id^="m-textMessage-"]::placeholder,input.text-input::placeholder,textarea.text-input::placeholder{color:#8192a3!important;opacity:1!important}
 .button-send,[id^="m-sendMessage-button-"]{background:#ffd166!important;color:#071019!important;border-color:#ffc94f!important;font-weight:800!important}
 .swir-gif-tools{display:none!important}
 .swir-ad-hidden{display:none!important;visibility:hidden!important;height:0!important;min-height:0!important;max-height:0!important;margin:0!important;padding:0!important;border:0!important;overflow:hidden!important}
 `;
}

function cleanupOldGifTools(){
 try{
  $$('.swir-gif-tools').forEach(el=>el.remove());
  $$('.swir-gif-wrap').forEach(w=>{
   try{
    const img=w.querySelector('img');
    if(img&&w.parentNode){w.parentNode.insertBefore(img,w);w.remove()}
   }catch(e){}
  });
 }catch(e){}
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

function installObserver(){
 if(window.__swirV03Observer)window.__swirV03Observer.disconnect();
 window.__swirV03Observer=new MutationObserver(ms=>{
  for(const m of ms){for(const n of m.addedNodes){if(n.nodeType===1){hideAds(n);cleanupOldGifTools()}}}
 });
 window.__swirV03Observer.observe(document.documentElement||document.body,{childList:true,subtree:true});
}
function polishNow(){installPolishTheme();hideAds(document);cleanupOldGifTools()}

polishNow();installObserver();
setTimeout(polishNow,800);setTimeout(polishNow,2200);setInterval(()=>{hideAds(document);cleanupOldGifTools()},8000);
window.SWIR_PATCH={version:VERSION,polishNow,hideAds};
toast('SWIR: wygląd + NO ADS gotowe');
})();
