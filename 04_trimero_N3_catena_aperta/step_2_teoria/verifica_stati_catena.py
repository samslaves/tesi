import numpy as np
from numpy import kron

I2 = np.eye(2)
X = np.array([[0,1],[1,0]], dtype=complex)
Y = np.array([[0,-1j],[1j,0]])
Z = np.array([[1,0],[0,-1]], dtype=complex)

def op(site, P):
    ops = [I2, I2, I2]
    ops[site-1] = P
    return kron(kron(ops[0], ops[1]), ops[2])

def dot(i,j):
    return op(i,X)@op(j,X) + op(i,Y)@op(j,Y) + op(i,Z)@op(j,Z)

def H_chain(J, b):
    H = J*(dot(1,2) + dot(2,3))
    for s in (1,2,3):
        H = H + b*op(s,Z)
    return H

# indice base computazionale |q1 q2 q3>, q=0 -> up (Z=+1), q=1 -> down (Z=-1)
def ket(bits):
    v = np.zeros(8, dtype=complex)
    idx = int(bits,2)
    v[idx] = 1.0
    return v

def state(coeffs):
    # coeffs: list of (amplitude, 'bits')
    v = np.zeros(8, dtype=complex)
    for a,b in coeffs:
        v += a*ket(b)
    n = np.linalg.norm(v)
    return v, n

s3=np.sqrt(3); s6=np.sqrt(6); s2=np.sqrt(2)

states = {
 ("A", 1.5): [(1.0,'000')],
 ("A", 0.5): [(1/s3,'001'),(1/s3,'010'),(1/s3,'100')],
 ("A",-0.5): [(1/s3,'011'),(1/s3,'101'),(1/s3,'110')],
 ("A",-1.5): [(1.0,'111')],
 ("B", 0.5): [(1/s6,'100'),(1/s6,'001'),(-np.sqrt(2/3),'010')],
 ("B",-0.5): [(1/s6,'011'),(1/s6,'110'),(-np.sqrt(2/3),'101')],
 ("C", 0.5): [(1/s2,'001'),(-1/s2,'100')],
 ("C",-0.5): [(1/s2,'011'),(-1/s2,'110')],
}

QN = {"A":(1,1.5), "B":(1,0.5), "C":(0,0.5)}  # (S13, S)

J, b = 1.3, -0.7
H = H_chain(J,b)

print(f"{'stato':10s} {'||v||^2':>12s} {'E_num':>12s} {'E_teor':>12s}")
vecs=[]
for (mult,M),coeffs in states.items():
    v,n = state(coeffs)
    S13,S = QN[mult]
    Eteor = 2*J*(S*(S+1)-S13*(S13+1)-0.75) + 2*b*M
    Enum = np.real(v.conj()@H@v)
    vecs.append((f"{mult},{M:+.1f}",v))
    print(f"{mult},{M:+.1f}   {n**2:12.9f} {Enum:12.5f} {Eteor:12.5f}")
    # verifica autovettore esatto
    resid = np.linalg.norm(H@v - Eteor*v)
    if resid>1e-9:
        print("  ATTENZIONE residuo alto:", resid)

# matrice di Gram (ortogonalita')
V = np.array([v for _,v in vecs]).T
Gram = V.conj().T@V
offdiag = Gram - np.diag(np.diag(Gram))
print("\nmax elemento fuori diagonale Gram:", np.max(np.abs(offdiag)))
print("max |diag-1|:", np.max(np.abs(np.diag(Gram)-1)))

# verifica residuo esatto per ogni stato
print()
for (mult,M),coeffs in states.items():
    v,n = state(coeffs)
    S13,S = QN[mult]
    Eteor = 2*J*(S*(S+1)-S13*(S13+1)-0.75) + 2*b*M
    resid = np.linalg.norm(H@v - Eteor*v)
    print(f"{mult},{M:+.1f}  ||Hv-Ev||={resid:.3e}")
