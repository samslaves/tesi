"""Famiglie di ansatz per il trimero a catena aperta (2 bond).

Mirror diretto di confronto_ansatz_entangler_trimero_anello.ipynb, adattato
alla topologia a catena: DUE bond fisici (1,2) e (2,3), nessun (3,1).

Conseguenze strutturali del passaggio 3 bond -> 2 bond (non cosmetiche):
  - pma_2q_*_exact: 2 blocchi nel primo giro invece di 3 -> nparam = 2 + 3k
  - pma_2q_*_cyclic: 5K parametri per ciclo invece di 6K (2 blocchi + 3 Ry)
  - pma_1q_*: il ciclo sui bond ha periodo 2, non 3

Convenzione sito<->qubit: Famiglia 1 (site_i -> qubit(3-i)), coerente con
trimer_chain_exact.py e con i moduli VQE gia' prodotti per la catena.
"""

import numpy as np
from qiskit.circuit import QuantumCircuit, ParameterVector

BOND12, BOND23 = (2, 1), (1, 0)
BONDS = [BOND12, BOND23]          # nessun BOND31: non esiste nella catena


# ----------------------------------------------------------------------
# Blocchi di base
# ----------------------------------------------------------------------

def rbs_block(qc, phi, q0, q1):
    """Rotazione di Givens reale nel settore {|01>,|10>}. 2 CZ + 4 H."""
    sub = QuantumCircuit(2, name="RBS")
    sub.h(0); sub.h(1); sub.cz(0, 1)
    sub.ry(phi, 0); sub.ry(-phi, 1)
    sub.cz(0, 1); sub.h(0); sub.h(1)
    qc.append(sub.to_gate(label="RBS"), [q0, q1])


def w_block(qc, theta, q0, q1):
    """Blocco della famiglia iSWAP (fase relativa immaginaria). 2 CX."""
    sub = QuantumCircuit(2, name="W")
    sub.cx(0, 1); sub.ry(theta, 0); sub.cx(0, 1)
    qc.append(sub.to_gate(label="W"), [q0, q1])


# ----------------------------------------------------------------------
# Ansatz generici (Ry - entangler - Ry, singolo layer)
# ----------------------------------------------------------------------

def ansatz_A():
    """Ry - CNOT (sui 2 legami fisici) - Ry. 6 parametri."""
    theta = ParameterVector("t", 6)
    qc = QuantumCircuit(3)
    for q in range(3):
        qc.ry(theta[q], q)
    qc.cx(*BOND12); qc.cx(*BOND23)
    for q in range(3):
        qc.ry(theta[3 + q], q)
    return qc


def ansatz_D(block=rbs_block):
    """Ry - blocco(theta) sui 2 legami - Ry. 8 parametri (9 nell'anello: 3 bond)."""
    theta = ParameterVector("t", 8)
    qc = QuantumCircuit(3)
    for q in range(3):
        qc.ry(theta[q], q)
    block(qc, theta[6], *BOND12)
    block(qc, theta[7], *BOND23)
    for q in range(3):
        qc.ry(theta[3 + q], q)
    return qc


# ----------------------------------------------------------------------
# Famiglia 1q: Ry su UN solo qubit, alternato a blocchi sui bond
# ----------------------------------------------------------------------

def pma_1q_trimer(nparam, block=rbs_block):
    p = ParameterVector("p", nparam)
    qc = QuantumCircuit(3)
    qc.x(0)
    i, bond_idx = 0, 0
    block(qc, p[i], *BONDS[bond_idx % len(BONDS)]); i += 1; bond_idx += 1
    while i < nparam:
        qc.ry(p[i], 0); i += 1
        if i < nparam:
            block(qc, p[i], *BONDS[bond_idx % len(BONDS)]); i += 1; bond_idx += 1
    return qc


# ----------------------------------------------------------------------
# Famiglia 2q: "esatta" (blocchi solo nel primo giro) e "ciclica"
# ----------------------------------------------------------------------

def pma_2q_trimer_exact(nparam, block=rbs_block):
    """Un solo giro di blocchi (2 par, uno per legame fisico), poi triple di
    Ry indipendenti sui 3 qubit. nparam valido: 2 + 3k."""
    p = ParameterVector("p", nparam)
    qc = QuantumCircuit(3)
    qc.x(0)
    block(qc, p[0], *BOND12)
    block(qc, p[1], *BOND23)
    i = 2
    while i < nparam:
        qc.ry(p[i], 0); qc.ry(p[i + 1], 1); qc.ry(p[i + 2], 2)
        i += 3
    return qc


def pma_2q_trimer_cyclic(K, block=rbs_block):
    """K cicli di [blocchi sui 2 legami, Ry indipendenti sui 3 qubit].
    5K parametri (6K nell'anello, che ha 3 bond)."""
    nparam = 5 * K
    p = ParameterVector("p", nparam)
    qc = QuantumCircuit(3)
    qc.x(0)
    idx = 0
    for _ in range(K):
        block(qc, p[idx], *BOND12); idx += 1
        block(qc, p[idx], *BOND23); idx += 1
        qc.ry(p[idx], 0); idx += 1
        qc.ry(p[idx], 1); idx += 1
        qc.ry(p[idx], 2); idx += 1
    return qc


def build_ansatze():
    """Le 15 varianti dello sweep. Nomenclatura identica all'anello, con i
    conteggi di parametri adattati ai 2 bond (2+3k invece di 3+3k)."""
    return {
        "A: Ry-CNOT-Ry": ansatz_A(),
        "D: Ry-RBS-Ry":  ansatz_D(rbs_block),
        "RBS-1q.3":   pma_1q_trimer(3, rbs_block),
        "RBS-1q.6":   pma_1q_trimer(6, rbs_block),
        "RBS-1q.9":   pma_1q_trimer(9, rbs_block),
        "RBS-2q.2":   pma_2q_trimer_exact(2, rbs_block),
        "RBS-2q.5":   pma_2q_trimer_exact(5, rbs_block),
        "RBS-2q.8":   pma_2q_trimer_exact(8, rbs_block),
        "RBS-2qC.K1": pma_2q_trimer_cyclic(1, rbs_block),
        "RBS-2qC.K2": pma_2q_trimer_cyclic(2, rbs_block),
        "W-1q.6":     pma_1q_trimer(6, w_block),
        "W-1q.9":     pma_1q_trimer(9, w_block),
        "W-2q.5":     pma_2q_trimer_exact(5, w_block),
        "W-2q.8":     pma_2q_trimer_exact(8, w_block),
        "W-2qC.K1":   pma_2q_trimer_cyclic(1, w_block),
    }


if __name__ == "__main__":
    for name, a in build_ansatze().items():
        print(f"  {name:14s} {a.num_parameters:2d} parametri")
