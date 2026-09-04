"""
Validazione di circuito_correlazioni_dimero.py contro il riferimento
classico esatto (formula spettrale, stessa convenzione -- coniugato
incluso, vedi log_decisioni.md per il bug gia' trovato e corretto).
"""
import numpy as np
import scipy.linalg as sla
from qiskit.quantum_info import SparsePauliOp

from dimer_exact import dimer_hamiltonian
from circuito_correlazioni_dimero import ground_state, correlator_from_circuit

J, b, D = 1.0, 0.35, 0.80  # punto test2


def site_op(site, alpha):
    paulis = {
        "x": np.array([[0, 1], [1, 0]], dtype=complex),
        "y": np.array([[0, -1j], [1j, 0]], dtype=complex),
        "z": np.diag([1, -1]).astype(complex),
    }
    I2 = np.eye(2, dtype=complex)
    P = paulis[alpha]
    return np.kron(P, I2) if site == 1 else np.kron(I2, P)


def classical_exact(i, alpha, j, beta, t, J, b, D, psi0, H):
    """Riferimento esatto via expm diretto (nessun errore di Trotter),
    formula <psi0| U^dag V U W |psi0> -- non la formula spettrale, per
    avere un secondo metodo indipendente di calcolo."""
    U = sla.expm(-1j * H * t)
    V = site_op(i, alpha)
    W = site_op(j, beta)
    return np.vdot(psi0, U.conj().T @ V @ U @ W @ psi0)


def main():
    H = dimer_hamiltonian(b=b, J=J, D=D).to_matrix()
    psi0, E = ground_state(b, J, D)

    cases = [
        (2, "x", 1, "x"),   # indicato dal relatore
        (2, "x", 1, "y"),   # migliore per a2/a1
        (1, "z", 1, "z"),   # "piatto" zz
        (1, "x", 1, "y"),
        (1, "y", 1, "x"),   # deve coincidere col precedente (eta_x eta_y=+1)
        (1, "z", 2, "y"),   # atteso ~0 a t=0 (una sola componente y, siti diversi)
    ]
    t_values = [0.5, 2.0, 5.0]
    N = 200

    print(f"{'correlatore':<14}{'t':>6}   {'esatto (expm)':>22}   "
          f"{'circuito (N=200)':>22}   {'|residuo|':>12}")
    for (i, al, j, be) in cases:
        for t in t_values:
            c_ref = classical_exact(i, al, j, be, t, J, b, D, psi0, H)
            c_circ = correlator_from_circuit(i, al, j, be, t, N, J, b, D, psi0)
            resid = abs(c_ref - c_circ)
            label = f"C_{i}{j}^{al}{be}"
            print(f"{label:<14}{t:>6.2f}   {c_ref.real:+.4f}{c_ref.imag:+.4f}i"
                  f"      {c_circ.real:+.4f}{c_circ.imag:+.4f}i        {resid:.2e}")
        print()

    print("=" * 70)
    print("Zero atteso a t=0 (siti diversi, una sola componente y):")
    for (i, al, j, be) in [(1, "z", 2, "y"), (2, "x", 1, "y")]:
        c_ref = classical_exact(i, al, j, be, 0.0, J, b, D, psi0, H)
        c_circ = correlator_from_circuit(i, al, j, be, 0.0, N, J, b, D, psi0)
        label = f"C_{i}{j}^{al}{be}(0)"
        print(f"  {label:<16} esatto={abs(c_ref):.2e}   circuito={abs(c_circ):.2e}")

    print()
    print("Convergenza in N (Trotter) su C_2,1^xx(t=2.0):")
    c_ref = classical_exact(2, "x", 1, "x", 2.0, J, b, D, psi0, H)
    prev = None
    for N_ in [10, 20, 40, 80, 160, 320]:
        c_circ = correlator_from_circuit(2, "x", 1, "x", 2.0, N_, J, b, D, psi0)
        err = abs(c_ref - c_circ)
        ratio = f"  (rapporto vs precedente: {prev / err:.2f})" if prev else ""
        print(f"  N={N_:4d}: |errore| = {err:.3e}{ratio}")
        prev = err
    print("atteso: errore ~ O(1/N) (Trotter 1o ordine), rapporto ~2 raddoppiando N")


if __name__ == "__main__":
    main()
