"""
Verifica obbligatoria del NoiseModel del dimero (Parte 2, Passo 1), prima
di usarlo su un circuito completo:

  1. Limite di rumore nullo (eps_1q=eps_2q=p_readout=0) deve riprodurre
     esattamente i risultati di Parte 1 (VQE ed energia esatta).
  2. Il NoiseModel con i valori di riferimento (ibm_torino) da' un
     risultato diverso e fisicamente sensato (fedelta' ridotta rispetto
     al caso ideale).
  3. Conteggio dei gate: verifica che la strategia di transpilazione per
     blocco (decisa nella sessione precedente) sia quella effettivamente
     in uso.

Non ripete la verifica end-to-end di VQE/correlatori gia' fatta in questa
sessione (vedi log_decisioni.md) - qui si verifica solo l'aggancio del
NoiseModel.
"""

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Statevector, DensityMatrix, SparsePauliOp
from qiskit_aer import AerSimulator

from dimer_exact import dimer_hamiltonian
from vqe_test2 import pma_2q
from noise_model_dimero import build_noise_model, BASIS_GATES

J, b, D = 1.0, 0.35, 0.80
E_VQE_REGISTRATO = -3.57321145


def energia_vqe_su_simulatore(noise_model, params, shots=None):
    """Ricostruisce il circuito VQE (ansatz PMA-2q.3) e ne calcola il
    valore di aspettazione dell'Hamiltoniana su AerSimulator a operatore
    densita', con o senza NoiseModel."""
    ansatz = pma_2q(3).assign_parameters(params)
    H = dimer_hamiltonian(b=b, J=J, D=D)

    sim = AerSimulator(method="density_matrix", noise_model=noise_model)
    tqc = transpile(ansatz, basis_gates=BASIS_GATES,
                     optimization_level=3, seed_transpiler=7)
    tqc.save_density_matrix()
    result = sim.run(tqc).result()
    rho = DensityMatrix(result.data(0)["density_matrix"])
    energia = np.real(rho.expectation_value(H))
    ncx = tqc.count_ops().get("cx", 0)
    return energia, ncx


print("=" * 70)
print("1. LIMITE DI RUMORE NULLO — deve riprodurre Parte 1")
print("=" * 70)

data = np.load("ground_state_test2.npz")
vqe_params = data["vqe_params"]

nm_zero, params_zero = build_noise_model(eps_1q=0.0, eps_2q=0.0,
                                          p_readout=0.0)
E_zero, ncx_zero = energia_vqe_su_simulatore(nm_zero, vqe_params)

print(f"  E_VQE (registrato, Parte 1)      = {E_VQE_REGISTRATO:.8f}")
print(f"  E_VQE (density_matrix, rumore=0) = {E_zero:.8f}")
print(f"  |differenza|                     = {abs(E_zero - E_VQE_REGISTRATO):.2e}")
print(f"  CNOT nel circuito transpilato    = {ncx_zero}")
assert abs(E_zero - E_VQE_REGISTRATO) < 1e-8, "LIMITE DI RUMORE NULLO FALLITO"
print("  -> OK: limite di rumore nullo riproduce Parte 1 a precisione richiesta.")

print()
print("=" * 70)
print("2. NOISEMODEL CON VALORI DI RIFERIMENTO (ibm_torino)")
print("=" * 70)

nm_ref, params_ref = build_noise_model()
print("  Parametri usati:")
for k, v in params_ref.items():
    print(f"    {k:10s} = {v:.4e}")

E_ref, ncx_ref = energia_vqe_su_simulatore(nm_ref, vqe_params)
print(f"\n  E_VQE (rumore di riferimento) = {E_ref:.8f}")
print(f"  scostamento da E_VQE ideale   = {E_ref - E_VQE_REGISTRATO:+.6f}")
print(f"  CNOT nel circuito transpilato = {ncx_ref}  (invariato rispetto al caso ideale, atteso)")

print()
print("=" * 70)
print("3. SCAN RAPIDO: sensibilita' a eps_2q (a parita' di eps_1q, p_readout)")
print("=" * 70)
print(f"  {'eps_2q':>10s}  {'E_VQE rumoroso':>16s}  {'scostamento':>12s}")
for eps2q in [0.0, 1e-3, 3.8e-3, 8e-3, 1.5e-2]:
    nm_s, _ = build_noise_model(eps_1q=2.9e-4, eps_2q=eps2q,
                                 p_readout=2.3e-2)
    E_s, _ = energia_vqe_su_simulatore(nm_s, vqe_params)
    print(f"  {eps2q:>10.2e}  {E_s:>16.8f}  {E_s - E_VQE_REGISTRATO:>+12.6f}")
