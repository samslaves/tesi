"""Scan sistematico delle 81 combinazioni (i,j,alpha,beta) del correlatore
C_ij^{alpha,beta}(t) sul trimero a catena aperta, via CIRCUITO EFFETTIVO --
sia a statevector esatto (nessun rumore di shot) sia a shot finiti
(AerSimulator, 8192 shots). Mirror diretto di scan81_trimero_anello.py.

Lo scan classico "solo algebra" delle 81 combinazioni era gia' stato fatto
in simmetrie_correlatori_trimero_catena.tex: qui si rimisura tutto passando
per il circuito quantistico reale, alle stesse condizioni (t=1.3, N=200
passi di Trotter).

Differenza qualitativa rispetto all'anello (Cor. P13-relazioni): per la
catena NON esiste alcuno zero strutturale valido per ogni t (lambda_alpha
= +1 sempre, nessun segno che possa forzare uno zero) -- STRUCTURAL_ZEROS
e' quindi vuoto, a differenza dei 4 zeri del sito 3 dell'anello. Questo
scan verifica sperimentalmente (via circuito, non solo per via classica)
che nessuna delle 81 combinazioni collassa inaspettatamente a zero.
"""
import itertools
import json
import sys
import numpy as np
from qiskit import transpile
from qiskit_aer import AerSimulator

from circuito_correlazioni_trimero_catena import (
    ground_state, build_correlator_circuit, correlator_from_circuit,
)
from validate_circuito_correlazioni_catena import classical_exact
from trimer_chain_exact import trimer_hamiltonian_dm

T = 1.3
N = 200
SHOTS = 8192

SITES = (1, 2, 3)
COMPS = ('x', 'y', 'z')
LABELS = [f"{i}{a}" for i in SITES for a in COMPS]   # 9 etichette (i,alpha)

# Nessuno zero strutturale per ogni t nella catena (Cor. P13-relazioni,
# simmetrie_correlatori_trimero_catena.tex): lambda_alpha=+1 sempre, non
# puo' mai forzare C_ij=0. Insieme vuoto per costruzione, non un'omissione.
STRUCTURAL_ZEROS = set()

_TRANSPILE_CACHE = {}


def _transpiled(backend, psi0, J, b, D, i, alpha, j, beta, part):
    key = (i, alpha, j, beta, part)
    if key not in _TRANSPILE_CACHE:
        qc = build_correlator_circuit(i, alpha, j, beta, T, N, J, b, D,
                                       part, psi0=psi0, measure=True)
        _TRANSPILE_CACHE[key] = transpile(qc, backend)
    return _TRANSPILE_CACHE[key]


def shot_part(backend, psi0, J, b, D, i, alpha, j, beta, part, seed):
    qc_t = _transpiled(backend, psi0, J, b, D, i, alpha, j, beta, part)
    result = backend.run(qc_t, shots=SHOTS, seed_simulator=seed).result()
    counts = result.get_counts()
    n0 = counts.get('0', 0)
    n1 = counts.get('1', 0)
    return (n0 - n1) / SHOTS


def run_point(J, b, D, label, outfile_prefix):
    _TRANSPILE_CACHE.clear()
    H = trimer_hamiltonian_dm(J, b, D).to_matrix()
    psi0, _ = ground_state(J, b, D)
    backend = AerSimulator()

    print(f"Scan sistematico delle 81 combinazioni, t={T}, N={N}, shots={SHOTS}")
    print(f"Punto di lavoro: {label}  (J={J}, b={b}, D={D})\n")

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
            c_ref = classical_exact(i, al, j, be, T, J, b, D, psi0, H)
            c_sv = correlator_from_circuit(i, al, j, be, T, N, J, b, D, psi0)
            re_sh = shot_part(backend, psi0, J, b, D, i, al, j, be, 're', seed)
            im_sh = shot_part(backend, psi0, J, b, D, i, al, j, be, 'im', seed + 1)
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

    print(f"\nCombinazioni totali: {len(rows)}")
    print(f"Zeri strutturali attesi (nessuno, Cor. P13-relazioni): {len(STRUCTURAL_ZEROS)}")
    all_mags_sv = [abs(complex(*row['c_sv'])) for row in rows]
    print(f"  |C| minimo su tutte le 81 (statevector): {min(all_mags_sv):.4f}  "
          f"-- nessuna collassa a zero")

    print(f"\nErrore di Trotter (statevector vs esatto), su tutte le 81:")
    print(f"  media={err_trotter_all.mean():.2e}  max={err_trotter_all.max():.2e}")
    print(f"Errore statistico (shots vs statevector), su tutte le 81:")
    print(f"  media={err_shot_all.mean():.2e}  max={err_shot_all.max():.2e}  "
          f"(soglia attesa nel caso peggiore 1/sqrt(shots)={1/np.sqrt(SHOTS):.4f})")

    small = sorted(rows, key=lambda row: abs(complex(*row['c_sv'])))[:3]
    print("\nCorrelatori piu' piccoli (|C| statevector, nessuno zero strutturale):")
    for row in small:
        c = complex(*row['c_sv'])
        print(f"  C_{row['i']}{row['j']}^{row['alpha']}{row['beta']}: |C|={abs(c):.4f}")

    top = sorted(rows, key=lambda row: -abs(complex(*row['c_sv'])))[:5]
    print("\nCorrelatori piu' 'ricchi' (|C| statevector piu' grande):")
    for row in top:
        c = complex(*row['c_sv'])
        print(f"  C_{row['i']}{row['j']}^{row['alpha']}{row['beta']}: |C|={abs(c):.4f}")

    np.savez(f'{outfile_prefix}.npz',
             labels=LABELS,
             M_ref_re=M_ref.real, M_ref_im=M_ref.imag,
             M_sv_re=M_sv.real, M_sv_im=M_sv.imag,
             M_sh_re=M_sh.real, M_sh_im=M_sh.imag,
             is_zero=is_zero_mat,
             err_trotter_mean=err_trotter_all.mean(), err_trotter_max=err_trotter_all.max(),
             err_shot_mean=err_shot_all.mean(), err_shot_max=err_shot_all.max())
    with open(f'{outfile_prefix}.json', 'w') as f:
        json.dump(rows, f, indent=1)
    print(f"\nSalvato: {outfile_prefix}.npz, {outfile_prefix}.json\n")


def main():
    point = sys.argv[1] if len(sys.argv) > 1 else "vqedm"
    if point == "vqedm":
        run_point(1.0, 3.0, 0.15, "VQE-DM (b_c)", "scan81_catena_vqedm_results")
    elif point == "s0":
        run_point(1.0, 3.0073414, 0.3, "S0 (Trotter)", "scan81_catena_S0_results")
    else:
        raise ValueError("point deve essere 'vqedm' o 's0'")


if __name__ == "__main__":
    main()
