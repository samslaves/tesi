"""Figure del documento 11 -- readout asimmetrico. |C(N)| simmetrico vs
asimmetrico, e N* in funzione del rapporto p10:p01 (stress test)."""
import os
import numpy as np
import matplotlib.pyplot as plt
from stile import *

from noise_model_dimero import build_noise_model
from correlatori_readout_asimmetrico import (
    trova_N_star_asimmetrico, P_READOUT_REF, P01_ILLUSTRATIVO, P10_ILLUSTRATIVO,
)

os.makedirs("figure", exist_ok=True)

data = np.load("ground_state_test2.npz")
vqe_params = data["vqe_params"]
J, b, D = 1.0, 0.35, 0.80
t = 2.0
N_grid = [1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 15, 20]
nm_ref, _ = build_noise_model()

# =====================================================================
# 1. fig_correlatore_N_asimmetrico -- simmetrico vs asimmetrico
# =====================================================================
_, _, vals_sym = trova_N_star_asimmetrico(
    vqe_params, t, N_grid, J, b, D, nm_ref,
    p01=P_READOUT_REF, p10=P_READOUT_REF)
Nstar_sym, Cstar_sym, _ = trova_N_star_asimmetrico(
    vqe_params, t, N_grid, J, b, D, nm_ref,
    p01=P_READOUT_REF, p10=P_READOUT_REF)
Nstar_asym, Cstar_asym, vals_asym = trova_N_star_asimmetrico(
    vqe_params, t, N_grid, J, b, D, nm_ref,
    p01=P01_ILLUSTRATIVO, p10=P10_ILLUSTRATIVO)

fig, ax = plt.subplots(figsize=(6.4, 4.6))
ax.plot(N_grid, vals_sym, color=C_BLU, marker="o", ms=5, lw=1.8,
        label=r"simmetrico ($p_{01}{=}p_{10}{=}0.023$)")
ax.plot(N_grid, vals_asym, color=C_ARANC, marker="s", ms=5, lw=1.8, ls="--",
        label=r"asimmetrico illustrativo")
ax.axvline(Nstar_sym, color="0.55", ls=":", lw=1.2)
ax.set_xlabel(r"$N$")
ax.set_ylabel(r"$|C_{21}^{xx}(t{=}2,N)|$")
ax.set_title("Readout simmetrico vs asimmetrico")
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
    Nst, _, _ = trova_N_star_asimmetrico(vqe_params, t, N_grid, J, b, D, nm_ref,
                                          p01=p01, p10=p10)
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
