import json,sys,os
for b in sys.argv[1:]:
    d=json.load(open(os.path.join(b,'source','parts.json'),encoding='utf-8'))
    print('='*20,b)
    for i,p in enumerate(d,1):
        print(f"[{i}] {p['part']}")
        print("    desc:",p.get('desc',''))
        if p.get('intro'): print("    intro:",p['intro'][:80])
        if p.get('summary'): print("    summary:",p['summary'][:80])
        print("    ch:",[(c['no'],c['title']) for c in p.get('chapters',[])])
