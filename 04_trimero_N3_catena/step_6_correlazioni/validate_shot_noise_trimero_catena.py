"""Validazione a shot finiti del circuito delle correlazioni, trimero
catena aperta. Mirror diretto di validate_shot_noise_trimero_anello.py.

Confronta la stima da conteggi (AerSimulator, shots finiti, rumore
statistico incluso) contro (a) il valore esatto classico e (b) la stima da
statevector con lo stesso N di Trotter (nessun rumore di shot) -- per
separare i due contributi di errore, algoritmico (Trotter) e statistico
(campionamento).
"""
import sys
import numpy as np
from qiskit import transpile
from qiskit_aer import AerSimulator

from circuito_correlazioni_trimero_catena import (
    ground_state, build_correlator_circuit, correlator_from_circuit,
)
from validate_circuito_correlazioni_catena import classical_exact
from trimer_chain_exact import trimer_hamiltonian_dm

_TRANSPILE_CACHE = {}


def _transpiled(backend, psi0, J, b, D, i, alpha, j, beta, t, N, part):
    key = (i, alpha, j, beta, t, N, part)
    if key not in _TRANSPILE_CACHE:
        qc = build_correlator_circuit(i, alpha, j, beta, t, N, J, b, D, part,
                                       psi0=psi0, measure=True)
        _TRANSPILE_CACHE[key] = transpile(qc, backend)
    return _TRANSPILE_CACHE[key]


def shot_estimate(backend, psi0, J, b, D, i, alpha, j, beta, t, N, shots, part, seed=None):
    qc_t = _transpiled(backend, psi0, J, b, D, i, alpha, j, beta, t, N, part)
    result = backend.run(qc_t, shots=shots, seed_simulator=seed).result()
    counts = result.get_counts()
    n0 = counts.get('0', 0)
    n1 = counts.get('1', 0)
    return (n0 - n1) / shots


def correlator_shots(backend, psi0, J, b, D, i, alpha, j, beta, t, N, shots, seed=None):
    re = shot_estimate(backend, psi0, J, b, D, i, alpha, j, beta, t, N, shots, 're', seed=seed)
    im = shot_estimate(backend, psi0, J, b, D, i, alpha, j, beta, t, N, shots, 'im',
                        seed=None if seed is None else seed + 1)
    return re + 1j * im


def run_point(J, b, D, label, npz_out):
    _TRANSPILE_CACHE.clear()
    H = trimer_hamiltonian_dm(J, b, D).to_matrix()
    psi0, _ = ground_state(J, b, D)
    backend = AerSimulator()

    N = 200
    shots = 8192
    print("=" * 78)
    print(f"Punto di lavoro: {label}  (J={J}, b={b}, D={D})")
    print(f"N (Trotter) = {N}, shots = {shots}\n")

    # casi rappresentativi: uno ricco (autocorrelazione zz), uno del sito
    # fisso (senza vincolo di simmetria), uno cross-site
    cases = [
        (1, 'z', 1, 'z', 1.3),
        (2, 'y', 2, 'y', 1.3),
        (1, 'x', 2, 'y', 2.7),
    ]

    print(f"{'correlatore':<12}{'t':>5}   {'esatto classico':>20}   "
          f"{'statevector (N=200)':>22}   {'shots (N=200, 8192)':>22}")
    for (i, al, j, be, t) in cases:
        c_ref = classical_exact(i, al, j, be, t, J, b, D, psi0, H)
        c_sv = correlator_from_circuit(i, al, j, be, t, N, J, b, D, psi0)
        c_sh = correlator_shots(backend, psi0, J, b, D, i, al, j, be, t, N, shots, seed=42)
        label2 = f"C_{i}{j}^{al}{be}"
        print(f"{label2:<12}{t:>5.1f}   {c_ref.real:+.4f}{c_ref.imag:+.4f}i"
              f"        {c_sv.real:+.4f}{c_sv.imag:+.4f}i"
              f"          {c_sh.real:+.4f}{c_sh.imag:+.4f}i")

    print()
    print("Separazione dei due contributi di errore (Trotter vs statistico)")
    i, al, j, be, t = 1, 'z', 1, 'z', 1.3
    c_ref = classical_exact(i, al, j, be, t, J, b, D, psi0, H)
    c_sv = correlator_from_circuit(i, al, j, be, t, N, J, b, D, psi0)
    err_trotter = abs(c_sv - c_ref)
    print(f"Errore di Trotter (statevector vs esatto), N={N}: {err_trotter:.2e}")
    print(f"Soglia statistica attesa nel caso peggiore, 1/sqrt({shots}): "
          f"{1/np.sqrt(shots):.4f}")
    print(f"Rapporto (statistico/Trotter): {(1/np.sqrt(shots))/err_trotter:.1f}x")

    print()
    print("Convergenza vs N_shots (media e dev.std su ripetizioni indipendenti)")
    shots_list = [256, 512, 1024, 2048, 4096, 8192, 16384]
    n_rep = 40
    c_ref_re = classical_exact(i, al, j, be, t, J, b, D, psi0, H).real
    results = {}
    for s in shots_list:
        vals = np.array([shot_estimate(backend, psi0, J, b, D, i, al, j, be, t, N, s,
                                        're', seed=1000 * s + r)
                          for r in range(n_rep)])
        results[s] = vals
        print(f"  shots={s:6d}: media={vals.mean():+.4f}  "
              f"dev.std={vals.std():.4f}  atteso~1/sqrt(shots)={1/np.sqrt(s):.4f}")
    print(f"Riferimento (Re, esatto classico): {c_ref_re:+.4f}")

    np.savez(npz_out,
             shots_list=shots_list,
             means=[results[s].mean() for s in shots_list],
             stds=[results[s].std() for s in shots_list],
             c_ref_re=c_ref_re,
             err_trotter=err_trotter)
    print(f"Salvato: {npz_out}\n")


def main():
    point = sys.argv[1] if len(sys.argv) > 1 else "vqedm"
    if point == "vqedm":
        run_point(1.0, 3.0, 0.15, "VQE-DM (b_c)", "shot_noise_catena_vqedm_results.npz")
    elif point == "s0":
        run_point(1.0, 3.0073414, 0.3, "S0 (Trotter)", "shot_noise_catena_S0_results.npz")
    else:
        raise ValueError("point deve essere 'vqedm' o 's0'")


if __name__ == "__main__":
    main()
