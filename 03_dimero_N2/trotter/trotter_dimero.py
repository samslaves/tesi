"""Quantum simulation del dimero: exp(-iHt) via Suzuki-Trotter (1o ordine).

Convenzione: spin 1 -> qubit 0, spin 2 -> qubit 1.
Stringhe di Pauli in notazione little-endian di Qiskit ('AB': B su q0, A su q1).
H = b(sz1+sz2) + J s1.s2 + D(sx1 sz2 - sz1 sx2) = H1 + H2
"""
import numpy as np, scipy.linalg as sla
from qiskit import QuantumCircuit
from qiskit.quantum_info import Pauli, Operator, Statevector

P = lambda s: Pauli(s).to_matrix()
Z1, Z2 = P('IZ'), P('ZI')
SZ_TOT = (Z1 + Z2) / 2
PSI0 = np.array([1, 0, 0, 0], dtype=complex)          # |00> = |up up>

def H_parts(b, J, D):
    H1 = b/2*(Z1+Z2) + J/4*(P('XX')+P('YY')+P('ZZ'))
    H2 = D/4*(P('ZX') - P('XZ'))                       # X1Z2 - Z1X2
    return H1, H2

# ---------- circuiti ----------
def step_H1(qc, b, J, tau):
    qc.rz(b*tau, 0); qc.rz(b*tau, 1)
    qc.rxx(J*tau/2, 0, 1); qc.ryy(J*tau/2, 0, 1); qc.rzz(J*tau/2, 0, 1)

def step_H2(qc, D, tau):
    qc.h(0); qc.rzz(D*tau/2, 0, 1); qc.h(0)            # exp(-i theta X1Z2)
    qc.h(1); qc.rzz(-D*tau/2, 0, 1); qc.h(1)           # exp(+i theta Z1X2)

def trotter_circuit(b, J, D, t, N, measure=False):
    qc = QuantumCircuit(2, 2) if measure else QuantumCircuit(2)
    tau = t/N
    for _ in range(N):
        step_H1(qc, b, J, tau); step_H2(qc, D, tau); qc.barrier()
    if measure: qc.measure([0, 1], [0, 1])
    return qc

# ---------- riferimenti a matrice ----------
def U_exact(b, J, D, t):
    H1, H2 = H_parts(b, J, D); return sla.expm(-1j*(H1+H2)*t)

def U_trotter_mat(b, J, D, t, N):
    H1, H2 = H_parts(b, J, D); tau = t/N
    # il circuito applica H1 e poi H2 -> in forma matriciale U_step = e^{-iH2 tau} e^{-iH1 tau}
    return np.linalg.matrix_power(sla.expm(-1j*H2*tau) @ sla.expm(-1j*H1*tau), N)

def sz(psi): return float(np.real(psi.conj() @ SZ_TOT @ psi))
