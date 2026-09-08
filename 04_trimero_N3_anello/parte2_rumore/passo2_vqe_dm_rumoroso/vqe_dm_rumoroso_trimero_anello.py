"""
Parte 2, Stadio 2 -- VQE con termine DM sotto rumore (trimero ad anello).

RUOLO NELL'INSIEME DEL PACCHETTO: mirror di `vqe_dm_rumoroso_dimero.py`.
Ripete la stima del ground state con lo stesso ansatz W-2q.6 gia'
ottimizzato in Parte 1 (parametri in w2q6_params_optimal.npz), ma valutato
su un simulatore a operatore densita' con il NoiseModel dello Stadio 1
agganciato (noise_model_trimero_anello.py, wrapper su noise_model_dimero.py).

Stessa scelta di modellazione dichiarata sul dimero: si RIUSANO i
parametri gia' ottimizzati nel caso ideale, senza rioptimizzare sotto
rumore. Questo modulo misura quindi "quanto degrada un risultato VQE
ideale se lo si esegue su hardware rumoroso", non la convergenza di un
VQE noise-aware (variante non nello scope attuale per il trimero).

Osservabili:
  - energia rumorosa E = Tr[rho H]
  - fedelta' rumorosa F = <psi_exact|rho|psi_exact>, stessa semplificazione
    della fedelta' di Uhlmann gia' derivata e verificata sul dimero
    (risultati_vqe_dm_rumoroso_dimero.tex).
"""
import numpy as np
from qiskit import transpile
from qiskit.quantum_info import DensityMatrix, state_fidelity, Statevector
from qiskit_aer import AerSimulator

from trimer_ring_exact import trimer_hamiltonian_dm
from vqe_w2q6_trimero_anello import w2q6_circuit
from noise_model_trimero_anello import build_noise_model, BASIS_GATES

J, Jp, b, D, MODE = 1.0, 0.4, 2.4, 0.15, "B"


def vqe_energia_fedelta_rumorosa(vqe_params, psi_exact, noise_model=None,
                                  optimization_level=3, seed_transpiler=7):
    """Energia e fedelta' del circuito VQE (W-2q.6) su simulatore a
    operatore densita', con o senza NoiseModel.

    Ritorna (energia, fedelta', n_cx).
    """
    ansatz = w2q6_circuit().assign_parameters(vqe_params)
    H = trimer_hamiltonian_dm(J, Jp, b, MODE, D)

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
    data = np.load("w2q6_params_optimal.npz")
    vqe_params = data["params"]
    E0_exact = float(data["E_exact"])

    H = trimer_hamiltonian_dm(J, Jp, b, MODE, D).to_matrix()
    Evals, V = np.linalg.eigh(H)
    psi_exact = V[:, 0]
    imax = np.argmax(np.abs(psi_exact))
    psi_exact = psi_exact * np.exp(-1j * np.angle(psi_exact[imax]))

    print("Caso ideale (rumore nullo):")
    E, F, ncx = vqe_energia_fedelta_rumorosa(vqe_params, psi_exact, noise_model=None)
    print(f"  E = {E:.8f}   F = {F:.10f}   CNOT = {ncx}")

    print("\nCaso rumoroso (ibm_torino, riferimento):")
    nm, params = build_noise_model()
    E_n, F_n, ncx_n = vqe_energia_fedelta_rumorosa(vqe_params, psi_exact, noise_model=nm)
    print(f"  E = {E_n:.8f}   F = {F_n:.10f}   CNOT = {ncx_n}")
    print(f"  scostamento energia: {E_n - E0_exact:+.6f}")
    print(f"  perdita di fedelta' (1-F): {1 - F_n:.6f}")
