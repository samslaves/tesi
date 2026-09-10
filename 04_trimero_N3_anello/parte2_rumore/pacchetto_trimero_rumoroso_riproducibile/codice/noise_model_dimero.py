"""
Modello di rumore per il dimero (Parte 2, Passo 1).

Due soli canali, confermati dal relatore il 02/09/2026 (domande_relatore.md,
sez. 12): errore di gate (depolarizzante, 1 e 2 qubit) ed errore di lettura
(readout, simmetrico). T1/T2 esclusi per decisione esplicita.

Formule usate (derivate in teoria_modello_rumore.tex):
    lambda_1q = 2 * eps_1q          (canale depolarizzante, n=1, d=2)
    lambda_2q = (4/3) * eps_2q      (canale depolarizzante, n=2, d=4)
dove eps_1q, eps_2q sono gli errori medi di gate da randomized benchmarking
(quelli riportati nelle calibrazioni pubblicate), non il parametro lambda
di Aer.

Valori di calibrazione: mediane pubblicate per ibm_torino (IBM Heron r1,
133 qubit), Appendice B di

    J. P. T. Stenger, G. Bazargan, N. T. Bronn, D. Gunlycke,
    "Method for simulating open-system dynamics using mid-circuit
    measurements on a quantum computer", arXiv:2504.15187 (2025).

    "The CZ gates have a median error of 3.8e-3 and the sx gates have a
    median error of 2.9e-4 [...] The median readout assignment error is
    2.3e-2."

Nota di modellazione: il gate nativo a 2 qubit di ibm_torino e' CZ, mentre
il nostro circuito e' scritto in base {rz, sx, x, cx}. Usiamo il valore di
errore del CZ come rappresentativo dell'ordine di grandezza dell'errore di
gate a 2 qubit (stesso approccio generico richiesto dal relatore: "usa dei
valori tipici... guardando qualche chip di riferimento", non una replica
esatta dell'hardware). Lo scan sui parametri di errore (Passo 5) copre
comunque un intorno di questi valori, non solo il punto singolo.
"""

import numpy as np
from qiskit_aer.noise import NoiseModel, depolarizing_error, ReadoutError

# ---------------------------------------------------------------------
# Calibrazione di riferimento: ibm_torino, mediane pubblicate (vedi sopra)
# ---------------------------------------------------------------------
EPS_1Q_REF = 2.9e-4    # errore medio di gate, sx (1 qubit)
EPS_2Q_REF = 3.8e-3    # errore medio di gate, CZ (2 qubit)
P_READOUT_REF = 2.3e-2  # errore di lettura, mediana

BASIS_GATES = ["rz", "sx", "x", "cx"]


def eps_to_lambda(eps_1q, eps_2q):
    """Converte l'errore medio di gate nel parametro lambda del canale
    depolarizzante di Aer (eps = lambda*(d-1)/d, d=2^n -> derivazione
    completa in teoria_modello_rumore.tex)."""
    lam_1q = 2.0 * eps_1q
    lam_2q = (4.0 / 3.0) * eps_2q
    return lam_1q, lam_2q


def build_noise_model(eps_1q=EPS_1Q_REF, eps_2q=EPS_2Q_REF,
                       p_readout=P_READOUT_REF):
    """Costruisce il NoiseModel con i due soli canali confermati.

    Parametri
    ---------
    eps_1q, eps_2q : errore medio di gate (randomized benchmarking),
        NON il parametro lambda di Aer. eps=0 disattiva il canale.
    p_readout : errore di lettura simmetrico (stessa probabilita' 0->1 e
        1->0). p_readout=0 disattiva il canale.

    Ritorna
    -------
    (NoiseModel, dict) - il modello e i lambda effettivamente usati, per
    poterli registrare/loggare insieme ai risultati.
    """
    lam_1q, lam_2q = eps_to_lambda(eps_1q, eps_2q)

    nm = NoiseModel(basis_gates=BASIS_GATES)

    if lam_1q > 0:
        err_1q = depolarizing_error(lam_1q, 1)
        nm.add_all_qubit_quantum_error(err_1q, ["rz", "sx", "x"])
    if lam_2q > 0:
        err_2q = depolarizing_error(lam_2q, 2)
        nm.add_all_qubit_quantum_error(err_2q, ["cx"])

    if p_readout > 0:
        conf_matrix = [[1 - p_readout, p_readout],
                        [p_readout, 1 - p_readout]]
        ro_err = ReadoutError(conf_matrix)
        nm.add_all_qubit_readout_error(ro_err)

    params = dict(eps_1q=eps_1q, eps_2q=eps_2q, p_readout=p_readout,
                   lambda_1q=lam_1q, lambda_2q=lam_2q)
    return nm, params


if __name__ == "__main__":
    nm, params = build_noise_model()
    print("Parametri di riferimento (ibm_torino, mediane, arXiv:2504.15187):")
    for k, v in params.items():
        print(f"  {k:10s} = {v:.4e}")
    print()
    print(nm)
