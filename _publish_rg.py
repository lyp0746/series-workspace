# -*- coding: utf-8 -*-
import json, io, os, sys, time
sys.path.insert(0,'_zenodo')
import api
import requests

SLUG_DIR='D:/0_Article/resolution-grain'
REL=os.path.join(SLUG_DIR,'release')
REC=24393431

zj=json.load(io.open(os.path.join(SLUG_DIR,'.zenodo.json'),encoding='utf-8'))

def meta():
    m={
      "title": zj['title'],
      "publication_date": zj['publication_date'],
      "version": zj['version'],
      "resource_type": {"id": "publication-book"},
      "creators": [{"person_or_org": {"type":"personal","name":"李毅芃","given_name":"毅芃","family_name":"李"},
                    "affiliations":[{"name":"独立研究者 / Independent Researcher"}]}],
      "description": zj['description'],
      "rights": [{"id": "cc-by-4.0"}],
      "subjects": [{"subject": k} for k in zj.get('keywords',[])] ,
      "languages": [{"id": "zho"}, {"id": "eng"}],
      "publisher": zj.get('publisher','独立出版 / Independently published'),
      "related_identifiers": [
          {"identifier": r['identifier'],
           "scheme": r.get('scheme','doi'),
           "relation_type": {"id": r['relation'].lower()}}
          for r in zj.get('related_identifiers',[])],
    }
    return m

def log(*a): print(*a, flush=True)

draft = int(sys.argv[1]) if len(sys.argv)>1 else None
if not draft:
    st, r = api.req("POST", f"{api.API}/records/{REC}/versions")
    draft = r['id']
log('draft', draft)

try:
    st, r = api.req("POST", f"{api.API}/records/{draft}/draft/pids/doi")
    doi = r.get('pids',{}).get('doi',{}).get('identifier')
except Exception as e:
    doi = None
    print('DOI 预留失败（发布时自动分配）：', str(e)[:120])
log('reserved doi', doi)

files=[]
for root,_,fs in os.walk(REL):
    if os.path.relpath(root, REL).split(os.sep)[0] == 'visuals':
        continue
    for f in fs:
        p=os.path.join(root,f)
        files.append((os.path.relpath(p,REL).replace('\\','/'), p))
files.sort()
log('files', len(files), 'bytes', sum(os.path.getsize(p) for _,p in files))

# 清空草稿里继承的文件
st, cur = api.req("GET", f"{api.API}/records/{draft}/draft/files?size=200")
existing=[e['key'] for e in cur.get('entries',[])]
if existing:
    st, r2 = api.req("DELETE", f"{api.API}/records/{draft}/draft/files",
                     data=[{"key":k} for k in existing])
    log('cleared inherited', len(existing))

# 建条目
B=200
for i in range(0,len(files),B):
    chunk=files[i:i+B]
    st, r3 = api.req("POST", f"{api.API}/records/{draft}/draft/files",
                     data=[{"key":k} for k,_ in chunk])
    log('entries created', i+len(chunk))

# 上传内容 + commit
for n,(k,p) in enumerate(files,1):
    with open(p,'rb') as fh:
        data=fh.read()
    url=f"{api.API}/records/{draft}/draft/files/{requests.utils.quote(k, safe='')}/content"
    h={"Authorization":"Bearer "+api.TOK,"Content-Type":"application/octet-stream"}
    r=requests.put(url, data=data, headers=h, timeout=600)
    r.raise_for_status()
    r=requests.post(f"{api.API}/records/{draft}/draft/files/{requests.utils.quote(k, safe='')}/commit",
                    headers={"Authorization":"Bearer "+api.TOK}, timeout=300)
    r.raise_for_status()
    if n%20==0 or n==len(files): log('uploaded', n)

st, r = api.req("PUT", f"{api.API}/records/{draft}/draft", data={"metadata": meta()})
log('meta', st)

st, r = api.req("POST", f"{api.API}/records/{draft}/draft/actions/publish")
log('published', st, r.get('doi'), r.get('links',{}).get('self_html'))
io.open('/tmp/publish_rg_result.json','w',encoding='utf-8').write(json.dumps({'draft':draft,'doi':doi,'resp':r},ensure_ascii=False)[:4000])
