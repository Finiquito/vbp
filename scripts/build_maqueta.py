"""Génère la maquette HTML autonome (toutes les pages) depuis les artboards du canvas."""
import json, re, shutil, pathlib, sys
SP = pathlib.Path('/tmp/claude-0/-home-user-vbp/945fbc51-cc31-5414-b401-471568f6bb93/scratchpad')
OUT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '/home/user/vbp/maqueta')
PAGES = [  # artboard, fichier, rubrique active du menu
    ('DisenoHome', 'index.html', None),
    ('DisenoLicences', 'licences.html', None),
    ('DisenoCalendrier', 'calendrier.html', 'calendrier'),
    ('DisenoEquipe', 'equipe.html', 'equipes'),
    ('DisenoActus', 'actualites.html', 'actus'),
    ('DisenoArticle', 'article.html', 'actus'),
    ('DisenoHistoire', 'histoire.html', 'club'),
    ('DisenoPalmares', 'palmares.html', 'club'),
    ('DisenoStandard', 'benevoles.html', 'club'),
]
LINKS = {a + '.dc.html': f for a, f, _ in PAGES}
LINKS['DisenoResultats.dc.html'] = 'index.html'
LINKS['DisenoMovil.dc.html'] = 'index.html'
bm = json.load(open(SP / 'prev/blobmap.json'))
(OUT / 'img').mkdir(parents=True, exist_ok=True)
names = {}
def slug(p):
    b = pathlib.Path(p)
    return re.sub(r'[^a-z0-9-]+', '-', b.stem.lower()).strip('-') + b.suffix.lower()
def img_for(bid):
    if bid in names: return names[bid]
    p = bm[bid]; n = slug(p)
    n = {'10.png': 'sponsor-restaurant-donjon.png', '15.webp': 'jeunes-m13m-entraineur.webp'}.get(n, n)
    if p.startswith(str(SP / 'sponsors')) and not n.startswith('sponsor-'): n = 'sponsor-' + n
    shutil.copy(p, OUT / 'img' / n); names[bid] = 'img/' + n
    return names[bid]
def ctl(t):
    t = re.sub(r'<sc-for\b', '<template data-sc="for"', t); t = t.replace('</sc-for>', '</template>')
    t = re.sub(r'<sc-if\b', '<template data-sc="if"', t); t = t.replace('</sc-if>', '</template>')
    return t
def fix(t):
    t = re.sub(r'/_blob/([0-9a-f]{32})', lambda m: img_for(m.group(1)) if m.group(1) in bm else m.group(0), t)
    t = re.sub(r"'/_blob/' \+ id", "IMG[id]", t)
    t = re.sub(r'(Diseno[A-Za-z]+\.dc\.html)', lambda m: LINKS.get(m.group(1), 'index.html'), t)
    return t
