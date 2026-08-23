"""Validazione del circuito delle correlazioni per il trimero anello.

Confronto: circuito (Trotter, N passi) vs riferimento classico ESATTO
(scipy.linalg.expm, nessun errore di Trotter), per una selezione di
correlatori rappresentativi al punto di lavoro confermato
J=1, J'=0.4, b=b_c=2.4, D=0.15 (Opzione B).
"""
import numpy as np
import scipy.linalg as sla

from trimer_ring_exact import trimer_hamiltonian_dm
from circuito_correlazioni_trimero_anello import ground_state, correlator_from_circuit

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


def classical_exact(i, alpha, j, beta, t, J, Jp, b, D, psi0, H):
    """<psi0| e^{iHt} A e^{-iHt} B |psi0>, A=sigma_i^alpha, B=sigma_j^beta."""
    A = site_op(i, alpha)
    B = site_op(j, beta)
    Ut = sla.expm(-1j * H * t)
    Bpsi = B @ psi0
    UBpsi = Ut @ Bpsi
    AUBpsi = A @ UBpsi
    UdagAUBpsi = Ut.conj().T @ AUBpsi
    return np.vdot(psi0, UdagAUBpsi)


def main():
    J, Jp, b, D = 1.0, 0.4, 2.4, 0.15
    H = trimer_hamiltonian_dm(J, Jp, b, "B", D).to_matrix()
    psi0, E = np.linalg.eigh(H)[1][:, 0], None
    psi0, E = ground_state(J, Jp, b, D)
    gap = np.sort(np.linalg.eigvalsh(H))
    print(f"Punto di lavoro: J={J}, J'={Jp}, b={b}, D={D} (Opzione B)")
    print(f"E0={np.linalg.eigvalsh(H)[0]:.6f}, gap E1-E0={gap[1]-gap[0]:.6f}")
    print()

    # correlatori rappresentativi: due ricchi (C_11^yy, C_33^yy), uno medio
    # (C_13^zy), uno predetto strutturalmente zero per ogni t (C_33^xz),
    # e la coppia C_12^yy / C_21^yy per verificare la relazione di simmetria
    # U (eta_y*eta_y = +1 => devono coincidere).
    cases = [
        (1, 'y', 1, 'y'),
        (3, 'y', 3, 'y'),
        (1, 'y', 3, 'y'),
        (3, 'x', 3, 'z'),   # atteso ~0 per ogni t (Corollario zero-sito3)
        (1, 'y', 2, 'y'),
        (2, 'y', 1, 'y'),   # deve coincidere con la precedente (eta_y eta_y=+1)
    ]

    t_values = [0.5, 1.3, 2.7]
    N = 200

    print(f"{'correlatore':<14}{'t':>6}   {'esatto classico':>22}   "
          f"{'circuito (N=200)':>22}   {'|residuo|':>12}")
    for (i, al, j, be) in cases:
        for t in t_values:
            c_ref = classical_exact(i, al, j, be, t, J, Jp, b, D, psi0, H)
            c_circ = correlator_from_circuit(i, al, j, be, t, N, J, Jp, b, D, psi0)
            resid = abs(c_ref - c_circ)
            label = f"C_{i}{j}^{al}{be}"
            print(f"{label:<14}{t:>6.2f}   {c_ref.real:+.4f}{c_ref.imag:+.4f}i"
                  f"      {c_circ.real:+.4f}{c_circ.imag:+.4f}i        {resid:.2e}")
        print()

    print("=" * 70)
    print("Convergenza in N (Trotter) su un caso singolo: C_11^yy(t=1.3)")
    c_ref = classical_exact(1, 'y', 1, 'y', 1.3, J, Jp, b, D, psi0, H)
    prev = None
    for N in [10, 20, 40, 80, 160, 320]:
        c_circ = correlator_from_circuit(1, 'y', 1, 'y', 1.3, N, J, Jp, b, D, psi0)
        err = abs(c_ref - c_circ)
        ratio = f"  (rapporto vs precedente: {prev/err:.2f})" if prev else ""
        print(f"  N={N:4d}: |errore| = {err:.3e}{ratio}")
        prev = err
    print("atteso: errore ~ O(1/N) (Trotter 1o ordine su ampiezza), rapporto ~2 raddoppiando N")


if __name__ == "__main__":
    main()