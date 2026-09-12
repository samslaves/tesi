"""Genera fig_gap_magnetizzazione.pdf.
Eseguire dalla RADICE del pacchetto (nessun dato precalcolato richiesto).

RUOLO NELL'INSIEME DEL PACCHETTO: mancava nella prima versione --
genera_fig_spettro_esatto.py mostra lo spettro completo (4 livelli) e la
magnetizzazione, ma non il GAP esplicito (distanza fondamentale-primo
eccitato) contro B/J, che è il contenuto specifico della Fig. 2 della
Parte 1 (dimero_01_sistema.tex): senza D il gap si annulla esattamente a
B/J=2 (vero incrocio); con D/J=0.2 resta finito (minimo atteso 0.565) --
è la prova diretta che il DM apre l'anticrossing, complementare allo
spettro completo (che mostra il fenomeno ma non lo quantifica).
"""
import sys
sys.path.insert(0, "codice")
import numpy as np
from stile import plt, C_NERO, C_ROSSO, C_GRIGIO, salva
from dimer_exact import exact_sweep

J = 1.0
b = np.linspace(1.0, 3.5, 300)  # zoom attorno all'incrocio, come nel documento
res0 = exact_sweep(b, J=J, D=0.0)
resD = exact_sweep(b, J=J, D=0.2)

gap0 = res0["energies"][:, 1] - res0["energies"][:, 0]
gapD = resD["energies"][:, 1] - resD["energies"][:, 0]
min_gapD = gapD.min()
print(f"Verifica: minimo del gap con D=0.2 = {min_gapD:.4f}  (atteso 0.565)")
assert abs(min_gapD - 0.565) < 0.01, "minimo del gap fuori dal range atteso"

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.5, 4.3))

ax1.plot(b / J, gap0, color=C_NERO, lw=2.2, label="$D=0$")
ax1.plot(b / J, gapD, color=C_ROSSO, ls="--", lw=2.2, label="$D/J=0.2$")
ax1.axvline(2.0, color=C_GRIGIO, ls=":", lw=1)
ax1.annotate(f"minimo: {min_gapD:.3f}", xy=(2.0, min_gapD),
             xytext=(2.3, min_gapD + 0.4), fontsize=9,
             arrowprops=dict(arrowstyle="->", color=C_GRIGIO))
ax1.set_xlabel(r"$B/J$"); ax1.set_ylabel(r"$\Delta E_{01}/J$")
ax1.set_title("Distanza fondamentale-primo eccitato")
ax1.legend(fontsize=9.5)

ax2.plot(b / J, res0["gs_mz"], color=C_NERO, lw=2.2, label="$D=0$ (salto)")
ax2.plot(b / J, resD["gs_mz"], color=C_ROSSO, ls="--", lw=2.2, label="$D/J=0.2$ (crossover)")
ax2.axvline(2.0, color=C_GRIGIO, ls=":", lw=1)
ax2.set_xlabel(r"$B/J$"); ax2.set_ylabel(r"$\langle M_z\rangle$")
ax2.set_title("Magnetizzazione del ground state")
ax2.legend(fontsize=9.5)

salva(fig, "fig_gap_magnetizzazione")
