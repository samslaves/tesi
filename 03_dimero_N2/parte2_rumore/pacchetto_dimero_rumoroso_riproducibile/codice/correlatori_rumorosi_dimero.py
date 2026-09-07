"""
Parte 2, Passo 4 -- correlazioni dinamiche sotto rumore.

Circuito Hadamard test completo (Passo 4 della pipeline), con rumore su
TUTTI i suoi ingredienti: preparazione (Passo 2), blocco U(t) ripetuto
(Passo 3), e infine la misura sull'ancilla (errore di lettura, Passo 1 --
mai agganciato finora perche' i Passi 2-3 non misuravano nulla).

Strategia di transpilazione per blocco (decisione della sessione
precedente, gia' applicata al Trotter nel Passo 3): OGNI sottocircuito a 2
qubit viene transpilato UNA VOLTA in base {rz,sx,x,cx}, poi composto nel
circuito finale -- mai transpilato tutto insieme, altrimenti si rischia la
stessa fusione gia' trovata. I quattro blocchi:
    1. preparazione (ansatz VQE PMA-2q.3, Passo 2)
    2. controlled-W sul sito j (ancilla + 1 qubit)
    3. singolo passo di Trotter (2 qubit), ripetuto N volte (Passo 3)
    4. anti-controlled-V + rotazione di base (ancilla + 1 qubit)

Errore di lettura: applicato ANALITICAMENTE, non via misura a shot finiti
(coerente con il resto del progetto, che lavora sempre a statevector/
operatore densita' esatti, mai con rumore di shot). Per un readout
simmetrico di parametro p, la distribuzione di probabilita' letta e'
p0' = (1-p)p0 + p*p1, p1' = (1-p)p1 + p*p0, da cui

    <Z>_readout = p0' - p1' = (1-2p) * (p0 - p1) = (1-2p) * <Z>_ideale

-- una singola moltiplicazione, applicata al <Z> gia' calcolato con il
rumore di gate. Derivazione e verifica indipendente (shot Monte Carlo con
ReadoutError vero) in validate_correlatori_rumorosi_dimero.py.

RUOLO NELL'INSIEME DEL PACCHETTO: e' il modulo piu' complesso della
pipeline base -- l'unico che combina tutti e tre gli "ingredienti" degli
stadi precedenti (preparazione, evoluzione, e ora anche la misura) in un
solo circuito. Riusa la convenzione sito<->qubit e i blocchi geometrici
di circuito_correlazioni_dimero.py, ma ricostruisce ogni blocco
transpilandolo separatamente (funzioni con prefisso _), a differenza di
quel modulo che lavora a rumore nullo su statevector. E' il modulo
importato dall'estensione readout asimmetrico
(correlatori_readout_asimmetrico.py), che generalizza qui la correzione
di lettura da (1-2p) a una trasformazione affine.
"""
import numpy as np
import scipy.linalg as sla
from qiskit import QuantumCircuit, QuantumRegister, transpile
from qiskit.circuit.library import UnitaryGate, XGate, YGate, ZGate
from qiskit.quantum_info import DensityMatrix, SparsePauliOp
from qiskit_aer import AerSimulator

from dimer_exact import dimer_hamiltonian
from vqe_test2 import pma_2q
from noise_model_dimero import build_noise_model, BASIS_GATES
from circuito_correlazioni_dimero import SITE_TO_QUBIT, PAULI_GATE

J_DEFAULT, b_DEFAULT, D_DEFAULT = 1.0, 0.35, 0.80


def _transpile_once(qc, optimization_level=3, seed_transpiler=7):
    """Transpila qc in base {rz,sx,x,cx} con parametri fissi, usata da
    tutte le altre funzioni "_..._block" qui sotto.

    Ruolo nel modulo: e' il punto unico attraverso cui passa OGNI blocco
    di questo file prima di essere composto nel circuito finale --
    concentrare qui optimization_level e seed_transpiler garantisce che
    tutti i blocchi siano transpilati in modo consistente fra loro.
    Ruolo nell'insieme: e' l'implementazione locale, per questo modulo,
    della strategia "transpilazione a blocchi" gia' stabilita in
    trotter_rumoroso_dimero.py -- qui applicata a quattro blocchi
    diversi invece che a uno solo.
    """
    return transpile(qc, basis_gates=BASIS_GATES,
                      optimization_level=optimization_level,
                      seed_transpiler=seed_transpiler)


