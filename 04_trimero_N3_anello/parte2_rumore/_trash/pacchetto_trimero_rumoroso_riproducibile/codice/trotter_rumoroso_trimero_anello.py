"""
Parte 2, Stadio 3 -- quantum simulation (Trotter) sotto rumore (trimero ad anello).

RUOLO NELL'INSIEME DEL PACCHETTO: mirror strutturale di
`trotter_rumoroso_dimero.py`, ma generico rispetto al punto di lavoro
(J, Jp, b, D) e allo stato iniziale, perche' qui vanno coperti ESPLICITAMENTE
due scenari diversi, gia' distinti in Parte 1 dell'anello:

  A) Punto VQE (b=b_c=2.4, D=0.15): preparazione via ansatz W-2q.6 (Stadio 2)
     + N passi di Trotter. Mirror esatto dello schema del dimero.
  B) Punto R0 (b=0.05, D=1.93), PROVVISORIO (dichiarato tale in Parte 1,
     quantum_simulation_trimero_anello_applicazione.tex): nessuna
     preparazione VQE, si parte da |000> -- stesso schema della
     dimostrazione Trotter di Parte 1 sull'anello, qui reso rumoroso.

Riusa i blocchi di gate ESATTI gia' derivati e validati in Parte 1
(`trotter_trimero_anello.py`: step_field, step_Hex, step_HDM) -- non li
reimplementa. La strategia di transpilazione a blocchi (assente in Parte 1,
verificato in Stadio 1) e' scritta qui per la prima volta: il singolo passo
esterno (Hex + campo + HDM, un tau) viene transpilato UNA VOLTA in base
{rz,sx,x,cx}, poi il blocco gia' compilato e' composto N volte -- mai
ritranspilato per intero (stessa trappola gia' documentata sul dimero).
"""
import numpy as np
import scipy.linalg as sla
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import DensityMatrix, Statevector, state_fidelity
from qiskit_aer import AerSimulator

from trotter_trimero_anello import step_Hex, step_field, step_HDM, H_parts
from vqe_w2q6_trimero_anello import w2q6_circuit
from noise_model_trimero_anello import build_noise_model, BASIS_GATES

# --- due punti di lavoro, entrambi esplicitamente dichiarati -----------
PUNTO_VQE = dict(J=1.0, Jp=0.4, b=2.4, D=0.15)     # Stadio 2, mode "B"
PUNTO_R0 = dict(J=1.0, Jp=0.4, b=0.05, D=1.93)     # Parte 1, provvisorio


def build_step_block(J, Jp, b, D, t, N, optimization_level=3, seed_transpiler=7):
    """Transpila UNA VOLTA il singolo passo esterno di Trotter (Hex, poi
    campo, poi HDM -- stesso ordine di trotter_circuit in Parte 1) al suo
    costo minimo. Ritorna un QuantumCircuit gia' in base {rz,sx,x,cx}."""
    tau = t / N
    qc = QuantumCircuit(3)
    step_Hex(qc, J, Jp, tau)
    step_field(qc, b, tau)
    step_HDM(qc, J, Jp, D, tau)
    return transpile(qc, basis_gates=BASIS_GATES,
                      optimization_level=optimization_level,
                      seed_transpiler=seed_transpiler)


def build_full_circuit(J, Jp, b, D, t, N, vqe_params=None):
    """Preparazione (ansatz W-2q.6 transpilato una volta, se vqe_params non
    e' None) + N passi di Trotter (blocco compilato una volta, composto N
    volte). Se vqe_params e' None, nessuna preparazione: stato iniziale
    |000> di default del registro Qiskit (punto R0)."""
    qc = QuantumCircuit(3)
    if vqe_params is not None:
        ansatz = w2q6_circuit().assign_parameters(vqe_params)
        ansatz_block = transpile(ansatz, basis_gates=BASIS_GATES,
                                  optimization_level=3, seed_transpiler=7)
        qc.compose(ansatz_block, [0, 1, 2], inplace=True)
    step_block = build_step_block(J, Jp, b, D, t, N)
    for _ in range(N):
        qc.compose(step_block, [0, 1, 2], inplace=True)
    return qc


