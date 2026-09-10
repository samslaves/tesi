"""Figure del documento 7 -- fedelta' F(N) della quantum simulation
(Trotter) sotto rumore, e zoom sulla regione non perturbativa a N piccolo."""
import os
import numpy as np
import matplotlib.pyplot as plt
from stile import *
from trotter_rumoroso_dimero import fedelta_trotter_rumoroso
from noise_model_dimero import build_noise_model

os.makedirs("figure", exist_ok=True)

data = np.load("ground_state_test2.npz")
vqe_params = data["vqe_params"]
psi0_exact = data["psi0_exact"]
t = 2.0
nm_ref, _ = build_noise_model()

N_grid = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 20, 25, 30, 40, 50, 60, 80,
          100, 120, 160]
F_nulla, F_rumorosa = [], []
for N in N_grid:
    F0, _ = fedelta_trotter_rumoroso(vqe_params, psi0_exact, t, N, noise_model=None)
    Fn, _ = fedelta_trotter_rumoroso(vqe_params, psi0_exact, t, N, noise_model=nm_ref)
    F_nulla.append(F0)
    F_rumorosa.append(Fn)
F_nulla, F_rumorosa = np.array(F_nulla), np.array(F_rumorosa)
Nstar_idx = int(np.argmax(F_rumorosa))
Nstar, Fstar = N_grid[Nstar_idx], F_rumorosa[Nstar_idx]

# ------------------------------------------------------------- fig: F(N)
fig, ax = plt.subplots(figsize=(6.4, 4.6))
ax.plot(N_grid, F_rumorosa, color=C_ROSSO, marker="o", ms=4.5, lw=2.0)
ax.axvline(Nstar, color="0.55", ls=":", lw=1.4)
ax.annotate(f"$N^*={Nstar}$", xy=(Nstar, Fstar), xytext=(Nstar + 12, Fstar - 0.08),
            fontsize=12, color=C_ROSSO,
            arrowprops=dict(arrowstyle="->", color=C_ROSSO, lw=1.1))
ax.set_xlabel(r"$N$ (passi di Trotter)")
ax.set_ylabel(r"$F(N)$")
ax.set_title("Fedelt\u00e0 rispetto allo stato bersaglio fisico, rumore di riferimento")
salva(fig, "fig_passo3_F_vs_N")

# --------------------------------------------------------- fig: zoom minimo
N_zoom = [1, 2, 3, 4, 5, 6, 7, 8]
idx_zoom = [N_grid.index(n) for n in N_zoom]
fig, ax = plt.subplots(figsize=(6.0, 4.4))
ax.plot(N_zoom, F_nulla[idx_zoom], color=C_NERO, marker="s", ms=6, lw=1.8,
        label="rumore nullo")
ax.plot(N_zoom, F_rumorosa[idx_zoom], color=C_ROSSO, marker="o", ms=6, lw=1.8,
        label="rumore (ibm\\_torino)")
imin = int(np.argmin(F_rumorosa[idx_zoom]))
ax.annotate(f"minimo a $N={N_zoom[imin]}$", xy=(N_zoom[imin], F_rumorosa[idx_zoom][imin]),
            xytext=(4.3, 0.55), fontsize=11.5, color="0.25",
            arrowprops=dict(arrowstyle="->", color="0.45", lw=1.1))
ax.set_xlabel(r"$N$ (passi di Trotter)")
ax.set_ylabel(r"$F(N)$")
ax.set_title("Zoom sulla regione non perturbativa")
ax.legend(loc="upper right")
salva(fig, "fig_passo3_zoom_minimo")

print("N* =", Nstar, "F(N*) =", Fstar)
print("minimo zoom: N=", N_zoom[imin], "F0=", F_nulla[idx_zoom][imin],
      "Fn=", F_rumorosa[idx_zoom][imin])
