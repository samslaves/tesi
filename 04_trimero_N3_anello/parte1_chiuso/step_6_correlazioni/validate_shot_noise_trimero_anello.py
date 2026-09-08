"""Validazione a shot finiti del circuito delle correlazioni, trimero anello.

Mirror per N=3 di circuito_correlazioni_tutte.ipynb (dimero): confronta la
stima da conteggi (AerSimulator, shots finiti, rumore statistico incluso)
contro (a) il valore esatto classico e (b) la stima da statevector con lo
stesso N di Trotter (nessun rumore di shot) -- per separare i due
contributi di errore, algoritmico (Trotter) e statistico (campionamento),
esattamente come gia' fatto per il dimero.
"""
import numpy as np
from qiskit import transpile
from qiskit_aer import AerSimulator

from circuito_correlazioni_trimero_anello import (
    ground_state, build_correlator_circuit, correlator_from_circuit,
)
from validate_circuito_correlazioni import classical_exact
from trimer_ring_exact import trimer_hamiltonian_dm

J, Jp, b, D = 1.0, 0.4, 2.4, 0.15
H = trimer_hamiltonian_dm(J, Jp, b, "B", D).to_matrix()
psi0, _ = ground_state(J, Jp, b, D)
BACKEND = AerSimulator()

_TRANSPILE_CACHE = {}


def _transpiled(i, alpha, j, beta, t, N, part):
    key = (i, alpha, j, beta, t, N, part)
    if key not in _TRANSPILE_CACHE:
        qc = build_correlator_circuit(i, alpha, j, beta, t, N, J, Jp, b, D, part,
                                       psi0=psi0, measure=True)
        _TRANSPILE_CACHE[key] = transpile(qc, BACKEND)
    return _TRANSPILE_CACHE[key]


def shot_estimate(i, alpha, j, beta, t, N, shots, part, seed=None):
    """<sigma_z> sull'ancilla da conteggi finiti (rumore statistico incluso)."""
    qc_t = _transpiled(i, alpha, j, beta, t, N, part)
    result = BACKEND.run(qc_t, shots=shots, seed_simulator=seed).result()
    counts = result.get_counts()
    n0 = counts.get('0', 0)
    n1 = counts.get('1', 0)
    return (n0 - n1) / shots


def correlator_shots(i, alpha, j, beta, t, N, shots, seed=None):
    re = shot_estimate(i, alpha, j, beta, t, N, shots, 're', seed=seed)
    im = shot_estimate(i, alpha, j, beta, t, N, shots, 'im',
                        seed=None if seed is None else seed + 1)
    return re + 1j * im


def main():
    N = 200
    shots = 8192
    print(f"Punto di lavoro: J={J}, J'={Jp}, b={b}, D={D} (Opzione B)")
    print(f"N (Trotter) = {N}, shots = {shots}\n")

    cases = [
        (1, 'y', 1, 'y', 1.3),
        (3, 'x', 3, 'z', 2.7),   # atteso ~0 per ogni t
        (1, 'y', 2, 'y', 2.7),
    ]

    print(f"{'correlatore':<12}{'t':>5}   {'esatto classico':>20}   "
          f"{'statevector (N=200)':>22}   {'shots (N=200, 8192)':>22}")
    for (i, al, j, be, t) in cases:
        c_ref = classical_exact(i, al, j, be, t, J, Jp, b, D, psi0, H)
        c_sv = correlator_from_circuit(i, al, j, be, t, N, J, Jp, b, D, psi0)
        c_sh = correlator_shots(i, al, j, be, t, N, shots, seed=42)
        label = f"C_{i}{j}^{al}{be}"
        print(f"{label:<12}{t:>5.1f}   {c_ref.real:+.4f}{c_ref.imag:+.4f}i"
              f"        {c_sv.real:+.4f}{c_sv.imag:+.4f}i"
              f"          {c_sh.real:+.4f}{c_sh.imag:+.4f}i")

    print()
    print("=" * 78)
    print("Separazione dei due contributi di errore (Trotter vs statistico)")
    print("=" * 78)
    i, al, j, be, t = 1, 'y', 1, 'y', 1.3
    c_ref = classical_exact(i, al, j, be, t, J, Jp, b, D, psi0, H)
    c_sv = correlator_from_circuit(i, al, j, be, t, N, J, Jp, b, D, psi0)
    err_trotter = abs(c_sv - c_ref)
    print(f"Errore di Trotter (statevector vs esatto), N={N}: {err_trotter:.2e}")
    print(f"Soglia statistica attesa nel caso peggiore, 1/sqrt({shots}): "
          f"{1/np.sqrt(shots):.4f}")
    print(f"Rapporto (statistico/Trotter): {(1/np.sqrt(shots))/err_trotter:.1f}x")

    print()
    print("=" * 78)
    print("Convergenza vs N_shots (media e dev.std su ripetizioni indipendenti)")
    print("=" * 78)
    shots_list = [256, 512, 1024, 2048, 4096, 8192, 16384]
    n_rep = 40
    i, al, j, be, t = 1, 'y', 1, 'y', 1.3
    c_ref_re = classical_exact(i, al, j, be, t, J, Jp, b, D, psi0, H).real
    results = {}
    for s in shots_list:
        vals = np.array([shot_estimate(i, al, j, be, t, N, s, 're', seed=1000 * s + r)
                          for r in range(n_rep)])
        results[s] = vals
        print(f"  shots={s:6d}: media={vals.mean():+.4f}  "
              f"dev.std={vals.std():.4f}  atteso~1/sqrt(shots)={1/np.sqrt(s):.4f}")
    print(f"Riferimento (Re, esatto classico): {c_ref_re:+.4f}")

    np.savez('/home/claude/thesis_work/shot_noise_results.npz',
             shots_list=shots_list,
             means=[results[s].mean() for s in shots_list],
             stds=[results[s].std() for s in shots_list],
             c_ref_re=c_ref_re,
             err_trotter=err_trotter)


if __name__ == "__main__":
    main()