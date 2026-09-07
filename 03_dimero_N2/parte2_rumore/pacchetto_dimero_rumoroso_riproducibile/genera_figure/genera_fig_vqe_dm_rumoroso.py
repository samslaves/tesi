"""Genera fig_passo2_scan_eps2q.pdf (documento: VQE con DM sotto rumore).
Eseguire dalla RADICE del pacchetto, DOPO 01_genera_dati_vqe_ideale.py
(serve dati/ground_state_test2.npz).

RUOLO NELL'INSIEME DEL PACCHETTO: produce l'unica figura del documento
sul VQE con termine DM sotto rumore (Passo 2) -- uno scan diretto di
vqe_energia_fedelta_rumorosa() (codice/vqe_dm_rumoroso_dimero.py) su
5 valori di eps_2q, senza toccare ne' l'ottimizzazione ne' il modello
di rumore.
"""
import sys
sys.path.insert(0, "codice")
import numpy as np
from stile import plt, C_BLU, C_GRIGIO, salva
from vqe_dm_rumoroso_dimero import vqe_energia_fedelta_rumorosa
from noise_model_dimero import build_noise_model

data = np.load("dati/ground_state_test2.npz")
vqe_params = data["vqe_params"]
psi0_exact = data["psi0_exact"]

eps2q_grid = [0.0, 1e-3, 3.8e-3, 8e-3, 1.5e-2]
E_ideale, F_ideale = [], []
for e in eps2q_grid:
    nm, _ = build_noise_model(eps_2q=e) if e > 0 else (None, None)
    E, F, _ = vqe_energia_fedelta_rumorosa(vqe_params, psi0_exact, noise_model=nm)
    E_ideale.append(E)
    F_ideale.append(F)

labels = [f"{e:.1e}" if e > 0 else "0" for e in eps2q_grid]
xs = np.arange(len(eps2q_grid))

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2))
ax1.plot(xs, E_ideale, "o-", color=C_BLU, ms=7)
ax1.axvline(2, color=C_GRIGIO, ls=":", lw=1.2)
ax1.set_xticks(xs); ax1.set_xticklabels(labels, rotation=20)
ax1.set_xlabel(r"$\varepsilon_{2q}$")
ax1.set_ylabel(r"$E$ (rumoroso)")
ax1.set_title("Energia", fontsize=12.5)

ax2.plot(xs, F_ideale, "o-", color=C_BLU, ms=7)
ax2.axvline(2, color=C_GRIGIO, ls=":", lw=1.2)
ax2.set_xticks(xs); ax2.set_xticklabels(labels, rotation=20)
ax2.set_xlabel(r"$\varepsilon_{2q}$")
ax2.set_ylabel(r"$F$ (rumorosa)")
ax2.set_title("Fedeltà", fontsize=12.5)

salva(fig, "fig_passo2_scan_eps2q")
print("E_ideale:", E_ideale)
print("F_ideale:", F_ideale)
