"""Genera tutti i diagrammi di circuito della Parte 1 (dimero) --
categoria interamente assente dalla prima versione del pacchetto (per
scelta esplicita dell'autore originale, vedi docstring di
ansatz_dimero.py: "script di illustrazione... non compresi in questo
pacchetto riproducibile perche' producono disegni di circuiti, non
risultati numerici"). Qui aggiunti per chiudere il divario rispetto ai
documenti narrativi (dimero_02_vqe.tex, dimero_03_dinamica.tex,
dimero_04_correlatori.tex), che li citano tutti.

Cinque di nove (circ_ha, circ_pma_base, circ_pma_esteso, circ_trotter,
circ_correlatore) riusano ESATTAMENTE le chiamate del vecchio script
fig_circuiti.py del progetto (non incluso in questo pacchetto, letto
come riferimento) -- stessi parametri, stessa scelta di punto di
lavoro. I restanti quattro (circ_pma_base_ramo2, circ_rbs_espanso,
circ_w_espanso, circ_cnotry) non avevano uno script sorgente
disponibile: costruiti qui direttamente dalle definizioni dei blocchi
(ansatz_dimero.py) e dalle didascalie dei documenti.

Eseguire dalla RADICE del pacchetto.
"""
import sys
sys.path.insert(0, "codice")
import os
import matplotlib
matplotlib.rcParams["pdf.fonttype"] = 42
matplotlib.rcParams["ps.fonttype"] = 42
import matplotlib.pyplot as plt
from qiskit.circuit import QuantumCircuit, Parameter
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


# --- i cinque con script sorgente originale disponibile (fig_circuiti.py) ---
ha = n_local(2, rotation_blocks="ry", entanglement_blocks="cz",
             entanglement="full", reps=2)
disegna(ha.decompose(), "circ_ha")

disegna(ansatz_PMA_W(0.35), "circ_pma_base")          # ramo b/J<2: singoletto
disegna(ansatz_PMA_2q(3), "circ_pma_esteso")
disegna(trotter_circuit(-0.18, 1.0, 1.0, 1.0, 1), "circ_trotter", fold=-1)
qc_corr = build_correlator_circuit(2, "x", 1, "x", 1.0, 2, 1.0, 0.35, 0.80, "re")
disegna(qc_corr, "circ_correlatore")

# --- i quattro senza script sorgente disponibile, costruiti qui ---

# ramo b/J>=2: |11>, stesso ansatz_PMA_W ma nel secondo settore
disegna(ansatz_PMA_W(2.5), "circ_pma_base_ramo2")

# RBS espanso: il blocco da solo, parametro simbolico
phi = Parameter(r"$\varphi$")
qc_rbs = QuantumCircuit(2)
rbs_block(qc_rbs, phi)
disegna(qc_rbs, "circ_rbs_espanso")

# W_ij(theta) = Rxx(theta/2) Ryy(theta/2) Rzz(theta/2) -- il vero gate di
# Crippa et al., diverso dal blocco CNOT-Ry-CNOT (circ_cnotry sotto)
theta = Parameter(r"$\theta$")
qc_w = QuantumCircuit(2)
qc_w.rxx(theta / 2, 0, 1)
qc_w.ryy(theta / 2, 0, 1)
qc_w.rzz(theta / 2, 0, 1)
disegna(qc_w, "circ_w_espanso")

# il blocco "ansatz base": due CNOT attorno a un'unica Ry
qc_cnotry = QuantumCircuit(2)
qc_cnotry.cx(0, 1)
qc_cnotry.ry(theta, 0)
qc_cnotry.cx(0, 1)
disegna(qc_cnotry, "circ_cnotry")

print("\nNota: circ_pma_base_ramo2, circ_rbs_espanso, circ_w_espanso, "
      "circ_cnotry non avevano uno script sorgente originale disponibile "
      "in questo progetto -- costruiti qui dalle definizioni dei blocchi "
      "e dalle didascalie dei documenti, non da un file preesistente.")
