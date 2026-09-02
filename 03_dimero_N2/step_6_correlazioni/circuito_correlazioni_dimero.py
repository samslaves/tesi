"""
Circuito Hadamard test per le correlazioni dinamiche C_ij^{alpha,beta}(t) sul
dimero di spin-1/2 con termine DM.

Modulo estratto da circuito_correlazioni_tutte.ipynb, dove la stessa logica
viveva solo dentro le celle del notebook, non importabile da nessuno script
(gap segnalato in una sessione precedente, dedicata al rumore quantico, e
confermato assente in una sessione successiva -- vedi log_decisioni.md).
Stessa API pubblica dei moduli equivalenti per N=3
(circuito_correlazioni_trimero_anello.py, circuito_correlazioni_trimero_catena.py):

    ground_state(...)                              -> stato iniziale (esatto)
    build_correlator_circuit(i, alpha, j, beta, t, N, ..., part)
    ancilla_z_expectation(qc)
    correlator_from_circuit(i, alpha, j, beta, t, N, ..., psi0=None, ...)

    C_ij^{alpha,beta}(t) = <psi0| sigma_i^alpha(t) sigma_j^beta(0) |psi0>
                          = <psi0| U(t)^dag V U(t) W |psi0>,   V=sigma_i^alpha, W=sigma_j^beta

Schema del circuito (derivazione completa in circuito_correlatori_spiegato.tex):
    0. preparazione |psi0> sul registro (ampiezze esatte via prepare_state;
       preparazione via VQE reale non ancora implementata per il dimero,
       vedi ansatz_params sotto)
    1. Hadamard sull'ancilla
    2. controlled-W (controllo pieno) sul sito j, PRIMA di U(t)
    3. U(t) = e^{-iHt} sul registro, NON controllato (Trotter al prim'ordine,
       H = H1 + H2 con H1 = scambio isotropo + Zeeman, H2 = solo DM)
    4. anti-controlled-V (attivo su ancilla=|0>) sul sito i, DOPO U(t)
    5. rotazione di base sull'ancilla (H per Re, Rx(pi/2) per Im) + misura Z

Convenzione sito<->qubit, VERIFICATA NUMERICAMENTE (non assunta -- un errore
di mapping qui e' invisibile sui correlatori simmetrici rispetto allo scambio
dei siti, ed e' esattamente il tipo di bug gia' anticipato come rischio in
una sessione precedente sul rumore quantico, poi realmente trovato durante lo
scan completo delle 36 combinazioni -- vedi log_decisioni.md):

    ancilla  = qubit assoluto 0
    sito 2   = qreg locale 0  (qubit assoluto 1)
    sito 1   = qreg locale 1  (qubit assoluto 2)

(deriva da: prepare_state(psi0, [qreg[0], qreg[1]]) mette la componente
qubit-indice-0 di psi0 -- che e' il sito 2 nella convenzione SparsePauliOp
di dimer_exact.py -- su qreg[0]).

Due bug trovati e corretti nella derivazione originale dentro il notebook,
PRIMA di questa estrazione (cronaca completa in log_decisioni.md):
  1. la formula spettrale del riferimento classico (usata in validazione)
     mancava un coniugato complesso -- invisibile per componenti reali
     (x, z), sbagliava il segno per la componente y;
  2. la mappatura sito->qubit sopra era inizialmente invertita -- invisibile
     sui correlatori C_21^xx, C_21^xy (validati per primi) per una
     coincidenza della simmetria U, diventata visibile solo scansionando
     sistematicamente tutte le 36 combinazioni.
Questo modulo incorpora la versione gia' corretta e riverificata.
"""
import numpy as np
import scipy.linalg as sla
from qiskit import QuantumCircuit, QuantumRegister
from qiskit.circuit.library import UnitaryGate, XGate, YGate, ZGate
from qiskit.quantum_info import Statevector, SparsePauliOp

from dimer_exact import dimer_hamiltonian  # mattone read-only, mai duplicato

ANCILLA = 0
SITE_TO_QUBIT = {1: 1, 2: 0}  # sito -> indice locale nel registro qreg (verificato)
PAULI_GATE = {"x": XGate(), "y": YGate(), "z": ZGate()}


