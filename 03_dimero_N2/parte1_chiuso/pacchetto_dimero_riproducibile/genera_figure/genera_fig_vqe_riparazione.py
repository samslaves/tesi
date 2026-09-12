"""Genera fig_vqe_riparazione.pdf.
Eseguire dalla RADICE del pacchetto (nessun dato precalcolato richiesto).
Tempo stimato: ~15 secondi (40 ottimizzazioni VQE).

RUOLO NELL'INSIEME DEL PACCHETTO: mancava nella prima versione --
genera_fig_confronto_ansatz.py mostra solo il PMA a K=1 (2 parametri,
a rami), che sotto DM ha un calo di fedeltà reale (minimo ~0.49)
all'anticrossing. Questa figura mostra la "riparazione": l'ansatz esteso
PMA-2q.3 (RBS + due R_y indipendenti, 3 parametri -- ansatz_PMA_2q in
ansatz_dimero.py, la stessa costruzione di pma_2q() in vqe_test2.py, la
scelta finale del progetto) raggiunge la stessa fedeltà di HA (6
parametri) su tutto lo sweep, con la metà dei parametri.
"""
import sys
sys.path.insert(0, "codice")
import numpy as np
from scipy.optimize import minimize
from qiskit.quantum_info import Statevector
from stile import plt, C_BLU, C_ROSSO, salva

from dimer_exact import dimer_hamiltonian, exact_sweep
from ansatz_dimero import ansatz_PMA_2q
from vqe_dimer import vqe_sweep  # per la curva HA di riferimento

J, D = 1.0, 0.2
b_values = np.linspace(0.0, 5.0, 20)

# --- ansatz esteso PMA-2q.3 ---
qc_template = ansatz_PMA_2q(3)


def fidelity_pma3(b, seed):
    H = dimer_hamiltonian(b, J=J, D=D).to_matrix()
    Ev, V = np.linalg.eigh(H)
    psi_exact = V[:, 0]

    def obj(params):
        psi = Statevector(qc_template.assign_parameters(params)).data
        return -abs(np.vdot(psi_exact, psi)) ** 2

    rng = np.random.default_rng(seed)
    best = (0.0, None)
    for _ in range(4):
        x0 = rng.uniform(-np.pi, np.pi, 3)
        res = minimize(obj, x0, method="COBYLA", options=dict(maxiter=400, tol=1e-10))
        if -res.fun > best[0]:
            best = (-res.fun, res.x)
    return best[0]


print("PMA-2q.3 (esteso, 3 parametri), sweep in b/J, D=0.2:")
fid_pma3 = []
for k, b in enumerate(b_values):
    f = fidelity_pma3(b, seed=k)
    fid_pma3.append(f)
print(f"  fedeltà minima sullo sweep: {min(fid_pma3):.6f}  (atteso: vicina a 1, non ~0.49)")
assert min(fid_pma3) > 0.999, "PMA-2q.3 dovrebbe restare vicino a F=1 ovunque"

# --- HA di riferimento (6 parametri), riuso diretto di vqe_sweep ---
print("HA (6 parametri, reps=2), sweep in b/J, D=0.2 -- per confronto:")
res_HA = vqe_sweep(b_values, J=J, D=D, ansatz_type="HA", reps=2, K=1, n_restarts=3, verbose=False)
fid_HA = [r["fidelity"] for r in res_HA]
print(f"  fedeltà minima sullo sweep: {min(fid_HA):.6f}")

fig, ax = plt.subplots(figsize=(6.6, 4.4))
ax.plot(b_values / J, fid_HA, "o-", color=C_BLU, ms=6, label="HA (6 par.)")
ax.plot(b_values / J, fid_pma3, "s--", color=C_ROSSO, ms=6, label="PMA-2q.3 (3 par.)")
ax.axvline(2.0, color="0.6", ls=":", lw=1)
ax.set_xlabel("$B/J$"); ax.set_ylabel(r"fedeltà $|\langle\psi_\mathrm{VQE}|\psi_\mathrm{esatto}\rangle|^2$")
ax.set_title(f"PMA esteso ripara il problema di K=1 (D/J={D})")
ax.legend(fontsize=9.5)
ax.set_ylim(0.95, 1.01)
salva(fig, "fig_vqe_riparazione")
