"""Figure del documento 2 — VQE: ansatz generico vs ansatz fisicamente motivato."""
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from qiskit.circuit import QuantumCircuit, ParameterVector
from qiskit.circuit.library import n_local
from qiskit.quantum_info import Statevector, Operator
from stile import *
from dimer_exact import dimer_hamiltonian, exact_sweep

os.makedirs("figure", exist_ok=True)
J = 1.0

from ansatz_dimero import (rbs_block, ansatz_HA, ansatz_PMA_Mcons,
                            ansatz_PMA_2q, ansatz_PMA_W, ansatz_PMA_1q)

# ------------------------------------------------------------------- VQE
def _fidelity_sottospazio(psi, b, D, tol=1e-9):
    """Fidelity rispetto al sottospazio fondamentale: al punto di degenerazione
    (D=0, B/J=2) il fondamentale non e' un singolo vettore, e confrontare con un
    autovettore arbitrario restituito dalla diagonalizzazione sarebbe privo di
    significato."""
    H = dimer_hamiltonian(b, J, D).to_matrix()
    w, v = np.linalg.eigh(H)
    sel = w - w[0] < tol
    return float(np.sqrt(sum(abs(psi.conj() @ v[:, k])**2 for k in np.where(sel)[0])))

def vqe(ansatz, b, D, R=8, seed=7):
    H = dimer_hamiltonian(b, J, D)
    ref = exact_sweep([b], J=J, D=D)
    E0 = float(ref["gs_energy"][0])
    n = ansatz.num_parameters
    rng = np.random.default_rng(seed)
    best = (np.inf, None)
    for _ in range(R):
        x0 = rng.uniform(-np.pi, np.pi, n)
        f = lambda x: float(np.real(Statevector(
            ansatz.assign_parameters(x)).expectation_value(H)))
        r = minimize(f, x0, method="L-BFGS-B", options={"maxiter": 2000, "ftol": 1e-14})
        if r.fun < best[0]:
            best = (r.fun, r.x)
    sv = Statevector(ansatz.assign_parameters(best[1])).data
    return dict(E=best[0], E0=E0, fid=_fidelity_sottospazio(sv, b, D), x=best[1])

B = np.linspace(0.0, 4.0, 33)
modelli = {
    "HA (6 par.)":       (None, C_BLU,   "o", "-"),
    "PMA base (1 par.)": (None, C_ROSSO, "s", "--"),
}
modelli_fix = {
    "PMA base (1 par.)":   (None, C_ROSSO, "s", "--"),
    "PMA esteso (3 par.)": (None, C_VERDE, "D", "-"),
    "HA (6 par.)":         (None, C_BLU,   "o", ":"),
}

def _ansatz(nome, b):
    if nome.startswith("HA"):          return ansatz_HA(2)
    if nome.startswith("PMA base"):    return ansatz_PMA_W(b)
    if nome.startswith("PMA-1q"):      return ansatz_PMA_1q(1)
    if nome.startswith("PMA esteso"):  return ansatz_PMA_2q(3)
    raise KeyError(nome)

def sweep(mods, D):
    return {nome: np.array([vqe(_ansatz(nome, b), b, D)["fid"] for b in B])
            for nome in mods}

fid_D0 = sweep(modelli, 0.0)
fid_D2 = sweep(modelli, 0.2)
fix_D2 = sweep(modelli_fix, 0.2)

# ------------------------------------------------- fig: HA vs PMA, D=0 e D=0.2
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.2, 4.3), sharey=True)
for ax, dati, D in ((a1, fid_D0, 0.0), (a2, fid_D2, 0.2)):
    for nome, (_, col, mk, ls) in modelli.items():
        ax.plot(B, dati[nome], ls, marker=mk, ms=5, color=col, label=nome)
    ax.axhline(1.0, color="0.5", lw=0.8, ls=":")
    ax.axvline(2.0, color="0.55", lw=1.2, ls=":")
    ax.set_xlabel(r"$B/J$")
    ax.set_ylim(0.35, 1.06)
    ax.set_title(rf"$D/J={D}$" + ("  (simmetria intatta)" if D == 0 else "  (simmetria rotta)"))
a1.set_ylabel(r"fidelity  $|\langle\psi_{\rm VQE}|\psi_0\rangle|$")
a1.legend(loc="lower left")
k = np.argmin(fid_D2["PMA base (1 par.)"])
a2.annotate(f"crollo\n{fid_D2['PMA base (1 par.)'][k]:.2f}",
            xy=(B[k], fid_D2["PMA base (1 par.)"][k]), xytext=(2.35, 0.58),
            fontsize=12, color=C_ROSSO,
            arrowprops=dict(arrowstyle="->", color=C_ROSSO, lw=1.2))
salva(fig, "fig03_vqe_ha_vs_pma")

# ------------------------------------------------------- fig: la riparazione
fig, ax = plt.subplots(figsize=(7.4, 4.5))
for nome, (_, col, mk, ls) in modelli_fix.items():
    ax.plot(B, fix_D2[nome], ls, marker=mk, ms=5.5, color=col, label=nome)
ax.axhline(1.0, color="0.5", lw=0.8, ls=":")
ax.axvline(2.0, color="0.55", lw=1.2, ls=":")
ax.set_xlabel(r"$B/J$"); ax.set_ylabel(r"fidelity")
ax.set_ylim(0.63, 1.04)
ax.set_title(r"$D/J=0.2$ — effetto delle rotazioni che rompono $M$")
ax.legend(loc="lower left", ncol=1)
ax.annotate("3 parametri bastano\ndove 1 non basta", xy=(2.28, 0.999),
            xytext=(2.55, 0.775), fontsize=12, color=C_VERDE,
            arrowprops=dict(arrowstyle="->", color=C_VERDE, lw=1.2))
salva(fig, "fig04_vqe_riparazione")

# ------------------------------------------------------------- numeri citati
print("\n--- minimi di fidelity ---")
for nome in modelli:
    print(f"D=0    {nome:22s} min F = {fid_D0[nome].min():.10f}")
for nome in modelli_fix:
    v = fix_D2[nome]
    print(f"D=0.2  {nome:22s} min F = {v.min():.10f}  a B/J={B[np.argmin(v)]:.2f}")
print(f"D=0.2  HA (6 par.)            min F = {fid_D2['HA (6 par.)'].min():.10f}")

print("\n--- tetto strutturale del settore M conservato (B/J=2, D=0.2) ---")
for K in (1, 2, 3, 4):
    r = vqe(ansatz_PMA_Mcons(K), 2.0, 0.2)
    print(f"  K={K} ({K} par.): F = {r['fid']:.6f}   dE = {r['E']-r['E0']:+.6f}")

print("\n--- errore in energia al punto di lavoro test 2 (b/J=0.35, D/J=0.80) ---")
for nome, a in (("HA (6 par.)", ansatz_HA(2)),
                ("PMA base (1 par.)", ansatz_PMA_W(0.35)),
                ("PMA esteso (3 par.)", ansatz_PMA_2q(3))):
    r = vqe(a, 0.35, 0.80)
    print(f"  {nome:22s} E={r['E']:.12f}  E0={r['E0']:.12f}  dE={r['E']-r['E0']:.2e}  F={r['fid']:.12f}")

np.savez("dati_vqe.npz", B=B, **{f"D0_{k}": v for k, v in fid_D0.items()},
         **{f"D2_{k}": v for k, v in fid_D2.items()},
         **{f"FIX_{k}": v for k, v in fix_D2.items()})
