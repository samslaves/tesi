"""Figure del documento 3 (trimero ad anello) — dinamica via Suzuki-Trotter."""
import os
import numpy as np
import scipy.linalg as sla
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, Operator
from stile import *
from trotter_trimero_anello import (trotter_circuit, step_Hex, step_field, step_HDM,
                                     H_parts, U_exact, sz_tot, PSI0, SZ_TOT)

os.makedirs("figure", exist_ok=True)

J, Jp, b, D = 1.0, 0.4, 0.05, 1.93

def single_step_matrix(tau):
    """Operatore Qiskit del singolo passo esterno (Hex-campo-HDM), fedele
    esattamente al circuito reale -- niente riderivazioni a mano."""
    qc = QuantumCircuit(3)
    step_Hex(qc, J, Jp, tau)
    step_field(qc, b, tau)
    step_HDM(qc, J, Jp, D, tau)
    return Operator(qc).data

def U_trotter_mat(t, N):
    """U^N del singolo passo, via potenza di matrice (veloce ed esatto,
    stesso operatore che il circuito applicherebbe N volte)."""
    tau = t / N
    U1 = single_step_matrix(tau)
    return np.linalg.matrix_power(U1, N)

# ------------------------------------------------------- Sz(t): esatto vs Trotter
ts = np.linspace(0.0, 12.0, 121)
psi0 = PSI0.data

def evolve_exact(t):
    return U_exact(J, Jp, b, D, t) @ psi0

sz_exact = np.array([sz_tot(evolve_exact(t)) for t in ts])

Ns = [50, 150, 500]
sz_trot = {N: np.array([sz_tot(U_trotter_mat(t, N) @ psi0) for t in ts]) for N in Ns}

# controllo indipendente: circuito Qiskit riproduce la matrice compatta
tc, Nc = 6.0, 60
psi_circ = Statevector(trotter_circuit(J, Jp, b, D, tc, Nc)).data
psi_mat = U_trotter_mat(tc, Nc) @ psi0
scarto = np.max(np.abs(psi_circ - psi_mat))
print(f"[check] circuito Qiskit vs matrice compatta, t={tc}, N={Nc}: "
      f"max scarto (ampiezze complesse) = {scarto:.2e}")

fig, ax = plt.subplots(figsize=(8.0, 4.6))
ax.plot(ts, sz_exact, color=C_NERO, lw=3.4, label="esatta", zorder=4)
for N, col, ls in zip(Ns, (C_ROSSO, C_ARANC, C_VERDE), ("--", "-.", (0,(4,3)))):
    ax.plot(ts, sz_trot[N], ls=ls, color=col, lw=1.9, label=f"Trotter, $N={N}$")
ax.set_xlabel(r"$t$  (unità di $1/J$)")
ax.set_ylabel(r"$\langle S_z^{\rm tot}\rangle(t)$")
ax.set_title(r"Magnetizzazione nel tempo, stato iniziale $|000\rangle$ (punto $R_0$)")
ax.set_xlim(0, 12)
ax.legend(loc="upper right", ncol=1, fontsize=10.5)
salva(fig, "fig05_trotter_sz_anello")

# ------------------------------------------------------- errore vs numero di passi
t_fix = 6.0
Nlist = np.array([10, 30, 100, 300, 1000, 3000])
Uex = U_exact(J, Jp, b, D, t_fix)
psi_ex = Uex @ psi0
err_op, err_fid = [], []
for N in Nlist:
    Ut = U_trotter_mat(t_fix, N)
    psi = Ut @ psi0
    err_op.append(np.linalg.norm(Ut - Uex, 2))
    err_fid.append(1.0 - abs(np.vdot(psi_ex, psi))**2)
err_op, err_fid = map(np.array, (err_op, err_fid))

fig, ax = plt.subplots(figsize=(7.4, 4.6))
ax.loglog(Nlist, err_op, "o-", color=C_BLU, ms=6, label=r"$\|U_{\rm Trotter}-U_{\rm esatto}\|$")
ax.loglog(Nlist, err_fid, "s-", color=C_ROSSO, ms=6, label=r"$1-\mathcal{F}$")
ref1 = err_op[0] * (Nlist[0]/Nlist)
ref2 = err_fid[0] * (Nlist[0]/Nlist)**2
ax.loglog(Nlist, ref1, ":", color=C_BLU, lw=1.4)
ax.loglog(Nlist, ref2, ":", color=C_ROSSO, lw=1.4)
ax.set_xlabel(r"numero di passi $N$")
ax.set_ylabel("errore")
ax.set_title(rf"Convergenza a $t={t_fix:.0f}$ (punto $R_0$)")
ax.legend(loc="lower left")
salva(fig, "fig06_trotter_errore_anello")

print("\n--- errore di Trotter a t=6 (punto R0) ---")
for N, eo, ef in zip(Nlist, err_op, err_fid):
    print(f"  N={N:5d}   ||dU||={eo:.3e}   1-F={ef:.3e}")
p_op = np.polyfit(np.log(Nlist), np.log(err_op), 1)[0]
p_fid = np.polyfit(np.log(Nlist), np.log(err_fid), 1)[0]
print(f"  pendenza misurata:  ||dU|| -> {p_op:.3f}   1-F -> {p_fid:.3f}")

for soglia in [1e-2, 1e-3, 1e-4]:
    idx = np.where(err_fid < soglia)[0]
    if len(idx):
        print(f"  1-F < {soglia}: gia' a N={Nlist[idx[0]]}")

from qiskit import transpile
qc1 = trotter_circuit(J, Jp, b, D, 1.0, 1)
print("\n--- costo in gate per passo esterno ---")
for lev in (0, 3):
    tq = transpile(qc1, basis_gates=["cx","rz","sx","x"], optimization_level=lev)
    print(f"  optimization_level={lev}: CNOT={tq.count_ops().get('cx',0)}, "
          f"profondita={tq.depth()}, ops={dict(tq.count_ops())}")
