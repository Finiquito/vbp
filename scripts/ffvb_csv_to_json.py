import csv, json, collections, sys
src, out, label = sys.argv[1], sys.argv[2], sys.argv[3]
VBP='VOLLEY-BALL PEXINOIS NIORT'
NAMES={'PLESSIS-ROBINSON VOLLEY-BALL':'Plessis-Robinson VB','J.S.A. BORDEAUX':'JSA Bordeaux','SPORTING CLUB DE L OUEST':"Sporting Club de l'Ouest",'RENNES ETUDIANTS CLUB 2':'Rennes Étudiants Club 2','AS VOLLEY-BALL VELIZY':'AS Vélizy','QUIMPER VOLLEY 29':'Quimper Volley 29','LES NEPTUNES NANTES VOLLEY ASSOCIATION 2 CFC':'Neptunes de Nantes 2','VOLLEY BALL CLUB LE HAILLAN':'VBC Le Haillan','SPORT ATHLETIQUE MERIGNACAIS':'SA Mérignac','ELAN SPORTIF DE CARPIQUET DE VOLLEY':'ES Carpiquet',
'CNM CHARENTON':'CNM Charenton','CONFLANS-ANDRESY-JOUY VB 2':'Conflans-Andrésy-Jouy VB 2','LESCAR PYRENEES VOLLEY-BALL':'Lescar Pyrénées VB','PARIS AMICALE CAMOU':'Paris Amicale Camou','SPORTING CLUB PARIS VOLLEY':'Sporting Club Paris','T.O.A.C. - T.U.C. VOLLEY-BALL 3':'TOAC-TUC Volley 3','UNION SPORTIVE DE VILLEJUIF':'US Villejuif','UNION SPORTIVE TALENCAISE':'US Talence',VBP:'VBP Niort'}
rows=list(csv.reader(open(src,encoding='latin-1'),delimiter=';'))[1:]
std=collections.defaultdict(lambda: dict(J=0,G=0,P=0,pts=0,sp=0,sc=0,pp=0,pc=0)); ours=[]
def pts(w,l,forf):
    if forf: return 0
    return 3 if (w==3 and l<=1) else 2 if w==3 else 1 if w==2 else 0
for r in rows:
    if len(r)<13 or not r[1]: continue
    ent,jo,m,date,heure,_,A,_,B,sets,score,tot,salle=r[:13]
    if 'xxxxx' in (A,B):
        if VBP in (A,B): ours.append(dict(j=int(jo),date=date,exempt=True))
        continue
    if not sets.strip():
        if VBP in (A,B): ours.append(dict(j=int(jo),date=date,heure=heure,home=A==VBP,adv=NAMES.get(B if A==VBP else A),joue=False))
        continue
    sa,sb=[x.strip() for x in sets.split('/')]
    fa=sa in 'PF'; fb=sb in 'PF'
    na=0 if fa else int(sa); nb=0 if fb else int(sb)
    ta,tb=std[A],std[B]
    for t in (ta,tb): t['J']+=1
    ta['pts']+=pts(na,nb,fa); tb['pts']+=pts(nb,na,fb)
    if na>nb: ta['G']+=1; tb['P']+=1
    else: tb['G']+=1; ta['P']+=1
    ta['sp']+=na; ta['sc']+=nb; tb['sp']+=nb; tb['sc']+=na
    a,b=[int(x) for x in tot.split('-')]
    ta['pp']+=a; ta['pc']+=b; tb['pp']+=b; tb['pc']+=a
    if VBP in (A,B):
        home=A==VBP
        sl=[tuple(int(y) for y in s.split('-')) for s in score.split(',')]
        ours.append(dict(j=int(jo),date=date,heure=heure,home=home,adv=NAMES[B if home else A],nous=na if home else nb,eux=nb if home else na,sets=[list(p) if home else [p[1],p[0]] for p in sl],salle=salle.title(),forfait=(fb if home else fa) or (fa if home else fb)))
table=sorted(([NAMES[k],v] for k,v in std.items()), key=lambda t:(-t[1]['pts'],-(t[1]['sp']/max(1,t[1]['sc'])),-(t[1]['pp']/max(1,t[1]['pc']))))
ours.sort(key=lambda x:x['j'])
json.dump(dict(competition=label,saison='2025-2026',source='FFVolley, export CSV',matchs=ours,classement=[dict(rang=i,club=n,**v) for i,(n,v) in enumerate(table,1)]),open(out,'w'),ensure_ascii=False,indent=1)
for i,(n,v) in enumerate(table,1): print(i,n,v['pts'],v['G'],'-',v['P'])
for o in ours: print(o.get('j'),o.get('date'),o.get('adv'),o.get('nous'),o.get('eux'),'EXEMPT' if o.get('exempt') else '')