def target_state(J, Jp, b, D, t, psi0):
    """Stato bersaglio fisico: evoluzione esatta e continua (no Trotter, no
    rumore) a partire da psi0, riusando H_parts di Parte 1 (stessa sorgente
    Hamiltoniana del benchmark esatto, zero ambiguita' di convenzione)."""
    H0, H_DM = H_parts(J, Jp, b, D)
    U = sla.expm(-1j * (H0 + H_DM) * t)
    return U @ psi0


def fedelta_trotter_rumoroso(J, Jp, b, D, t, N, psi0, noise_model=None,
                              vqe_params=None):
    """Fedelta' rispetto allo stato bersaglio fisico, dopo N passi di
    Trotter rumorosi. Ritorna (fedelta', n_cx_totali)."""
    qc = build_full_circuit(J, Jp, b, D, t, N, vqe_params=vqe_params)
    ncx = qc.count_ops().get("cx", 0)

    sim = AerSimulator(method="density_matrix", noise_model=noise_model)
    qc = qc.copy()
    qc.save_density_matrix()
    result = sim.run(qc).result()
    rho = DensityMatrix(result.data(0)["density_matrix"])

    psi_t = target_state(J, Jp, b, D, t, psi0)
    F = float(state_fidelity(rho, Statevector(psi_t)))
    return F, ncx


if __name__ == "__main__":
    nm_ref, _ = build_noise_model()
    psi0_000 = np.zeros(8, dtype=complex); psi0_000[0] = 1.0

    print("=" * 78)
    print("SCENARIO A -- punto VQE (b=2.4, D=0.15), preparazione W-2q.6")
    print("=" * 78)
    data = np.load("w2q6_params_optimal.npz")
    vqe_params = data["params"]
    # Stato bersaglio: deve evolvere dallo stesso stato che il circuito
    # prepara (il fondamentale ESATTO a questo punto), non da |000> -- il
    # circuito applica l'ansatz PRIMA di Trotter, quindi il bersaglio deve
    # partire da dove l'ansatz porta, non dal registro appena inizializzato.
    from trimer_ring_exact import trimer_hamiltonian_dm
    H_vqe = trimer_hamiltonian_dm(PUNTO_VQE["J"], PUNTO_VQE["Jp"],
                                   PUNTO_VQE["b"], "B", PUNTO_VQE["D"]).to_matrix()
    Evals, V = np.linalg.eigh(H_vqe)
    psi0_vqe_exact = V[:, 0]
    imax = np.argmax(np.abs(psi0_vqe_exact))
    psi0_vqe_exact = psi0_vqe_exact * np.exp(-1j * np.angle(psi0_vqe_exact[imax]))

    t_A = 2.0
    print(f"{'N':>4} {'CNOT':>6} {'F (rumore nullo)':>18} {'F (rumore ibm_torino)':>22}")
    for N in [1, 2, 5, 10, 20, 40, 80]:
        F0, ncx = fedelta_trotter_rumoroso(**PUNTO_VQE, t=t_A, N=N, psi0=psi0_vqe_exact,
                                            noise_model=None, vqe_params=vqe_params)
        Fn, _ = fedelta_trotter_rumoroso(**PUNTO_VQE, t=t_A, N=N, psi0=psi0_vqe_exact,
                                          noise_model=nm_ref, vqe_params=vqe_params)
        print(f"{N:>4} {ncx:>6} {F0:>18.10f} {Fn:>22.10f}")

    print()
    print("=" * 78)
    print("SCENARIO B -- punto R0 (b=0.05, D=1.93), da |000>, nessuna preparazione")
    print("=" * 78)
    t_B = 2.0
    print(f"{'N':>4} {'CNOT':>6} {'F (rumore nullo)':>18} {'F (rumore ibm_torino)':>22}")
    for N in [1, 2, 5, 10, 20, 40, 80]:
        F0, ncx = fedelta_trotter_rumoroso(**PUNTO_R0, t=t_B, N=N, psi0=psi0_000,
                                            noise_model=None, vqe_params=None)
        Fn, _ = fedelta_trotter_rumoroso(**PUNTO_R0, t=t_B, N=N, psi0=psi0_000,
                                          noise_model=nm_ref, vqe_params=None)
        print(f"{N:>4} {ncx:>6} {F0:>18.10f} {Fn:>22.10f}")
