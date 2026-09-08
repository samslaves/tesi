"""Quantum simulation del trimero anello isoscele: exp(-iHt) via Suzuki-Trotter.

Convenzione IDENTICA a trimer_ring_exact.py (sorgente unica per l'Hamiltoniana):
site1 -> qubit2, site2 -> qubit1, site3 -> qubit0. Convenzione Pauli DIRETTA
(non spin s=sigma/2): H = b*Sz_tot + H_ex + H_DM, con

    H_ex = J (sigma1.sigma2) + J' (sigma2.sigma3 + sigma3.sigma1)
    H_DM = D*J (X1Z2-Z1X2) + D*J' (X2Z3-Z2X3) + D*J' (X3Z1-Z3X1)   [Opzione B]

ATTENZIONE convenzione: questa e' DIVERSA da trotter_dimero.py, che usa la
convenzione a spin (s=sigma/2, coefficienti J/4, b/2, quella degli appunti
del relatore per il dimero). Qui si segue invece la convenzione diretta
del resto del progetto trimero (VQE, benchmark esatto). Gli angoli dei gate
sono stati ri-derivati da zero per questa convenzione (vedi deriva_angoli.py):

    qc.rxx/ryy/rzz(theta) = exp(-i theta/2 PP)  ->  per exp(-i tau*Jij*PP): theta = 2*Jij*tau
    qc.rz(theta) = exp(-i theta/2 Z)             ->  per exp(-i tau*b*Zi):   theta = 2*b*tau
    blocco XiZj-ZiXj: stesso trucco H-sandwich del dimero, angolo 2*Dij*tau

Struttura a TRE livelli annidati (verificata numericamente in
verifica_tre_livelli.py, vedi anche deriva_angoli.py per la validazione
dei singoli blocchi di gate):
    livello 0 (ESATTO, nessun errore): H0 = b*Sz_tot + H_ex fattorizza
        esattamente perche' [Sz_tot, H_ex] = 0 (anche bond per bond).
    livello 1: H_ex spezzato in Trotter nei 3 bond (single pass, M=1 per
        passo esterno) -- i bond 12 e 23 condividono il qubit 2 e non
        commutano fra loro.
    livello 2: H_DM spezzato in Trotter nei 3 bond (single pass, M=1) --
        stesso motivo, verificato non trascurabile rispetto al livello 1.
Trotter ESTERNO di 1o ordine fra H0 e H_DM, N passi, errore O((t/N)^2) per
passo (dovuto solo a [Sz_tot, H_DM] != 0; H_ex non contribuisce all'errore
esterno perche' commuta esattamente col campo).
"""
import numpy as np
import scipy.linalg as sla
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, Operator

from trimer_ring_exact import trimer_hamiltonian, trimer_hamiltonian_dm, magnetization_operator

# ---------------------------------------------------------------------
# convenzione sito <-> qubit, identica a trimer_ring_exact.py
# ---------------------------------------------------------------------
Q = {1: 2, 2: 1, 3: 0}                 # sito -> indice qubit Qiskit
BONDS = [(1, 2), (2, 3), (3, 1)]       # ordine di applicazione nel passo interno

PSI0 = Statevector.from_label('000')   # |000>, stato iniziale di lavoro
SZ_TOT = magnetization_operator().to_matrix() * 2   # occhio: magnetization_operator() e' Mz=(Z1+Z2+Z3)/2 (convenzione s=sigma/2);
                                                      # qui vogliamo Sz_tot "diretto" = Z1+Z2+Z3, quindi *2


def _Jij(bond, J, Jp):
    return J if bond == (1, 2) else Jp


# ---------------------------------------------------------------------
# blocchi di circuito (Trotter 1o ordine, single pass sui bond)
# ---------------------------------------------------------------------
def step_field(qc, b, tau):
    """exp(-i tau b Sz_tot), ESATTO (nessuna approssimazione)."""
    for site in (1, 2, 3):
        qc.rz(2 * b * tau, Q[site])


