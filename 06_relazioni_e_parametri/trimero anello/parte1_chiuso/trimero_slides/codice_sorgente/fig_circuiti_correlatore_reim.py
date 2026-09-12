"""Circuiti del correlatore, parte reale e immaginaria, N=1 per
leggibilita', comprensivi del blocco di misura."""
import os
import matplotlib
matplotlib.rcParams["pdf.fonttype"] = 42
matplotlib.rcParams["ps.fonttype"] = 42
import matplotlib.pyplot as plt
from circuito_correlazioni_trimero_anello import build_correlator_circuit

os.makedirs("figure", exist_ok=True)

for part in ("re", "im"):
    qc = build_correlator_circuit(2, "x", 1, "x", 1.0, 1, 1.0, 0.4, 2.4, 0.15,
                                   part, measure=True)
    fig = qc.draw("mpl", style="iqp", fold=-1, scale=1.0)
    fig.savefig(f"figure/circ_correlatore_anello_{part}.pdf", bbox_inches="tight")
    fig.savefig(f"figure/circ_correlatore_anello_{part}.png", bbox_inches="tight", dpi=200)
    plt.close(fig)
    print(f"[ok] figure/circ_correlatore_anello_{part}.pdf")
