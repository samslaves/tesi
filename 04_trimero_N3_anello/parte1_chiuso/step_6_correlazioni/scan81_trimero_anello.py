"""Scan sistematico delle 81 combinazioni (i,j,alpha,beta) del correlatore
C_ij^{alpha,beta}(t) sul trimero anello, via CIRCUITO EFFETTIVO -- sia a
statevector esatto (nessun rumore di shot) sia a shot finiti (AerSimulator,
8192 shots). Estende a tutte le 81 combinazioni quanto gia' fatto su 6 casi
rappresentativi (validate_circuito_correlazioni.py, solo statevector) e su 3
casi (validate_shot_noise_trimero_anello.py, statevector + shots).

Lo scan classico "solo algebra" delle 81 combinazioni era gia' stato fatto in
simmetrie_correlatori_trimero_anello.tex: qui si rimisura tutto passando per
il circuito quantistico reale, alle stesse condizioni (t=1.3, N=200 passi di
Trotter, punto di lavoro confermato J=1,J'=0.4,b=b_c=2.4,D=0.15, Opzione B).
"""
import itertools
import json
import numpy as np
from qiskit import transpile
from qiskit_aer import AerSimulator

from circuito_correlazioni_trimero_anello import (
    ground_state, build_correlator_circuit, correlator_from_circuit,
)
from validate_circuito_correlazioni import classical_exact
from trimer_ring_exact import trimer_hamiltonian_dm

J, Jp, b, D = 1.0, 0.4, 2.4, 0.15
T = 1.3
N = 200
SHOTS = 8192

H = trimer_hamiltonian_dm(J, Jp, b, "B", D).to_matrix()
psi0, _ = ground_state(J, Jp, b, D)
BACKEND = AerSimulator()

SITES = (1, 2, 3)
COMPS = ('x', 'y', 'z')
LABELS = [f"{i}{a}" for i in SITES for a in COMPS]   # 9 etichette (i,alpha)

# zeri strutturali attesi (Corollario del sito fisso, simmetria U_anello,
# vedi simmetrie_correlatori_trimero_anello.tex): validi per OGNI t.
STRUCTURAL_ZEROS = {(3, a, 3, bt) for a, bt in
                     [('x', 'z'), ('z', 'x'), ('y', 'z'), ('z', 'y')]}

_TRANSPILE_CACHE = {}


def _transpiled(i, alpha, j, beta, part):
    key = (i, alpha, j, beta, part)
    if key not in _TRANSPILE_CACHE:
        qc = build_correlator_circuit(i, alpha, j, beta, T, N, J, Jp, b, D,
                                       part, psi0=psi0, measure=True)
        _TRANSPILE_CACHE[key] = transpile(qc, BACKEND)
    return _TRANSPILE_CACHE[key]


def shot_part(i, alpha, j, beta, part, seed):
    qc_t = _transpiled(i, alpha, j, beta, part)
    result = BACKEND.run(qc_t, shots=SHOTS, seed_simulator=seed).result()
    counts = result.get_counts()
    n0 = counts.get('0', 0)
    n1 = counts.get('1', 0)
    return (n0 - n1) / SHOTS


