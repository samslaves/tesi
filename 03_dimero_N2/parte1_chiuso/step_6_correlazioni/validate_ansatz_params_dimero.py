"""
Ricostruito da zero secondo la descrizione in log_decisioni.md (sessione
3 settembre 2026, "ansatz_params per il dimero -- lacuna colmata"), perche'
il file originale non e' stato ritrovato. Tre controlli, come descritti:

  1. consistenza fra le due preparazioni (ampiezze esatte vs ansatz_params)
     su 3 correlatori diversi;
  2. nessuna regressione sul percorso ansatz_params=None;
  3. costo in gate: preparazione VQE vs preparazione esatta.

Ogni numero qui sotto e' ricalcolato adesso, non copiato dal log.
"""
import numpy as np
from qiskit import transpile

from circuito_correlazioni_dimero import (
    ground_state, build_correlator_circuit, correlator_from_circuit,
)
from vqe_test2 import pma_2q
from noise_model_dimero import BASIS_GATES

J, b, D = 1.0, 0.35, 0.80
data = np.load("ground_state_test2.npz")
vqe_params = data["vqe_params"]
fidelity_registrata = float(data["fidelity"])

print("=" * 70)
print("0. Corrispondenza qubit: nessuna permutazione necessaria?")
print("=" * 70)
psi_esatto, _ = ground_state(b, J, D)
from qiskit.quantum_info import Statevector
psi_ansatz = Statevector(pma_2q(3).assign_parameters(vqe_params)).data
fid_diretta = abs(np.vdot(psi_esatto, psi_ansatz)) ** 2
print(f"  fidelity |<esatto|ansatz>|^2 (nessun riordino) = {fid_diretta:.14f}")
print(f"  1 - fidelity = {1 - fid_diretta:.3e}")
print(f"  fidelity registrata in ground_state_test2.npz = {fidelity_registrata:.14f}")
assert abs(fid_diretta - fidelity_registrata) < 1e-12
print("  -> OK: confermato, nessuna permutazione di qubit necessaria.")

print()
print("=" * 70)
print("1. CONSISTENZA fra le due preparazioni, su 3 correlatori diversi")
print("=" * 70)
cases = [(2, "x", 1, "x"), (1, "z", 1, "z"), (1, "x", 1, "y")]
N = 200
t = 0.5
print(f"{'correlatore':<12} {'esatto (psi0=None)':>22} {'ansatz_params':>22} {'|diff|':>10}")
for (i, al, j, be) in cases:
    c_esatto = correlator_from_circuit(i, al, j, be, t, N, J, b, D, psi0=None)
    c_ansatz = correlator_from_circuit(i, al, j, be, t, N, J, b, D,
                                        ansatz_params=vqe_params)
    diff = abs(c_esatto - c_ansatz)
    label = f"C_{i}{j}^{al}{be}"
    print(f"{label:<12} {c_esatto.real:+.6f}{c_esatto.imag:+.6f}i "
          f"{c_ansatz.real:+.6f}{c_ansatz.imag:+.6f}i   {diff:.3e}")
print("  (il log dichiarava uno scarto atteso ~1e-6--1e-7)")

print()
print("=" * 70)
print("2. NESSUNA REGRESSIONE sul percorso ansatz_params=None")
print("=" * 70)
import scipy.linalg as sla
from dimer_exact import dimer_hamiltonian


def site_op(site, alpha):
    paulis = {
        "x": np.array([[0, 1], [1, 0]], dtype=complex),
        "y": np.array([[0, -1j], [1j, 0]], dtype=complex),
        "z": np.diag([1, -1]).astype(complex),
    }
    I2 = np.eye(2, dtype=complex)
    P = paulis[alpha]
    return np.kron(P, I2) if site == 1 else np.kron(I2, P)


H = dimer_hamiltonian(b=b, J=J, D=D).to_matrix()
psi0, _ = ground_state(b, J, D)


