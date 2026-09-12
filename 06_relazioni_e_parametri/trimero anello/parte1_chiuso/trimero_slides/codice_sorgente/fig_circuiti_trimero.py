"""Disegni dei circuiti per il trimero ad anello (resa Qiskit)."""
import os
import matplotlib
matplotlib.rcParams["pdf.fonttype"] = 42
matplotlib.rcParams["ps.fonttype"] = 42
import matplotlib.pyplot as plt
from ansatz_trimero_anello import rbs2q_circuit, w2q_circuit, rbs_block, w_block
from qiskit.circuit import QuantumCircuit, ParameterVector
from trotter_trimero_anello import trotter_circuit
from circuito_correlazioni_trimero_anello import build_correlator_circuit

os.makedirs("figure", exist_ok=True)
STILE = "iqp"

def disegna(qc, nome, fold=-1, scale=1.0):
    fig = qc.draw("mpl", style=STILE, fold=fold, scale=scale)
    fig.savefig(f"figure/{nome}.pdf", bbox_inches="tight")
    fig.savefig(f"figure/{nome}.png", bbox_inches="tight", dpi=200)
    plt.close(fig)
    print(f"[ok] figure/{nome}.pdf")

# blocco RBS singolo (espanso)
p = ParameterVector("phi", 1)
qc = QuantumCircuit(2)
rbs_block(qc, p[0], 0, 1)
disegna(qc.decompose(), "circ_rbs_espanso_anello")

# blocco W singolo (espanso)
p2 = ParameterVector("theta", 1)
qc2 = QuantumCircuit(2)
w_block(qc2, p2[0], 0, 1)
disegna(qc2.decompose(), "circ_w_espanso_anello")

# ansatz completi (compattati)
disegna(rbs2q_circuit(6), "circ_rbs2q_anello")
disegna(w2q_circuit(6), "circ_w2q_anello")

# passo di Trotter (1 passo, leggibilita')
disegna(trotter_circuit(1.0, 0.4, 0.05, 1.93, 1.0, 1), "circ_trotter_anello", fold=-1)

# circuito correlatore (Hadamard test, re e im, N=1 per leggibilita',
# con blocco di misura): generato da fig_circuiti_correlatore_reim.py,
# non qui.

# la forma estesa dell'ansatz completo (RBS-2q.6, W-2q.6) e' generata da
# fig_circuiti_espansi.py, non qui: quella versione usa X esplicita
# (non decompose(), che la trasformerebbe in U) e barriere fra i blocchi.