morph = (SP / 'npmdl/package/dist/morphdom-umd.min.js').read_text()
HEADER = json.load(open(SP / 'prev/header.json')) if (SP / 'prev/header.json').exists() else None
MM_CSS = r'''
.los{display:inline-block;clip-path:polygon(50% 0,100% 50%,50% 100%,0 50%)}
.mm-btn{transition:color .2s}.mm-btn:hover{color:#1c5fa6 !important}.mm-btn svg{transition:transform .25s}
.mm-col{transition:opacity .3s,filter .3s}
.mm-col.dim,.mm-grid:hover .mm-col,.mm-grid:focus-within .mm-col{opacity:.36;filter:blur(1.4px) saturate(.5)}
.mm-grid .mm-col:hover,.mm-grid .mm-col:focus-within{opacity:1 !important;filter:none !important}
.mm-lien{transition:background-color .2s}.mm-lien:hover{background:#eaf3fa}.mm-lien:hover .mm-t{color:#1c5fa6}
.mm-off{cursor:default;pointer-events:none}.mm-off span{color:#9aa6b6 !important}.mm-off span span{background:#c3ccd7 !important}
@keyframes mmIn{from{opacity:0;transform:translateY(-8px)}to{opacity:1;transform:none}}.mm-panel{animation:mmIn .28s cubic-bezier(.2,.7,.2,1)}
.nav-m{display:none !important}.nav-d{flex-wrap:nowrap !important;white-space:nowrap}
@media (max-width:1360px){.nav-d{gap:20px !important;font-size:15px !important}.h-boutique{display:none !important}}
@media (max-width:1200px){.h-ffv{display:none !important}.nav-d{gap:16px !important}.nav-d svg{display:none}}
@media (max-width:1080px){.nav-d,#mega-menu,.mm-voile{display:none !important}.only-m.nav-m{display:flex !important}}
@media (min-width:761px) and (max-width:1080px){.only-m.nav-m{margin-left:0 !important}}
'''
HEADER_JS = r'''
(function(){
var hd=document.getElementById('vbp-header');if(!hd)return;
var btns=[].slice.call(hd.querySelectorAll('.mm-btn')),panel=hd.querySelector('#mega-menu'),voile=hd.querySelector('.mm-voile'),cols=[].slice.call(hd.querySelectorAll('.mm-col')),cur=null;
var actif=hd.getAttribute('data-actif');
function paint(){btns.forEach(function(b,i){var on=cur===i,here=b.getAttribute('data-id')===actif;b.setAttribute('aria-expanded',on?'true':'false');
 b.style.borderBottomColor=on?'#1c5fa6':'transparent';b.style.color=(on||here)?'#1c5fa6':'#0b1b33';var sv=b.querySelector('svg');if(sv)sv.style.transform=on?'rotate(180deg)':''});
 cols.forEach(function(c,i){c.classList.toggle('dim',cur!==null&&cur!==i);var t=c.firstElementChild;if(t)t.style.borderBottomColor=cur===i?t.getAttribute('data-c'):'#d3e1ee'});
 panel.hidden=voile.hidden=cur===null}
btns.forEach(function(b,i){b.addEventListener('click',function(){cur=cur===i?null:i;paint()})});
voile.addEventListener('click',function(){cur=null;paint()});
panel.addEventListener('click',function(e){if(e.target.closest('a'))setTimeout(function(){cur=null;paint()},0)});
document.addEventListener('keydown',function(e){if(e.key==='Escape'&&cur!==null){cur=null;paint()}});
var mb=hd.querySelector('.nav-m'),mm=hd.querySelector('#menu-mobile');
if(mb&&mm)mb.addEventListener('click',function(){var o=mm.hidden;mm.hidden=!o;mb.setAttribute('aria-expanded',o?'true':'false');var l=mb.lastChild;if(l&&l.nodeType===3)l.textContent=o?'Fermer':'Menu'});
paint();
})();
'''
ENGINE = r'''
(function(){
var ancre=decodeURIComponent(location.hash.slice(1));
var C=new Component({ancre:ancre});var tpl=document.getElementById('dc-tpl').content;var root=document.getElementById('app');var pending=false;
window.schedule=function(){if(pending)return;pending=true;requestAnimationFrame(function(){pending=false;draw()})};
function get(ctx,e){e=e.trim();if(e==='true')return true;if(e==='false')return false;if(/^-?\d+(\.\d+)?$/.test(e))return +e;return e.split('.').reduce(function(o,k){return o==null?o:o[k]},ctx)}
function sub(s,ctx){var m=s.match(/^\s*\{\{([^}]+)\}\}\s*$/);if(m)return get(ctx,m[1]);return s.replace(/\{\{([^}]+)\}\}/g,function(_,e){var v=get(ctx,e);return v==null?'':v})}
function bind(el,type){el.addEventListener(type,function(ev){var h=el.__h&&el.__h[type];if(h)h(ev)})}
var SVGNS='http://www.w3.org/2000/svg';
function proc(node,ctx,parent){
 if(node.nodeType===3){parent.appendChild(document.createTextNode(sub(node.textContent,ctx)));return}
 if(node.nodeType!==1)return;var tag=node.localName;
 var sc=tag==='template'&&node.getAttribute('data-sc');var kids=sc&&node.content&&node.content.childNodes.length?node.content.childNodes:node.childNodes;
 if(sc==='for'){var list=get(ctx,node.getAttribute('list').replace(/[{}]/g,''))||[];var as=node.getAttribute('as');list.forEach(function(it,i){var c=Object.create(ctx);c[as]=it;c.$index=i;kids.forEach(function(ch){proc(ch,c,parent)})});return}
 if(sc==='if'){if(get(ctx,node.getAttribute('value').replace(/[{}]/g,'')))kids.forEach(function(ch){proc(ch,ctx,parent)});return}
 if(tag==='dc-import')return;
 var el=node.namespaceURI===SVGNS?document.createElementNS(SVGNS,tag):document.createElement(tag);
 for(var i=0;i<node.attributes.length;i++){var a=node.attributes[i];var v=sub(a.value,ctx);
  if(/^on/i.test(a.name)){var t=a.name.slice(2).toLowerCase();el.__h=el.__h||{};el.__h[t]=v;bind(el,t);continue}
  if(typeof v==='function'||v===false||v==null)continue;el.setAttribute(a.name,v===true?'':v)}
 node.childNodes.forEach(function(ch){proc(ch,ctx,el)});parent.appendChild(el)}
function build(){var vals=C.renderVals();var frag=document.createElement('div');tpl.childNodes.forEach(function(n){proc(n,vals,frag)});return frag}
var first=true;
function draw(){var nx=build();
 if(first){while(nx.firstChild)root.appendChild(nx.firstChild);first=false;return}
 var wrap=document.createElement('div');wrap.id='app';while(nx.firstChild)wrap.appendChild(nx.firstChild);
 morphdom(root,wrap,{onBeforeElUpdated:function(from,to){
   if(to.__h){var had=from.__h||{};from.__h=to.__h;Object.keys(to.__h).forEach(function(t){if(!(t in had))bind(from,t)})}
   if(from===document.activeElement&&(from.tagName==='INPUT'||from.tagName==='SELECT'))return false;
   return true}})}
draw();if(C.componentDidMount)C.componentDidMount();
if(ancre&&document.getElementById(ancre))setTimeout(function(){document.getElementById(ancre).scrollIntoView()},50);
window.addEventListener('hashchange',function(){var h=decodeURIComponent(location.hash.slice(1));if(h&&!document.getElementById(h))location.reload()});
var toast=document.getElementById('toast');var tt;
document.addEventListener('click',function(ev){var a=ev.target.closest&&ev.target.closest('a[href]');if(!a)return;var h=a.getAttribute('href');
 if(h==='#'){ev.preventDefault();toast.classList.add('on');clearTimeout(tt);tt=setTimeout(function(){toast.classList.remove('on')},2600)}});
document.addEventListener('keydown',function(ev){if(ev.key==='Escape'&&C.state&&C.state.mm){C.setState({mm:null})}});
})();
'''
def page(art, fname, actif):
    src = (SP / 'wf/project' / (art + '.dc.html')).read_text()
    title = re.search(r'<title>(.*?)</title>', src).group(1)
    helmet = src[src.index('<helmet>') + 8:src.index('</helmet>')]
    tpl = src[src.index('</helmet>') + 9:src.rindex('</x-dc>')]
    script = re.search(r'<script type="text/x-dc"[^>]*>([\s\S]*?)</script>', src).group(1)
    shared = ''
    extra_css = ''
    if art != 'DisenoHome' and HEADER:
        a = tpl.index('<header'); b = tpl.index('</header>', a) + len('</header>')
        tpl = tpl[:a] + tpl[b:]
        shared = ('<div id="vbp-header" data-actif="%s" style="position: relative; z-index: 60; color: #0b1b33; font-family: \'Open Sans\', \'Segoe UI\', Arial, sans-serif; font-size: 17px; line-height: 27px">' % (actif or '')
                  + HEADER['header'] + '</div>')
        extra_css = MM_CSS
    imgmap = json.dumps({k: img_for(k) for k in set(re.findall(r"'([0-9a-f]{32})'", script)) if k in bm})
    html = f'''<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="robots" content="noindex">
<link rel="icon" href="{img_for('bf82c9595487efdd2b707c895efeb63e')}">
{fix(helmet)}
<style>{extra_css}
#toast{{position:fixed;left:50%;bottom:24px;transform:translate(-50%,20px);opacity:0;pointer-events:none;z-index:100;max-width:calc(100% - 32px);padding:14px 20px;border-radius:12px;background:#0b1b33;color:#fff;font:600 15px/22px 'Open Sans',Arial,sans-serif;transition:opacity .25s,transform .25s}}
#toast.on{{opacity:1;transform:translate(-50%,0)}}
.maq-tag{{position:fixed;right:12px;bottom:12px;z-index:90;padding:6px 10px;border-radius:8px;background:rgba(11,27,51,.85);color:#fff;font:600 12px/16px 'Open Sans',Arial,sans-serif;letter-spacing:.04em}}
</style>
</head>
<body>
<template id="dc-tpl">{ctl(fix(tpl))}</template>
{fix(shared)}
<div id="app"></div>
<div id="toast" role="status" aria-live="polite">Cette page sera ajoutée dans une prochaine version de la maquette.</div>
<div class="maq-tag" aria-hidden="true">Maquette · contenus provisoires</div>
<script>{morph}</script>
<script>(function(){{class DCLogic{{constructor(p){{this.props=p||{{}};this.state={{}}}}setState(o){{Object.assign(this.state,typeof o==='function'?o(this.state):o);schedule()}}forceUpdate(){{schedule()}}}}window.DCLogic=DCLogic;}})();</script>
<script>var IMG={imgmap};
{fix(script)}
window.Component=Component;</script>
<script>{ENGINE}</script>
<script>{HEADER_JS if shared else ''}</script>
</body>
</html>
'''
    (OUT / fname).write_text(html)
for a, f, act in PAGES:
    page(a, f, act)
print('ok', len(PAGES), 'pages,', len(names), 'images, header partagé:', bool(HEADER))
