"""Genera fig_correlatore_noise_aware_confronto.pdf.
Eseguire dalla RADICE del pacchetto, dopo 01_ e 02_.

RUOLO NELL'INSIEME DEL PACCHETTO: produce la figura centrale
dell'estensione VQE noise-aware sul lato dei correlatori -- il
controllo DIRETTO (non per analogia dal Trotter) che N*=5 resta
invariato fra le due preparazioni, richiamando correlator_rumoroso()
(codice/correlatori_rumorosi_dimero.py) con entrambi i set di
parametri salvati in dati/vqe_noise_aware_result.npz.
"""
import sys
sys.path.insert(0, "codice")
import numpy as np
from stile import plt, C_BLU, C_ARANC, C_GRIGIO, salva
from correlatori_rumorosi_dimero import correlator_rumoroso, J_DEFAULT, b_DEFAULT, D_DEFAULT
from noise_model_dimero import build_noise_model

data = np.load("dati/ground_state_test2.npz")
vqe_params_ideali = data["vqe_params"]
na = np.load("dati/vqe_noise_aware_result.npz")
theta_na = na["x_noise_aware"]

nm_ref, _ = build_noise_model()
t = 2.0
N_grid = list(range(1, 21))

vals_i, vals_n = [], []
for N in N_grid:
    c_i = correlator_rumoroso(2, "x", 1, "x", t, N, J_DEFAULT, b_DEFAULT, D_DEFAULT,
                               vqe_params_ideali, noise_model=nm_ref, p_readout=0.023)
    c_n = correlator_rumoroso(2, "x", 1, "x", t, N, J_DEFAULT, b_DEFAULT, D_DEFAULT,
                               theta_na, noise_model=nm_ref, p_readout=0.023)
    vals_i.append(abs(c_i))
    vals_n.append(abs(c_n))

imax_i = int(np.argmax(vals_i))
imax_n = int(np.argmax(vals_n))
print(f"N* ideale={N_grid[imax_i]} |C|={vals_i[imax_i]:.6f}  N* noise-aware={N_grid[imax_n]} |C|={vals_n[imax_n]:.6f}")
print("(atteso: N*=5 in entrambi i casi, |C(N*)| = 0.250002 e 0.249933)")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2))
ax1.plot(N_grid, vals_i, "o-", color=C_BLU, label=r"$\theta^*_\mathrm{ideale}$")
ax1.plot(N_grid, vals_n, "s--", color=C_ARANC, ms=5, label=r"$\theta^*_\mathrm{noise\text{-}aware}$")
ax1.axvline(5, color=C_GRIGIO, ls=":", lw=1.3)
ax1.annotate(r"$N^*=5$ (entrambi)", xy=(5, max(vals_i[4], vals_n[4])), xytext=(8.5, 0.15),
             arrowprops=dict(arrowstyle="->", color=C_GRIGIO))
ax1.set_xlabel(r"$N$ (passi di Trotter)")
ax1.set_ylabel(r"$|C_{21}^{xx}(t{=}2, N)|$")
ax1.set_title("Correlatore rumoroso: ideale vs noise-aware", fontsize=12.5)
ax1.legend(loc="upper right", fontsize=9.5)

diff = np.array(vals_n) - np.array(vals_i)
ax2.plot(N_grid, diff, "o-", color="#009E73")
ax2.axhline(0, color=C_GRIGIO, lw=1)
ax2.set_xlabel(r"$N$ (passi di Trotter)")
ax2.set_ylabel(r"$|C|_\mathrm{noise\text{-}aware} - |C|_\mathrm{ideale}$")
ax2.set_title("Scostamento (scala ingrandita, ${\\sim}10^{-5}$)", fontsize=12.5)
ax2.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))

salva(fig, "fig_correlatore_noise_aware_confronto")
