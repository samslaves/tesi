"""Genera fig_passo4_correlatore_vs_N.pdf.
Eseguire dalla RADICE del pacchetto, dopo 01_genera_dati_vqe_ideale.py.
Usa circuito_correlazioni_dimero.py -- verificare che sia la versione
CORRETTA (con supporto ansatz_params, non il placeholder con
NotImplementedError): senza quella correzione questo script fallisce.

RUOLO NELL'INSIEME DEL PACCHETTO: produce l'unica figura del documento
sui correlatori dinamici sotto rumore -- la curva |C(N)| che individua
N*=5, tramite correlator_rumoroso() (codice/correlatori_rumorosi_dimero.py).
E' anche, indirettamente, un test di fumo per il modulo
circuito_correlazioni_dimero.py: se quel modulo fosse regredito al
placeholder (vedi nota sopra), questo script fallirebbe subito.
"""
import sys
sys.path.insert(0, "codice")
import numpy as np
from stile import plt, C_BLU, C_GRIGIO, salva
from correlatori_rumorosi_dimero import correlator_rumoroso, J_DEFAULT, b_DEFAULT, D_DEFAULT
from noise_model_dimero import build_noise_model

data = np.load("dati/ground_state_test2.npz")
vqe_params = data["vqe_params"]
nm_ref, _ = build_noise_model()
t = 2.0
N_grid = list(range(1, 21))

vals = []
for N in N_grid:
    c = correlator_rumoroso(2, "x", 1, "x", t, N, J_DEFAULT, b_DEFAULT, D_DEFAULT,
                             vqe_params, noise_model=nm_ref, p_readout=0.023)
    vals.append(abs(c))

imax = int(np.argmax(vals))
N_star = N_grid[imax]
print(f"N* = {N_star}  |C(N*)| = {vals[imax]:.6f}  (atteso: N*=5, |C|=0.250002)")

fig, ax = plt.subplots(figsize=(6.6, 4.3))
ax.plot(N_grid, vals, "o-", color=C_BLU, ms=6)
ax.axvline(N_star, color=C_GRIGIO, ls=":", lw=1.3)
ax.annotate(rf"$N^*={N_star}$", xy=(N_star, vals[imax]), xytext=(10, 0.16),
            arrowprops=dict(arrowstyle="->", color=C_GRIGIO))
ax.set_xlabel(r"$N$ (passi di Trotter)")
ax.set_ylabel(r"$|C_{21}^{xx}(t{=}2,N)|$")
ax.set_title("Modulo del correlatore rumoroso")
salva(fig, "fig_passo4_correlatore_vs_N")
