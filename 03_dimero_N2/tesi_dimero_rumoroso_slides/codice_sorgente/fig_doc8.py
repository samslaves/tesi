"""Figura del documento 8 -- modulo del correlatore dinamico rumoroso
|C_11^yz(t=2,N)| in funzione di N, rumore di riferimento ibm_torino.
Readout genuinamente campionato a shot finiti (misura vera + ReadoutError
di Aer), non una formula analitica -- vedi correlatori_shots_dimero.py."""
import os
import numpy as np
import matplotlib.pyplot as plt
from stile import *
from correlatori_shots_dimero import correlator_shots, SHOTS_DEFAULT

os.makedirs("figure", exist_ok=True)

data = np.load("ground_state_test2.npz")
vqe_params = data["vqe_params"]
I, ALPHA, J_IDX, BETA = 1, "y", 1, "z"

N_grid = [1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 15, 20, 25, 30, 40]
mods = []
for N in N_grid:
    c = correlator_shots(I, ALPHA, J_IDX, BETA, 2.0, N, vqe_params,
                          p01=0.023, p10=0.023, shots=SHOTS_DEFAULT, seed=0)
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
ax.set_ylabel(r"$|C_{11}^{yz}(t{=}2,N)|$")
ax.set_title("Correlatore dinamico rumoroso, readout a shot finiti")
salva(fig, "fig_passo4_correlatore_vs_N")

print("N* =", Nstar, "|C(N*)| =", Cstar)

# =====================================================================
# Seconda figura: confronto rumore nullo vs shot finiti sull'intera
# griglia -- stesso tipo di confronto gia' fatto nel Documento 7
# (fig_passo3_zoom_minimo), qui sul correlatore invece che sulla fedelta'.
# =====================================================================
from correlatori_rumorosi_dimero import correlator_rumoroso, J_DEFAULT, b_DEFAULT, D_DEFAULT

mods_nullo = []
for N in N_grid:
    c0 = correlator_rumoroso(I, ALPHA, J_IDX, BETA, 2.0, N, J_DEFAULT, b_DEFAULT, D_DEFAULT,
                              vqe_params, noise_model=None, p_readout=0.0)
    mods_nullo.append(abs(c0))
mods_nullo = np.array(mods_nullo)
imin_nullo = int(np.argmin(mods_nullo))

fig, ax = plt.subplots(figsize=(6.8, 4.8))
ax.plot(N_grid, mods_nullo, color=C_NERO, marker="s", ms=5, lw=1.8,
        label="rumore nullo")
ax.plot(N_grid, mods, color=C_BLU, marker="o", ms=5, lw=1.8,
        label="shot finiti (ibm_torino)")
ax.annotate(f"minimo locale, $N={N_grid[imin_nullo]}$",
            xy=(N_grid[imin_nullo], mods_nullo[imin_nullo]),
            xytext=(N_grid[imin_nullo] + 8, mods_nullo[imin_nullo] + 0.12),
            fontsize=10.5, color="0.25",
            arrowprops=dict(arrowstyle="->", color="0.45", lw=1.1))
ax.set_xlabel(r"$N$ (passi di Trotter)")
ax.set_ylabel(r"$|C_{11}^{yz}(t{=}2,N)|$")
ax.set_title("Rumore nullo contro shot finiti, intera griglia")
ax.legend(loc="upper right")
salva(fig, "fig_passo4_confronto_rumore")
