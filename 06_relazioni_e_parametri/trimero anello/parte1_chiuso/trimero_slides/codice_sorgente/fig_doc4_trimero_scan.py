"""Documento 4 (trimero anello) — validazione e scan sistematico 81 combinazioni."""
import os, itertools, time
import numpy as np
import scipy.linalg as sla
from qiskit.quantum_info import SparsePauliOp
from circuito_correlazioni_trimero_anello import ground_state, correlator_from_circuit
from trotter_trimero_anello import Q

os.makedirs("figure", exist_ok=True)
J, Jp, b, D = 1.0, 0.4, 2.4, 0.15   # Scenario A
psi0, E = ground_state(J, Jp, b, D)

PAULI = {"x":"X","y":"Y","z":"Z"}
def op_sito(sito, alpha):
    lab = ["I","I","I"]
    lab[2-Q[sito]] = PAULI[alpha]     # Q: sito->qubit; stringa scritta q2 q1 q0
    return SparsePauliOp("".join(lab)).to_matrix()

from trimer_ring_exact import trimer_hamiltonian_dm
H = trimer_hamiltonian_dm(J, Jp, b, "B", D).to_matrix()

def C_esatto(i, alpha, j, beta, ts):
    Vop, Wop = op_sito(i, alpha), op_sito(j, beta)
    out = []
    for t in ts:
        U = sla.expm(-1j*H*t)
        out.append(psi0.conj() @ U.conj().T @ Vop @ U @ Wop @ psi0)
    return np.array(out)

# ---- validazione circuito vs esatto (un correlatore rappresentativo)
ts_fine = np.linspace(0, 6, 121)
ts_circ = np.linspace(0, 6, 13)
i,al,j,be = 2,"x",1,"x"
t0=time.time()
C_ref = C_esatto(i,al,j,be,ts_fine)
C_cir = np.array([correlator_from_circuit(i,al,j,be,t,60,J,Jp,b,D,psi0=psi0) for t in ts_circ])
C_ref_at = C_esatto(i,al,j,be,ts_circ)
res = np.abs(C_cir - C_ref_at)
print(f"[validazione] C_{i}{j}^{al}{be}: residuo medio {res.mean():.2e}, max {res.max():.2e}  (N=60, t={time.time()-t0:.0f}s)")
np.savez("_val_doc4.npz", ts_fine=ts_fine, ts_circ=ts_circ, C_ref=C_ref, C_cir=C_cir)

# ---- scan 81 combinazioni
siti = [1,2,3]; comp=["x","y","z"]
ts_scan = np.linspace(0, 8, 81)
dati = {}
t0=time.time()
for (i_,al_) in itertools.product(siti,comp):
    for (j_,be_) in itertools.product(siti,comp):
        dati[(i_,al_,j_,be_)] = C_esatto(i_,al_,j_,be_,ts_scan)
print(f"[scan] 81 combinazioni calcolate, t={time.time()-t0:.0f}s")

ampiezza = np.zeros((9,9)); istante0=np.zeros((9,9))
righe=[]; colonne=[]
combos = list(itertools.product(siti,comp))
for a_idx,(i_,al_) in enumerate(combos):
    righe.append(rf"$\sigma_{{{i_}}}^{{{al_}}}(t)$")
    for b_idx,(j_,be_) in enumerate(combos):
        if a_idx==0: colonne.append(rf"$\sigma_{{{j_}}}^{{{be_}}}(0)$")
        c = dati[(i_,al_,j_,be_)]
        ampiezza[a_idx,b_idx] = np.abs(c).max()
        istante0[a_idx,b_idx] = abs(c[0])

np.savez("_scan81_doc4.npz", ampiezza=ampiezza, istante0=istante0,
         righe=righe, colonne=colonne, ts_scan=ts_scan,
         combos=np.array(combos,dtype=object),
         **{f"C_{k[0]}{k[1]}{k[2]}{k[3]}": v for k,v in dati.items()})

nulli0 = [(i_,al_,j_,be_) for (i_,al_,j_,be_),c in dati.items() if abs(c[0])<1e-10]
print(f"[scan] combinazioni nulle a t=0: {len(nulli0)}")
print(nulli0)

chiavi = list(dati.keys())
varianza = {k: np.std(np.real(dati[k]))+np.std(np.imag(dati[k])) for k in chiavi}
ricco = max(varianza, key=varianza.get)
piatto = min(varianza, key=varianza.get)
print(f"[scan] piu' strutturato: {ricco} (std={varianza[ricco]:.3f})")
print(f"[scan] piu' piatto: {piatto} (std={varianza[piatto]:.3f})")
print(f"[scan] ampiezza min/max: {ampiezza.min():.3f} / {ampiezza.max():.3f}")
