"""Due diagrammi schematici (non transpilati) del circuito di Hadamard
test -- uno per la parte reale (rotazione finale H) e uno per la parte
immaginaria (rotazione finale R_x(pi/2)) di C_ij^{alpha,beta}(t). Sostituisce
il diagramma unico precedente: le due varianti differiscono solo
nell'ultima rotazione sull'ancilla, prima della misura -- vale la pena
mostrarle entrambe, non una sola con la differenza lasciata a parole."""
import os
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from stile import *  # pdf.fonttype=42 -- evita i font Type 3

os.makedirs("figure", exist_ok=True)


def costruisci(rotazione_finale):
    anc = QuantumRegister(1, "anc")
    site = QuantumRegister(2, "sito")
    c = ClassicalRegister(1, "c")
    qc = QuantumCircuit(anc, site, c)

    prep = QuantumCircuit(2, name="prep $\\psi_0$")
    qc.append(prep.to_gate(), [site[0], site[1]])
    qc.barrier()
    qc.h(anc[0])

    ctrlW = QuantumCircuit(1, name="$W$")
    qc.append(ctrlW.to_gate().control(1), [anc[0], site[0]])
    qc.barrier()

    Ut = QuantumCircuit(2, name="$U(t)$")
    qc.append(Ut.to_gate(), [site[0], site[1]])
    qc.barrier()

    antiV = QuantumCircuit(1, name="$V$")
    qc.append(antiV.to_gate().control(1, ctrl_state=0), [anc[0], site[1]])
    qc.barrier()

    if rotazione_finale == "re":
        qc.h(anc[0])
    else:
        qc.rx(3.14159265 / 2, anc[0])
    qc.measure(anc[0], c[0])
    return qc


qc_re = costruisci("re")
fig = qc_re.draw("mpl", style={"backgroundcolor": "#FFFFFF"})
fig.savefig("figure/circ_correlatore_schema_re.pdf", bbox_inches="tight")

qc_im = costruisci("im")
fig = qc_im.draw("mpl", style={"backgroundcolor": "#FFFFFF"})
fig.savefig("figure/circ_correlatore_schema_im.pdf", bbox_inches="tight")

print("fatto: due circuiti separati (re, im)")
