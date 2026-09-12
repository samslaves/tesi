import sys
sys.path.insert(0, "codice")


"""Il correlatore "ricco" C_11^yz(t) con preparazione VQE reale, due
ansatz del Documento 2 (PMA base, 1 parametro, a rami; PMA esteso, 3
parametri) -- assente dalla prima versione di questo pacchetto (che
usa sempre ampiezze esatte per la preparazione, mai il circuito VQE
vero, benché build_correlator_circuit lo supporti già via
ansatz_params).

Punto di lavoro: b/J=-0.18, D/J=1 (lo stesso della Sez. "Nota sul punto
di lavoro" del Documento 3, non "test 2") -- qui le fedeltà dei due
ansatz sono molto diverse (0.9229 per PMA base, 1 a dodici cifre per
PMA esteso), l'occasione per vedere l'effetto di preparazione
imperfetta sul correlatore.
"""
import numpy as np
import scipy.linalg as sla
from scipy.optimize import minimize
from qiskit import QuantumCircuit, QuantumRegister
from qiskit.circuit.library import XGate, YGate, ZGate
from qiskit.quantum_info import Statevector, SparsePauliOp

from dimer_exact import dimer_hamiltonian
from ansatz_dimero import ansatz_PMA_W, ansatz_PMA_2q
from circuito_correlazioni_dimero import ground_state, _H1_H2, SITE_TO_QUBIT

b, J, D = -0.18, 1.0, 1.0
H = dimer_hamiltonian(b, J=J, D=D).to_matrix()
psi0_exact, _ = ground_state(b, J=J, D=D)

PAULI_GATE = {"x": XGate(), "y": YGate(), "z": ZGate()}


def ottimizza(qc_template, nparam, seed=0, R=15):
    """Minimizza l'ENERGIA (non la fidelity direttamente) -- per un
    ansatz incompleto (PMA base, K=1) i due criteri non danno
    necessariamente lo stesso theta ottimo; il VQE vero minimizza
    sempre l'energia, quindi e' quello il criterio corretto per
    riprodurre le fidelity gia' stabilite nel Documento 2."""
    def energia(params):
        psi = Statevector(qc_template.assign_parameters(params)).data
        return np.real(np.vdot(psi, H @ psi))
    rng = np.random.default_rng(seed)
    best = (np.inf, None)
    for _ in range(R):
        x0 = rng.uniform(-np.pi, np.pi, nparam)
        res = minimize(energia, x0, method="COBYLA", options=dict(maxiter=800, tol=1e-11))
        if res.fun < best[0]:
            best = (res.fun, res.x)
    res = minimize(energia, best[1], method="L-BFGS-B")
    if res.fun < best[0]:
        best = (res.fun, res.x)
    psi_finale = Statevector(qc_template.assign_parameters(best[1])).data
    fidelity = abs(np.vdot(psi0_exact, psi_finale)) ** 2
    return best[1], fidelity


def build_correlator_circuit_ansatz(ansatz_circuit, i, alpha, j, beta, t, N, part):
    """Mirror locale di build_correlator_circuit (circuito_correlazioni_
    dimero.py), con la SOLA differenza che l'ansatz di preparazione e'
    un argomento esplicito invece di essere fissato a pma_2q(3) --
    necessario qui per confrontare DUE ansatz diversi (base ed esteso),
    non solo quello codificato nel modulo originale."""
    a = QuantumRegister(1, "a")
    qreg = QuantumRegister(2, "q")
    qc = QuantumCircuit(a, qreg)
    qc.compose(ansatz_circuit, [qreg[0], qreg[1]], inplace=True)
    qc.h(a[0])
    q_W = qreg[SITE_TO_QUBIT[j]]
    {"x": qc.cx, "y": qc.cy, "z": qc.cz}[beta](a[0], q_W)
    H1, H2 = _H1_H2(J, b, D)
    tau = t / N
    step = sla.expm(-1j * H2 * tau) @ sla.expm(-1j * H1 * tau)
    from qiskit.circuit.library import UnitaryGate
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
    return qc


