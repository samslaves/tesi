"""
Parte 2, Passo 2 -- VQE con termine DM sotto rumore.

Ripete la stima del ground state con lo stesso ansatz PMA-2q.3 gia'
ottimizzato in Parte 1 (parametri in ground_state_test2.npz), ma valutato
su un simulatore a operatore densita' con il NoiseModel del Passo 1
agganciato (noise_model_dimero.py).

Scelta di modellazione dichiarata: si RIUSANO i parametri gia' ottimizzati
nel caso ideale, senza rioptimizzare sotto rumore. Il Passo 2 misura quindi
"quanto degrada un risultato VQE ideale se lo si esegue su hardware
rumoroso", non "quanto bene converge il VQE se il rumore e' presente gia'
durante l'ottimizzazione" (VQE noise-aware, variante diversa, non nello
scope attuale -- estensione naturale se restera' tempo).

Osservabili:
  - energia rumorosa E = Tr[rho H]
  - fedelta' rumorosa F = <psi_exact|rho|psi_exact>, semplificazione della
    fedelta' di Uhlmann quando uno dei due stati e' puro (derivazione nel
    documento dei risultati).
"""
import numpy as np
from qiskit import transpile
from qiskit.quantum_info import DensityMatrix, state_fidelity, Statevector
from qiskit_aer import AerSimulator

from dimer_exact import dimer_hamiltonian
from vqe_test2 import pma_2q
from noise_model_dimero import build_noise_model, BASIS_GATES

J, b, D = 1.0, 0.35, 0.80


def vqe_energia_fedelta_rumorosa(vqe_params, psi_exact, noise_model=None,
                                  optimization_level=3, seed_transpiler=7):
    """Energia e fedelta' del circuito VQE (PMA-2q.3) su simulatore a
    operatore densita', con o senza NoiseModel.

    Ritorna (energia, fedelta', n_cx).
    """
    ansatz = pma_2q(3).assign_parameters(vqe_params)
    H = dimer_hamiltonian(b=b, J=J, D=D)

    sim = AerSimulator(method="density_matrix", noise_model=noise_model)
    tqc = transpile(ansatz, basis_gates=BASIS_GATES,
                     optimization_level=optimization_level,
                     seed_transpiler=seed_transpiler)
    ncx = tqc.count_ops().get("cx", 0)
    tqc.save_density_matrix()
    result = sim.run(tqc).result()
    rho = DensityMatrix(result.data(0)["density_matrix"])

    energia = float(np.real(rho.expectation_value(H)))
    fedelta = float(state_fidelity(rho, Statevector(psi_exact)))
    return energia, fedelta, ncx


if __name__ == "__main__":
    data = np.load("ground_state_test2.npz")
    vqe_params = data["vqe_params"]
    psi_exact = data["psi0_exact"]
    E0_exact = float(data["E0_exact"])

    print("Caso ideale (rumore nullo):")
    E, F, ncx = vqe_energia_fedelta_rumorosa(vqe_params, psi_exact, noise_model=None)
    print(f"  E = {E:.8f}   F = {F:.10f}   CNOT = {ncx}")

    print("\nCaso rumoroso (ibm_torino, riferimento):")
    nm, params = build_noise_model()
    E_n, F_n, ncx_n = vqe_energia_fedelta_rumorosa(vqe_params, psi_exact, noise_model=nm)
    print(f"  E = {E_n:.8f}   F = {F_n:.10f}   CNOT = {ncx_n}")
    print(f"  scostamento energia: {E_n - E0_exact:+.6f}")
    print(f"  perdita di fedelta' (1-F): {1 - F_n:.6f}")
