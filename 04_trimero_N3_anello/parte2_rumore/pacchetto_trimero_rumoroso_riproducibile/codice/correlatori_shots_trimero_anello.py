"""
Parte 2, Stadio 4bis -- correlazioni dinamiche sotto rumore, readout
GENUINAMENTE CAMPIONATO a shot finiti (trimero ad anello).

RUOLO NELL'INSIEME DEL PACCHETTO: estensione di
`correlatori_rumorosi_trimero_anello.py` (Stadio 4), non una riscrittura.
Riusa integralmente la costruzione del circuito a 4 qubit di quel modulo
(`build_noisy_correlator_circuit`) -- l'unica differenza e' COME si legge
l'ancilla: la' analiticamente (<Z>_readout = (1-2p)*<Z>_ideale, mai una
misura vera), qui con un `ReadoutError` vero agganciato al `NoiseModel` e
una misura a shot finiti campionata da `AerSimulator`.

Perche' questa estensione: la formula analitica presuppone readout
simmetrico e un canale scorrelato dal resto del circuito -- ipotesi
corretta ma mai verificata contro una misura vera in questo pacchetto.
Qui si verifica esplicitamente che le due strade coincidano entro
l'errore statistico atteso, e si fornisce il metodo che serve comunque
per il readout ASIMMETRICO (Stadio 6bis,
`correlatori_readout_asimmetrico_trimero_anello.py`), dove la formula
analitica (1-2p) non si applica piu' cosi' com'e'.

Convenzione qubit e punto di lavoro: IDENTICI allo Stadio 4 (registro =
qubit 0,1,2; ancilla = qubit 3; J=1, J'=0.4, b=b_c=2.4, D=0.15).
"""
import numpy as np
from qiskit import ClassicalRegister
from qiskit_aer import AerSimulator

from noise_model_trimero_anello import build_noise_model
from correlatori_rumorosi_trimero_anello import (
    build_noisy_correlator_circuit, ANCILLA,
    J_DEFAULT, JP_DEFAULT, B_DEFAULT, D_DEFAULT,
)

SHOTS_DEFAULT = 100_000


def _circuito_con_misura(i, alpha, j, beta, t, N, J, Jp, b, D, part, ansatz_params):
    """Stesso circuito di build_noisy_correlator_circuit (Stadio 4), con
    l'aggiunta della misura sull'ancilla in un registro classico a 1 bit.

    RUOLO NEL MODULO: unico punto di contatto col circuito dello Stadio
    4 -- nessuna logica di costruzione duplicata qui. RUOLO NELL'INSIEME:
    la misura e' l'ingrediente che manca al circuito dello Stadio 4 per
    poter essere eseguito a shot finiti invece che letto analiticamente
    dall'operatore densita'."""
    qc = build_noisy_correlator_circuit(i, alpha, j, beta, t, N, J, Jp, b, D,
                                         part, ansatz_params)
    qc.add_register(ClassicalRegister(1, "c"))
    qc.measure(ANCILLA, 0)
    return qc


def ancilla_z_shots(qc, noise_model=None, shots=SHOTS_DEFAULT, seed_simulator=0):
    """<Z> sull'ancilla stimato da conteggi a shot finiti, con il
    ReadoutError del noise_model (se fornito) applicato dalla misura
    vera di AerSimulator -- non da una formula.

    RUOLO NEL MODULO: sostituisce ancilla_z_gate_noisy (Stadio 4) come
    fonte del valore di aspettazione. RUOLO NELL'INSIEME: e' la funzione
    che rende "genuino" il readout in tutta questa estensione -- il
    ReadoutError dentro noise_model (gia' costruito da build_noise_model,
    Stadio 1, mai usato finora perche' nessun circuito faceva una misura
    vera) qui viene finalmente esercitato."""
    sim = AerSimulator(noise_model=noise_model, seed_simulator=seed_simulator)
    result = sim.run(qc, shots=shots).result()
    counts = result.get_counts()
    n0 = counts.get("0", 0)
    n1 = counts.get("1", 0)
    tot = n0 + n1
    return (n0 - n1) / tot


def correlator_shots(i, alpha, j, beta, t, N, J, Jp, b, D, ansatz_params,
                      noise_model=None, shots=SHOTS_DEFAULT, seed_simulator=0):
    """Re/Im di C_ij^{alpha,beta}(t) con rumore di gate E di lettura
    ENTRAMBI applicati dalla simulazione (nessuna correzione analitica
    dopo) -- mirror di correlator_rumoroso (Stadio 4), stessa firma
    tranne p_readout (qui dentro noise_model) sostituito da shots."""
    qc_re = _circuito_con_misura(i, alpha, j, beta, t, N, J, Jp, b, D, "re", ansatz_params)
    qc_im = _circuito_con_misura(i, alpha, j, beta, t, N, J, Jp, b, D, "im", ansatz_params)
    z_re = ancilla_z_shots(qc_re, noise_model, shots, seed_simulator)
    z_im = ancilla_z_shots(qc_im, noise_model, shots, seed_simulator + 1)
    return z_re + 1j * z_im


if __name__ == "__main__":
    from correlatori_rumorosi_trimero_anello import correlator_rumoroso

    data = np.load("w2q6_params_optimal.npz")
    vqe_params = data["params"]
    nm_ref, params_ref = build_noise_model()

    print("Verifica: formula analitica (Stadio 4) contro shot finiti (qui), N=3, t=2:")
    c_analitico = correlator_rumoroso(2, "x", 1, "x", 2.0, 3,
                                       J_DEFAULT, JP_DEFAULT, B_DEFAULT, D_DEFAULT,
                                       vqe_params, noise_model=nm_ref,
                                       p_readout=params_ref["p_readout"])
    c_shots = correlator_shots(2, "x", 1, "x", 2.0, 3,
                                J_DEFAULT, JP_DEFAULT, B_DEFAULT, D_DEFAULT,
                                vqe_params, noise_model=nm_ref, shots=SHOTS_DEFAULT)
    print(f"  analitico    = {c_analitico.real:+.4f}{c_analitico.imag:+.4f}i")
    print(f"  shot finiti  = {c_shots.real:+.4f}{c_shots.imag:+.4f}i")
    print(f"  scarto       = {abs(c_analitico - c_shots):.2e}  "
          f"(atteso ~1/sqrt({SHOTS_DEFAULT}) = {1/np.sqrt(SHOTS_DEFAULT):.2e})")

    print("\nCurva |C(N)| a shot finiti, rumore di riferimento:")
    for N in [1, 2, 3, 4, 5, 6, 8, 10, 15, 20]:
        c = correlator_shots(2, "x", 1, "x", 2.0, N,
                              J_DEFAULT, JP_DEFAULT, B_DEFAULT, D_DEFAULT,
                              vqe_params, noise_model=nm_ref, shots=SHOTS_DEFAULT)
        print(f"  N={N:3d}: |C| = {abs(c):.4f}")
