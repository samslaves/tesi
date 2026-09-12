import time
import numpy as np
import scipy.linalg as sla
from qiskit.quantum_info import SparsePauliOp
from circuito_correlazioni_trimero_anello import ground_state, correlator_from_circuit
from trotter_trimero_anello import Q

J, Jp, b, D = 1.0, 0.4, 2.4, 0.15
psi0_exact, E = ground_state(J, Jp, b, D)
data = np.load("w2q6_params_optimal.npz")
vqe_params = data["params"]

# --- curva C(t): esatto vs VQE, entrambe via circuito completo ---
ts = np.linspace(0.0, 6.0, 13)
N = 60
t0 = time.time()
C_esatto = np.array([correlator_from_circuit(2,"x",1,"x",t,N,J,Jp,b,D, psi0=psi0_exact) for t in ts])
C_vqe    = np.array([correlator_from_circuit(2,"x",1,"x",t,N,J,Jp,b,D, ansatz_params=vqe_params) for t in ts])
print(f"curva C(t): tempo={time.time()-t0:.0f}s")
scarto_t = np.abs(C_vqe - C_esatto)
print(f"scarto su C(t): medio={scarto_t.mean():.3e}  massimo={scarto_t.max():.3e}")
np.savez("_vqe_vs_esatto_curva.npz", ts=ts, C_esatto=C_esatto, C_vqe=C_vqe)

# --- scan 81 combinazioni, a t=2 fisso, N=60 ---
import itertools
siti = [1,2,3]; comp = ["x","y","z"]
t0 = time.time()
scarti = []
righe_dati = []
for (i_,al_) in itertools.product(siti,comp):
    for (j_,be_) in itertools.product(siti,comp):
        ce = correlator_from_circuit(i_,al_,j_,be_,2.0,N,J,Jp,b,D, psi0=psi0_exact)
        cv = correlator_from_circuit(i_,al_,j_,be_,2.0,N,J,Jp,b,D, ansatz_params=vqe_params)
        s = abs(cv-ce)
        scarti.append(s)
        righe_dati.append((i_,al_,j_,be_,abs(ce),abs(cv),s))
scarti = np.array(scarti)
print(f"scan 81: tempo={time.time()-t0:.0f}s")
print(f"scarto medio={scarti.mean():.3e}  massimo={scarti.max():.3e}  minimo={scarti.min():.3e}")

idx_max = np.argmax(scarti)
print("combinazione con scarto massimo:", righe_dati[idx_max][:4], "scarto=", righe_dati[idx_max][-1])

np.savez("_vqe_vs_esatto_scan81.npz", scarti=scarti,
         righe=np.array(righe_dati, dtype=object))
