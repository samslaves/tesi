"""Genera fig_trotter_convergenza.pdf.
Eseguire dalla RADICE del pacchetto (nessun dato precalcolato richiesto).

RUOLO NELL'INSIEME DEL PACCHETTO: produce la figura che mostra la
convergenza O(1/N) dell'errore di Trotter al prim'ordine, confrontando
l'evoluzione a circuito (trotter_dimero.py, decomposizione esplicita)
con l'evoluzione esatta e continua (nessun Trotter). Stesso fenomeno
verificato numericamente in validate_circuito_correlazioni_dimero.py
(li' sul correlatore, qui direttamente sulla fedeltà dello stato) --
due evidenze indipendenti della stessa legge di scala.
"""
import sys
sys.path.insert(0, "codice")
import numpy as np
from stile import plt, C_BLU, C_GRIGIO, salva
from trotter_dimero import U_exact, U_trotter_mat, PSI0

b, J, D = 1.0, 1.0, 0.2
t = 2.0

N_grid = [5, 10, 20, 40, 80, 160, 320, 640]
psi_exact = U_exact(b, J, D, t) @ PSI0

errori = []
for N in N_grid:
    psi_N = U_trotter_mat(b, J, D, t, N) @ PSI0
    err = np.linalg.norm(psi_exact - psi_N)
    errori.append(err)

print(f"{'N':>5} {'errore':>12} {'rapporto':>10}")
prev = None
for N, e in zip(N_grid, errori):
    r = f"{prev/e:.2f}" if prev else "--"
    print(f"{N:>5} {e:>12.4e} {r:>10}")
    prev = e
print("atteso: rapporto -> 2 raddoppiando N (Trotter al prim'ordine, errore O(1/N))")

fig, ax = plt.subplots(figsize=(6.4, 4.4))
ax.loglog(N_grid, errori, "o-", color=C_BLU, ms=7)
# retta di riferimento 1/N, normalizzata al primo punto
riferimento = errori[0] * N_grid[0] / np.array(N_grid)
ax.loglog(N_grid, riferimento, "--", color=C_GRIGIO, lw=1.3, label=r"$\propto 1/N$")
ax.set_xlabel(r"$N$ (passi di Trotter)")
ax.set_ylabel(r"$\||\psi_\mathrm{esatto}\rangle - |\psi_\mathrm{Trotter}\rangle\|$")
ax.set_title("Convergenza dell'errore di Trotter (nessun rumore)")
ax.legend(fontsize=9.5)
salva(fig, "fig_trotter_convergenza")