def classical_exact(i, alpha, j, beta, t):
    U = sla.expm(-1j * H * t)
    V, W = site_op(i, alpha), site_op(j, beta)
    return np.vdot(psi0, U.conj().T @ V @ U @ W @ psi0)


c_ref = classical_exact(2, "x", 1, "x", 0.5)
c_none = correlator_from_circuit(2, "x", 1, "x", 0.5, 200, J, b, D, psi0=None)
resid = abs(c_ref - c_none)
print(f"  C_21^xx(t=0.5, N=200), psi0=None: residuo di Trotter = {resid:.3e}")
print("  (atteso: residuo piccolo e coerente con la Fig. gia' validata "
      "in Parte 1, non zero -- e' comunque Trotter al prim'ordine)")

print()
print("=" * 70)
print("3. COSTO IN GATE: preparazione VQE vs preparazione esatta")
print("=" * 70)
print("(transpilazione blocco per blocco, MAI sull'intero circuito insieme:")
print(" transpilare tutto insieme collassa gli N passi di Trotter e da'")
print(" un conteggio falsato -- stessa cautela gia' in uso in")
print(" correlatori_rumorosi_dimero.py)")
import scipy.linalg as sla
from qiskit import QuantumCircuit
from qiskit.circuit.library import UnitaryGate
from circuito_correlazioni_dimero import _H1_H2, PAULI_GATE


def transpila(qc):
    return transpile(qc, basis_gates=BASIS_GATES, optimization_level=3,
                      seed_transpiler=7)


N_test = 5
t_test = 2.0
tau = t_test / N_test
H1, H2 = _H1_H2(J, b, D)
step = sla.expm(-1j * H2 * tau) @ sla.expm(-1j * H1 * tau)
qc_step = QuantumCircuit(2); qc_step.append(UnitaryGate(step), [0, 1])
cx_per_step = transpila(qc_step).count_ops().get("cx", 0)

qc_prep_esatto = QuantumCircuit(2); qc_prep_esatto.prepare_state(psi0, [0, 1])
cx_prep_esatto = transpila(qc_prep_esatto).count_ops().get("cx", 0)

qc_prep_vqe = pma_2q(3).assign_parameters(vqe_params)
cx_prep_vqe = transpila(qc_prep_vqe).count_ops().get("cx", 0)

qc_ctrl = QuantumCircuit(2); qc_ctrl.h(0); qc_ctrl.cx(0, 1)
cx_ctrl = transpila(qc_ctrl).count_ops().get("cx", 0)

qc_final = QuantumCircuit(2)
qc_final.append(PAULI_GATE["x"].control(1, ctrl_state=0), [0, 1]); qc_final.h(0)
cx_final = transpila(qc_final).count_ops().get("cx", 0)

totale_esatto = cx_prep_esatto + cx_ctrl + N_test * cx_per_step + cx_final
totale_vqe = cx_prep_vqe + cx_ctrl + N_test * cx_per_step + cx_final
print(f"  CNOT per singolo passo di Trotter: {cx_per_step}")
print(f"  CNOT preparazione esatta:  {cx_prep_esatto}")
print(f"  CNOT preparazione VQE:     {cx_prep_vqe}")
print(f"  CNOT blocco controlled-W:  {cx_ctrl}   blocco finale: {cx_final}")
print(f"  TOTALE (N={N_test}) con preparazione esatta: {totale_esatto}")
print(f"  TOTALE (N={N_test}) con preparazione VQE:    {totale_vqe}")
print(f"  differenza: {totale_vqe - totale_esatto}")
print("  (il log dichiarava 19 vs 18, cioe' +1 CNOT per la preparazione VQE)")
assert totale_esatto == 18 and totale_vqe == 19, \
    "il conteggio blocco-per-blocco non coincide con quanto dichiarato nel log"
print("  -> OK: coincide esattamente.")
