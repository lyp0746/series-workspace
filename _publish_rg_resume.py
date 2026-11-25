# -*- coding: utf-8 -*-
"""Resume Zenodo V3 upload without deleting already-committed files."""
import io, json, os, sys, time
sys.path.insert(0, '_zenodo')
import api
import requests

SLUG_DIR = 'D:/0_Article/resolution-grain'
REL = os.path.join(SLUG_DIR, 'release')
DRAFT = int(sys.argv[1]) if len(sys.argv) > 1 else 24413260
zj = json.load(io.open(os.path.join(SLUG_DIR, '.zenodo.json'), encoding='utf-8'))

def meta():
    return {
        "title": zj['title'],
        "publication_date": zj['publication_date'],
        "version": zj['version'],
        "resource_type": {"id": "publication-book"},
        "creators": [{"person_or_org": {"type": "personal", "name": "李毅芃", "given_name": "毅芃", "family_name": "李"},
                      "affiliations": [{"name": "独立研究者 / Independent Researcher"}]}],
        "description": zj['description'],
        "rights": [{"id": "cc-by-4.0"}],
        "subjects": [{"subject": k} for k in zj.get('keywords', [])],
        "languages": [{"id": "zho"}, {"id": "eng"}],
        "publisher": zj.get('publisher', '独立出版 / Independently published'),
        "related_identifiers": [
            {"identifier": r['identifier'], "scheme": r.get('scheme', 'doi'),
             "relation_type": {"id": r['relation'].lower()}}
            for r in zj.get('related_identifiers', [])],
    }

def files():
    out = []
    for root, _, fs in os.walk(REL):
        if os.path.relpath(root, REL).split(os.sep)[0] == 'visuals':
            continue
        for f in fs:
            p = os.path.join(root, f)
            out.append((os.path.relpath(p, REL).replace('\\', '/'), p))
    return sorted(out)

def log(*a): print(*a, flush=True)

log('draft', DRAFT)
st, cur = api.req('GET', f'{api.API}/records/{DRAFT}/draft/files?size=200')
existing = {e['key']: e for e in cur.get('entries', [])}
log('existing', len(existing), [(k, v.get('status')) for k, v in existing.items()])

targets = files()
log('targets', len(targets), 'bytes', sum(os.path.getsize(p) for _, p in targets))

for n, (key, path) in enumerate(targets, 1):
    ent = existing.get(key)
    if ent and ent.get('status') in ('done', 'completed'):
        log('skip done', key)
        continue
    if ent:
        try:
            api.req('DELETE', f'{api.API}/records/{DRAFT}/draft/files/{requests.utils.quote(key, safe="")}')
            log('deleted stale', key)
        except Exception as e:
            log('delete failed', key, str(e)[:120])
    st, r = api.req('POST', f'{api.API}/records/{DRAFT}/draft/files', data=[{"key": key}])
    with open(path, 'rb') as fh:
        data = fh.read()
    url = f'{api.API}/records/{DRAFT}/draft/files/{requests.utils.quote(key, safe="")}/content'
    h = {'Authorization': 'Bearer ' + api.TOK, 'Content-Type': 'application/octet-stream'}
    for attempt in range(6):
        try:
            rr = requests.put(url, data=data, headers=h, timeout=600)
            if rr.status_code in (200, 201):
                break
            log('put', key, rr.status_code, rr.text[:120])
        except Exception as e:
            log('put err', key, type(e).__name__, str(e)[:120])
        time.sleep(5 * (attempt + 1))
    else:
        raise SystemExit('upload failed: ' + key)
    st, r = api.req('POST', f'{api.API}/records/{DRAFT}/draft/files/{requests.utils.quote(key, safe="")}/commit')
    log('uploaded', n, key)

st, r = api.req('PUT', f'{api.API}/records/{DRAFT}/draft', data={'metadata': meta()})
log('meta', st)
st, r = api.req('POST', f'{api.API}/records/{DRAFT}/draft/actions/publish')
log('published', st, r.get('doi'), r.get('links', {}).get('self_html'))
io.open('/tmp/publish_rg_result.json', 'w', encoding='utf-8').write(
    json.dumps({'draft': DRAFT, 'doi': r.get('doi'), 'resp': r}, ensure_ascii=False)[:4000])
