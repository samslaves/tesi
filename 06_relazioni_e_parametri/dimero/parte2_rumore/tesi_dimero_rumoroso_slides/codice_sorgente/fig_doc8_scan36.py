"""Figura aggiuntiva del documento 8 -- scan completo sulle 36 combinazioni
C_ij^{alpha,beta}(t=2) sotto rumore di riferimento, readout genuinamente
campionato a shot finiti (50000 shot per punto -- ridotti rispetto ai
200000 usati altrove in questo documento per contenere il tempo di calcolo
su 36x16 valutazioni; errore statistico atteso 1/sqrt(50000)=0.0045,
piccolo rispetto ai salti fra N vicini nelle curve). Verifica che il
correlatore di riferimento (C_11^yz) sia un caso rappresentativo e non un
estremo della distribuzione."""
import json
import os
import numpy as np
import matplotlib.pyplot as plt
from stile import *
from correlatori_shots_dimero import correlator_shots

os.makedirs("figure", exist_ok=True)

data = np.load("ground_state_test2.npz")
vqe_params = data["vqe_params"]

N_grid = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 20, 25, 30, 40]
t = 2.0
SHOTS = 50_000

combos = [(i, alpha, j, beta)
          for i in [1, 2] for alpha in ["x", "y", "z"]
          for j in [1, 2] for beta in ["x", "y", "z"]]

righe = []
for (i, alpha, j, beta) in combos:
    vals = []
    for N in N_grid:
        c = correlator_shots(i, alpha, j, beta, t, N, vqe_params,
                              p01=0.023, p10=0.023, shots=SHOTS, seed=11)
        vals.append(abs(c))
    vals = np.array(vals)
    idx = int(np.argmax(vals))
    righe.append({"i": i, "alpha": alpha, "j": j, "beta": beta,
                   "Nstar": N_grid[idx], "Cstar": float(vals[idx]),
                   "vals": vals.tolist()})

with open("scan36_rumore_shots.json", "w") as f:
    json.dump({"N_grid": N_grid, "righe": righe}, f, indent=1)

# ------------------------------------------------------------- figura
fig, (a1, a2) = plt.subplots(2, 1, figsize=(8.0, 9.0))

Nstars = [r["Nstar"] for r in righe]
vals_u, counts = np.unique(Nstars, return_counts=True)
a1.bar(vals_u, counts, color=C_BLU, width=0.6)
a1.set_xlabel(r"$N^*$")
a1.set_ylabel("numero di combinazioni (su 36)")
a1.set_title(r"Distribuzione di $N^*$ sulle 36 combinazioni")
a1.set_xticks(range(1, 6))

for r in righe:
    a2.plot(N_grid, r["vals"], color="0.75", lw=0.8, zorder=1)
highlight = {(2, "x", 1, "x"): (C_ROSSO, r"$C_{21}^{xx}$ ($N^*{=}5$, più fragile)"),
             (1, "y", 1, "z"): (C_BLU, r"$C_{11}^{yz}$ ($N^*{=}2$, riferimento)"),
             (2, "z", 1, "z"): (C_VERDE, r"$C_{21}^{zz}$ ($N^*{=}1$, più ampio)")}
for r in righe:
    key = (r["i"], r["alpha"], r["j"], r["beta"])
    if key in highlight:
        col, lab = highlight[key]
        a2.plot(N_grid, r["vals"], color=col, lw=2.2, label=lab, zorder=3)
a2.set_xlabel(r"$N$")
a2.set_ylabel(r"$|C(N)|$")
a2.set_title("Tutte le 36 curve, readout a shot finiti")
a2.legend(fontsize=9, loc="upper right")

fig.tight_layout()
salva(fig, "fig_scan36_rumore_dimero")

Cstars = [r["Cstar"] for r in righe]
print(f"N* min={min(Nstars)} max={max(Nstars)} media={np.mean(Nstars):.2f}")
print(f"|C(N*)| min={min(Cstars):.4f} max={max(Cstars):.4f}")