def step_Hex(qc, J, Jp, tau):
    """Trotter interno 1o ordine per H_ex, singola passata sui 3 bond (livello 1)."""
    for (i, j) in BONDS:
        Jij = _Jij((i, j), J, Jp)
        qi, qj = Q[i], Q[j]
        qc.rxx(2 * Jij * tau, qi, qj)
        qc.ryy(2 * Jij * tau, qi, qj)
        qc.rzz(2 * Jij * tau, qi, qj)


def step_HDM(qc, J, Jp, D, tau):
    """Trotter interno 1o ordine per H_DM (Opzione B), singola passata (livello 2)."""
    for (i, j) in BONDS:
        Dij = D * _Jij((i, j), J, Jp)
        qi, qj = Q[i], Q[j]
        qc.h(qi); qc.rzz(2 * Dij * tau, qi, qj); qc.h(qi)      # exp(-i tau Dij Xi Zj)
        qc.h(qj); qc.rzz(-2 * Dij * tau, qi, qj); qc.h(qj)     # exp(+i tau Dij Zi Xj)


def trotter_circuit(J, Jp, b, D, t, N, measure=False):
    """Circuito completo: N passi esterni, ordine H_ex - campo - H_DM per passo."""
    qc = QuantumCircuit(3, 3) if measure else QuantumCircuit(3)
    tau = t / N
    for _ in range(N):
        step_Hex(qc, J, Jp, tau)
        step_field(qc, b, tau)
        step_HDM(qc, J, Jp, D, tau)
        qc.barrier()
    if measure:
        qc.measure([0, 1, 2], [0, 1, 2])
    return qc


# ---------------------------------------------------------------------
# riferimenti a matrice (stessa sorgente Hamiltoniana del benchmark esatto)
# ---------------------------------------------------------------------
def H_parts(J, Jp, b, D):
    """(H0, H_DM) come matrici 8x8, H0 = b*Sz_tot + H_ex, riuso diretto di
    trimer_ring_exact.py per zero ambiguita' di convenzione."""
    H_base = trimer_hamiltonian(J, Jp, b).to_matrix()          # = H0
    H_full = trimer_hamiltonian_dm(J, Jp, b, "B", D).to_matrix()
    return H_base, H_full - H_base


def U_exact(J, Jp, b, D, t):
    H0, H_DM = H_parts(J, Jp, b, D)
    return sla.expm(-1j * (H0 + H_DM) * t)


def sz_tot(psi):
    return float(np.real(np.asarray(psi).conj() @ SZ_TOT @ np.asarray(psi)))


