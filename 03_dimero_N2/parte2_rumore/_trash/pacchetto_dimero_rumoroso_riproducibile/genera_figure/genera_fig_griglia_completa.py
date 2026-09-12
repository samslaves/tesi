"""Genera fig_passo5_griglia_completa.pdf.
Eseguire dalla RADICE del pacchetto, dopo 01_ e 02_.

RUOLO NELL'INSIEME DEL PACCHETTO: produce la figura che estende il
controllo dell'estensione VQE noise-aware dal punto di riferimento
all'intera griglia dello scan sui parametri di rumore -- usa
trova_N_star() (Trotter) e N_star_correlatore() di
codice/verifica_passo5_noise_aware.py, con doppia assertion che
interrompe lo script se anche un solo punto della griglia mostrasse
N* diverso fra le due preparazioni.
"""
import sys
sys.path.insert(0, "codice")
import numpy as np
from stile import plt, C_BLU, C_ARANC, salva
from scan_parametri_rumore_dimero import trova_N_star
from verifica_passo5_noise_aware import N_star_correlatore

data = np.load("dati/ground_state_test2.npz")
vqe_params_ideali = data["vqe_params"]
psi_exact = data["psi0_exact"]
na = np.load("dati/vqe_noise_aware_result.npz")
theta_na = na["x_noise_aware"]

# --- N* Trotter su griglia eps2q ---
eps2q_grid = [1e-3, 2e-3, 3.8e-3, 6e-3, 1e-2, 1.5e-2, 2.5e-2]
Ns_ideale, Ns_na = [], []
for e in eps2q_grid:
    Ni, _, _ = trova_N_star(vqe_params_ideali, psi_exact, eps_1q=2.9e-4, eps_2q=e)
    Nn, _, _ = trova_N_star(theta_na, psi_exact, eps_1q=2.9e-4, eps_2q=e)
    Ns_ideale.append(Ni); Ns_na.append(Nn)
print("N* Trotter, ideale:", Ns_ideale)
print("N* Trotter, noise-aware:", Ns_na)
assert Ns_ideale == Ns_na, "N* Trotter diverso fra le due preparazioni!"

# --- N* correlatore su griglia eps2q ---
eps2q_grid_c = [1e-3, 2e-3, 3.8e-3, 6e-3, 1e-2]
Ni_corr, Nn_corr = [], []
for e in eps2q_grid_c:
    Ni, _ = N_star_correlatore(vqe_params_ideali, 2.9e-4, e)
    Nn, _ = N_star_correlatore(theta_na, 2.9e-4, e)
    Ni_corr.append(Ni); Nn_corr.append(Nn)
print("N* correlatore, ideale:", Ni_corr)
print("N* correlatore, noise-aware:", Nn_corr)
assert Ni_corr == Nn_corr, "N* correlatore diverso fra le due preparazioni!"

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.3))
ax1.plot(eps2q_grid, Ns_ideale, "o-", color=C_BLU, ms=7, label=r"$\theta^*_\mathrm{ideale}$")
ax1.plot(eps2q_grid, Ns_na, "x--", color=C_ARANC, ms=10, mew=2.5, label=r"$\theta^*_\mathrm{nuovo}$")
ax1.set_xscale("log")
ax1.set_xlabel(r"$\varepsilon_{2q}$")
ax1.set_ylabel("N* (fedeltà di Trotter)")
ax1.set_title("N* Trotter su tutta la griglia", fontsize=12)
ax1.legend(fontsize=9.5)

ax2.plot(eps2q_grid_c, Ni_corr, "o-", color=C_BLU, ms=8, label=r"$\theta^*_\mathrm{ideale}$")
ax2.plot(eps2q_grid_c, Nn_corr, "x--", color=C_ARANC, ms=10, mew=2.5, label=r"$\theta^*_\mathrm{nuovo}$")
ax2.set_xscale("log")
ax2.set_xlabel(r"$\varepsilon_{2q}$")
ax2.set_ylabel(r"$N^*$ (correlatore)")
ax2.set_ylim(4, 6)
ax2.set_title("N* correlatore su tutta la griglia", fontsize=12)
ax2.legend(fontsize=9.5)

salva(fig, "fig_passo5_griglia_completa")
