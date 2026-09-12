"""Genera fig_correlatore_N_asimmetrico.pdf e fig_Nstar_vs_rapporto.pdf.
Eseguire dalla RADICE del pacchetto, dopo 01_genera_dati_vqe_ideale.py.

RUOLO NELL'INSIEME DEL PACCHETTO: produce entrambe le figure
dell'estensione readout asimmetrico -- il confronto diretto simmetrico
contro asimmetrico (split illustrativo) e lo stress test a rapporti
p10:p01 fino a 50x, entrambi tramite trova_N_star_asimmetrico()
(codice/correlatori_readout_asimmetrico.py). E' lo script che rende
visivamente il risultato "N*=5 resta invariato anche qui, ma non era
garantito dalla teoria come nel caso simmetrico".
"""
import sys
sys.path.insert(0, "codice")
import numpy as np
from stile import plt, C_BLU, C_ARANC, C_VERDE, C_GRIGIO, salva
from correlatori_readout_asimmetrico import (
    trova_N_star_asimmetrico, P_READOUT_REF, P01_ILLUSTRATIVO, P10_ILLUSTRATIVO,
)
from correlatori_rumorosi_dimero import J_DEFAULT, b_DEFAULT, D_DEFAULT
from noise_model_dimero import build_noise_model

data = np.load("dati/ground_state_test2.npz")
vqe_params = data["vqe_params"]
nm_ref, _ = build_noise_model()
t = 2.0
N_grid = list(range(1, 21))

# --- figura 1: correlatore simmetrico vs asimmetrico ---
_, _, vals_s = trova_N_star_asimmetrico(
    vqe_params, t, N_grid, J_DEFAULT, b_DEFAULT, D_DEFAULT,
    nm_ref, p01=P_READOUT_REF, p10=P_READOUT_REF)
N_star_s = N_grid[int(np.argmax(vals_s))]

_, _, vals_a = trova_N_star_asimmetrico(
    vqe_params, t, N_grid, J_DEFAULT, b_DEFAULT, D_DEFAULT,
    nm_ref, p01=P01_ILLUSTRATIVO, p10=P10_ILLUSTRATIVO)
N_star_a = N_grid[int(np.argmax(vals_a))]
print(f"N* simmetrico={N_star_s}  N* asimmetrico={N_star_a}  (atteso: 5, 5)")

fig, ax = plt.subplots(figsize=(6.4, 4.2))
ax.plot(N_grid, vals_s, "o-", color=C_BLU, label=r"simmetrico ($p_{01}=p_{10}=0.023$)")
ax.plot(N_grid, vals_a, "s--", color=C_ARANC, label=r"asimmetrico ($p_{01}=0.0115$, $p_{10}=0.0345$)")
ax.axvline(5, color=C_GRIGIO, ls=":", lw=1.3)
ax.annotate(r"$N^*=5$ (entrambi)", xy=(5, max(vals_s[4], vals_a[4])),
            xytext=(8.5, 0.22), arrowprops=dict(arrowstyle="->", color=C_GRIGIO))
ax.set_xlabel(r"$N$ (passi di Trotter)")
ax.set_ylabel(r"$|C_{21}^{xx}(t{=}2, N)|$")
ax.set_title("Correlatore rumoroso: simmetrico vs asimmetrico")
ax.legend(fontsize=9.5, loc="upper right")
salva(fig, "fig_correlatore_N_asimmetrico")

# --- figura 2: N* vs rapporto p10:p01 (stress test) ---
rapporti = [1, 3, 5, 10, 20, 50]
N_star_vs_rapporto = []
for r in rapporti:
    tot = 2 * P_READOUT_REF
    p01_r = tot / (1 + r)
    p10_r = r * p01_r
    Nr, _, _ = trova_N_star_asimmetrico(
        vqe_params, t, N_grid, J_DEFAULT, b_DEFAULT, D_DEFAULT,
        nm_ref, p01=p01_r, p10=p10_r)
    N_star_vs_rapporto.append(Nr)
print("N* vs rapporto:", list(zip(rapporti, N_star_vs_rapporto)))

fig, ax = plt.subplots(figsize=(6.0, 4.0))
ax.plot(rapporti, N_star_vs_rapporto, "o-", color=C_VERDE, ms=7)
ax.axhline(5, color=C_GRIGIO, ls=":", lw=1.3)
ax.set_xscale("log")
ax.set_xlabel(r"rapporto $p_{10}:p_{01}$ (scala log)")
ax.set_ylabel(r"$N^*$")
ax.set_ylim(3.5, 6.5)
ax.set_title(r"Robustezza di $N^*$ oltre il range realistico")
salva(fig, "fig_Nstar_vs_rapporto")
