import numpy as np
from numpy import kron

I2 = np.eye(2)
X = np.array([[0,1],[1,0]], dtype=complex)
Y = np.array([[0,-1j],[1j,0]])
Z = np.array([[1,0],[0,-1]], dtype=complex)

def op(site, P):
    # site in {1,2,3}, embed P at that site, identity elsewhere (3 qubits)
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

rng = np.random.default_rng(0)
maxerr = 0
for _ in range(200):
    J = rng.uniform(-3,3)
    b = rng.uniform(-3,3)
    H = H_chain(J,b)
    ev_num = np.sort(np.linalg.eigvalsh(H))

    # closed form: blocks A'(S13=1,S=3/2): E=2J*1 + 2b*M, M=3/2,1/2,-1/2,-3/2
    # B'(S13=1,S=1/2): E=2J*(-2)+2b*M, M=1/2,-1/2
    # C'(S13=0,S=1/2): E=0+2b*M, M=1/2,-1/2
    Ms_A = [1.5,0.5,-0.5,-1.5]
    Ms_B = [0.5,-0.5]
    Ms_C = [0.5,-0.5]
    ev_closed = []
    for M in Ms_A: ev_closed.append(2*J*1 + 2*b*M)
    for M in Ms_B: ev_closed.append(2*J*(-2) + 2*b*M)
    for M in Ms_C: ev_closed.append(2*J*0 + 2*b*M)
    ev_closed = np.sort(np.array(ev_closed))

    err = np.max(np.abs(ev_num-ev_closed))
    maxerr = max(maxerr, err)

print("max error over 200 random (J,b):", maxerr)

# trace check
J,b = 1.3, -0.7
H = H_chain(J,b)
print("trace H:", np.trace(H))

# verify P13 symmetry: [P13, H]=0 for J12=J23 (uniform), and S13^2 conservation
# build swap of qubits 1 and 3 (3-qubit permutation matrix)
def perm_13():
    P = np.zeros((8,8))
    for idx in range(8):
        b0 = (idx>>2)&1; b1=(idx>>1)&1; b2 = idx&1  # bits for qubit1,2,3 (MSB=qubit1)
        new_idx = (b2<<2)|(b1<<1)|b0  # swap qubit1 and qubit3 bits
        P[new_idx, idx] = 1
    return P

P13 = perm_13()
J,b = 0.9, 0.4
H = H_chain(J,b)
comm = P13@H - H@P13
print("‖[P13,H]‖ uniform case:", np.max(np.abs(comm)))

# non-uniform case J12 != J23
def H_chain_nonuniform(J12,J23,b):
    H = J12*dot(1,2) + J23*dot(2,3)
    for s in (1,2,3):
        H = H + b*op(s,Z)
    return H
Hnu = H_chain_nonuniform(0.9,0.5,0.4)
comm2 = P13@Hnu - Hnu@P13
print("‖[P13,H]‖ non-uniform case:", np.max(np.abs(comm2)))

# ground state crossing field for J>0: check b_c = 3J numerically
J = 1.0
bs = np.linspace(0,5,2001)
gs_M = []
for b in bs:
    H = H_chain(J,b)
    w = np.linalg.eigvalsh(H)
    gs_M.append(w[0])
gs_M = np.array(gs_M)
# find where slope changes (kink) numerically via second difference
d2 = np.diff(gs_M,2)
kink_idx = np.argmax(np.abs(d2))
print("numerical b_c (J=1):", bs[kink_idx+1], " expected 3J=3.0")

# J<0 : check ground state stays in A' block (S=3/2) for all b (no crossing)
Jn = -1.0
prev_slope=None
kinks=0
gsE=[]
for b in bs:
    H=H_chain(Jn,b)
    w=np.linalg.eigvalsh(H)
    gsE.append(w[0])
gsE=np.array(gsE)
d2n = np.diff(gsE,2)
print("max curvature J<0 case (should be ~0, no kink):", np.max(np.abs(d2n)))
