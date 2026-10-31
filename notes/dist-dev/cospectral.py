import itertools, numpy as np
from collections import defaultdict
def trees(n):
    # 生成所有 n 顶点树（Pruefer 序列）
    seen=set()
    if n==1: yield (); return
    for seq in itertools.product(range(n), repeat=n-2):
        deg=[1]*n
        for x in seq: deg[x]+=1
        seq=list(seq); edges=[]
        for x in seq:
            for i in range(n):
                if deg[i]==1:
                    edges.append((i,x)); deg[i]-=1; deg[x]-=1; break
        rest=[i for i in range(n) if deg[i]==1]
        edges.append(tuple(sorted(rest)))
        e=tuple(sorted(tuple(sorted(x)) for x in edges))
        if e in seen: continue
        seen.add(e); yield e
for n in (8,9,10,11):
    buckets=defaultdict(list)
    for e in trees(n):
        A=np.zeros((n,n))
        for u,v in e: A[u,v]=A[v,u]=1
        ev=np.round(np.linalg.eigvalsh(A),4)
        buckets[tuple(ev)].append(e)
    pairs=[(k,v) for k,v in buckets.items() if len(v)>1]
    print("n=%d 树数=%d 同谱组=%d"%(n,len(buckets),len(pairs)))
    for k,v in pairs[:2]:
        print("   spec",k[:5],"...")
        for e in v[:2]: print("     ",sorted(e))
