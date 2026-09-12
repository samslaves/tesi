"""Documento 4 (trimero anello) — figure: validazione, heatmap 81, ricco/piatto, spettro."""
import os
import numpy as np
import matplotlib.pyplot as plt
from stile import *

os.makedirs("figure", exist_ok=True)

# ---- validazione
dv = np.load("_val_doc4.npz")
ts_fine, ts_circ = dv["ts_fine"], dv["ts_circ"]
C_ref, C_cir = dv["C_ref"], dv["C_cir"]

fig, ax = plt.subplots(figsize=(8.0, 4.6))
ax.plot(ts_fine, C_ref.real, color=C_NERO, lw=2.4, label="Re, riferimento esatto")
ax.plot(ts_fine, C_ref.imag, color=C_GRIGIO, lw=2.4, label="Im, riferimento esatto")
ax.plot(ts_circ, C_cir.real, "o", ms=8, mfc="none", mew=2, color=C_BLU, label="Re, circuito")
ax.plot(ts_circ, C_cir.imag, "s", ms=8, mfc="none", mew=2, color=C_ROSSO, label="Im, circuito")
ax.set_xlabel(r"$t$  (unità di $1/J$)")
ax.set_ylabel(r"$C_{21}^{xx}(t)$")
ax.set_title("Il circuito con l'ancilla riproduce il calcolo classico (Scenario A)")
ax.legend(loc="upper center", ncol=2)
salva(fig, "fig07_correlatore_validazione_anello")

# ---- heatmap 81
ds = np.load("_scan81_doc4.npz", allow_pickle=True)
ampiezza, istante0 = ds["ampiezza"], ds["istante0"]
righe, colonne = list(ds["righe"]), list(ds["colonne"])

fig, (ax0, ax1) = plt.subplots(1, 2, figsize=(14.5, 6.6))
for ax, M, titolo in ((ax0, istante0, r"$|C_{ij}^{\alpha\beta}(0)|$  (istante iniziale)"),
                      (ax1, ampiezza, r"$\max_t\,|C_{ij}^{\alpha\beta}(t)|$  su $t\in[0,8]$")):
    im = ax.imshow(M, cmap="viridis", vmin=0, vmax=1.0)
    ax.set_xticks(range(9), colonne, fontsize=9, rotation=90)
    ax.set_yticks(range(9), righe, fontsize=9)
    for r in range(9):
        for c in range(9):
            val = M[r, c]
            ax.text(c, r, "0" if val < 1e-9 else f"{val:.2f}",
                    ha="center", va="center", fontsize=8,
                    color="white" if val < 0.6 else "black")
    ax.set_title(titolo, fontsize=12.5)
    ax.grid(False)
cb = fig.colorbar(im, ax=(ax0, ax1), shrink=0.75)
cb.set_label("modulo del correlatore")
salva(fig, "fig08_scan81_anello")

print(f"[scan] ampiezza: min={ampiezza.min():.3f} max={ampiezza.max():.3f}")
print(f"[scan] zeri strutturali (max_t=0): {(ampiezza<1e-9).sum()}")
print(f"[scan] zeri a t=0 (tutti):        {(istante0<1e-9).sum()}")
