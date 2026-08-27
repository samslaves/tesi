"""Ottimizzazione VQE dell'ansatz W-2qC.K2 (pma_2q_trimer_cyclic(2, w_block))
per il trimero a catena aperta con DM, mirror diretto di
vqe_w2q6_trimero_anello.py per la topologia a catena (2 bond).

Ottimizza su ENTRAMBI i punti di lavoro attualmente in uso nel progetto,
per confronto diretto nella fase circuito-correlazioni:
  - VQE-DM: J=1, b=b_c=3.0, D=0.15 (trimero_catena_vqe_dm.tex, dove
    W-2qC.K2 e' gia' identificato come canonico, F=1 esatto a 60+ restart)
  - S0 (Trotter): J=1, b=3.0073414, D=0.3 (trotter_trimero_catena.py,
    punto provvisorio della fase Trotter gia' chiusa)

Il punto b_c=3.0 e' l'incrocio esatto B'->A' (Sez. Oss.1 di
simmetrie_correlatori_trimero_catena.tex): a D=0 sarebbe degenere, ma con
D=0.15 il gap e' aperto (g_min=2*sqrt(6)*D, verificato), quindi il
fondamentale e' non degenere ma vicino a un level crossing -- da qui la
cautela sui restart gia' documentata in trimero_catena_vqe_dm.tex (60+
restart necessari per distinguere un vero ceiling strutturale da un
artefatto di pochi restart). Usiamo lo stesso numero di restart qui.

Metodo a due stadi (stesso schema del dimero e dell'anello): multistart
COBYLA (esplorazione) + polish L-BFGS-B (convergenza a precisione di
macchina).

Dipende da trimer_chain_exact.py e ansatz_catena.py (BONDS a 2 legami,
nessun bond31 -- non esiste nella catena).
"""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import ParameterVector
from qiskit.quantum_info import Statevector
from scipy.optimize import minimize

from trimer_chain_exact import trimer_hamiltonian_dm

# --- ansatz W-2qC.K2, identico a ansatz_catena.pma_2q_trimer_cyclic(2, w_block) ---
# Ridefinito qui (non importato) per rendere questo modulo autosufficiente,
# stessa scelta fatta per il mirror dell'anello.
BOND12, BOND23 = (2, 1), (1, 0)   # nessun BOND31: non esiste nella catena
BONDS = [BOND12, BOND23]


def w_block(qc, theta, q0, q1):
    sub = QuantumCircuit(2, name="W")
    sub.cx(0, 1); sub.ry(theta, 0); sub.cx(0, 1)
    qc.append(sub.to_gate(label="W"), [q0, q1])


def pma_2q_trimer_cyclic(K, block=w_block):
    """K cicli di [blocchi sui 2 legami, Ry indipendenti sui 3 qubit]. 5K parametri."""
    nparam = 5 * K
    p = ParameterVector("p", nparam)
    qc = QuantumCircuit(3)
    qc.x(0)
    idx = 0
    for _ in range(K):
        block(qc, p[idx], *BOND12); idx += 1
        block(qc, p[idx], *BOND23); idx += 1
        qc.ry(p[idx], 0); idx += 1
        qc.ry(p[idx], 1); idx += 1
        qc.ry(p[idx], 2); idx += 1
    return qc


def w2qC_k2_circuit():
    return pma_2q_trimer_cyclic(2, w_block)


def bound_statevector(params):
    qc = w2qC_k2_circuit().assign_parameters(params)
    return Statevector(qc).data


def _ground_state(J, b, D):
    """Stessa definizione usata in circuito_correlazioni_trimero_catena.py
    (duplicata qui per evitare import circolare, stessa scelta del mirror
    dell'anello)."""
    H = trimer_hamiltonian_dm(J, b, D).to_matrix()
    E, V = np.linalg.eigh(H)
    psi0 = V[:, 0]
    imax = np.argmax(np.abs(psi0))
    psi0 = psi0 * np.exp(-1j * np.angle(psi0[imax]))
    return psi0, E


def optimize_point(J, b, D, n_restarts=60, seed=0, label=""):
    H = trimer_hamiltonian_dm(J, b, D).to_matrix()
    psi0_exact, E = _ground_state(J, b, D)
    E0 = E[0]
    gap = E[1] - E[0]

    def energy(params):
        psi = bound_statevector(params)
        return np.real(np.vdot(psi, H @ psi))

    rng = np.random.default_rng(seed)
    best = None
    for k in range(n_restarts):
        x0 = rng.uniform(-np.pi, np.pi, size=10)
        res = minimize(energy, x0, method="COBYLA",
                        options=dict(maxiter=2000, rhobeg=1.0, tol=1e-10))
        if best is None or res.fun < best.fun:
            best = res

    polish = minimize(energy, best.x, method="L-BFGS-B",
                       options=dict(maxiter=5000, ftol=1e-16, gtol=1e-12))
    if polish.fun < best.fun:
        best = polish

    params_opt = best.x
    E_vqe = best.fun
    psi_vqe = bound_statevector(params_opt)
    fidelity = abs(np.vdot(psi0_exact, psi_vqe)) ** 2

    print(f"--- {label}: J={J}, b={b}, D={D} (gap={gap:.4f}, {n_restarts} restart) ---")
    print(f"E_vqe    = {E_vqe:.14f}")
    print(f"E_exact  = {E0:.14f}")
    print(f"delta_E  = {abs(E_vqe - E0):.3e}")
    print(f"fidelity = {fidelity:.14f}")

    return dict(J=J, b=b, D=D, params=params_opt, E_vqe=E_vqe, E_exact=E0,
                fidelity=fidelity, gap=gap)


def main():
    points = [
        dict(J=1.0, b=3.0, D=0.15, label="VQE-DM (b_c)", seed=0,
             outfile="w2qC_k2_params_vqedm.npz"),
        dict(J=1.0, b=3.0073414, D=0.3, label="S0 (Trotter)", seed=1,
             outfile="w2qC_k2_params_S0.npz"),
    ]
    results = {}
    for p in points:
        r = optimize_point(p["J"], p["b"], p["D"], n_restarts=60,
                            seed=p["seed"], label=p["label"])
        np.savez(p["outfile"], params=r["params"], E_vqe=r["E_vqe"],
                  E_exact=r["E_exact"], fidelity=r["fidelity"],
                  J=r["J"], b=r["b"], D=r["D"])
        print(f"Salvato: {p['outfile']}\n")
        results[p["label"]] = r
    return results


if __name__ == "__main__":
    main()