# ---------------------------------------------------------------------
# self-test
# ---------------------------------------------------------------------
def _self_test():
    rng = np.random.default_rng(0)
    print("=" * 70)
    print("[self-test 1] Sz_tot: coerenza con magnetization_operator()*2")
    Sz_check = (trimer_hamiltonian(0, 0, 0.5).to_matrix() - trimer_hamiltonian(0, 0, 0).to_matrix())
    # trimer_hamiltonian(J=0,Jp=0,b) = b*(Z1+Z2+Z3) -> derivata rispetto a b da' Sz_tot
    err = np.linalg.norm(Sz_check / 0.5 - SZ_TOT)
    print(f"    ||Sz_tot(qui) - Sz_tot(da trimer_hamiltonian)|| = {err:.3e}")
    assert err < 1e-12

    print("[self-test 2] circuito N=1 (livello 1+2 espliciti) vs prodotto a matrice")
    for _ in range(5):
        J, Jp, b, D = rng.uniform(-2, 2, 4)
        t, N = rng.uniform(0.1, 1.0), 1
        qc = trotter_circuit(J, Jp, b, D, t, N)
        U_circ = Operator(qc).data
        H0, H_DM = H_parts(J, Jp, b, D)
        tau = t / N
        # stessa costruzione "a mano" del circuito, ma a livello di matrice 8x8
        U_field = sla.expm(-1j * b * tau * SZ_TOT)
        U_hex_bond = np.eye(8, dtype=complex)
        for (i, j) in BONDS:
            Jij = _Jij((i, j), J, Jp)
            Hij = _bond_exchange_matrix(i, j)
            U_hex_bond = sla.expm(-1j * Jij * tau * Hij) @ U_hex_bond
        U_hdm_bond = np.eye(8, dtype=complex)
        for (i, j) in BONDS:
            Dij = D * _Jij((i, j), J, Jp)
            Hij = _bond_dm_matrix(i, j)
            U_hdm_bond = sla.expm(-1j * Dij * tau * Hij) @ U_hdm_bond
        U_mat = U_hdm_bond @ U_field @ U_hex_bond
        err = np.linalg.norm(U_circ - U_mat)
        print(f"    J={J:+.3f} J'={Jp:+.3f} b={b:+.3f} D={D:+.3f} t={t:.3f}: "
              f"||U_circuito - U_matrice|| = {err:.3e}")
        assert err < 1e-10

    print("[self-test 3] convergenza N->infinito verso U_exact (fidelity su |000>)")
    J, Jp, b, D, t = 1.0, 0.4, 1.0, 0.3, 2.0
    psi_ref = U_exact(J, Jp, b, D, t) @ PSI0.data
    prev_err = None
    for N in [5, 10, 20, 40, 80]:
        qc = trotter_circuit(J, Jp, b, D, t, N)
        psi = Statevector(qc).data
        infid = 1 - abs(np.vdot(psi_ref, psi)) ** 2
        ratio = f"  (rapporto vs precedente: {prev_err / infid:.2f})" if prev_err else ""
        print(f"    N={N:4d}: infedelta = {infid:.3e}{ratio}")
        prev_err = infid
    print("    atteso: infedelta ~ O(1/N^2) [energia/fidelity], rapporto ~4 raddoppiando N")

    print("[self-test 4] livello 0: H0 fattorizza esattamente (indipendente da Trotter)")
    for _ in range(3):
        J, Jp, b = rng.uniform(-2, 2, 3)
        tau = rng.uniform(0.05, 0.5)
        H0, _ = H_parts(J, Jp, b, 0.0)
        H_ex_only = H0 - b * SZ_TOT
        U_H0_exact = sla.expm(-1j * H0 * tau)
        U_field = sla.expm(-1j * b * tau * SZ_TOT)
        U_hex_exact = sla.expm(-1j * H_ex_only * tau)
        err = np.linalg.norm(U_H0_exact - U_field @ U_hex_exact)
        print(f"    J={J:+.3f} J'={Jp:+.3f} b={b:+.3f}: ||U_H0 - U_campo*U_Hex_esatto|| = {err:.3e}")
        assert err < 1e-12

    print("=" * 70)
    print("[self-test] TUTTI I TEST SUPERATI")
    print("=" * 70)


def _bond_exchange_matrix(i, j):
    from qiskit.quantum_info import Pauli
    chars = {}
    for s in (1, 2, 3):
        chars[s] = 'I'
    labs = []
    for P in ('X', 'Y', 'Z'):
        c = ['I', 'I', 'I']
        pos = {1: 0, 2: 1, 3: 2}
        c[pos[i]] = P
        c[pos[j]] = P
        labs.append(''.join(c))
    return sum(Pauli(l).to_matrix() for l in labs)


def _bond_dm_matrix(i, j):
    from qiskit.quantum_info import Pauli
    pos = {1: 0, 2: 1, 3: 2}
    c1, c2 = ['I', 'I', 'I'], ['I', 'I', 'I']
    c1[pos[i]], c1[pos[j]] = 'X', 'Z'
    c2[pos[i]], c2[pos[j]] = 'Z', 'X'
    return Pauli(''.join(c1)).to_matrix() - Pauli(''.join(c2)).to_matrix()


if __name__ == "__main__":
    from qiskit.quantum_info import Pauli
    _self_test()
