"""Genera fig_trotter_sz.pdf e fig_trotter_errore.pdf.
Eseguire dalla RADICE del pacchetto (nessun dato precalcolato richiesto).

RUOLO NELL'INSIEME DEL PACCHETTO: mancava nella prima versione -- lo
script esistente (genera_fig_trotter_convergenza.py) usa solo la
matrice compatta (U_trotter_mat) come unico metodo di calcolo, senza
mai confrontarla col circuito vero (trotter_circuit + Statevector).
Qui si producono entrambe le grandezze della Parte 1
(dimero_03_dinamica.tex): <Sz>(t) a pochi N fissati, ed errore contro N
in scala log-log -- ciascuna volta CON ENTRAMBI i metodi sovrapposti
(matrice e circuito), per mostrare esplicitamente che coincidono, non
solo usare la matrice perche' piu' veloce.

Punto di lavoro: b/J=-0.18, D/J=1 (J=1), stato iniziale |00> --
deliberatamente asimmetrico (nessuno dei due pezzi H1/H2 lo lascia
invariato), altrimenti l'errore di Trotter non emergerebbe (vedi nota
nel documento). NON e' il punto "test 2" (b=1, D=0.2) usato nel resto
del pacchetto.
"""
import sys
sys.path.insert(0, "codice")
import numpy as np
from qiskit.quantum_info import Statevector
from stile import plt, C_NERO, C_BLU, C_ROSSO, C_ARANC, C_VERDE, C_GRIGIO, salva
from trotter_dimero import U_exact, U_trotter_mat, trotter_circuit, sz

b, J, D = -0.18, 1.0, 1.0
PSI0 = np.array([1, 0, 0, 0], dtype=complex)  # |00>

# ---------------------------------------------------------------------
# fig_trotter_sz: <Sz>(t) a pochi N, matrice e circuito sovrapposti
# ---------------------------------------------------------------------
ts = np.linspace(0.0, 10.0, 101)
sz_esatto = [sz(U_exact(b, J, D, t) @ PSI0) for t in ts]

Ns_sz = [2, 5, 20]
colori_N = {2: C_ROSSO, 5: C_ARANC, 20: C_VERDE}

fig, ax = plt.subplots(figsize=(7.4, 4.6))
ax.plot(ts, sz_esatto, color=C_NERO, lw=2.4, label="esatta", zorder=5)
for N in Ns_sz:
    sz_mat = [sz(U_trotter_mat(b, J, D, t, N) @ PSI0) for t in ts]
    sz_circ = []
    for t in ts:
        qc = trotter_circuit(b, J, D, t, N)
        psi = Statevector(qc).data
        sz_circ.append(sz(psi))
    scarto = np.max(np.abs(np.array(sz_mat) - np.array(sz_circ)))
    print(f"N={N:3d}: scarto massimo matrice/circuito su <Sz>(t) = {scarto:.2e}")
    assert scarto < 1e-10, f"matrice e circuito non coincidono a N={N}"
    ax.plot(ts, sz_mat, color=colori_N[N], lw=1.8, ls="--", label=f"$N={N}$ (matrice)")
    ax.plot(ts[::5], np.array(sz_circ)[::5], "o", color=colori_N[N], ms=4,
            mfc="none", label=f"$N={N}$ (circuito)")

ax.set_xlabel("$t$"); ax.set_ylabel(r"$\langle S_z^{\rm tot}\rangle(t)$")
ax.set_title(r"$\langle S_z\rangle(t)$, $b/J=-0.18$, $D/J=1$, stato $|00\rangle$")
ax.legend(fontsize=8, ncol=2)
salva(fig, "fig_trotter_sz")

# ---------------------------------------------------------------------
# fig_trotter_errore: errore a t=6 vs N, matrice e circuito, log-log
# ---------------------------------------------------------------------
t_fix = 6.0
psi_ref = U_exact(b, J, D, t_fix) @ PSI0
N_grid = [2, 5, 10, 20, 40, 80]

err_operatore, err_fidelity_mat, err_fidelity_circ = [], [], []
for N in N_grid:
    U_mat = U_trotter_mat(b, J, D, t_fix, N)
    err_operatore.append(np.linalg.norm(U_mat - U_exact(b, J, D, t_fix)))
    psi_mat = U_mat @ PSI0
    err_fidelity_mat.append(1 - abs(np.vdot(psi_ref, psi_mat)) ** 2)
    qc = trotter_circuit(b, J, D, t_fix, N)
    psi_circ = Statevector(qc).data
    err_fidelity_circ.append(1 - abs(np.vdot(psi_ref, psi_circ)) ** 2)

scarto_fid = np.max(np.abs(np.array(err_fidelity_mat) - np.array(err_fidelity_circ)))
print(f"\nScarto massimo matrice/circuito sull'infedeltà: {scarto_fid:.2e}")
assert scarto_fid < 1e-10, "matrice e circuito non coincidono sull'infedeltà"

fig, ax = plt.subplots(figsize=(6.2, 4.6))
ax.loglog(N_grid, err_operatore, "o-", color=C_BLU, label="distanza fra operatori")
ax.loglog(N_grid, err_fidelity_mat, "s-", color=C_ROSSO, label="1-fidelity (matrice)")
ax.loglog(N_grid, np.array(err_fidelity_circ), "^", color=C_ROSSO, mfc="none", ms=8,
          label="1-fidelity (circuito)")
rif1 = err_operatore[0] * N_grid[0] / np.array(N_grid)
rif2 = err_fidelity_mat[0] * (N_grid[0] / np.array(N_grid)) ** 2
ax.loglog(N_grid, rif1, "--", color=C_GRIGIO, lw=1, label=r"$\propto1/N$")
ax.loglog(N_grid, rif2, ":", color=C_GRIGIO, lw=1, label=r"$\propto1/N^2$")
ax.set_xlabel("$N$ (passi di Trotter)"); ax.set_ylabel("errore")
ax.set_title(f"Errore a $t={t_fix:.0f}$, matrice e circuito")
ax.legend(fontsize=8)
salva(fig, "fig_trotter_errore")
