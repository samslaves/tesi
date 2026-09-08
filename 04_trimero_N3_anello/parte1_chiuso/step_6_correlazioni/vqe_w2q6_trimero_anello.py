"""Ottimizzazione VQE dell'ansatz W-2q.6 (pma_2q_trimer_exact(6, w_block))
per il trimero ad anello con DM (Opzione B), al punto di lavoro confermato
J=1, J'=0.4, b=b_c=2.4, D=0.15.

Fonte dell'ansatz: confronto_ansatz_entangler_trimero_anello.ipynb /
analisi_espressivita_PMA_anello.ipynb (i file vqe_trimer_ring_W.py etc.
citati in trimero_anello_vqe.tex non esistono come file separati: il codice
vive nei notebook). Qui si isola la costruzione in un modulo minimo,
riusabile da circuito_correlazioni_trimero_anello.py.

Metodo a due stadi (stesso schema usato per il dimero, vqe_test2.py):
multistart COBYLA (esplorazione) + polish L-BFGS-B (convergenza a
precisione di macchina), perche' un residuo non trascurabile propagherebbe
errore sistematico nelle correlazioni.
"""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import ParameterVector
from qiskit.quantum_info import Statevector
from scipy.optimize import minimize

from trimer_ring_exact import trimer_hamiltonian_dm


def _ground_state(J, Jp, b, D, mode="B"):
    """Stessa definizione di ground_state in
    circuito_correlazioni_trimero_anello.py (duplicata qui per evitare un
    import circolare: quel modulo importa w2q6_circuit da qui)."""
    H = trimer_hamiltonian_dm(J, Jp, b, mode, D).to_matrix()
    E, V = np.linalg.eigh(H)
    psi0 = V[:, 0]
    imax = np.argmax(np.abs(psi0))
    psi0 = psi0 * np.exp(-1j * np.angle(psi0[imax]))
    return psi0, E

# --- ansatz W-2q.6, mirror del PMA "originale" di Crippa et al. ---------
BOND12, BOND23, BOND31 = (2, 1), (1, 0), (0, 2)
BONDS = [BOND12, BOND23, BOND31]


def w_block(qc, theta, q0, q1):
    sub = QuantumCircuit(2, name="W")
    sub.cx(0, 1); sub.ry(theta, 0); sub.cx(0, 1)
    qc.append(sub.to_gate(label="W"), [q0, q1])


def pma_2q_trimer_exact(nparam, block):
    p = ParameterVector("p", nparam)
    qc = QuantumCircuit(3)
    qc.x(0)
    block(qc, p[0], *BOND12); block(qc, p[1], *BOND23); block(qc, p[2], *BOND31)
    i = 3
    while i < nparam:
        qc.ry(p[i], 0); qc.ry(p[i + 1], 1); qc.ry(p[i + 2], 2)
        i += 3
    return qc


def w2q6_circuit():
    return pma_2q_trimer_exact(6, w_block)


def bound_statevector(params):
    qc = w2q6_circuit().assign_parameters(params)
    return Statevector(qc).data


def main():
    J, Jp, b, D = 1.0, 0.4, 2.4, 0.15
    H = trimer_hamiltonian_dm(J, Jp, b, "B", D).to_matrix()
    psi0_exact, E = _ground_state(J, Jp, b, D)
    E0 = E[0]

    def energy(params):
        psi = bound_statevector(params)
        return np.real(np.vdot(psi, H @ psi))

    rng = np.random.default_rng(0)
    best = None
    N_START = 12
    for k in range(N_START):
        x0 = rng.uniform(-np.pi, np.pi, size=6)
        res = minimize(energy, x0, method="COBYLA",
                        options=dict(maxiter=2000, rhobeg=1.0, tol=1e-10))
        if best is None or res.fun < best.fun:
            best = res
        print(f"  start {k+1}/{N_START}: E={res.fun:.10f}")

    polish = minimize(energy, best.x, method="L-BFGS-B",
                       options=dict(maxiter=5000, ftol=1e-16, gtol=1e-12))
    if polish.fun < best.fun:
        best = polish

    params_opt = best.x
    E_vqe = best.fun
    psi_vqe = bound_statevector(params_opt)
    fidelity = abs(np.vdot(psi0_exact, psi_vqe)) ** 2

    print("\n--- risultato finale ---")
    print(f"E_vqe   = {E_vqe:.14f}")
    print(f"E_exact = {E0:.14f}")
    print(f"delta_E = {abs(E_vqe - E0):.3e}")
    print(f"fidelity = {fidelity:.14f}")
    print(f"parametri ottimali (rad):\n{params_opt.tolist()}")

    np.savez("w2q6_params_optimal.npz", params=params_opt,
             E_vqe=E_vqe, E_exact=E0, fidelity=fidelity)
    print("\nSalvato: w2q6_params_optimal.npz")


if __name__ == "__main__":
    main()