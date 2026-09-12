"""Circuiti compilati in base {rz,sx,x,cx}, entrambi gli ansatz, a Scenario A."""
import os
import matplotlib
matplotlib.rcParams["pdf.fonttype"] = 42
matplotlib.rcParams["ps.fonttype"] = 42
import matplotlib.pyplot as plt
import numpy as np
from qiskit import transpile
from ansatz_trimero_anello import rbs2q_circuit, w2q_circuit

os.makedirs("figure", exist_ok=True)
BASIS = ["rz", "sx", "x", "cx"]

def disegna(qc, nome, fold=-1, scale=0.8):
    fig = qc.draw("mpl", style="iqp", fold=fold, scale=scale)
    fig.savefig(f"figure/{nome}.pdf", bbox_inches="tight")
    fig.savefig(f"figure/{nome}.png", bbox_inches="tight", dpi=200)
    plt.close(fig)
    print(f"[ok] figure/{nome}.pdf")

x_rbs = np.load("rbs2q6_params_optimal.npz")["params"]
x_w = np.load("w2q6_params_optimal.npz")["params"]

tqc_rbs = transpile(rbs2q_circuit(6).assign_parameters(x_rbs),
                     basis_gates=BASIS, optimization_level=3, seed_transpiler=7)
tqc_w = transpile(w2q_circuit(6).assign_parameters(x_w),
                   basis_gates=BASIS, optimization_level=3, seed_transpiler=7)

print("RBS-2q.6 compilato:", dict(tqc_rbs.count_ops()))
print("W-2q.6 compilato:  ", dict(tqc_w.count_ops()))

disegna(tqc_rbs, "circ_rbs2q_anello_compilato", scale=0.75)
disegna(tqc_w, "circ_w2q_anello_compilato", scale=0.75)
