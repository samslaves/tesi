"""Disegni dei circuiti usati nei documenti (resa Qiskit, non schemi a mano)."""
import os
import matplotlib
matplotlib.rcParams["pdf.fonttype"] = 42   # font vettoriali veri, non Type 3 bitmap
matplotlib.rcParams["ps.fonttype"] = 42
import matplotlib.pyplot as plt
from qiskit.circuit import QuantumCircuit, ParameterVector
from qiskit.circuit.library import n_local
from ansatz_dimero import rbs_block, ansatz_PMA_W, ansatz_PMA_2q
from trotter_dimero import trotter_circuit
from circuito_correlazioni_dimero import build_correlator_circuit

os.makedirs("figure", exist_ok=True)
STILE = "iqp"

def disegna(qc, nome, fold=-1, scale=1.0):
    fig = qc.draw("mpl", style=STILE, fold=fold, scale=scale)
    fig.savefig(f"figure/{nome}.pdf", bbox_inches="tight")
    fig.savefig(f"figure/{nome}.png", bbox_inches="tight", dpi=200)
    plt.close(fig)
    print(f"[ok] figure/{nome}.pdf")

# --- ansatz hardware-efficient
ha = n_local(2, rotation_blocks="ry", entanglement_blocks="cz",
             entanglement="full", reps=2)
disegna(ha.decompose(), "circ_ha")

# --- ansatz PMA base (settore scelto a mano + un gate a due qubit)
disegna(ansatz_PMA_W(0.35), "circ_pma_base")

# --- ansatz PMA esteso (3 parametri)
disegna(ansatz_PMA_2q(3), "circ_pma_esteso")

# --- passo di Trotter (2 passi, per mostrare la ripetizione)
disegna(trotter_circuit(-0.18, 1.0, 1.0, 1.0, 1), "circ_trotter", fold=-1)

# --- circuito dei correlatori (Hadamard test), N=2 per leggibilità
qc = build_correlator_circuit(2, "x", 1, "x", 1.0, 2, 1.0, 0.35, 0.80, "re")
disegna(qc, "circ_correlatore")
