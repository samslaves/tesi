"""Figure aggiuntive del documento 8, sotto-sezione 'Perche' N* varia
cosi' tanto' -- guadagno non perturbativo (N=1 -> picco entro N<=7) per
tutte le 36 combinazioni, a rumore nullo, e quattro curve rappresentative.
Script separato da fig_doc8_scan36.py: stesso scan di base, analisi
diversa (il guadagno, non la distribuzione di N*)."""
import json
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from stile import *
from correlatori_rumorosi_dimero import correlator_rumoroso, J_DEFAULT, b_DEFAULT, D_DEFAULT

os.makedirs("figure", exist_ok=True)

data = np.load("ground_state_test2.npz")
vqe_params = data["vqe_params"]

with open("scan36_rumore_shots.json") as f:
    scan36 = json.load(f)
combos = [(r["i"], r["alpha"], r["j"], r["beta"], r["Nstar"]) for r in scan36["righe"]]

N_grid = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 20, 25, 30, 40]

results = []
for i, alpha, j, beta, nstar_noisy in combos:
    vals = []
    for N in N_grid:
        c = correlator_rumoroso(i, alpha, j, beta, 2.0, N, J_DEFAULT, b_DEFAULT, D_DEFAULT,
                                 vqe_params, noise_model=None, p_readout=0.0)
        vals.append(abs(c))
    vals = np.array(vals)
    v1 = vals[0]
    vpeak = vals[:7].max()
    gain = (vpeak - v1) / v1 * 100
    results.append({"i": i, "alpha": alpha, "j": j, "beta": beta,
                     "nstar_noisy": nstar_noisy, "gain_pct": float(gain),
                     "vals": vals.tolist()})

with open("gain_early_peak_36.json", "w") as f:
    json.dump({"N_grid": N_grid, "results": results}, f, indent=1)

# ---------------------------------------------------------- fig A: barre
results_sorted = sorted(results, key=lambda r: r["gain_pct"])
gains = [r["gain_pct"] for r in results_sorted]
nstars = [r["nstar_noisy"] for r in results_sorted]

colors_map = {1: C_NERO, 2: C_BLU, 3: C_VERDE, 4: C_ARANC, 5: C_ROSSO}
colors = [colors_map[n] for n in nstars]

fig, ax = plt.subplots(figsize=(10.5, 5.2))
x = np.arange(36)
ax.bar(x, np.array(gains) + 0.5, color=colors, width=0.75)
ax.set_yscale("log")
ax.set_ylabel(r"guadagno $N{=}1\to$ picco precoce ($N\leq7$), % ($t=2$)")
ax.set_xlabel("combinazione (ordinate per guadagno crescente)")
ax.set_xticks([])
ax.set_title(r"Guadagno non perturbativo vs $N^*$ rumoroso, tutte le 36 combinazioni")
handles = [Patch(color=colors_map[n], label=f"$N^*={n}$") for n in sorted(set(nstars))]
ax.legend(handles=handles, loc="upper left", title=r"$N^*$ (rumoroso)")
salva(fig, "fig_scan36_guadagno_early")

# --------------------------------------------- fig B: curve rappresentative
by_key = {(r["i"], r["alpha"], r["j"], r["beta"]): r for r in results}
fig, ax = plt.subplots(figsize=(7.2, 5.0))
picks = [
    ((1, "y", 1, "x"), C_NERO, "-", r"$C_{11}^{yx}$ ($N^*{=}1$, guadagno $0\%$)"),
    ((1, "z", 1, "z"), "0.5", "-", r"$C_{11}^{zz}$ ($N^*{=}1$, guadagno $1\%$)"),
    ((1, "y", 1, "z"), C_BLU, "--", r"$C_{11}^{yz}$ ($N^*{=}2$, guadagno $36\%$)"),
    ((1, "x", 1, "z"), C_ROSSO, "--", r"$C_{11}^{xz}$ ($N^*{=}3$, guadagno $1229\%$)"),
]
for key, col, ls, lab in picks:
    r = by_key[key]
    ax.plot(N_grid, r["vals"], color=col, ls=ls, marker="o", ms=4, lw=1.8, label=lab)
ax.set_xlim(0, 15)
ax.set_xlabel(r"$N$")
ax.set_ylabel(r"$|C(N)|$, rumore nullo ($t=2$)")
ax.set_title(r"Quattro casi rappresentativi (zoom $N\leq15$)")
ax.legend(fontsize=9, loc="upper right")
salva(fig, "fig_scan36_curve_rappresentative")

print("fatto:", len(results), "combinazioni analizzate")
