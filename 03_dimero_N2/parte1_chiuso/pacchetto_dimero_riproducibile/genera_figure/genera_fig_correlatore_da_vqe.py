"""Genera fig_correlatore_da_vqe.pdf: il correlatore C_11^yz(t) in modulo,
due ansatz (PMA base, PMA esteso), tre curve ciascuno (esatto dalla vera
GS, esatto-da-VQE, circuito vero con N=200 passi di Trotter).
Richiede dati/correlatore_da_vqe.npz (da 03_correlatore_da_vqe.py).
"""
import sys
sys.path.insert(0, "codice")
import numpy as np
from stile import plt, C_NERO, C_BLU, C_ROSSO, salva

data = np.load("dati/correlatore_da_vqe.npz")
t_denso, t_rado = data["t_denso"], data["t_rado"]

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.5, 4.6), sharey=True)

for ax, nome, titolo in ((a1, "base", "PMA base (1 par.)"),
                          (a2, "esteso", "PMA esteso (3 par.)")):
    ax.plot(t_denso, data[f"c_esatto_{nome}"], color=C_NERO, lw=2.0, label="esatto (vera GS)")
    ax.plot(t_denso, data[f"c_da_vqe_{nome}"], color=C_BLU, lw=1.6, ls="--", label="esatto da $\\psi_{VQE}$")
    ax.plot(t_rado, data[f"c_circuito_{nome}"], "o", color=C_ROSSO, ms=4, mfc="none", label="circuito vero ($N{=}200$)")
    ax.set_xlabel("$t$")
    ax.set_title(titolo)
    ax.legend(fontsize=8.5)
a1.set_ylabel(r"$|C_{11}^{yz}(t)|$")

fig.suptitle("Correlatore con preparazione VQE reale, $b/J=-0.18$, $D/J=1$")
salva(fig, "fig_correlatore_da_vqe")
print(f"F(PMA base)={float(data['F_base']):.6f}  F(PMA esteso)={float(data['F_esteso']):.10f}")
