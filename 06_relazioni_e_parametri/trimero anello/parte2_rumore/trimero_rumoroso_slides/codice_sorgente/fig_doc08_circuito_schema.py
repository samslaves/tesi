"""Schema circuitale (non transpilato) del Hadamard test per l'anello,
4 qubit: 3 di registro + ancilla."""
import os
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from stile import *

os.makedirs("figure", exist_ok=True)

def costruisci(rotazione_finale):
    anc = QuantumRegister(1, "anc")
    reg = QuantumRegister(3, "reg")
    c = ClassicalRegister(1, "c")
    qc = QuantumCircuit(reg, anc, c)

    prep = QuantumCircuit(3, name="prep $\\psi_0$ ($W$-2q.6)")
    qc.append(prep.to_gate(), [reg[0], reg[1], reg[2]])
    qc.barrier()
    qc.h(anc[0])

    ctrlW = QuantumCircuit(1, name="$W$")
    qc.append(ctrlW.to_gate().control(1), [anc[0], reg[1]])
    qc.barrier()

    Ut = QuantumCircuit(3, name="$U(t)$")
    qc.append(Ut.to_gate(), [reg[0], reg[1], reg[2]])
    qc.barrier()

    antiV = QuantumCircuit(1, name="$V$")
    qc.append(antiV.to_gate().control(1, ctrl_state=0), [anc[0], reg[0]])
    qc.barrier()

    if rotazione_finale == "re":
        qc.h(anc[0])
    else:
        qc.rx(3.14159265/2, anc[0])
    qc.measure(anc[0], c[0])
    return qc

qc_re = costruisci("re")
fig = qc_re.draw("mpl", style={"backgroundcolor": "#FFFFFF"})
fig.savefig("figure/circ_correlatore_schema_re_anello.pdf", bbox_inches="tight")

qc_im = costruisci("im")
fig = qc_im.draw("mpl", style={"backgroundcolor": "#FFFFFF"})
fig.savefig("figure/circ_correlatore_schema_im_anello.pdf", bbox_inches="tight")
print("fatto")
