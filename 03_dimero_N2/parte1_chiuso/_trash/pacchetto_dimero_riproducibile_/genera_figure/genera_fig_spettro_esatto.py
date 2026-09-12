"""Genera fig_spettro_dimero.pdf.
Eseguire dalla RADICE del pacchetto (nessun dato precalcolato richiesto:
diagonalizza direttamente).

RUOLO NELL'INSIEME DEL PACCHETTO: produce la figura di apertura della
Parte 1 -- spettro esatto (le 4 energie del dimero) e magnetizzazione
del ground state, in funzione di B/J, per D=0 (salto discontinuo
all'anticrossing) e D=0.2 (crossover continuo, gap aperto). E' la
figura che mostra visivamente perche' il termine DM sia stato introdotto:
senza D il ground state cambia bruscamente natura a B/J=2, con D il
cambiamento e' smussato.
"""
import sys
sys.path.insert(0, "codice")
import numpy as np
from stile import plt, C_NERO, C_ROSSO, C_GRIGIO, salva
from dimer_exact import exact_sweep

J = 1.0
b = np.linspace(0.0, 5.0, 300)
res0 = exact_sweep(b, J=J, D=0.0)
resD = exact_sweep(b, J=J, D=0.2)

print("Verifica rapida: E0(b=0, D=0) =", res0["gs_energy"][0], " (atteso -3.0, singoletto)")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.3))

for k in range(4):
    ax1.plot(b / J, res0["energies"][:, k], color=C_GRIGIO, lw=1)
ax1.plot(b / J, res0["gs_energy"], color=C_NERO, lw=2.2, label="GS (D=0)")
ax1.plot(b / J, resD["gs_energy"], color=C_ROSSO, ls="--", lw=2.2, label="GS (D=0.2)")
ax1.axvline(2.0, color=C_GRIGIO, ls=":", lw=1)
ax1.set_xlabel(r"$B/J$"); ax1.set_ylabel(r"$E/J$")
ax1.set_title("Spettro del dimero")
ax1.legend(fontsize=9.5)

ax2.plot(b / J, res0["gs_mz"], color=C_NERO, lw=2.2, label="D=0 (salto)")
ax2.plot(b / J, resD["gs_mz"], color=C_ROSSO, ls="--", lw=2.2, label="D=0.2 (crossover)")
ax2.axvline(2.0, color=C_GRIGIO, ls=":", lw=1)
ax2.set_xlabel(r"$B/J$"); ax2.set_ylabel(r"$\langle M_z\rangle$")
ax2.set_title("Magnetizzazione del ground state")
ax2.legend(fontsize=9.5)

salva(fig, "fig_spettro_dimero")
