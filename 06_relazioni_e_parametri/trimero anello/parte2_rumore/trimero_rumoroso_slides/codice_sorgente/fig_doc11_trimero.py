"""Figure documento 11 (anello) -- readout asimmetrico, shot finiti."""
import os
import numpy as np
import matplotlib.pyplot as plt
from stile import *

os.makedirs("figure", exist_ok=True)

d1 = np.load("_doc11_confronto.npz")
N_grid, vals_sym, vals_asym = d1["N_grid"], d1["vals_sym"], d1["vals_asym"]

fig, ax = plt.subplots(figsize=(6.4, 4.6))
ax.plot(N_grid, vals_sym, color=C_BLU, marker="o", ms=5, lw=1.8,
        label=r"simmetrico ($p_{01}{=}p_{10}{=}0.023$)")
ax.plot(N_grid, vals_asym, color=C_ARANC, marker="s", ms=5, lw=1.8, ls="--",
        label="asimmetrico illustrativo")
ax.axvline(3, color="0.55", ls=":", lw=1.2)
ax.set_xlabel(r"$N$")
ax.set_ylabel(r"$|C_{21}^{xx}(t{=}2,N)|$")
ax.set_title("Readout simmetrico vs asimmetrico (shot finiti)")
ax.legend(loc="lower right", fontsize=10)
salva(fig, "fig_correlatore_N_asimmetrico_anello")

d2 = np.load("_doc11_stress.npz")
rapporti, Nstars = d2["rapporti"], d2["Nstars"]
fig, ax = plt.subplots(figsize=(5.8, 4.4))
ax.plot(rapporti, Nstars, color=C_VIOLA, marker="o", ms=7, lw=2.0)
ax.set_xscale("log")
ax.set_xlabel(r"rapporto $p_{10}{:}p_{01}$")
ax.set_ylabel(r"$N^*$")
ax.set_ylim(0, max(Nstars)+2)
ax.set_title(r"$N^*$ vs asimmetria del readout, media fissa $2.3\times10^{-2}$")
salva(fig, "fig_Nstar_vs_rapporto_anello")
