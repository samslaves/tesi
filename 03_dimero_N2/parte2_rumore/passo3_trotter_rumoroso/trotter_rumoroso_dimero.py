"""
Parte 2, Passo 3 -- quantum simulation (Trotter) sotto rumore.

Prima applicazione reale della strategia decisa nella sessione precedente:
il singolo passo di Trotter viene transpilato UNA VOLTA al suo costo minimo
(3 CNOT), poi il blocco gia' compilato viene composto N volte -- MAI
ritranspilato per intero (altrimenti il transpiler fonde gli N passi in un
unico blocco a costo costante, cancellando la dipendenza da N: vedi
log_decisioni.md, sessione precedente).

Osservabile: fedelta' rispetto allo stato bersaglio FISICO, cioe' evoluto
in modo continuo ed esatto (nessun Trotter, nessun rumore) a partire dal
ground state esatto:

    |psi_target(t)> = exp(-iHt) |psi0_exact>
    F(N, rumore) = <psi_target(t)| rho_N |psi_target(t)>

dove rho_N e' lo stato ottenuto da: preparazione (ansatz VQE, come nel
Passo 2) -> N passi di Trotter rumorosi. Questa singola quantita' impacchetta
tutti e tre i contributi caratterizzati nella sessione precedente:
preparazione (costante in N), Trotter (decresce con N), rumore accumulato
(cresce con N).
"""
import numpy as np
import scipy.linalg as sla
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import UnitaryGate
from qiskit.quantum_info import DensityMatrix, Statevector, state_fidelity
from qiskit_aer import AerSimulator

from dimer_exact import dimer_hamiltonian
from vqe_test2 import pma_2q
from noise_model_dimero import build_noise_model, BASIS_GATES

J, b, D = 1.0, 0.35, 0.80


def build_step_block(t, N, optimization_level=3, seed_transpiler=7):
    """Transpila UNA VOLTA il singolo passo di Trotter (H1 poi H2, come
    trotter_dimero.py) al suo costo minimo. Ritorna un QuantumCircuit gia'
    in base {rz,sx,x,cx} -- da riusare via compose(), mai da ritranspilare
    per intero insieme alle sue ripetizioni."""
    tau = t / N
    H1 = dimer_hamiltonian(b=b, J=J, D=0.0).to_matrix()
    H2 = dimer_hamiltonian(b=0.0, J=0.0, D=D).to_matrix()
    step = sla.expm(-1j * H2 * tau) @ sla.expm(-1j * H1 * tau)
    qc = QuantumCircuit(2)
    qc.append(UnitaryGate(step), [0, 1])
    return transpile(qc, basis_gates=BASIS_GATES,
                      optimization_level=optimization_level,
                      seed_transpiler=seed_transpiler)


def build_full_circuit(vqe_params, t, N):
    """Ansatz VQE (preparazione, Passo 2) + N passi di Trotter, blocco
    compilato una volta e composto (mai ritranspilato per intero).
    L'ansatz stesso contiene il gate custom RBS (non nativo per Aer):
    va transpilato in base {rz,sx,x,cx} una sola volta, come il passo di
    Trotter -- stessa logica, stesso motivo."""
    ansatz = pma_2q(3).assign_parameters(vqe_params)
    ansatz_block = transpile(ansatz, basis_gates=BASIS_GATES,
                              optimization_level=3, seed_transpiler=7)
    step_block = build_step_block(t, N)

    qc = QuantumCircuit(2)
    qc.compose(ansatz_block, [0, 1], inplace=True)
    for _ in range(N):
        qc.compose(step_block, [0, 1], inplace=True)
    return qc


def target_state(psi0_exact, t):
    """Stato bersaglio fisico: evoluzione esatta e continua (no Trotter,
    no rumore) del ground state esatto."""
    H = dimer_hamiltonian(b=b, J=J, D=D).to_matrix()
    U = sla.expm(-1j * H * t)
    return U @ psi0_exact


def fedelta_trotter_rumoroso(vqe_params, psi0_exact, t, N, noise_model=None):
    """Fedelta' rispetto allo stato bersaglio fisico, dopo N passi di
    Trotter rumorosi. Ritorna (fedelta', n_cx_totali)."""
    qc = build_full_circuit(vqe_params, t, N)
    ncx = qc.count_ops().get("cx", 0)

    sim = AerSimulator(method="density_matrix", noise_model=noise_model)
    qc = qc.copy()
    qc.save_density_matrix()
    result = sim.run(qc).result()
    rho = DensityMatrix(result.data(0)["density_matrix"])

    psi_t = target_state(psi0_exact, t)
    F = float(state_fidelity(rho, Statevector(psi_t)))
    return F, ncx


if __name__ == "__main__":
    data = np.load("ground_state_test2.npz")
    vqe_params = data["vqe_params"]
    psi0_exact = data["psi0_exact"]
    t = 2.0

    nm_ref, _ = build_noise_model()

    print(f"{'N':>4} {'CNOT':>6} {'F (rumore nullo)':>18} {'F (rumore ibm_torino)':>22}")
    for N in [1, 2, 5, 10, 20, 40, 80, 160]:
        F0, ncx = fedelta_trotter_rumoroso(vqe_params, psi0_exact, t, N, noise_model=None)
        Fn, _ = fedelta_trotter_rumoroso(vqe_params, psi0_exact, t, N, noise_model=nm_ref)
        print(f"{N:>4} {ncx:>6} {F0:>18.10f} {Fn:>22.10f}")
