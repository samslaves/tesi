"""Genera fig_scan36.pdf: griglia 6x6 delle 36 combinazioni
C_ij^{alpha,beta}, valore a t=0 (sinistra) e max_t su [0,8] (destra).
Richiede dati/scan36_correlatori.npz (da 02_scan36_correlatori.py).
"""
import sys
sys.path.insert(0, "codice")
import numpy as np
from stile import plt, salva

data = np.load("dati/scan36_correlatori.npz", allow_pickle=True)
righe = data["righe"]

SITI = (1, 2); COMP = ("x", "y", "z")
labels = [f"{i}{a}" for i in SITI for a in COMP]  # 1x,1y,1z,2x,2y,2z

grid_t0 = np.zeros((6, 6))
grid_max = np.zeros((6, 6))
idx = {lab: k for k, lab in enumerate(labels)}
for i, al, j, be, v0, vmax in righe:
    r, c = idx[f"{i}{al}"], idx[f"{j}{be}"]
    grid_t0[r, c] = v0
    grid_max[r, c] = vmax

fig, axs = plt.subplots(1, 2, figsize=(11.5, 5.2))
for ax, grid, title in ((axs[0], grid_t0, "$t=0$"),
                         (axs[1], grid_max, r"$\max_t\,|C(t)|$, $t\in[0,8]$")):
    im = ax.imshow(np.abs(grid), cmap="viridis", vmin=0, vmax=np.abs(grid_max).max())
    ax.set_xticks(range(6)); ax.set_xticklabels(labels, fontsize=9)
    ax.set_yticks(range(6)); ax.set_yticklabels(labels, fontsize=9)
    ax.set_title(title)
    fig.colorbar(im, ax=ax, shrink=0.8)

fig.suptitle("Le 36 combinazioni, punto di lavoro \"test 2\"")
salva(fig, "fig_scan36")
