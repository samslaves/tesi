"""Validazione del circuito delle correlazioni per il trimero a catena
aperta. Mirror di validate_circuito_correlazioni.py (anello).

Confronto: circuito (Trotter, N passi) vs riferimento classico ESATTO
(scipy.linalg.expm, nessun errore di Trotter), su ENTRAMBI i punti di
lavoro attualmente in uso nel progetto:
  - VQE-DM: J=1, b=b_c=3.0, D=0.15
  - S0 (Trotter): J=1, b=3.0073414, D=0.3

Casi scelti sulla base delle predizioni di simmetrie_correlatori_trimero_catena.tex:
  - C_11^xx / C_33^xx: devono COINCIDERE per ogni t (Cor. P13-relazioni)
  - C_22^xx: ricco, nessun vincolo di simmetria (sito fisso non protetto)
  - C_11^xz(0): deve essere ESATTAMENTE zero (Cor. zero-t0-same)
  - C_12^yz(0): deve essere ESATTAMENTE zero (Cor. zero-t0-diff, una y)
"""
import numpy as np
import scipy.linalg as sla

from trimer_chain_exact import trimer_hamiltonian_dm
from circuito_correlazioni_trimero_catena import ground_state, correlator_from_circuit

I2 = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)
PAULI = {'x': X, 'y': Y, 'z': Z}


def kron3(A, B, C):
    return np.kron(np.kron(A, B), C)


def site_op(site, alpha):
    ops = [I2, I2, I2]
    ops[site - 1] = PAULI[alpha]
    return kron3(*ops)


def classical_exact(i, alpha, j, beta, t, J, b, D, psi0, H):
    A = site_op(i, alpha)
    B = site_op(j, beta)
    Ut = sla.expm(-1j * H * t)
    return np.vdot(psi0, Ut.conj().T @ A @ Ut @ B @ psi0)


def run_point(J, b, D, label):
    H = trimer_hamiltonian_dm(J, b, D).to_matrix()
    psi0, E = ground_state(J, b, D)
    gap = np.sort(np.linalg.eigvalsh(H))
    print("=" * 78)
    print(f"Punto: {label}  (J={J}, b={b}, D={D})")
    print(f"E0={gap[0]:.6f}, gap E1-E0={gap[1]-gap[0]:.6f}")
    print()

    cases_t = [(1, 'x', 1, 'x'), (3, 'x', 3, 'x'), (2, 'x', 2, 'x'),
               (1, 'y', 1, 'y'), (3, 'y', 3, 'y')]
    cases_t0 = [(1, 'x', 1, 'z'), (1, 'z', 1, 'x'), (2, 'x', 2, 'z'),
                (1, 'y', 2, 'z'), (2, 'y', 1, 'z')]

    t_values = [0.5, 1.3, 2.7]
    N = 200

    print(f"{'correlatore':<14}{'t':>6}   {'esatto classico':>22}   "
          f"{'circuito (N=200)':>22}   {'|residuo|':>12}")
    for (i, al, j, be) in cases_t:
        for t in t_values:
            c_ref = classical_exact(i, al, j, be, t, J, b, D, psi0, H)
            c_circ = correlator_from_circuit(i, al, j, be, t, N, J, b, D, psi0)
            resid = abs(c_ref - c_circ)
            label2 = f"C_{i}{j}^{al}{be}"
            print(f"{label2:<14}{t:>6.2f}   {c_ref.real:+.4f}{c_ref.imag:+.4f}i"
                  f"      {c_circ.real:+.4f}{c_circ.imag:+.4f}i        {resid:.2e}")
        print()

    print("Zeri predetti a t=0 (Cor. zero-t0-same / zero-t0-diff):")
    for (i, al, j, be) in cases_t0:
        c_ref = classical_exact(i, al, j, be, 0.0, J, b, D, psi0, H)
        c_circ = correlator_from_circuit(i, al, j, be, 0.0, N, J, b, D, psi0)
        label2 = f"C_{i}{j}^{al}{be}(0)"
        print(f"  {label2:<16} esatto={abs(c_ref):.2e}   circuito={abs(c_circ):.2e}")

    print()
    print("Relazione P13: C_11^xx(t) == C_33^xx(t) via circuito?")
    for t in [0.5, 1.3, 2.7]:
        c11 = correlator_from_circuit(1, 'x', 1, 'x', t, N, J, b, D, psi0)
        c33 = correlator_from_circuit(3, 'x', 3, 'x', t, N, J, b, D, psi0)
        print(f"  t={t}: |C11-C33| = {abs(c11-c33):.2e}")

    print()
    print("Convergenza in N (Trotter) su C_11^xx(t=1.3):")
    c_ref = classical_exact(1, 'x', 1, 'x', 1.3, J, b, D, psi0, H)
    prev = None
    for N_ in [10, 20, 40, 80, 160, 320]:
        c_circ = correlator_from_circuit(1, 'x', 1, 'x', 1.3, N_, J, b, D, psi0)
        err = abs(c_ref - c_circ)
        ratio = f"  (rapporto vs precedente: {prev/err:.2f})" if prev else ""
        print(f"  N={N_:4d}: |errore| = {err:.3e}{ratio}")
        prev = err
    print()


def main():
    run_point(1.0, 3.0, 0.15, "VQE-DM (b_c)")
    run_point(1.0, 3.0073414, 0.3, "S0 (Trotter)")


if __name__ == "__main__":
    main()
