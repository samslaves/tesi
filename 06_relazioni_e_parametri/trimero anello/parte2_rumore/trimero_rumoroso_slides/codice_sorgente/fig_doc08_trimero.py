"""Figura documento 08 (anello) -- |C(N)| a shot finiti, rumore di riferimento."""
import os
import numpy as np
import matplotlib.pyplot as plt
from stile import *

os.makedirs("figure", exist_ok=True)
d = np.load("_doc08_scan.npz")
N_grid, vals, Nstar, Cstar = d["N_grid"], d["vals"], int(d["Nstar"]), float(d["Cstar"])

fig, ax = plt.subplots(figsize=(6.4, 4.6))
ax.plot(N_grid, vals, color=C_BLU, marker="o", ms=5, lw=2.0)
ax.axvline(Nstar, color="0.55", ls=":", lw=1.4)
ax.annotate(f"$N^*={Nstar}$", xy=(Nstar, Cstar), xytext=(Nstar+4, Cstar-0.05),
            fontsize=12, color=C_BLU, arrowprops=dict(arrowstyle="->", color=C_BLU))
ax.set_xlabel(r"$N$ (passi di Trotter)")
ax.set_ylabel(r"$|C_{21}^{xx}(t{=}2,N)|$")
ax.set_title("Correlatore dinamico rumoroso, readout a shot finiti")
salva(fig, "fig_passo4_correlatore_vs_N_anello")
print(f"N*={Nstar}  |C(N*)|={Cstar:.4f}")