def ground_state(b, J=1.0, D=0.0):
    """Ground state esatto (fase fissata reale), stesso punto di lavoro
    usato ovunque nel progetto per il dimero (es. J=1, b/J=0.35, D/J=0.80
    per il 'test 2')."""
    H = dimer_hamiltonian(b=b, J=J, D=D).to_matrix()
    E, V = np.linalg.eigh(H)
    psi0 = V[:, 0]
    imax = np.argmax(np.abs(psi0))
    psi0 = psi0 * np.exp(-1j * np.angle(psi0[imax]))  # fase globale fissata reale
    return psi0, E


def _H1_H2(J, b, D):
    """Split H = H1 + H2 usato per il passo di Trotter: H1 = scambio
    isotropo + Zeeman (fattorizza esattamente, [Sz_tot,H1]=0 bond per
    bond), H2 = solo DM. Convenzione Pauli dirette (dimer_exact.py), non
    spin s=sigma/2 -- vedi dimero_spin.pdf App. B per il confronto fra le
    due convenzioni in uso nel progetto."""
    H1 = dimer_hamiltonian(b=b, J=J, D=0.0).to_matrix()
    H2 = dimer_hamiltonian(b=0.0, J=0.0, D=D).to_matrix()
    return H1, H2


def build_correlator_circuit(i, alpha, j, beta, t, N, J, b, D, part,
                              psi0=None, measure=False, ansatz_params=None):
    """Costruisce il circuito a 3 qubit (1 ancilla + 2 di registro) per
    Re/Im di C_ij^{alpha,beta}(t).

    part: 're' o 'im'.
    psi0: se None, ricalcolato via ground_state(b, J, D) (ampiezze esatte).
    ansatz_params: NON ancora implementato per il dimero (placeholder di
        firma per coerenza con i moduli N=3, dove seleziona la
        preparazione via il circuito VQE reale al posto delle ampiezze
        esatte). Passare un valore diverso da None solleva
        NotImplementedError.
    """
    if ansatz_params is not None:
        raise NotImplementedError(
            "preparazione via VQE reale non ancora implementata per il "
            "dimero (a differenza di anello/catena); usare ansatz_params=None."
        )
    if psi0 is None:
        psi0, _ = ground_state(b, J, D)

    a = QuantumRegister(1, "a")
    qreg = QuantumRegister(2, "q")
    qc = QuantumCircuit(a, qreg)
    qc.prepare_state(psi0, [qreg[0], qreg[1]])
    qc.h(a[0])

    q_W = qreg[SITE_TO_QUBIT[j]]
    {"x": qc.cx, "y": qc.cy, "z": qc.cz}[beta](a[0], q_W)

    H1, H2 = _H1_H2(J, b, D)
    tau = t / N
    step = sla.expm(-1j * H2 * tau) @ sla.expm(-1j * H1 * tau)
    gate = UnitaryGate(step, label="U(t)")
    for _ in range(N):
        qc.append(gate, [qreg[0], qreg[1]])

    q_V = qreg[SITE_TO_QUBIT[i]]
    anti_gate = PAULI_GATE[alpha].control(1, ctrl_state=0)
    qc.append(anti_gate, [a[0], q_V])

    if part == "re":
        qc.h(a[0])
    elif part == "im":
        qc.rx(np.pi / 2, a[0])
    else:
        raise ValueError(f"part deve essere 're' o 'im', ricevuto {part!r}")

    if measure:
        qc.measure_all()
    return qc


def ancilla_z_expectation(qc):
    """<sigma_z> sull'ancilla dallo statevector esatto -- nessun rumore di
    shot, per validazione della logica del circuito. La stima da conteggi
    reali (shot finiti, rumore di gate) e' materia della Parte 2, non
    implementata in questo modulo."""
    sv = Statevector(qc)
    op = SparsePauliOp.from_sparse_list([("Z", [ANCILLA], 1.0)], num_qubits=3)
    return sv.expectation_value(op).real


def correlator_from_circuit(i, alpha, j, beta, t, N, J, b, D, psi0=None,
                             ansatz_params=None):
    """Stima Re/Im di C_ij^{alpha,beta}(t) via due esecuzioni del circuito
    (statevector esatto, non rumore reale -- vedi ancilla_z_expectation)."""
    qc_re = build_correlator_circuit(i, alpha, j, beta, t, N, J, b, D, "re",
                                      psi0, ansatz_params=ansatz_params)
    qc_im = build_correlator_circuit(i, alpha, j, beta, t, N, J, b, D, "im",
                                      psi0, ansatz_params=ansatz_params)
    return ancilla_z_expectation(qc_re) + 1j * ancilla_z_expectation(qc_im)
