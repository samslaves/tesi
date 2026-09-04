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
    return transpile(qc, basis_gates=BASIS_GATES,
                      optimization_level=optimization_level,
                      seed_transpiler=seed_transpiler)


def _prep_block(ansatz_params):
    ansatz = pma_2q(3).assign_parameters(ansatz_params)
    return _transpile_once(ansatz)


def _ctrl_W_block(beta):
    """H sull'ancilla + controlled-beta su (ancilla, target). 2 qubit
    locali: 0=ancilla, 1=target."""
    qc = QuantumCircuit(2)
    qc.h(0)
    {"x": qc.cx, "y": qc.cy, "z": qc.cz}[beta](0, 1)
    return _transpile_once(qc)


def _trotter_step_block(J, b, D, t, N):
    tau = t / N
    H1 = dimer_hamiltonian(b=b, J=J, D=0.0).to_matrix()
    H2 = dimer_hamiltonian(b=0.0, J=0.0, D=D).to_matrix()
    step = sla.expm(-1j * H2 * tau) @ sla.expm(-1j * H1 * tau)
    qc = QuantumCircuit(2)
    qc.append(UnitaryGate(step), [0, 1])
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


def build_noisy_correlator_circuit(i, alpha, j, beta, t, N, J, b, D, part,
                                    ansatz_params):
    """Circuito completo a 3 qubit (0=ancilla, 1=site2, 2=site1), interamente
    gia' in base {rz,sx,x,cx} -- pronto per essere eseguito senza ulteriore
    transpilazione."""
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
    dopo, analiticamente."""
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
    e di lettura (via p_readout, applicato analiticamente)."""
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
