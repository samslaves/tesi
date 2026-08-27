"""
Circuito Hadamard test per le correlazioni dinamiche C_ij^{alpha,beta}(t) sul
trimero a catena aperta (N=3), con termine DM. Mirror diretto, per la
catena, del circuito gia' derivato e validato per l'anello
(circuito_correlazioni_trimero_anello.py), a sua volta mirror del dimero.

4 qubit totali (3 di registro + 1 ancilla). Il registro usa la stessa
convenzione sito<->qubit di trimer_chain_exact.py / trotter_trimero_catena.py
(site1->q2, site2->q1, site3->q0); l'ancilla e' il qubit aggiuntivo, indice 3.

    C_ij^{alpha,beta}(t) = <psi0| sigma_i^alpha(t) sigma_j^beta(0) |psi0>
                          = <psi0| U(t)^dag V U(t) W |psi0>,   V=sigma_i^alpha, W=sigma_j^beta

Schema (identico nella struttura all'anello e al dimero):
    0. preparazione |psi0> sul registro (ampiezze esatte o circuito VQE reale
       W-2qC.K2, vedi ansatz_params sotto)
    1. Hadamard sull'ancilla
    2. controlled-W (controllo pieno) sul qubit Q[j], prima di U(t)
    3. U(t) = e^{-iHt} sul registro, NON controllato (Trotter, da
       trotter_trimero_catena.py)
    4. anti-controlled-V sul qubit Q[i], dopo U(t)
    5. rotazione di base sull'ancilla (H per Re, Rx(pi/2) per Im) + misura

DIFFERENZE DI CONVENZIONE DA circuito_correlazioni_trimero_anello.py:
  1. U(t) ha solo 2 bond (nessun (3,1)): trotter_circuit prende (J,b,D,t,N),
     non (J,Jp,b,D,t,N). Le combinazioni misurabili restano pero' 81 come
     nell'anello: il conteggio 3(siti i)x3(siti j)x3(alpha)x3(beta) dipende
     da quanti SITI ha il sistema (N=3 in entrambi i casi), non da quanti
     legami ha H. C_13^{alpha,beta}, ad esempio, e' un correlatore ben
     definito e generalmente non nullo anche se il legame (1,3) non esiste:
     l'evoluzione U(t) propaga comunque la correlazione tramite il sito 2
     intermedio (verificato: C_13 non e' fra le combinazioni piu' piccole
     dello scan). Cio' che dipende dai 2 legami e' la simmetria residua
     (P13, non U_anello) e quindi quali delle 81 risultino vincolate -- non
     il numero totale di combinazioni.
  2. Preparazione VQE reale: ansatz W-2qC.K2 (10 parametri, 2 cicli), non
     W-2q.6 (6 parametri, un solo giro) -- vedi vqe_w2qC_k2_trimero_catena.py.
  3. Nessuna ambiguita' di opzione DM (A/B): un solo termine possibile,
     fissato dalla simmetria P13 (D12=-D23=D).

Nota sulla preparazione dello stato: selezionabile tramite l'argomento
ansatz_params di build_correlator_circuit:
  - ansatz_params=None (default): preparazione esatta delle ampiezze
    (QuantumCircuit.prepare_state), come nell'anello e nel dimero;
  - ansatz_params=<10 parametri>: preparazione via il circuito VQE reale
    W-2qC.K2 (w2qC_k2_circuit(), vedi vqe_w2qC_k2_trimero_catena.py),
    ottimizzato a due punti di lavoro (VQE-DM b_c e S0 Trotter, entrambi
    F=1 esatto) -- chiude la pipeline VQE->correlazioni con il circuito
    effettivo al posto dello stand-in a ampiezze esatte.
"""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import XGate, YGate, ZGate
from qiskit.quantum_info import Statevector, SparsePauliOp

from trimer_chain_exact import trimer_hamiltonian_dm
from trotter_trimero_catena import Q, trotter_circuit
from vqe_w2qC_k2_trimero_catena import w2qC_k2_circuit

ANCILLA = 3
PAULI_GATE = {'x': XGate(), 'y': YGate(), 'z': ZGate()}


def ground_state(J, b, D):
    """Ground state esatto (fase fissata reale), stesso punto usato per il
    VQE-con-DM (W-2qC.K2) e per il controllo classico dei correlatori."""
    H = trimer_hamiltonian_dm(J, b, D).to_matrix()
    E, V = np.linalg.eigh(H)
    psi0 = V[:, 0]
    imax = np.argmax(np.abs(psi0))
    psi0 = psi0 * np.exp(-1j * np.angle(psi0[imax]))
    return psi0, E


def build_correlator_circuit(i, alpha, j, beta, t, N, J, b, D, part,
                              psi0=None, measure=False, ansatz_params=None,
                              alternate=False):
    """Costruisce il circuito a 4 qubit per Re/Im di C_ij^{alpha,beta}(t).

    part: 're' o 'im'.
    ansatz_params: se None, preparazione esatta delle ampiezze (psi0, o
        ground_state se psi0 non e' dato); se forniti (10 parametri),
        preparazione via il circuito VQE reale W-2qC.K2.
    alternate: propagato a trotter_circuit (alternanza dei bond, vedi
        trotter_trimero_catena.py); default False, mirror del comportamento
        dell'anello (che non ha questa opzione).
    """
    qc = QuantumCircuit(4, 1) if measure else QuantumCircuit(4)

    if ansatz_params is not None:
        ansatz = w2qC_k2_circuit().assign_parameters(ansatz_params)
        qc.compose(ansatz, qubits=[0, 1, 2], inplace=True)
    else:
        if psi0 is None:
            psi0, _ = ground_state(J, b, D)
        qc.prepare_state(list(psi0), [0, 1, 2])

    qc.h(ANCILLA)

    W = PAULI_GATE[beta].control(1, ctrl_state=1)
    qc.append(W, [ANCILLA, Q[j]])

    sub = trotter_circuit(J, b, D, t, N, measure=False, alternate=alternate)
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


def correlator_from_circuit(i, alpha, j, beta, t, N, J, b, D, psi0=None,
                             ansatz_params=None, alternate=False):
    """Stima Re/Im di C_ij^{alpha,beta}(t) via due esecuzioni del circuito
    (statevector esatto, nessun rumore di shot -- validazione della logica).

    ansatz_params: se forniti, preparazione via il circuito VQE reale
        W-2qC.K2 al posto delle ampiezze esatte (vedi build_correlator_circuit).
    """
    qc_re = build_correlator_circuit(i, alpha, j, beta, t, N, J, b, D, 're',
                                      psi0, ansatz_params=ansatz_params,
                                      alternate=alternate)
    qc_im = build_correlator_circuit(i, alpha, j, beta, t, N, J, b, D, 'im',
                                      psi0, ansatz_params=ansatz_params,
                                      alternate=alternate)
    return ancilla_z_expectation(qc_re) + 1j * ancilla_z_expectation(qc_im)
