import itertools, numpy as np
from collections import defaultdict
def trees(n):
    seen=set()
    for seq in itertools.product(range(n), repeat=n-2):
        deg=[1]*n
        for x in seq: deg[x]+=1
        seq=list(seq); edges=[]; d=deg[:]
        for x in seq:
            for i in range(n):
                if d[i]==1:
                    edges.append((i,x)); d[i]-=1; d[x]-=1; break
        rest=[i for i in range(n) if d[i]==1]
        edges.append(tuple(sorted(rest)))
        e=tuple(sorted(tuple(sorted(x)) for x in edges))
        if e not in seen:
            seen.add(e); yield e
def spec(n,e,rounded=4):
    A=np.zeros((n,n))
    for u,v in e: A[u,v]=A[v,u]=1
    return tuple(np.round(np.linalg.eigvalsh(A),rounded))
for n in (8,9):
    b=defaultdict(list)
    cnt=0
    for e in trees(n):
        cnt+=1; b[spec(n,e)].append(e)
    pairs={k:v for k,v in b.items() if len(v)>1}
    print("n=%d 无标号树=%d 同谱组=%d"%(n,cnt,len(pairs)))
    for k,v in list(pairs.items())[:3]:
        print("  spec:",k)
        for e in v[:2]:
            deg=[0]*n
            for u,w in e: deg[u]+=1; deg[w]+=1
            print("    边:",sorted(e)," 度序列:",sorted(deg,reverse=True))
