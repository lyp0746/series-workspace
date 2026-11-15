# -*- coding: utf-8 -*-
import io, json, os, re, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import api, republish_book as R

ROOT = R.ROOT

def update(slug, did, doi):
    p = os.path.join(ROOT, 'inventory.tsv')
    lines = io.open(p, encoding='utf-8').read().split('\n')
    for i, l in enumerate(lines):
        if l.startswith('PAPER\t%s\t' % slug):
            c = l.split('\t'); c[5] = doi; lines[i] = '\t'.join(c)
    io.open(p, 'w', encoding='utf-8').write('\n'.join(lines))
    for f in ('CITATION.cff', 'README.md'):
        q = os.path.join(ROOT, slug, f)
        if os.path.exists(q):
            t = io.open(q, encoding='utf-8').read()
            t = re.sub(r'10\.5281/zenodo\.\d+', doi, t, count=1)
            io.open(q, 'w', encoding='utf-8').write(t)
    p = os.path.join(ROOT, '_zenodo', 'registry.json')
    d = json.load(io.open(p, encoding='utf-8'))
    for w in d['works']:
        if w['slug'] == slug:
            w['记录ID'] = str(did)
    json.dump(d, io.open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

for slug in sys.argv[1:]:
    did, _ = R.new(slug)
    rc = subprocess.call([sys.executable, os.path.join(ROOT, '_zenodo', 'upload_resume.py'), slug, str(did)])
    if rc:
        print('UPLOAD FAILED', slug); continue
    R.meta(slug, did)
    R.publish(did)
    _, rec = api.req('GET', 'https://zenodo.org/api/records/%s' % did, tries=3, timeout=120)
    update(slug, did, rec['doi'])
    print('DONE', slug, rec['doi'])