def main():
    print(f"Scan sistematico delle 81 combinazioni, t={T}, N={N}, shots={SHOTS}")
    print(f"Punto di lavoro: J={J}, J'={Jp}, b={b}, D={D} (Opzione B)\n")

    n = len(LABELS)
    M_ref = np.zeros((n, n), dtype=complex)
    M_sv = np.zeros((n, n), dtype=complex)
    M_sh = np.zeros((n, n), dtype=complex)
    is_zero_mat = np.zeros((n, n), dtype=bool)

    rows = []
    seed = 10000
    idx = {lab: k for k, lab in enumerate(LABELS)}
    for i, al in itertools.product(SITES, COMPS):
        for j, be in itertools.product(SITES, COMPS):
            r, c = idx[f"{i}{al}"], idx[f"{j}{be}"]
            c_ref = classical_exact(i, al, j, be, T, J, Jp, b, D, psi0, H)
            c_sv = correlator_from_circuit(i, al, j, be, T, N, J, Jp, b, D, psi0)
            re_sh = shot_part(i, al, j, be, 're', seed)
            im_sh = shot_part(i, al, j, be, 'im', seed + 1)
            c_sh = re_sh + 1j * im_sh
            seed += 2

            M_ref[r, c] = c_ref
            M_sv[r, c] = c_sv
            M_sh[r, c] = c_sh
            is_zero_mat[r, c] = (i, al, j, be) in STRUCTURAL_ZEROS

            err_trotter = abs(c_sv - c_ref)
            err_shot = abs(c_sh - c_sv)
            rows.append(dict(i=i, alpha=al, j=j, beta=be,
                              c_ref=[c_ref.real, c_ref.imag],
                              c_sv=[c_sv.real, c_sv.imag],
                              c_sh=[c_sh.real, c_sh.imag],
                              err_trotter=err_trotter, err_shot=err_shot,
                              is_zero=bool(is_zero_mat[r, c])))
        print(f"  fatto: sito {i}, componente {al}  ({idx[f'{i}{al}']+1}/9 righe)")

    err_trotter_all = np.array([row['err_trotter'] for row in rows])
    err_shot_all = np.array([row['err_shot'] for row in rows])
    zero_rows = [row for row in rows if row['is_zero']]
    nonzero_rows = [row for row in rows if not row['is_zero']]

    print(f"\nCombinazioni totali: {len(rows)}")
    print(f"Zeri strutturali attesi (Corollario sito 3): {len(zero_rows)}")
    print("  |C| massimo fra questi:")
    print(f"    statevector: {max(abs(complex(*row['c_sv'])) for row in zero_rows):.2e}")
    print(f"    shots:       {max(abs(complex(*row['c_sh'])) for row in zero_rows):.2e}")

    print(f"\nErrore di Trotter (statevector vs esatto), su tutte le 81:")
    print(f"  media={err_trotter_all.mean():.2e}  max={err_trotter_all.max():.2e}")
    print(f"Errore statistico (shots vs statevector), su tutte le 81:")
    print(f"  media={err_shot_all.mean():.2e}  max={err_shot_all.max():.2e}  "
          f"(soglia attesa nel caso peggiore 1/sqrt(shots)={1/np.sqrt(SHOTS):.4f})")

    # eventuali zeri "spuri" non predetti dalla simmetria nota (residuo
    # piccolo ma non nullo per altri motivi, gia' notato in
    # simmetrie_correlatori_trimero_anello.tex per C_33^zz)
    small_nonzero = sorted(nonzero_rows, key=lambda row: abs(complex(*row['c_sv'])))[:3]
    print("\nCorrelatori non-zero piu' piccoli (|C| statevector):")
    for row in small_nonzero:
        c = complex(*row['c_sv'])
        print(f"  C_{row['i']}{row['j']}^{row['alpha']}{row['beta']}: |C|={abs(c):.2e}")

    top = sorted(nonzero_rows, key=lambda row: -abs(complex(*row['c_sv'])))[:5]
    print("\nCorrelatori piu' 'ricchi' (|C| statevector piu' grande):")
    for row in top:
        c = complex(*row['c_sv'])
        print(f"  C_{row['i']}{row['j']}^{row['alpha']}{row['beta']}: |C|={abs(c):.4f}")

    np.savez('scan81_results.npz',
             labels=LABELS,
             M_ref_re=M_ref.real, M_ref_im=M_ref.imag,
             M_sv_re=M_sv.real, M_sv_im=M_sv.imag,
             M_sh_re=M_sh.real, M_sh_im=M_sh.imag,
             is_zero=is_zero_mat,
             err_trotter_mean=err_trotter_all.mean(), err_trotter_max=err_trotter_all.max(),
             err_shot_mean=err_shot_all.mean(), err_shot_max=err_shot_all.max())
    with open('scan81_results.json', 'w') as f:
        json.dump(rows, f, indent=1)
    print("\nSalvato: scan81_results.npz, scan81_results.json")


if __name__ == "__main__":
    main()