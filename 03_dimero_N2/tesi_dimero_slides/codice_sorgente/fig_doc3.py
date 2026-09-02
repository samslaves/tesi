"""Figure del documento 3 — simulazione quantistica: evoluzione temporale via Trotter."""
import os
import numpy as np
import scipy.linalg as sla
import matplotlib.pyplot as plt
from qiskit.quantum_info import Statevector
from stile import *
from trotter_dimero import H_parts, trotter_circuit, U_exact, U_trotter_mat, sz, PSI0, SZ_TOT

os.makedirs("figure", exist_ok=True)

# punto di lavoro R1: dinamica non monocromatica (piu' righe spettrali visibili)
b, J, D = -0.18, 1.0, 1.0

# ------------------------------------------------------- Sz(t): esatto vs Trotter
ts = np.linspace(0.0, 12.0, 241)
sz_exact = np.array([sz(U_exact(b, J, D, t) @ PSI0) for t in ts])

Ns = [2, 5, 20]
sz_trot = {}
for N in Ns:
    sz_trot[N] = np.array([sz(U_trotter_mat(b, J, D, t, N) @ PSI0) for t in ts])

# controllo indipendente: il circuito Qiskit riproduce la matrice di Trotter
tc = 6.0
psi_circ = Statevector(trotter_circuit(b, J, D, tc, 20)).data
psi_mat = U_trotter_mat(b, J, D, tc, 20) @ PSI0
scarto = np.max(np.abs(np.abs(psi_circ) - np.abs(psi_mat)))
print(f"[check] circuito Qiskit vs matrice di Trotter, t={tc}, N=20: "
      f"max scarto sui moduli = {scarto:.2e}")
print(f"[check] <Sz> circuito = {sz(psi_circ):+.9f}   matrice = {sz(psi_mat):+.9f}")

fig, ax = plt.subplots(figsize=(8.0, 4.6))
ax.plot(ts, sz_exact, color=C_NERO, lw=3.6, label="esatta", zorder=4)
for N, col, ls, lw, z in zip(Ns, (C_ROSSO, C_ARANC, C_VERDE),
                             ("--", "-.", (0, (4, 3))), (1.9, 1.9, 1.7), (3, 3, 6)):
    ax.plot(ts, sz_trot[N], ls=ls, color=col, lw=lw, zorder=z, label=f"Trotter, $N={N}$")
ax.set_xlabel(r"$t$  (unità di $1/J$)")
ax.set_ylabel(r"$\langle S_z^{\rm tot}\rangle(t)$")
ax.set_title(r"Magnetizzazione nel tempo, stato iniziale $|{\uparrow\uparrow}\rangle$")
ax.set_xlim(0, 12)
ax.set_ylim(0.02, 1.62)
ax.legend(loc="upper center", ncol=2)
ax.annotate("a $N=20$ la curva\nsi sovrappone all'esatta", xy=(3.35, 0.50),
            xytext=(0.35, 1.16), fontsize=12, color=C_VERDE,
            arrowprops=dict(arrowstyle="->", color=C_VERDE, lw=1.1))
salva(fig, "fig05_trotter_sz")

# ------------------------------------------------------- errore vs numero di passi
t_fix = 6.0
Nlist = np.array([1, 2, 4, 8, 16, 32, 64, 128, 256, 512])
Uex = U_exact(b, J, D, t_fix)
psi_ex = Uex @ PSI0
err_op, err_fid, err_sz = [], [], []
for N in Nlist:
    Ut = U_trotter_mat(b, J, D, t_fix, N)
    psi = Ut @ PSI0
    err_op.append(np.linalg.norm(Ut - Uex, 2))
    err_fid.append(1.0 - abs(np.vdot(psi_ex, psi))**2)
    err_sz.append(abs(sz(psi) - sz(psi_ex)))
err_op, err_fid, err_sz = map(np.array, (err_op, err_fid, err_sz))

fig, ax = plt.subplots(figsize=(7.4, 4.6))
ax.loglog(Nlist, err_op, "o-", color=C_BLU, ms=6, label=r"$\|U_{\rm Trotter}-U_{\rm esatto}\|$")
ax.loglog(Nlist, err_fid, "s-", color=C_ROSSO, ms=6, label=r"$1-\mathcal{F}$")
ref1 = err_op[0] * (Nlist[0] / Nlist)
ref2 = err_fid[0] * (Nlist[0] / Nlist) ** 2
ax.loglog(Nlist, ref1, ":", color=C_BLU, lw=1.4)
ax.loglog(Nlist, ref2, ":", color=C_ROSSO, lw=1.4)
ax.set_xlabel(r"numero di passi $N$")
ax.set_ylabel("errore")
ax.set_title(rf"Convergenza a $t={t_fix:.0f}$")
ax.legend(loc="lower left")
ax.annotate(r"pendenza $-1$", xy=(180, 5.5e-3), xytext=(60, 2.0e-1),
            color=C_BLU, fontsize=12,
            arrowprops=dict(arrowstyle="->", color=C_BLU, lw=1.1))
ax.annotate(r"pendenza $-2$", xy=(70, 8.0e-5), xytext=(26, 4.0e-6),
            color=C_ROSSO, fontsize=12,
            arrowprops=dict(arrowstyle="->", color=C_ROSSO, lw=1.1))
ax.set_ylim(6e-7, 5)
salva(fig, "fig06_trotter_errore")

print("\n--- errore di Trotter a t = 6 ---")
for N, eo, ef, es in zip(Nlist, err_op, err_fid, err_sz):
    print(f"  N={N:4d}   ||dU||={eo:.3e}   1-F={ef:.3e}   |d<Sz>|={es:.3e}")
p_op = np.polyfit(np.log(Nlist[3:]), np.log(err_op[3:]), 1)[0]
p_fid = np.polyfit(np.log(Nlist[3:]), np.log(err_fid[3:]), 1)[0]
print(f"  pendenza misurata (N>=8):  ||dU|| -> {p_op:.3f}   1-F -> {p_fid:.3f}")

# --------------------------------------------------- costo in gate (transpilazione)
from qiskit import transpile
qc = trotter_circuit(b, J, D, 1.0, 1)
for lev in (0, 3):
    tq = transpile(qc, basis_gates=["cx", "rz", "sx", "x"], optimization_level=lev)
    print(f"  passo singolo, optimization_level={lev}: "
          f"CNOT = {tq.count_ops().get('cx', 0)}, profondità = {tq.depth()}")