def _prep_block(ansatz_params):
    """Blocco di preparazione: ansatz PMA-2q.3 con i parametri dati,
    transpilato una volta.

    Ruolo nel modulo: e' il primo dei quattro blocchi che
    build_noisy_correlator_circuit() compone nel circuito completo --
    corrisponde al Passo 2 (VQE con termine DM sotto rumore) reinserito
    qui come sottocircuito.
    Ruolo nell'insieme: usa lo stesso ansatz pma_2q() di vqe_test2.py e
    vqe_dm_rumoroso_dimero.py -- la preparazione e' concettualmente la
    stessa in tutta la pipeline, cambia solo cosa viene composto dopo.
    """
    ansatz = pma_2q(3).assign_parameters(ansatz_params)
    return _transpile_once(ansatz)


def _ctrl_W_block(beta):
    """H sull'ancilla + controlled-beta su (ancilla, target). 2 qubit
    locali: 0=ancilla, 1=target.

    Ruolo nel modulo: e' il secondo blocco composto da
    build_noisy_correlator_circuit() -- mette l'ancilla in sovrapposizione
    e applica l'operatore W=sigma_j^beta condizionato, PRIMA
    dell'evoluzione temporale (schema a 5 passi di
    circuito_correlazioni_dimero.py).
    Ruolo nell'insieme: e' l'ingrediente che rende questo circuito un
    vero test di Hadamard (non presente ne' nel modulo VQE ne' in
    quello di Trotter) -- da qui in poi nella pipeline l'ancilla e'
    sempre presente.
    """
    qc = QuantumCircuit(2)
    qc.h(0)
    {"x": qc.cx, "y": qc.cy, "z": qc.cz}[beta](0, 1)
    return _transpile_once(qc)


def _trotter_step_block(J, b, D, t, N):
    """Singolo passo di Trotter (H1 poi H2), transpilato una volta --
    stessa costruzione di build_step_block() in trotter_rumoroso_dimero.py.

    Ruolo nel modulo: e' il terzo blocco, quello che
    build_noisy_correlator_circuit() ripete N volte -- l'unico blocco la
    cui composizione ripetuta dipende dal parametro N che tutta la
    pipeline vuole scansionare.
    Ruolo nell'insieme: e' una reimplementazione locale (non un'importazione)
    dello stesso passo di Trotter usato in trotter_rumoroso_dimero.py --
    stessa formula, stessa Hamiltoniana, ricostruita qui per tenere il
    modulo autosufficiente rispetto ai suoi quattro blocchi.
    """
    tau = t / N
    H1 = dimer_hamiltonian(b=b, J=J, D=0.0).to_matrix()
    H2 = dimer_hamiltonian(b=0.0, J=0.0, D=D).to_matrix()
    step = sla.expm(-1j * H2 * tau) @ sla.expm(-1j * H1 * tau)
    qc = QuantumCircuit(2)
    qc.append(UnitaryGate(step), [0, 1])
    return _transpile_once(qc)


def _final_block(alpha, part):
    """Anti-controlled-alpha su (ancilla, target) + rotazione di base
    sull'ancilla. 2 qubit locali: 0=ancilla, 1=target.

    Ruolo nel modulo: e' il quarto e ultimo blocco composto da
    build_noisy_correlator_circuit() -- applica V=sigma_i^alpha
    condizionato (attivo su ancilla=|0>) DOPO l'evoluzione, poi ruota
    l'ancilla nella base giusta per misurare la parte reale o
    immaginaria del correlatore.
    Ruolo nell'insieme: la scelta re/im qui determina se il circuito
    prodotto contribuisce alla parte reale o immaginaria del numero
    complesso finale -- correlator_rumoroso() chiama questa catena due
    volte, una per parte.
    """
    qc = QuantumCircuit(2)
    anti_gate = PAULI_GATE[alpha].control(1, ctrl_state=0)
    qc.append(anti_gate, [0, 1])
    if part == "re":
        qc.h(0)
    elif part == "im":
        qc.rx(np.pi / 2, 0)
    else:
        raise ValueError(f"part deve essere 're' o 'im', ricevuto {part!r}")
    return _transpile_once(qc)


def build_noisy_correlator_circuit(i, alpha, j, beta, t, N, J, b, D, part,
                                    ansatz_params):
    """Circuito completo a 3 qubit (0=ancilla, 1=site2, 2=site1), interamente
    gia' in base {rz,sx,x,cx} -- pronto per essere eseguito senza ulteriore
    transpilazione.

    Ruolo nel modulo: assembla, componendo in sequenza i quattro blocchi
    definiti sopra, il circuito che ancilla_z_gate_noisy() poi esegue --
    e' la funzione che materializza lo schema a 5 passi del docstring di
    modulo in un oggetto QuantumCircuit concreto.
    Ruolo nell'insieme: e' l'analogo, sotto rumore e a blocchi separati,
    di build_correlator_circuit() in circuito_correlazioni_dimero.py --
    stessa geometria di circuito, stessa convenzione sito<->qubit
    (SITE_TO_QUBIT importato da li'), ma costruito qui gate-per-blocco
    invece che con prepare_state/UnitaryGate diretti, per compatibilita'
    con la strategia di transpilazione a blocchi.
    """
    qc = QuantumCircuit(3)

    prep = _prep_block(ansatz_params)
    qc.compose(prep, [1, 2], inplace=True)

    ctrlW = _ctrl_W_block(beta)
    q_W_abs = 1 + SITE_TO_QUBIT[j]
    qc.compose(ctrlW, [0, q_W_abs], inplace=True)

    step_block = _trotter_step_block(J, b, D, t, N)
    for _ in range(N):
        qc.compose(step_block, [1, 2], inplace=True)

    final = _final_block(alpha, part)
    q_V_abs = 1 + SITE_TO_QUBIT[i]
    qc.compose(final, [0, q_V_abs], inplace=True)

    return qc


