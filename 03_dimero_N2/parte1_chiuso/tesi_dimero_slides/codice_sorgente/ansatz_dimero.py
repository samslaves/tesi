"""Ansatz per il dimero: definizione unica, importata da tutti gli script."""
import numpy as np
from qiskit.circuit import QuantumCircuit, ParameterVector
from qiskit.circuit.library import n_local

J = 1.0


def rbs_block(qc, phi, q0=0, q1=1):
    """Blocco M-conservante (rotazione di Givens reale nel settore {|01>,|10>})."""
    sub = QuantumCircuit(2, name="RBS")
    sub.h(0); sub.h(1); sub.cz(0, 1)
    sub.ry(phi, 0); sub.ry(-phi, 1)
    sub.cz(0, 1); sub.h(0); sub.h(1)
    qc.append(sub.to_gate(label="RBS"), [q0, q1])

def ansatz_HA(reps=2):
    return n_local(2, rotation_blocks="ry", entanglement_blocks="cz",
                   entanglement="full", reps=reps)

def ansatz_PMA_Mcons(K=1):
    """PMA nel settore M conservato: X + K blocchi RBS."""
    p = ParameterVector("p", K)
    qc = QuantumCircuit(2); qc.x(1)
    for k in range(K):
        rbs_block(qc, p[k])
    return qc

def ansatz_PMA_2q(nparam=3):
    """PMA esteso: RBS + coppie di Ry indipendenti (rompono la conservazione di M)."""
    p = ParameterVector("p", nparam)
    qc = QuantumCircuit(2); qc.x(1)
    rbs_block(qc, p[0]); i = 1
    while i < nparam:
        qc.ry(p[i], 0); qc.ry(p[i + 1], 1); i += 2
    return qc

def ansatz_PMA_W(b):
    """PMA alla Crippa: stato iniziale scelto nel settore giusto + gate W (1 par.)."""
    th = ParameterVector("th", 1)
    qc = QuantumCircuit(2)
    if b / J < 2.0:
        qc.x(0); qc.h(0); qc.cx(0, 1); qc.x(0)      # singoletto
    else:
        qc.x(0); qc.x(1)                             # |11>
    qc.cx(0, 1); qc.ry(th[0], 0); qc.cx(0, 1)        # W_01(theta)
    return qc

def ansatz_PMA_1q(nparam=1):
    p = ParameterVector("p", nparam)
    qc = QuantumCircuit(2); qc.x(1); i = 0
    rbs_block(qc, p[i]); i += 1
    while i < nparam:
        qc.ry(p[i], 1); i += 1
        if i < nparam:
            rbs_block(qc, p[i]); i += 1
    return qc

