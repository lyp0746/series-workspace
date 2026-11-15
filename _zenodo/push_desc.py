# -*- coding: utf-8 -*-
"""只更新已发布记录的 description（不产生新版本、DOI 不变）。"""
import io, json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import api, fix_rights_subjects as F

ROOT = F.ROOT

def push(slug, rid):
    z = json.load(io.open(os.path.join(ROOT, slug, '.zenodo.json'), encoding='utf-8'))
    desc = z.get('description') or ''
    m = F.build(slug, rid)
    m['description'] = desc
    try:
        api.req('POST', 'https://zenodo.org/api/records/%s/draft' % rid, tries=1, timeout=90)
    except Exception:
        pass
    for i in range(3):
        try:
            api.req('PUT', 'https://zenodo.org/api/records/%s/draft' % rid, data={'metadata': m}, tries=1, timeout=300)
            break
        except Exception as e:
            if i == 2: raise
            time.sleep(5)
    api.req('POST', 'https://zenodo.org/api/records/%s/draft/actions/publish' % rid, tries=1, timeout=300)
    try:
        _, r = api.req('GET', 'https://zenodo.org/api/records/%s' % rid, tries=1, timeout=60)
        md = r.get('metadata') or {}
    except Exception as e:
        print(slug, 'pushed (verify skipped:', type(e).__name__, ')'); return
    print(slug, 'desc', len(md.get('description') or ''), 'stars', (md.get('description') or '').count('*'),
          'lic', bool(md.get('rights') or md.get('license')), 'ver', md.get('version'), 'doi', r.get('doi'))

if __name__ == '__main__':
    g = {w['slug']: w for w in json.load(io.open(os.path.join(ROOT, '_zenodo', 'registry.json'), encoding='utf-8'))['works']}
    for slug in sys.argv[1:]:
        try:
            push(slug, g[slug]['记录ID'])
        except Exception as e:
            print(slug, 'FAILED', type(e).__name__, str(e)[:80])
