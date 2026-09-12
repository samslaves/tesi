import sys
sys.path.insert(0, "codice")


"""Scan sistematico delle 36 combinazioni C_ij^{alpha,beta}(t) al punto
di lavoro "test 2" (Documento 4) -- assente dalla prima versione di
questo pacchetto.

  1. Zeri all'istante iniziale: verificati 12/36 (stato fondamentale
     reale, prodotti hermitiani-ma-immaginari hanno media nulla su
     t=0) -- due famiglie: otto combinazioni a siti diversi con una
     sola componente y, quattro sullo stesso sito con componenti x,z.
  2. Nessuna casella resta nulla per max_t su t in [0,8]: gli zeri a
     t=0 non sono zeri strutturali (a differenza del trimero, dove 4/81
     lo sono).
"""
import itertools
import numpy as np
import scipy.linalg as sla

from circuito_correlazioni_dimero import ground_state

b, J, D = 0.35, 1.0, 0.80
I2 = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)
PAULI = {"x": X, "y": Y, "z": Z}
SITI = (1, 2)
COMP = ("x", "y", "z")


def site_op(site, alpha):
    ops = [I2, I2]
    ops[site - 1] = PAULI[alpha]
    return np.kron(ops[0], ops[1])


def dimer_H(b, J, D):
    # H = J(XX+YY+ZZ) + b(Z1+Z2) + D(X1Z2-Z1X2) -- stessa Hamiltoniana di
    # dimer_exact.dimer_hamiltonian, ricostruita qui in forma di matrice
    # esplicita per il solo scopo di classical_exact (nessuna nuova fisica).
    from dimer_exact import dimer_hamiltonian
    return dimer_hamiltonian(b, J=J, D=D).to_matrix()


H = dimer_H(b, J, D)
psi0, _ = ground_state(b, J=J, D=D)


def classical_exact(i, alpha, j, beta, t):
    A = site_op(i, alpha); B = site_op(j, beta)
    Ut = sla.expm(-1j * H * t)
    return np.vdot(psi0, Ut.conj().T @ A @ Ut @ B @ psi0)


print("=" * 70)
print("1. ZERI ALL'ISTANTE INIZIALE (t=0)")
print("=" * 70)
zeri_t0 = []
righe = []
for (i, al), (j, be) in itertools.product(itertools.product(SITI, COMP),
                                            itertools.product(SITI, COMP)):
    c0 = classical_exact(i, al, j, be, 0.0)
    if abs(c0) < 1e-9:
        zeri_t0.append((i, al, j, be))
print(f"  zeri a t=0: {len(zeri_t0)}/36  (atteso: 12)")
assert len(zeri_t0) == 12, f"atteso 12, trovati {len(zeri_t0)}"
print("  -> OK")

print()
print("=" * 70)
print("2. MASSIMO SU t IN [0,8]: nessuna casella nulla")
print("=" * 70)
t_grid = np.linspace(0, 8, 161)
val_t0, val_max = [], []
for (i, al), (j, be) in itertools.product(itertools.product(SITI, COMP),
                                            itertools.product(SITI, COMP)):
    c0 = abs(classical_exact(i, al, j, be, 0.0))
    cmax = max(abs(classical_exact(i, al, j, be, t)) for t in t_grid)
    val_t0.append(c0); val_max.append(cmax)
    righe.append((i, al, j, be, c0, cmax))

n_nulli_max = sum(1 for v in val_max if v < 1e-6)
print(f"  caselle nulle nel pannello max_t: {n_nulli_max}  (atteso: 0)")
assert n_nulli_max == 0, "atteso nessuna casella nulla in max_t"
print("  -> OK: gli zeri a t=0 non sono zeri strutturali")

np.savez("dati/scan36_correlatori.npz",
         righe=np.array(righe, dtype=object),
         val_t0=np.array(val_t0), val_max=np.array(val_max))
print("\nSalvato: dati/scan36_correlatori.npz")
