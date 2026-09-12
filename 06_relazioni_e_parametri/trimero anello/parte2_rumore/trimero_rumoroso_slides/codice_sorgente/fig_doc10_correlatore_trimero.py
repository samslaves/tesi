"""Figura documento 10 (anello) -- correlatore ideale vs noise-aware, shot finiti."""
import os
import numpy as np
import matplotlib.pyplot as plt
from stile import *

os.makedirs("figure", exist_ok=True)
d = np.load("_doc10_corr.npz")
N_grid, vals_i, vals_n = d["N_grid"], d["vals_i"], d["vals_n"]

fig, (a1,a2) = plt.subplots(1,2, figsize=(11.0,4.2))
a1.plot(N_grid, vals_i, color=C_BLU, marker="o", ms=4, lw=1.8, label=r"$\theta^*_\mathrm{ideale}$")
a1.plot(N_grid, vals_n, color=C_ARANC, marker="s", ms=4, lw=1.4, ls="--", label="noise-aware")
a1.axvline(3, color="0.55", ls=":", lw=1.2)
a1.set_xlabel(r"$N$"); a1.set_ylabel(r"$|C(N)|$"); a1.legend(loc="lower right")
a1.set_title("Correlatore, shot finiti")

a2.plot(N_grid, vals_n - vals_i, color=C_VERDE, marker="o", ms=4, lw=1.6)
a2.axhline(0, color="0.6", lw=1)
a2.set_xlabel(r"$N$"); a2.set_ylabel(r"noise-aware $-$ ideale")
a2.set_title("Scostamento")
salva(fig, "fig_correlatore_noise_aware_confronto_anello_shots")
