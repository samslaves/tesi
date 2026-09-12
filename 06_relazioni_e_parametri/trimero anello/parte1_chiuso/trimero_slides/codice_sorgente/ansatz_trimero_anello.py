"""Ansatz per il trimero ad anello: famiglia RBS e famiglia W, stessa
struttura esterna (X + tre blocchi sui legami + rotazioni Ry finali),
definite una sola volta e importate da tutti gli script — mirror di
ansatz_dimero.py."""
import numpy as np
from qiskit.circuit import QuantumCircuit, ParameterVector

BOND12, BOND23, BOND31 = (2, 1), (1, 0), (0, 2)
BONDS = [BOND12, BOND23, BOND31]


def rbs_block(qc, phi, q0, q1):
    """Blocco M-conservante RBS (rotazione di Givens reale), stessa
    definizione di ansatz_dimero.py."""
    sub = QuantumCircuit(2, name="RBS")
    sub.h(0); sub.h(1); sub.cz(0, 1)
    sub.ry(phi, 0); sub.ry(-phi, 1)
    sub.cz(0, 1); sub.h(0); sub.h(1)
    qc.append(sub.to_gate(label="RBS"), [q0, q1])


def w_block(qc, theta, q0, q1):
    """Blocco M-conservante W_ij(theta) = CNOT-Ry(theta)-CNOT, stessa
    definizione di vqe_w2q6_trimero_anello.py."""
    sub = QuantumCircuit(2, name="W")
    sub.cx(0, 1); sub.ry(theta, 0); sub.cx(0, 1)
    qc.append(sub.to_gate(label="W"), [q0, q1])


def pma_2q_trimer(nparam, block):
    """Struttura comune: X sul qubit 0, poi un blocco per ciascuno dei tre
    legami (3 parametri), poi eventuali giri aggiuntivi di Ry indipendenti
    a gruppi di 3 (uno per qubit)."""
    p = ParameterVector("p", nparam)
    qc = QuantumCircuit(3)
    qc.x(0)
    block(qc, p[0], *BOND12); block(qc, p[1], *BOND23); block(qc, p[2], *BOND31)
    i = 3
    while i < nparam:
        qc.ry(p[i], 0); qc.ry(p[i + 1], 1); qc.ry(p[i + 2], 2)
        i += 3
    return qc


def rbs2q_circuit(nparam=6):
    return pma_2q_trimer(nparam, rbs_block)


def w2q_circuit(nparam=6):
    return pma_2q_trimer(nparam, w_block)


def bound_statevector(qc, params):
    from qiskit.quantum_info import Statevector
    return Statevector(qc.assign_parameters(params)).data