def ancilla_z_gate_noisy(qc, noise_model=None):
    """<Z> sull'ancilla da operatore densita' (rumore di gate incluso se
    noise_model e' fornito), SENZA errore di lettura -- quello si applica
    dopo, analiticamente.

    Ruolo nel modulo: chiude la catena di calcolo del rumore di GATE --
    prende il circuito assemblato da build_noisy_correlator_circuit() e
    lo esegue, ritornando l'aspettazione su Z prima di applicare la
    correzione di readout (fatta da correlator_rumoroso(), non qui).
    Ruolo nell'insieme: e' il punto in cui il rumore di gate (modellato
    da noise_model_dimero.py) entra effettivamente in azione per questo
    stadio della pipeline -- l'analogo, per i correlatori, della
    simulazione a operatore densita' gia' vista in
    vqe_dm_rumoroso_dimero.py e trotter_rumoroso_dimero.py.
    """
    sim = AerSimulator(method="density_matrix", noise_model=noise_model)
    qc = qc.copy()
    qc.save_density_matrix()
    result = sim.run(qc).result()
    rho = DensityMatrix(result.data(0)["density_matrix"])
    op = SparsePauliOp.from_sparse_list([("Z", [0], 1.0)], num_qubits=3)
    return float(np.real(rho.expectation_value(op)))


def correlator_rumoroso(i, alpha, j, beta, t, N, J, b, D, ansatz_params,
                         noise_model=None, p_readout=0.0):
    """Re/Im di C_ij^{alpha,beta}(t) con rumore di gate (via noise_model)
    e di lettura (via p_readout, applicato analiticamente).

    Ruolo nel modulo: e' la funzione pubblica del file -- combina i due
    circuiti (parte reale e immaginaria), il rumore di gate
    (ancilla_z_gate_noisy) e la correzione di readout (1-2*p_readout,
    derivata nel docstring di modulo) in un unico numero complesso.
    Ruolo nell'insieme: e' la funzione piu' importata di questo modulo
    da fuori -- scan_parametri_rumore_dimero.py la usa (indirettamente,
    tramite le sue stesse funzioni di supporto) per trovare N*,
    l'estensione VQE noise-aware la chiama per confrontare preparazione
    ideale e ottimizzata di nuovo, l'estensione readout asimmetrico la
    riusa come termine di paragone per il caso simmetrico.
    """
    qc_re = build_noisy_correlator_circuit(i, alpha, j, beta, t, N, J, b, D,
                                            "re", ansatz_params)
    qc_im = build_noisy_correlator_circuit(i, alpha, j, beta, t, N, J, b, D,
                                            "im", ansatz_params)
    z_re = ancilla_z_gate_noisy(qc_re, noise_model) * (1 - 2 * p_readout)
    z_im = ancilla_z_gate_noisy(qc_im, noise_model) * (1 - 2 * p_readout)
    return z_re + 1j * z_im


if __name__ == "__main__":
    data = np.load("ground_state_test2.npz")
    vqe_params = data["vqe_params"]
    nm_ref, params_ref = build_noise_model()

    print("C_21^xx(t=2), rumore nullo vs rumore di riferimento (ibm_torino):")
    for N in [1, 5, 10, 20, 40]:
        c0 = correlator_rumoroso(2, "x", 1, "x", 2.0, N, J_DEFAULT, b_DEFAULT,
                                  D_DEFAULT, vqe_params,
                                  noise_model=None, p_readout=0.0)
        cn = correlator_rumoroso(2, "x", 1, "x", 2.0, N, J_DEFAULT, b_DEFAULT,
                                  D_DEFAULT, vqe_params,
                                  noise_model=nm_ref,
                                  p_readout=params_ref["p_readout"])
        print(f"  N={N:3d}: rumore nullo = {c0.real:+.6f}{c0.imag:+.6f}i   "
              f"rumoroso = {cn.real:+.6f}{cn.imag:+.6f}i")
