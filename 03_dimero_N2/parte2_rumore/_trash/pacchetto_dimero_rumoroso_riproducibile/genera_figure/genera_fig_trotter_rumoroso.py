"""Genera fig_passo3_F_vs_N.pdf e fig_passo3_zoom_minimo.pdf.
Eseguire dalla RADICE del pacchetto, dopo 01_genera_dati_vqe_ideale.py.

RUOLO NELL'INSIEME DEL PACCHETTO: produce entrambe le figure del
documento sulla quantum simulation (Trotter) sotto rumore -- la curva
F(N) su range esteso (dove sta N*=8) e lo zoom sulla regione non
perturbativa (dove sta il vero minimo, N=3). Chiama
fedelta_trotter_rumoroso() (codice/trotter_rumoroso_dimero.py) sia con
rumore acceso sia spento, per separare l'effetto del solo Trotter da
quello del rumore accumulato.
"""
import sys
sys.path.insert(0, "codice")
import numpy as np
from stile import plt, C_BLU, C_ARANC, C_GRIGIO, salva
from trotter_rumoroso_dimero import fedelta_trotter_rumoroso
from noise_model_dimero import build_noise_model

data = np.load("dati/ground_state_test2.npz")
vqe_params = data["vqe_params"]
psi0_exact = data["psi0_exact"]
nm_ref, _ = build_noise_model()
t = 2.0

# --- figura 1: curva F(N) su range esteso ---
N_grid = list(range(1, 21)) + [30, 40, 60, 80, 120, 160]
F_rumoroso = []
for N in N_grid:
    F, _ = fedelta_trotter_rumoroso(vqe_params, psi0_exact, t, N, noise_model=nm_ref)
    F_rumoroso.append(F)

imax = int(np.argmax(F_rumoroso))
N_star = N_grid[imax]
print(f"N* = {N_star}  F(N*) = {F_rumoroso[imax]:.6f}  (atteso: N*=8, F=0.817725)")

fig, ax = plt.subplots(figsize=(6.6, 4.3))
ax.plot(N_grid, F_rumoroso, "o-", color=C_BLU, ms=6)
ax.axvline(N_star, color=C_GRIGIO, ls=":", lw=1.3)
ax.annotate(rf"$N^*={N_star}$", xy=(N_star, F_rumoroso[imax]), xytext=(20, 0.72),
            arrowprops=dict(arrowstyle="->", color=C_GRIGIO))
ax.set_xlabel(r"$N$ (passi di Trotter)")
ax.set_ylabel(r"$F(N)$ (rumore ibm_torino)")
ax.set_title("Fedeltà rispetto allo stato bersaglio fisico")
salva(fig, "fig_passo3_F_vs_N")

# --- figura 2: zoom sulla regione non perturbativa, N=1..8, con rumore nullo ---
N_zoom = list(range(1, 9))
F0_zoom, Fn_zoom = [], []
for N in N_zoom:
    F0, _ = fedelta_trotter_rumoroso(vqe_params, psi0_exact, t, N, noise_model=None)
    Fn, _ = fedelta_trotter_rumoroso(vqe_params, psi0_exact, t, N, noise_model=nm_ref)
    F0_zoom.append(F0)
    Fn_zoom.append(Fn)

imin = int(np.argmin(F0_zoom))
N_min = N_zoom[imin]
print(f"Minimo non perturbativo: N={N_min}  F0={F0_zoom[imin]:.4f}  Fn={Fn_zoom[imin]:.4f}")
print("(atteso: minimo a N=3, F~0.40)")

fig, ax = plt.subplots(figsize=(6.6, 4.3))
ax.plot(N_zoom, F0_zoom, "o-", color=C_BLU, ms=7, label="rumore nullo")
ax.plot(N_zoom, Fn_zoom, "s--", color=C_ARANC, ms=7, label="ibm_torino")
ax.axvline(N_min, color=C_GRIGIO, ls=":", lw=1.3)
ax.annotate(f"minimo, $N={N_min}$", xy=(N_min, F0_zoom[imin]), xytext=(4.3, 0.42),
            arrowprops=dict(arrowstyle="->", color=C_GRIGIO))
ax.set_xlabel(r"$N$ (passi di Trotter)")
ax.set_ylabel(r"$F(N)$")
ax.set_title("Regione non perturbativa: $N=1$ a $8$")
ax.legend(fontsize=9.5)
salva(fig, "fig_passo3_zoom_minimo")
