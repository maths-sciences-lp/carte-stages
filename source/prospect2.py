import json,sys
sys.argv=['x']
exec(open('prospect.py').read().split('rows={}')[0])
exec('rows={}\n'+open('prospect.py').read().split('rows={}')[1].split('for naf,fil in NAF.items()')[0])
rows.update({r['siret']:r for r in json.load(open('prospects.json'))})
before=set(rows)
for naf,fil in {'43.32C':'Menuiserie-agencement','31.09A':'Ébénisterie'}.items():
    # remplace les résultats mots-clés éventuels par la classe NAF
    for s in [s for s,r in rows.items() if r['naf']==naf and r['how'].startswith('mot')]: del rows[s]
    run({'activite_principale':naf},fil,'naf '+naf)
OK={'Signalétique-graphisme':{'73.11Z','73.12Z','74.10Z','25.99B','27.40Z','23.19Z','43.29B','43.21A','18.12Z','18.13Z'},
 'Menuiserie-agencement':{'43.32A','43.32C','41.20A','41.20B','43.99C','74.10Z','43.29A','43.34Z','43.39Z','16.23Z'},
 'Énergie':{'33.20B','43.22A','43.22B'},'Ébénisterie':{'74.10Z','31.09A','31.09B','31.01Z','95.24Z'}}
drop=[s for s,r in rows.items() if r['how'].startswith('mot') and r['naf'] not in OK.get(r['fil'],{r['naf']})]
for s in drop: del rows[s]
print('retirés',len(drop),'total',len(rows))
json.dump(list(rows.values()),open('prospects.json','w'),ensure_ascii=False)