def ancilla_z(qc):
    sv = Statevector(qc)
    op = SparsePauliOp.from_sparse_list([("Z", [0], 1.0)], num_qubits=3)
    return sv.expectation_value(op).real


def correlatore_circuito(ansatz_circuit, i, alpha, j, beta, t, N):
    qc_re = build_correlator_circuit_ansatz(ansatz_circuit, i, alpha, j, beta, t, N, "re")
    qc_im = build_correlator_circuit_ansatz(ansatz_circuit, i, alpha, j, beta, t, N, "im")
    return ancilla_z(qc_re) + 1j * ancilla_z(qc_im)


print("Ottimizzazione PMA base (1 parametro, a rami)...")
qc_base = ansatz_PMA_W(b)
params_base, F_base = ottimizza(qc_base, 1, seed=1)
print(f"  fedeltà = {F_base:.6f}  (atteso ~0.9229)")

print("Ottimizzazione PMA esteso (3 parametri)...")
qc_esteso = ansatz_PMA_2q(3)
params_esteso, F_esteso = ottimizza(qc_esteso, 3, seed=2)
print(f"  fedeltà = {F_esteso:.10f}  (atteso ~1, dodici cifre)")

psi_vqe_base = Statevector(qc_base.assign_parameters(params_base)).data
psi_vqe_esteso = Statevector(qc_esteso.assign_parameters(params_esteso)).data


def classical_from_state(psi0, i, alpha, j, beta, t):
    I2 = np.eye(2, dtype=complex)
    PAULI = {"x": np.array([[0, 1], [1, 0]], dtype=complex),
             "y": np.array([[0, -1j], [1j, 0]], dtype=complex),
             "z": np.array([[1, 0], [0, -1]], dtype=complex)}

    def site_op(site, comp):
        ops = [I2, I2]; ops[site - 1] = PAULI[comp]
        return np.kron(ops[0], ops[1])
    A = site_op(i, alpha); B = site_op(j, beta)
    Ut = sla.expm(-1j * H * t)
    return np.vdot(psi0, Ut.conj().T @ A @ Ut @ B @ psi0)


t_denso = np.linspace(0, 8, 161)
t_rado = np.linspace(0, 8, 41)
N_TROTTER = 200

print("\nCalcolo curve (esatto, esatto-da-VQE, circuito vero) per entrambi gli ansatz...")
risultati = {}
for nome, psi_vqe, params, qc_t in (("base", psi_vqe_base, params_base, qc_base),
                                     ("esteso", psi_vqe_esteso, params_esteso, qc_esteso)):
    ansatz_bound = qc_t.assign_parameters(params)
    c_esatto = [abs(classical_from_state(psi0_exact, 1, "y", 1, "z", t)) for t in t_denso]
    c_da_vqe = [abs(classical_from_state(psi_vqe, 1, "y", 1, "z", t)) for t in t_denso]
    c_circuito = [abs(correlatore_circuito(ansatz_bound, 1, "y", 1, "z", t, N_TROTTER))
                  for t in t_rado]
    risultati[nome] = dict(c_esatto=c_esatto, c_da_vqe=c_da_vqe, c_circuito=c_circuito)
    print(f"  {nome}: fatto")

np.savez("dati/correlatore_da_vqe.npz",
         t_denso=t_denso, t_rado=t_rado,
         c_esatto_base=risultati["base"]["c_esatto"],
         c_da_vqe_base=risultati["base"]["c_da_vqe"],
         c_circuito_base=risultati["base"]["c_circuito"],
         c_esatto_esteso=risultati["esteso"]["c_esatto"],
         c_da_vqe_esteso=risultati["esteso"]["c_da_vqe"],
         c_circuito_esteso=risultati["esteso"]["c_circuito"],
         F_base=F_base, F_esteso=F_esteso)
print("\nSalvato: dati/correlatore_da_vqe.npz")
