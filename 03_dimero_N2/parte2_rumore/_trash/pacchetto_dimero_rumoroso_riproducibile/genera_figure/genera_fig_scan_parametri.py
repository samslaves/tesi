"""Genera fig_passo5_Nstar_vs_eps.pdf.
Eseguire dalla RADICE del pacchetto, dopo 01_genera_dati_vqe_ideale.py.

RUOLO NELL'INSIEME DEL PACCHETTO: produce l'unica figura del documento
sullo scan dei parametri di rumore -- due pannelli (N* contro eps_2q,
N* contro eps_1q) generati chiamando trova_N_star()
(codice/scan_parametri_rumore_dimero.py) a molti valori di rumore,
mostrando la monotonia non-crescente discussa nel documento.
"""
import sys
sys.path.insert(0, "codice")
import numpy as np
from stile import plt, C_BLU, C_ARANC, C_GRIGIO, salva
from scan_parametri_rumore_dimero import trova_N_star

data = np.load("dati/ground_state_test2.npz")
vqe_params = data["vqe_params"]
psi_exact = data["psi0_exact"]

eps2q_grid = [1e-3, 2e-3, 3.8e-3, 6e-3, 1e-2, 1.5e-2, 2.5e-2]
Ns_eps2q = []
for e in eps2q_grid:
    N, F, _ = trova_N_star(vqe_params, psi_exact, eps_1q=2.9e-4, eps_2q=e)
    Ns_eps2q.append(N)
print("N* vs eps_2q:", list(zip(eps2q_grid, Ns_eps2q)))

eps1q_grid = [1e-4, 2.9e-4, 1e-3, 3e-3, 1e-2, 3e-2]
Ns_eps1q = []
for e in eps1q_grid:
    N, F, _ = trova_N_star(vqe_params, psi_exact, eps_1q=e, eps_2q=3.8e-3)
    Ns_eps1q.append(N)
print("N* vs eps_1q:", list(zip(eps1q_grid, Ns_eps1q)))

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.3))
ax1.plot(eps2q_grid, Ns_eps2q, "o-", color=C_BLU, ms=7)
ax1.set_xscale("log")
ax1.axvline(3.8e-3, color=C_GRIGIO, ls=":", lw=1.2)
ax1.set_xlabel(r"$\varepsilon_{2q}$ (scala log)")
ax1.set_ylabel(r"$N^*$")
ax1.set_title(r"$N^*$ contro $\varepsilon_{2q}$ ($\varepsilon_{1q}$ fisso)", fontsize=12)

ax2.plot(eps1q_grid, Ns_eps1q, "o-", color=C_ARANC, ms=7)
ax2.set_xscale("log")
ax2.axvline(2.9e-4, color=C_GRIGIO, ls=":", lw=1.2)
ax2.set_xlabel(r"$\varepsilon_{1q}$ (scala log)")
ax2.set_ylabel(r"$N^*$")
ax2.set_title(r"$N^*$ contro $\varepsilon_{1q}$ ($\varepsilon_{2q}$ fisso)", fontsize=12)

salva(fig, "fig_passo5_Nstar_vs_eps")
