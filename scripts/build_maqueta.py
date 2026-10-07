import json, re, shutil, pathlib, sys
SP = pathlib.Path('/tmp/claude-0/-home-user-vbp/945fbc51-cc31-5414-b401-471568f6bb93/scratchpad')
OUT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '/home/user/vbp/maqueta')
src = (SP/'wf/project/DisenoHome.dc.html').read_text()
bm = json.load(open(SP/'prev/blobmap.json'))
(OUT/'img').mkdir(parents=True, exist_ok=True)
names = {}
def slug(p):
    b = pathlib.Path(p)
    n = re.sub(r'[^a-z0-9-]+', '-', b.stem.lower()).strip('-')
    return n + b.suffix.lower()
for bid in sorted(set(re.findall(r'[0-9a-f]{32}', src))):
    if bid not in bm: continue
    p = bm[bid]; n = slug(p)
    if n in ('10.png', '15.webp'): n = {'10.png': 'sponsor-restaurant-donjon.png', '15.webp': 'jeunes-m13m-entraineur.webp'}[n]
    if p.startswith(str(SP/'sponsors')) and not n.startswith('sponsor-'): n = 'sponsor-' + n
    shutil.copy(p, OUT/'img'/n); names[bid] = 'img/' + n
def fix(t):
    t = re.sub(r'/_blob/([0-9a-f]{32})', lambda m: names.get(m.group(1), m.group(0)), t)
    t = re.sub(r"'/_blob/' \+ id", "IMG[id]", t)
    return t
helmet = src[src.index('<helmet>')+8:src.index('</helmet>')]
tpl = src[src.index('</helmet>')+9:src.rindex('</x-dc>')]
script = re.search(r'<script type="text/x-dc"[^>]*>([\s\S]*?)</script>', src).group(1)
morph = (SP/'npmdl/package/dist/morphdom-umd.min.js').read_text()
imgmap = json.dumps({k: v for k, v in names.items()})
runtime = r'''
(function(){
class DCLogic{constructor(p){this.props=p||{};this.state={}}setState(o){Object.assign(this.state,typeof o==='function'?o(this.state):o);schedule()}forceUpdate(){schedule()}}
window.DCLogic=DCLogic;
})();
'''
engine = r'''
(function(){
var C=new Component({});var tpl=document.getElementById('dc-tpl').content;var root=document.getElementById('app');var pending=false;
window.schedule=function(){if(pending)return;pending=true;requestAnimationFrame(function(){pending=false;draw()})};
function get(ctx,e){e=e.trim();if(e==='true')return true;if(e==='false')return false;if(/^-?\d+(\.\d+)?$/.test(e))return +e;return e.split('.').reduce(function(o,k){return o==null?o:o[k]},ctx)}
function sub(s,ctx){var m=s.match(/^\s*\{\{([^}]+)\}\}\s*$/);if(m)return get(ctx,m[1]);return s.replace(/\{\{([^}]+)\}\}/g,function(_,e){var v=get(ctx,e);return v==null?'':v})}
function bind(el,type){el.addEventListener(type,function(ev){var h=el.__h&&el.__h[type];if(h)h(ev)})}
var SVGNS='http://www.w3.org/2000/svg';
function proc(node,ctx,parent){
 if(node.nodeType===3){parent.appendChild(document.createTextNode(sub(node.textContent,ctx)));return}
 if(node.nodeType!==1)return;var tag=node.localName;
 if(tag==='sc-for'){var list=get(ctx,node.getAttribute('list').replace(/[{}]/g,''))||[];var as=node.getAttribute('as');list.forEach(function(it,i){var c=Object.create(ctx);c[as]=it;c.$index=i;node.childNodes.forEach(function(ch){proc(ch,c,parent)})});return}
 if(tag==='sc-if'){if(get(ctx,node.getAttribute('value').replace(/[{}]/g,'')))node.childNodes.forEach(function(ch){proc(ch,ctx,parent)});return}
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
// liens vers des pages non encore maquettées
var toast=document.getElementById('toast');var tt;
document.addEventListener('click',function(ev){var a=ev.target.closest&&ev.target.closest('a[href]');if(!a)return;var h=a.getAttribute('href');
 if(h==='#'||/\.dc\.html/.test(h)){ev.preventDefault();toast.classList.add('on');clearTimeout(tt);tt=setTimeout(function(){toast.classList.remove('on')},2600)}});
document.addEventListener('keydown',function(ev){if(ev.key==='Escape'&&C.state.mm){C.setState({mm:null})}});
})();
'''
html = f'''<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>VBP Niort · Maquette de la page d’accueil</title>
<meta name="robots" content="noindex">
<link rel="icon" href="{names['bf82c9595487efdd2b707c895efeb63e']}">
{fix(helmet)}
<style>
#toast{{position:fixed;left:50%;bottom:24px;transform:translate(-50%,20px);opacity:0;pointer-events:none;z-index:100;max-width:calc(100% - 32px);padding:14px 20px;border-radius:12px;background:#0b1b33;color:#fff;font:600 15px/22px 'Open Sans',Arial,sans-serif;transition:opacity .25s,transform .25s}}
#toast.on{{opacity:1;transform:translate(-50%,0)}}
.maq-tag{{position:fixed;right:12px;bottom:12px;z-index:90;padding:6px 10px;border-radius:8px;background:rgba(11,27,51,.85);color:#fff;font:600 12px/16px 'Open Sans',Arial,sans-serif;letter-spacing:.04em}}
</style>
</head>
<body>
<template id="dc-tpl">{fix(tpl)}</template>
<div id="app"></div>
<div id="toast" role="status" aria-live="polite">Cette page sera ajoutée dans une prochaine version de la maquette.</div>
<div class="maq-tag" aria-hidden="true">Maquette · contenus provisoires</div>
<script>{morph}</script>
<script>{runtime}</script>
<script>var IMG={imgmap};
{fix(script)}
window.Component=Component;</script>
<script>{engine}</script>
</body>
</html>
'''
(OUT/'index.html').write_text(html)
print('ok', len(html), len(names), 'images')
