"""Figura: correlatore C_21^xx(t), preparazione esatta vs VQE (W-2q.6)."""
import numpy as np
import matplotlib.pyplot as plt
from stile import *

d = np.load("_vqe_vs_esatto_curva.npz")
ts, C_esatto, C_vqe = d["ts"], d["C_esatto"], d["C_vqe"]

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.4, 4.4))
a1.plot(ts, C_esatto.real, color=C_NERO, lw=2.2, label="Re, preparazione esatta")
a1.plot(ts, C_esatto.imag, color=C_GRIGIO, lw=2.2, label="Im, preparazione esatta")
a1.plot(ts, C_vqe.real, "o", ms=6, mfc="none", mew=1.6, color=C_BLU, label="Re, VQE ($W$-2q.6)")
a1.plot(ts, C_vqe.imag, "s", ms=6, mfc="none", mew=1.6, color=C_ROSSO, label="Im, VQE ($W$-2q.6)")
a1.set_xlabel(r"$t$ (unità di $1/J$)")
a1.set_ylabel(r"$C_{21}^{xx}(t)$")
a1.set_title("Preparazione esatta contro VQE")
a1.legend(loc="upper center", ncol=2, fontsize=8.5)

scarto = np.abs(C_vqe - C_esatto)
a2.semilogy(ts, scarto, "o-", color=C_VERDE, ms=6, lw=1.8)
a2.set_xlabel(r"$t$ (unità di $1/J$)")
a2.set_ylabel(r"$|C_\mathrm{VQE}-C_\mathrm{esatto}|$")
a2.set_title("Scostamento (scala log)")
salva(fig, "fig_vqe_vs_esatto_correlatore")
