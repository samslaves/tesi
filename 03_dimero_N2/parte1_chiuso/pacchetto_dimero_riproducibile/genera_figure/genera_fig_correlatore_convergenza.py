"""Genera fig_correlatore_convergenza.pdf.
Eseguire dalla RADICE del pacchetto (nessun dato precalcolato richiesto).

RUOLO NELL'INSIEME DEL PACCHETTO: produce la figura che mostra la
convergenza O(1/N) dell'errore di Trotter sul correlatore dinamico
C_21^xx(t), confrontando circuito_correlazioni_dimero.py (via
UnitaryGate + transpilazione) con il riferimento classico esatto
(esponenziale di matrice diretto) -- stessa metodologia di
validate_circuito_correlazioni_dimero.py, qui trasformata in figura.
"""
import sys
sys.path.insert(0, "codice")
import numpy as np
import scipy.linalg as sla
from stile import plt, C_VIOLA, C_GRIGIO, salva
from dimer_exact import dimer_hamiltonian
from circuito_correlazioni_dimero import ground_state, correlator_from_circuit

J, b, D = 1.0, 0.35, 0.80
t = 2.0


def site_op(site, alpha):
    paulis = {
        "x": np.array([[0, 1], [1, 0]], dtype=complex),
        "y": np.array([[0, -1j], [1j, 0]], dtype=complex),
        "z": np.diag([1, -1]).astype(complex),
    }
    I2 = np.eye(2, dtype=complex)
    P = paulis[alpha]
    return np.kron(P, I2) if site == 1 else np.kron(I2, P)


H = dimer_hamiltonian(b=b, J=J, D=D).to_matrix()
psi0, _ = ground_state(b, J, D)
U = sla.expm(-1j * H * t)
V, W = site_op(2, "x"), site_op(1, "x")
c_ref = np.vdot(psi0, U.conj().T @ V @ U @ W @ psi0)

N_grid = [10, 20, 40, 80, 160, 320]
errori = []
for N in N_grid:
    c_circ = correlator_from_circuit(2, "x", 1, "x", t, N, J, b, D, psi0)
    errori.append(abs(c_ref - c_circ))

print(f"{'N':>5} {'errore':>12} {'rapporto':>10}")
prev = None
for N, e in zip(N_grid, errori):
    r = f"{prev/e:.2f}" if prev else "--"
    print(f"{N:>5} {e:>12.4e} {r:>10}")
    prev = e

fig, ax = plt.subplots(figsize=(6.4, 4.4))
ax.loglog(N_grid, errori, "o-", color=C_VIOLA, ms=7)
riferimento = errori[0] * N_grid[0] / np.array(N_grid)
ax.loglog(N_grid, riferimento, "--", color=C_GRIGIO, lw=1.3, label=r"$\propto 1/N$")
ax.set_xlabel(r"$N$ (passi di Trotter)")
ax.set_ylabel(r"$|C_{21}^{xx}(t)_\mathrm{esatto} - C_{21}^{xx}(t)_\mathrm{circuito}|$")
ax.set_title("Convergenza dell'errore di Trotter sul correlatore")
ax.legend(fontsize=9.5)
salva(fig, "fig_correlatore_convergenza")
