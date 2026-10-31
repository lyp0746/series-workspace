import numpy as np, itertools, json
def lap(n, edges):
    A=np.zeros((n,n))
    for u,v in edges: A[u,v]=A[v,u]=1
    return np.diag(A.sum(1))-A
def R(ev):
    ev=np.sort(np.asarray(ev)); nz=ev[np.abs(ev)>1e-9]
    return ev[-1]/nz[0] if len(nz)>1 else float('nan')
def show(name, n, edges):
    ev=np.linalg.eigvalsh(lap(n,edges))
    ev=np.round(np.sort(ev),6)
    print("%-18s n=%2d  λ2=%.4f λn=%.4f  R=%.4f   spec=%s"%(name,n,ev[1],ev[-1],R(ev),np.round(ev,3)))
# families
def Kn(n): return [(i,j) for i in range(n) for j in range(i+1,n)]
def Kmn(m,nn): return [(i,m+j) for i in range(m) for j in range(nn)]
def cycle(n): return [(i,(i+1)%n) for i in range(n)]
def path(n): return [(i,i+1) for i in range(n-1)]
def star(n): return [(0,i) for i in range(1,n)]
def hyper(d):
    n=1<<d; return [(i,i^(1<<b)) for i in range(n) for b in range(d) if i < (i^(1<<b))]
def petersen():
    out=[(i,(i+1)%5) for i in range(5)]; inn=[(5+i,5+(i+2)%5) for i in range(5)]; sp=[(i,5+i) for i in range(5)]
    return out+inn+sp
show("K5",5,Kn(5)); show("K20",20,Kn(20))
show("K1,9",10,star(10)); show("K2,3",5,Kmn(2,3)); show("K3,7",10,Kmn(3,7))
show("C10",10,cycle(10)); show("C100",100,cycle(100))
show("P10",10,path(10)); show("P100",100,path(100))
show("Q3",8,hyper(3)); show("Q6",64,hyper(6))
show("Petersen",10,petersen())
# grid P_n x P_n
def grid(n):
    E=[]
    idx=lambda i,j: i*n+j
    for i in range(n):
        for j in range(n):
            if i+1<n: E.append((idx(i,j),idx(i+1,j)))
            if j+1<n: E.append((idx(i,j),idx(i,j+1)))
    return n*n,E
for n in (5,10,20,40):
    N,E=grid(n); show("grid%d"%n,N,E)
# torus C_n x C_n
def torus(n):
    N=n*n; idx=lambda i,j:(i%n)*n+(j%n); E=[]
    for i in range(n):
        for j in range(n):
            E.append((idx(i,j),idx(i+1,j))); E.append((idx(i,j),idx(i,j+1)))
    return N,E
for n in (4,8,16):
    N,E=torus(n); show("torus%d"%n,N,E)
print()
print("理论值对照：")
for n in (10,100,1000):
    print("  C_n: λ2=%.6f λn=4  R=%.2f  (approx (2n/π)²=%.1f)"%(2-2*np.cos(2*np.pi/n),4/(2-2*np.cos(2*np.pi/n)),(2*n/np.pi)**2))
for n in (10,100,1000):
    l2=2-2*np.cos(np.pi/n); ln=2-2*np.cos(np.pi*(n-1)/n)
    print("  P_n: λ2=%.6f λn=%.6f R=%.2f"%(l2,ln,ln/l2))
