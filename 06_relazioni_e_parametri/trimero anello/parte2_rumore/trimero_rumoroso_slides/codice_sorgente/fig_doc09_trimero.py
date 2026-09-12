"""Figura documento 09 (anello) -- N* vs eps_2q, Trotter e correlatore."""
import os
import numpy as np
import matplotlib.pyplot as plt
from stile import *

os.makedirs("figure", exist_ok=True)

eps2q_vals = [1e-3, 2e-3, 3.8e-3, 6e-3, 1e-2]
Nstar_trotter = [4, 4, 3, 2, 2]
Nstar_corr = [3, 3, 3, 3, 3]
EPS_2Q_REF = 3.8e-3

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.4, 4.4))
a1.plot(eps2q_vals, Nstar_trotter, color=C_ROSSO, marker="o", ms=7, lw=2.0)
a1.axvline(EPS_2Q_REF, color="0.55", ls=":", lw=1.4)
a1.set_xscale("log"); a1.set_xlabel(r"$\varepsilon_{2q}$"); a1.set_ylabel(r"$N^*$")
a1.set_title(r"Fedeltà di Trotter (Scenario A)")
a1.set_ylim(0, 5)

a2.plot(eps2q_vals, Nstar_corr, color=C_BLU, marker="s", ms=7, lw=2.0)
a2.axvline(EPS_2Q_REF, color="0.55", ls=":", lw=1.4)
a2.set_xscale("log"); a2.set_xlabel(r"$\varepsilon_{2q}$"); a2.set_ylabel(r"$N^*$")
a2.set_title("Correlatore (shot finiti)")
a2.set_ylim(0, 5)
salva(fig, "fig_passo5_Nstar_vs_eps_anello")
