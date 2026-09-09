"""Figure del documento 11 -- readout asimmetrico. |C(N)| simmetrico vs
asimmetrico, e N* in funzione del rapporto p10:p01 (stress test).
Readout genuinamente campionato a shot finiti in entrambi i casi (simmetrico
e asimmetrico): non c'e' piu' una formula analitica da confrontare con un
Monte Carlo -- il Monte Carlo E' il metodo, l'unico usato."""
import os
import numpy as np
import matplotlib.pyplot as plt
from stile import *

from correlatori_shots_dimero import correlator_shots, SHOTS_DEFAULT

os.makedirs("figure", exist_ok=True)

data = np.load("ground_state_test2.npz")
vqe_params = data["vqe_params"]
t = 2.0
N_grid = [1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 15, 20]
I, ALPHA, J_IDX, BETA = 1, "y", 1, "z"
P_READOUT_REF = 0.023
P01_ILLUSTRATIVO, P10_ILLUSTRATIVO = 0.0115, 0.0345


def curva(p01, p10, seed):
    vals = []
    for N in N_grid:
        c = correlator_shots(I, ALPHA, J_IDX, BETA, t, N, vqe_params,
                              p01=p01, p10=p10, shots=SHOTS_DEFAULT, seed=seed)
        vals.append(abs(c))
    vals = np.array(vals)
    idx = int(np.argmax(vals))
    return N_grid[idx], vals[idx], vals


# =====================================================================
# 1. fig_correlatore_N_asimmetrico -- simmetrico vs asimmetrico
# =====================================================================
Nstar_sym, Cstar_sym, vals_sym = curva(P_READOUT_REF, P_READOUT_REF, seed=7)
Nstar_asym, Cstar_asym, vals_asym = curva(P01_ILLUSTRATIVO, P10_ILLUSTRATIVO, seed=7)

fig, ax = plt.subplots(figsize=(6.4, 4.6))
ax.plot(N_grid, vals_sym, color=C_BLU, marker="o", ms=5, lw=1.8,
        label=r"simmetrico ($p_{01}{=}p_{10}{=}0.023$)")
ax.plot(N_grid, vals_asym, color=C_ARANC, marker="s", ms=5, lw=1.8, ls="--",
        label=r"asimmetrico illustrativo")
ax.axvline(Nstar_sym, color="0.55", ls=":", lw=1.2)
ax.set_xlabel(r"$N$")
ax.set_ylabel(r"$|C_{11}^{yz}(t{=}2,N)|$")
ax.set_title("Readout simmetrico vs asimmetrico (shot finiti)")
ax.legend(loc="lower right", fontsize=10)
salva(fig, "fig_correlatore_N_asimmetrico")
print("N* sym/asym:", Nstar_sym, Cstar_sym, Nstar_asym, Cstar_asym)

# =====================================================================
# 2. fig_Nstar_vs_rapporto -- stress test oltre il range realistico
# =====================================================================
media = P_READOUT_REF
rapporti = [1, 3, 5, 10, 20, 50]
Ns = []
for r in rapporti:
    # p01 + p10 = 2*media, p10/p01 = r  =>  p01 = 2*media/(1+r), p10 = r*p01
    p01 = 2 * media / (1 + r)
    p10 = r * p01
    Nst, Cst, _ = curva(p01, p10, seed=9)
    Ns.append(Nst)
    print(f"rapporto={r}  p01={p01:.4f}  p10={p10:.4f}  N*={Nst}")

fig, ax = plt.subplots(figsize=(5.8, 4.4))
ax.plot(rapporti, Ns, color=C_VIOLA, marker="o", ms=7, lw=2.0)
ax.set_xscale("log")
ax.set_xlabel(r"rapporto $p_{10}{:}p_{01}$")
ax.set_ylabel(r"$N^*$")
ax.set_ylim(0, max(Ns) + 2)
ax.set_title(r"$N^*$ vs asimmetria del readout, media fissa $2.3\times10^{-2}$")
salva(fig, "fig_Nstar_vs_rapporto")
