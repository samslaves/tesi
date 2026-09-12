"""Genera fig_F_vs_N_confronto.pdf.
Eseguire dalla RADICE del pacchetto, dopo 01_ e 02_.

RUOLO NELL'INSIEME DEL PACCHETTO: produce la figura che confronta,
sulla fedelta' di Trotter, la curva F(N) ottenuta con i parametri
ideali contro quella ottenuta con i parametri noise-aware -- l'analogo,
per il Trotter, di genera_fig_correlatore_confronto.py per i
correlatori. Il pannello destro (scostamento) e' cio' che rende visibile
quanto le due curve siano vicine (scala 1e-4), non solo che lo sono.
"""
import sys
sys.path.insert(0, "codice")
import numpy as np
from stile import plt, C_BLU, C_ARANC, C_GRIGIO, C_VERDE, salva
from trotter_rumoroso_dimero import fedelta_trotter_rumoroso
from noise_model_dimero import build_noise_model

data = np.load("dati/ground_state_test2.npz")
vqe_params_ideali = data["vqe_params"]
psi0_exact = data["psi0_exact"]
na = np.load("dati/vqe_noise_aware_result.npz")
theta_na = na["x_noise_aware"]

nm_ref, _ = build_noise_model()
t = 2.0
N_grid = list(range(1, 21)) + [30, 40, 60, 80, 120, 160]

F_i, F_n = [], []
for N in N_grid:
    Fi, _ = fedelta_trotter_rumoroso(vqe_params_ideali, psi0_exact, t, N, noise_model=nm_ref)
    Fn, _ = fedelta_trotter_rumoroso(theta_na, psi0_exact, t, N, noise_model=nm_ref)
    F_i.append(Fi)
    F_n.append(Fn)

Ni = N_grid[int(np.argmax(F_i))]
Nn = N_grid[int(np.argmax(F_n))]
print(f"N* ideale={Ni}  N* noise-aware={Nn}  (atteso: 8, 8)")
print(f"F(N*) ideale={max(F_i):.6f}  F(N*) noise-aware={max(F_n):.6f}")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2))
ax1.plot(N_grid, F_i, "o-", color=C_BLU, label=r"$\theta^*_\mathrm{ideale}$ (VQE+DM rumoroso)")
ax1.plot(N_grid, F_n, "s--", color=C_ARANC, ms=5, label=r"$\theta^*_\mathrm{noise\text{-}aware}$")
ax1.axvline(Ni, color=C_GRIGIO, ls=":", lw=1.3)
ax1.annotate(rf"$N^*={Ni}$", xy=(Ni, max(F_i)), xytext=(20, 0.65),
             arrowprops=dict(arrowstyle="->", color=C_GRIGIO))
ax1.set_xlabel(r"$N$ (passi di Trotter)")
ax1.set_ylabel(r"$F(N)$ (rumore ibm_torino)")
ax1.set_title("Fedeltà rispetto allo stato bersaglio fisico", fontsize=12.5)
ax1.legend(fontsize=9)

diff = np.array(F_n) - np.array(F_i)
ax2.plot(N_grid, diff, "o-", color=C_VERDE)
ax2.axhline(0, color=C_GRIGIO, lw=1)
ax2.set_xlabel(r"$N$ (passi di Trotter)")
ax2.set_ylabel(r"$F_\mathrm{noise\text{-}aware} - F_\mathrm{ideale}$")
ax2.set_title("Scostamento (scala ingrandita, ${\\sim}10^{-4}$)", fontsize=12.5)
ax2.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))

salva(fig, "fig_F_vs_N_confronto")
