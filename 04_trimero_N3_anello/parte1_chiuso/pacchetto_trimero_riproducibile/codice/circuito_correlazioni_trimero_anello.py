"""
Circuito Hadamard test per le correlazioni dinamiche C_ij^{alpha,beta}(t) sul
trimero ad anello isoscele (N=3), con termine DM (Opzione B).

Mirror diretto, per N=3, del circuito già derivato e validato per il dimero
(circuito_correlatori_spiegato.tex): 4 qubit totali (3 di registro + 1
ancilla). Il registro usa la stessa convenzione sito<->qubit di
trimer_ring_exact.py / trotter_trimero_anello.py (site1->q2, site2->q1,
site3->q0); l'ancilla è il qubit aggiuntivo, indice 3.

    C_ij^{alpha,beta}(t) = <psi0| sigma_i^alpha(t) sigma_j^beta(0) |psi0>
                          = <psi0| U(t)^dag V U(t) W |psi0>,   V=sigma_i^alpha, W=sigma_j^beta

Schema (identico nella struttura al dimero, Sez. "Costruzione del circuito"
di circuito_correlatori_spiegato.tex):
    0. preparazione |psi0> sul registro (qui: ampiezze esatte del ground
       state VQE-con-DM, W-2q.6 -- vedi nota sotto)
    1. Hadamard sull'ancilla
    2. controlled-W (controllo pieno) sul qubit Q[j], prima di U(t)
    3. U(t) = e^{-iHt} sul registro, NON controllato (Trotter, da
       trotter_trimero_anello.py)
    4. anti-controlled-V sul qubit Q[i], dopo U(t)
    5. rotazione di base sull'ancilla (H per Re, Rx(pi/2) per Im) + misura

Nota sulla preparazione dello stato: la preparazione può avvenire in due
modi, selezionabili tramite l'argomento ansatz_params di
build_correlator_circuit:
  - ansatz_params=None (default): preparazione esatta delle ampiezze
    (QuantumCircuit.prepare_state), come nel dimero;
  - ansatz_params=<6 parametri>: preparazione via il circuito VQE reale
    W-2q.6 (pma_2q_trimer_exact(6, w_block), vedi
    vqe_w2q6_trimero_anello.py), ottimizzato al punto di lavoro con
    fidelity F=0.99999999999961 (vedi log_decisioni.md) -- chiude la
    pipeline VQE->correlazioni con il circuito effettivo al posto dello
    stand-in a ampiezze esatte.
"""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import XGate, YGate, ZGate
from qiskit.quantum_info import Statevector, SparsePauliOp

from trimer_ring_exact import trimer_hamiltonian_dm
from trotter_trimero_anello import Q, trotter_circuit
from vqe_w2q6_trimero_anello import w2q6_circuit

ANCILLA = 3
PAULI_GATE = {'x': XGate(), 'y': YGate(), 'z': ZGate()}


def ground_state(J, Jp, b, D, mode="B"):
    """Ground state esatto (fase fissata reale), stesso punto usato per il
    VQE-con-DM (W-2q.6) e per il controllo classico dei correlatori."""
    H = trimer_hamiltonian_dm(J, Jp, b, mode, D).to_matrix()
    E, V = np.linalg.eigh(H)
    psi0 = V[:, 0]
    imax = np.argmax(np.abs(psi0))
    psi0 = psi0 * np.exp(-1j * np.angle(psi0[imax]))
    return psi0, E


def build_correlator_circuit(i, alpha, j, beta, t, N, J, Jp, b, D, part,
                              psi0=None, measure=False, ansatz_params=None):
    """Costruisce il circuito a 4 qubit per Re/Im di C_ij^{alpha,beta}(t).

    part: 're' o 'im'.
    ansatz_params: se None, preparazione esatta delle ampiezze (psi0, o
        ground_state se psi0 non e' dato); se forniti (6 parametri),
        preparazione via il circuito VQE reale W-2q.6.
    """
    qc = QuantumCircuit(4, 1) if measure else QuantumCircuit(4)

    if ansatz_params is not None:
        ansatz = w2q6_circuit().assign_parameters(ansatz_params)
        qc.compose(ansatz, qubits=[0, 1, 2], inplace=True)
    else:
        if psi0 is None:
            psi0, _ = ground_state(J, Jp, b, D)
        qc.prepare_state(list(psi0), [0, 1, 2])

    qc.h(ANCILLA)

    W = PAULI_GATE[beta].control(1, ctrl_state=1)
    qc.append(W, [ANCILLA, Q[j]])

    sub = trotter_circuit(J, Jp, b, D, t, N, measure=False)
    qc.compose(sub, qubits=[0, 1, 2], inplace=True)

    V = PAULI_GATE[alpha].control(1, ctrl_state=0)
    qc.append(V, [ANCILLA, Q[i]])

    if part == 're':
        qc.h(ANCILLA)
    elif part == 'im':
        qc.rx(np.pi / 2, ANCILLA)
    else:
        raise ValueError("part deve essere 're' o 'im'")

    if measure:
        qc.measure(ANCILLA, 0)
    return qc


def ancilla_z_expectation(qc):
    """<sigma_z> esatto sull'ancilla, dallo statevector (nessun rumore di shot)."""
    sv = Statevector(qc)
    op = SparsePauliOp.from_sparse_list([("Z", [ANCILLA], 1.0)], num_qubits=4)
    return sv.expectation_value(op).real


def correlator_from_circuit(i, alpha, j, beta, t, N, J, Jp, b, D, psi0=None,
                             ansatz_params=None):
    """Stima Re/Im di C_ij^{alpha,beta}(t) via due esecuzioni del circuito
    (statevector esatto, nessun rumore di shot -- validazione della logica).

    ansatz_params: se forniti, preparazione via il circuito VQE reale
        W-2q.6 al posto delle ampiezze esatte (vedi build_correlator_circuit).
    """
    qc_re = build_correlator_circuit(i, alpha, j, beta, t, N, J, Jp, b, D, 're',
                                      psi0, ansatz_params=ansatz_params)
    qc_im = build_correlator_circuit(i, alpha, j, beta, t, N, J, Jp, b, D, 'im',
                                      psi0, ansatz_params=ansatz_params)
    return ancilla_z_expectation(qc_re) + 1j * ancilla_z_expectation(qc_im)