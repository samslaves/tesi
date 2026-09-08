"""
Parte 2, Stadio 4 -- correlazioni dinamiche sotto rumore (trimero ad anello).

RUOLO NELL'INSIEME DEL PACCHETTO: mirror strutturale di
`correlatori_rumorosi_dimero.py`, per il circuito Hadamard test a 4 qubit
(3 di registro + 1 ancilla) gia' derivato in Parte 1
(`circuito_correlazioni_trimero_anello.py`). NON reimplementa il blocco di
Trotter: lo importa da `trotter_rumoroso_trimero_anello.py` (Stadio 3),
gia' verificato li' (conteggio gate, cross-check numpy, N*) -- stesso
principio "verificare prima di scrivere" gia' applicato in tutta la
sessione.

Convenzione qubit IDENTICA a Parte 1 (non al dimero, che usa ancilla=0):
registro = qubit 0,1,2; ancilla = qubit 3 (vedi ANCILLA in
circuito_correlazioni_trimero_anello.py).

Punto di lavoro: J=1, J'=0.4, b=b_c=2.4, D=0.15 (mode "B") -- STESSO punto
usato per l'esplorazione dei correlatori in Parte 1
(trimero_anello_correlazioni.tex), non il punto R0 (quello serve solo per
la dimostrazione Trotter, Scenario B dello Stadio 3, mai usato per i
correlatori in Parte 1).

Strategia di transpilazione a blocchi (stessa dello Stadio 3, qui estesa
a due nuovi blocchi locali a 2 qubit): quattro blocchi, ciascuno
transpilato UNA VOLTA in base {rz,sx,x,cx}, poi composti nel circuito
finale -- mai transpilato tutto insieme.
    1. preparazione (ansatz W-2q.6, Stadio 2)
    2. controlled-W sul sito j (ancilla + 1 qubit di registro)
    3. singolo passo esterno di Trotter (3 qubit), ripetuto N volte --
       RIUSATO da trotter_rumoroso_trimero_anello.build_step_block
    4. anti-controlled-V + rotazione di base (ancilla + 1 qubit di registro)

Errore di lettura: applicato ANALITICAMENTE (stessa formula del dimero,
verificata li' indipendente dal numero di qubit -- Stadio 1):
    <Z>_readout = (1-2p) * <Z>_ideale
"""
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import XGate, YGate, ZGate
from qiskit.quantum_info import DensityMatrix, SparsePauliOp
from qiskit_aer import AerSimulator

from trimer_ring_exact import trimer_hamiltonian_dm
from trotter_trimero_anello import Q
from vqe_w2q6_trimero_anello import w2q6_circuit
from trotter_rumoroso_trimero_anello import build_step_block
from noise_model_trimero_anello import build_noise_model, BASIS_GATES

ANCILLA = 3
PAULI_GATE = {'x': XGate(), 'y': YGate(), 'z': ZGate()}

J_DEFAULT, JP_DEFAULT, B_DEFAULT, D_DEFAULT = 1.0, 0.4, 2.4, 0.15
MODE_DEFAULT = "B"


def _transpile_once(qc, optimization_level=3, seed_transpiler=7):
    return transpile(qc, basis_gates=BASIS_GATES,
                      optimization_level=optimization_level,
                      seed_transpiler=seed_transpiler)


def _prep_block(ansatz_params):
    ansatz = w2q6_circuit().assign_parameters(ansatz_params)
    return _transpile_once(ansatz)


def _ctrl_W_block(beta):
    """H sull'ancilla + controlled-beta su (ancilla, target). 2 qubit
    locali: 0=ancilla, 1=target."""
    qc = QuantumCircuit(2)
    qc.h(0)
    {"x": qc.cx, "y": qc.cy, "z": qc.cz}[beta](0, 1)
    return _transpile_once(qc)


def _final_block(alpha, part):
    """Anti-controlled-alpha su (ancilla, target) + rotazione di base
    sull'ancilla. 2 qubit locali: 0=ancilla, 1=target."""
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


def build_noisy_correlator_circuit(i, alpha, j, beta, t, N, J, Jp, b, D, part,
                                    ansatz_params):
    """Circuito completo a 4 qubit (0,1,2=registro, 3=ancilla), interamente
    gia' in base {rz,sx,x,cx} -- pronto per essere eseguito senza ulteriore
    transpilazione."""
    qc = QuantumCircuit(4)

    prep = _prep_block(ansatz_params)
    qc.compose(prep, [0, 1, 2], inplace=True)

    ctrlW = _ctrl_W_block(beta)
    qc.compose(ctrlW, [ANCILLA, Q[j]], inplace=True)

    step_block = build_step_block(J, Jp, b, D, t, N)
    for _ in range(N):
        qc.compose(step_block, [0, 1, 2], inplace=True)

    final = _final_block(alpha, part)
    qc.compose(final, [ANCILLA, Q[i]], inplace=True)

    return qc


def ancilla_z_gate_noisy(qc, noise_model=None):
    """<Z> sull'ancilla da operatore densita' (rumore di gate incluso se
    noise_model e' fornito), SENZA errore di lettura -- quello si applica
    dopo, analiticamente."""
    sim = AerSimulator(method="density_matrix", noise_model=noise_model)
    qc = qc.copy()
    qc.save_density_matrix()
    result = sim.run(qc).result()
    rho = DensityMatrix(result.data(0)["density_matrix"])
    op = SparsePauliOp.from_sparse_list([("Z", [ANCILLA], 1.0)], num_qubits=4)
    return float(np.real(rho.expectation_value(op)))


def correlator_rumoroso(i, alpha, j, beta, t, N, J, Jp, b, D, ansatz_params,
                         noise_model=None, p_readout=0.0):
    """Re/Im di C_ij^{alpha,beta}(t) con rumore di gate (via noise_model)
    e di lettura (via p_readout, applicato analiticamente)."""
    qc_re = build_noisy_correlator_circuit(i, alpha, j, beta, t, N, J, Jp, b, D,
                                            "re", ansatz_params)
    qc_im = build_noisy_correlator_circuit(i, alpha, j, beta, t, N, J, Jp, b, D,
                                            "im", ansatz_params)
    z_re = ancilla_z_gate_noisy(qc_re, noise_model) * (1 - 2 * p_readout)
    z_im = ancilla_z_gate_noisy(qc_im, noise_model) * (1 - 2 * p_readout)
    return z_re + 1j * z_im


if __name__ == "__main__":
    data = np.load("w2q6_params_optimal.npz")
    vqe_params = data["params"]
    nm_ref, params_ref = build_noise_model()

    print("C_21^xx(t=2), rumore nullo vs rumore di riferimento (ibm_torino):")
    for N in [1, 5, 10, 20, 40]:
        c0 = correlator_rumoroso(2, "x", 1, "x", 2.0, N,
                                  J_DEFAULT, JP_DEFAULT, B_DEFAULT, D_DEFAULT,
                                  vqe_params, noise_model=None, p_readout=0.0)
        cn = correlator_rumoroso(2, "x", 1, "x", 2.0, N,
                                  J_DEFAULT, JP_DEFAULT, B_DEFAULT, D_DEFAULT,
                                  vqe_params, noise_model=nm_ref,
                                  p_readout=params_ref["p_readout"])
        print(f"  N={N:3d}: rumore nullo = {c0.real:+.6f}{c0.imag:+.6f}i   "
              f"rumoroso = {cn.real:+.6f}{cn.imag:+.6f}i")
