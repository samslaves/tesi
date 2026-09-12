"""Versione corretta delle figure espanse: X resta X (non U), e barriere
esplicite separano i blocchi funzionali per un allineamento leggibile."""
import os
import matplotlib
matplotlib.rcParams["pdf.fonttype"] = 42
matplotlib.rcParams["ps.fonttype"] = 42
import matplotlib.pyplot as plt
from qiskit.circuit import QuantumCircuit, ParameterVector

os.makedirs("figure", exist_ok=True)
STILE = "iqp"
BOND12, BOND23, BOND31 = (2, 1), (1, 0), (0, 2)
BONDS = [BOND12, BOND23, BOND31]

def disegna(qc, nome, fold=-1, scale=0.85):
    fig = qc.draw("mpl", style=STILE, fold=fold, scale=scale)
    fig.savefig(f"figure/{nome}.pdf", bbox_inches="tight")
    fig.savefig(f"figure/{nome}.png", bbox_inches="tight", dpi=200)
    plt.close(fig)
    print(f"[ok] figure/{nome}.pdf")

def rbs_espanso_con_barriere(nparam=6):
    p = ParameterVector("p", nparam)
    qc = QuantumCircuit(3)
    qc.x(0)
    qc.barrier()
    for k, (q0, q1) in enumerate(BONDS):
        phi = p[k]
        qc.h(q0); qc.h(q1)
        qc.cz(q0, q1)
        qc.ry(phi, q0); qc.ry(-phi, q1)
        qc.cz(q0, q1)
        qc.h(q0); qc.h(q1)
        qc.barrier()
    qc.ry(p[3], 0); qc.ry(p[4], 1); qc.ry(p[5], 2)
    return qc

def w_espanso_con_barriere(nparam=6):
    p = ParameterVector("p", nparam)
    qc = QuantumCircuit(3)
    qc.x(0)
    qc.barrier()
    for k, (q0, q1) in enumerate(BONDS):
        theta = p[k]
        qc.cx(q0, q1); qc.ry(theta, q0); qc.cx(q0, q1)
        qc.barrier()
    qc.ry(p[3], 0); qc.ry(p[4], 1); qc.ry(p[5], 2)
    return qc

disegna(rbs_espanso_con_barriere(), "circ_rbs2q_anello_espanso")
disegna(w_espanso_con_barriere(), "circ_w2q_anello_espanso")
