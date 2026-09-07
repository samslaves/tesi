"""Figura del documento 8 -- modulo del correlatore dinamico rumoroso
|C_21^xx(t=2,N)| in funzione di N, rumore di riferimento ibm_torino."""
import os
import numpy as np
import matplotlib.pyplot as plt
from stile import *
from correlatori_rumorosi_dimero import correlator_rumoroso, J_DEFAULT, b_DEFAULT, D_DEFAULT
from noise_model_dimero import build_noise_model

os.makedirs("figure", exist_ok=True)

data = np.load("ground_state_test2.npz")
vqe_params = data["vqe_params"]
nm_ref, params_ref = build_noise_model()

N_grid = [1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 15, 20, 25, 30, 40]
mods = []
for N in N_grid:
    c = correlator_rumoroso(2, "x", 1, "x", 2.0, N, J_DEFAULT, b_DEFAULT, D_DEFAULT,
                             vqe_params, noise_model=nm_ref,
                             p_readout=params_ref["p_readout"])
    mods.append(abs(c))
mods = np.array(mods)
Nstar_idx = int(np.argmax(mods))
Nstar, Cstar = N_grid[Nstar_idx], mods[Nstar_idx]

fig, ax = plt.subplots(figsize=(6.4, 4.6))
ax.plot(N_grid, mods, color=C_BLU, marker="o", ms=4.5, lw=2.0)
ax.axvline(Nstar, color="0.55", ls=":", lw=1.4)
ax.annotate(f"$N^*={Nstar}$", xy=(Nstar, Cstar), xytext=(Nstar + 6, Cstar - 0.03),
            fontsize=12, color=C_BLU,
            arrowprops=dict(arrowstyle="->", color=C_BLU, lw=1.1))
ax.set_xlabel(r"$N$ (passi di Trotter)")
ax.set_ylabel(r"$|C_{21}^{xx}(t{=}2,N)|$")
ax.set_title("Correlatore dinamico rumoroso, rumore di riferimento")
salva(fig, "fig_passo4_correlatore_vs_N")

print("N* =", Nstar, "|C(N*)| =", Cstar)
