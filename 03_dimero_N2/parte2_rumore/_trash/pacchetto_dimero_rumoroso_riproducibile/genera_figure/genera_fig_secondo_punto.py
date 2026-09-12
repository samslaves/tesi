"""Genera fig_secondo_punto_confronto.pdf.
Eseguire dalla RADICE del pacchetto, dopo 01_, 02_ e 03_.

RUOLO NELL'INSIEME DEL PACCHETTO: produce la figura che verifica la
generalita' del risultato (N* invariato) a un secondo punto di lavoro
fisico -- l'unico script di figura che, come 03_genera_dati_secondo_punto.py,
deve monkey-patchare esplicitamente i moduli trotter_rumoroso_dimero e
correlatori_rumorosi_dimero per lavorare a un punto diverso da "test 2"
(vedi commenti inline e GUIDA_USO.md sez. 6).
"""
import sys
sys.path.insert(0, "codice")
import numpy as np
from stile import plt, C_BLU, C_ARANC, C_GRIGIO, salva
import trotter_rumoroso_dimero as trd
import correlatori_rumorosi_dimero as crd
from noise_model_dimero import build_noise_model

data = np.load("dati/ground_state_punto2.npz")
vqe_params_ideali = data["vqe_params"]
psi_exact = data["psi0_exact"]
na = np.load("dati/vqe_noise_aware_punto2.npz")
x_na = na["x_noise_aware"]

J, b, D = 1.0, -0.18, 1.0
nm_ref, _ = build_noise_model()
t = 2.0

# --- N* Trotter al secondo punto: serve puntare i globali del modulo
#     al punto giusto (trappola nota, vedi 03_genera_dati_secondo_punto.py) ---
trd.J, trd.b, trd.D = J, b, D
N_grid_trotter = list(range(1, 21)) + [30, 40, 60, 80, 120, 160]
F_i, F_n = [], []
for N in N_grid_trotter:
    Fi, _ = trd.fedelta_trotter_rumoroso(vqe_params_ideali, psi_exact, t, N, noise_model=nm_ref)
    Fn, _ = trd.fedelta_trotter_rumoroso(x_na, psi_exact, t, N, noise_model=nm_ref)
    F_i.append(Fi); F_n.append(Fn)
Ni_trotter = N_grid_trotter[int(np.argmax(F_i))]
Nn_trotter = N_grid_trotter[int(np.argmax(F_n))]
print(f"N* Trotter: ideale={Ni_trotter}  noise-aware={Nn_trotter}  (atteso: 8, 8)")

# --- N* correlatore al secondo punto ---
crd.J_DEFAULT, crd.b_DEFAULT, crd.D_DEFAULT = J, b, D
N_grid_corr = list(range(1, 21))
vals_i, vals_n = [], []
for N in N_grid_corr:
    c_i = crd.correlator_rumoroso(2, "x", 1, "x", t, N, J, b, D, vqe_params_ideali,
                                   noise_model=nm_ref, p_readout=0.023)
    c_n = crd.correlator_rumoroso(2, "x", 1, "x", t, N, J, b, D, x_na,
                                   noise_model=nm_ref, p_readout=0.023)
    vals_i.append(abs(c_i)); vals_n.append(abs(c_n))
Ni_corr = N_grid_corr[int(np.argmax(vals_i))]
Nn_corr = N_grid_corr[int(np.argmax(vals_n))]
print(f"N* correlatore: ideale={Ni_corr}  noise-aware={Nn_corr}  (atteso: 3, 3)")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2))
ax1.plot(N_grid_trotter, F_i, "o-", color=C_BLU, label=r"$\theta^*_\mathrm{ideale}$")
ax1.plot(N_grid_trotter, F_n, "s--", color=C_ARANC, ms=5, label=r"$\theta^*_\mathrm{noise\text{-}aware}$")
ax1.axvline(Ni_trotter, color=C_GRIGIO, ls=":", lw=1.3)
ax1.annotate(rf"$N^*={Ni_trotter}$", xy=(Ni_trotter, max(F_i[7], F_n[7])), xytext=(20, 0.65),
             arrowprops=dict(arrowstyle="->", color=C_GRIGIO))
ax1.set_xlabel(r"$N$ (passi di Trotter)"); ax1.set_ylabel(r"$F(N)$")
ax1.set_title("Fedeltà di Trotter (secondo punto)", fontsize=12)
ax1.legend(fontsize=9)

ax2.plot(N_grid_corr, vals_i, "o-", color=C_BLU, label=r"$\theta^*_\mathrm{ideale}$")
ax2.plot(N_grid_corr, vals_n, "s--", color=C_ARANC, ms=5, label=r"$\theta^*_\mathrm{noise\text{-}aware}$")
ax2.axvline(Ni_corr, color=C_GRIGIO, ls=":", lw=1.3)
ax2.annotate(rf"$N^*={Ni_corr}$", xy=(Ni_corr, max(vals_i[2], vals_n[2])), xytext=(9, 0.40),
             arrowprops=dict(arrowstyle="->", color=C_GRIGIO))
ax2.set_xlabel(r"$N$ (passi di Trotter)"); ax2.set_ylabel(r"$|C_{21}^{xx}(t{=}2,N)|$")
ax2.set_title("Correlatore rumoroso (secondo punto)", fontsize=12)
ax2.legend(fontsize=9)

salva(fig, "fig_secondo_punto_confronto")
