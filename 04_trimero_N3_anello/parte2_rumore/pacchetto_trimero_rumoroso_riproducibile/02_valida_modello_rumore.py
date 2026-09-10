import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "codice"))
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "dati"))


"""
Verifica obbligatoria del NoiseModel applicato al trimero ad anello (Parte 2,
Stadio 1), prima di usarlo su un circuito completo a 3 qubit.

RUOLO NELL'INSIEME DEL PACCHETTO: prima verifica dell'aggancio del
modello di rumore (esposto da `noise_model_trimero_anello.py`, wrapper
sottile su `noise_model_dimero.py` -- Parte 2 del dimero) al sistema a 3
spin. La logica del NoiseModel NON viene duplicata ne' riscritta: e'
gia' indipendente dal numero di qubit (usa add_all_qubit_quantum_error /
add_all_qubit_readout_error, che si applicano a tutti i qubit del
circuito su cui gira, quale che sia N), quindi il riuso e' diretto.
Questo script lo dimostra empiricamente sul circuito VQE+DM dell'anello
(ansatz W-2q.6, 3 qubit), invece di darlo per assunto.

Controlli:
  1. Limite di rumore nullo deve riprodurre l'energia VQE di Parte 1
     (verificata qui stesso, rieseguendo vqe_w2q6_trimero_anello.py).
  2. Il NoiseModel con i valori di riferimento (ibm_torino) da' un risultato
     diverso e fisicamente sensato (energia piu' alta del fondamentale).
  3. Conteggio dei gate: singola transpilazione del circuito VQE (non
     ripetuto N volte come Trotter/correlatori, quindi qui basta una
     transpilazione diretta, non ancora la strategia "a blocchi" che serve
     dallo Stadio 3 in poi).
"""

import numpy as np
from qiskit import transpile
from qiskit.quantum_info import DensityMatrix
from qiskit_aer import AerSimulator

from trimer_ring_exact import trimer_hamiltonian_dm
from vqe_w2q6_trimero_anello import w2q6_circuit, _ground_state
from noise_model_trimero_anello import build_noise_model, BASIS_GATES

J, Jp, b, D, MODE = 1.0, 0.4, 2.4, 0.15, "B"


def energia_vqe_su_simulatore(noise_model, params):
    """Ricostruisce il circuito VQE (ansatz W-2q.6, 3 qubit) e ne calcola il
    valore di aspettazione dell'Hamiltoniana su AerSimulator a operatore
    densita', con o senza NoiseModel.

    RUOLO NEL MODULO: nucleo dei controlli 1-3. RUOLO NELL'INSIEME: verra'
    riusato tal quale allo Stadio 2 (VQE con DM sotto rumore) come base per
    la funzione di costo rumorosa."""
    ansatz = w2q6_circuit().assign_parameters(params)
    H = trimer_hamiltonian_dm(J, Jp, b, MODE, D)

    sim = AerSimulator(method="density_matrix", noise_model=noise_model)
    tqc = transpile(ansatz, basis_gates=BASIS_GATES,
                     optimization_level=3, seed_transpiler=7)
    tqc.save_density_matrix()
    result = sim.run(tqc).result()
    rho = DensityMatrix(result.data(0)["density_matrix"])
    energia = np.real(rho.expectation_value(H))
    ncx = tqc.count_ops().get("cx", 0)
    return energia, ncx


data = np.load("w2q6_params_optimal.npz")
vqe_params = data["params"]
E_VQE_REGISTRATO = float(data["E_vqe"])

print("=" * 70)
print("1. LIMITE DI RUMORE NULLO — deve riprodurre Parte 1 (anello)")
print("=" * 70)

nm_zero, _ = build_noise_model(eps_1q=0.0, eps_2q=0.0, p_readout=0.0)
E_zero, ncx_zero = energia_vqe_su_simulatore(nm_zero, vqe_params)

print(f"  E_VQE (registrato, Parte 1)      = {E_VQE_REGISTRATO:.10f}")
print(f"  E_VQE (density_matrix, rumore=0) = {E_zero:.10f}")
print(f"  |differenza|                     = {abs(E_zero - E_VQE_REGISTRATO):.2e}")
print(f"  CNOT nel circuito transpilato    = {ncx_zero}")
assert abs(E_zero - E_VQE_REGISTRATO) < 1e-8, "LIMITE DI RUMORE NULLO FALLITO"
print("  -> OK: limite di rumore nullo riproduce Parte 1 a precisione richiesta.")

print()
print("=" * 70)
print("2. NOISEMODEL CON VALORI DI RIFERIMENTO (ibm_torino)")
print("=" * 70)

nm_ref, params_ref = build_noise_model()
print("  Parametri usati (condivisi col dimero, stessa calibrazione):")
for k, v in params_ref.items():
    print(f"    {k:10s} = {v:.4e}")

E_ref, ncx_ref = energia_vqe_su_simulatore(nm_ref, vqe_params)
print(f"\n  E_VQE (rumore di riferimento) = {E_ref:.8f}")
print(f"  scostamento da E_VQE ideale   = {E_ref - E_VQE_REGISTRATO:+.6f}")
print(f"  CNOT nel circuito transpilato = {ncx_ref}")
assert E_ref > E_VQE_REGISTRATO, "energia rumorosa non superiore all'ideale: sospetto"
print("  -> OK: energia rumorosa piu' alta del fondamentale, come atteso fisicamente.")

print()
print("=" * 70)
print("3. SCAN RAPIDO: sensibilita' a eps_2q (a parita' di eps_1q, p_readout)")
print("=" * 70)
print(f"  {'eps_2q':>10s}  {'E_VQE rumoroso':>16s}  {'scostamento':>12s}  {'CNOT':>5s}")
for eps2q in [0.0, 1e-3, 3.8e-3, 8e-3, 1.5e-2]:
    nm_s, _ = build_noise_model(eps_1q=2.9e-4, eps_2q=eps2q, p_readout=2.3e-2)
    E_s, ncx_s = energia_vqe_su_simulatore(nm_s, vqe_params)
    print(f"  {eps2q:>10.2e}  {E_s:>16.8f}  {E_s - E_VQE_REGISTRATO:>+12.6f}  {ncx_s:>5d}")
