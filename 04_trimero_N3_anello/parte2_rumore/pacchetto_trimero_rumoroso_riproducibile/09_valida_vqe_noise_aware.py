import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "codice"))
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "dati"))


"""
Verifica obbligatoria di vqe_noise_aware_trimero_anello.py (Stadio 2bis)
prima di considerarlo concluso. Mirror concettuale di
validate_vqe_noise_aware_dimero.py, con una differenza di risultato
dichiarata esplicitamente (non solo di codice): sul dimero questa
estensione non trovava nessun vantaggio a riottimizzare; qui SI', e il
motivo (mescolamento fra i settori S12=1, non un limite di parametri) e'
discusso in risultati_vqe_noise_aware_trimero_anello_definitivo.tex.

  1. Verifica dell'artefatto del transpilatore: a struttura fissa
     (livello 0), il conteggio CX deve restare 6 su assegnazioni casuali
     di theta (nessuna semplificazione spuria).
  2. Riproducibilita' dei valori di riferimento gia' documentati:
     E_riuso, F_riuso, E_noise_aware, F_noise_aware, entro tolleranza
     numerica (il multistart e' stocastico, non bit-per-bit).
  3. Segno atteso: E_noise_aware < E_riuso (l'ottimizzazione diretta
     sotto rumore non puo' peggiorare l'energia rispetto al riuso dei
     parametri ideali) - assert diretto, non solo stampa.
"""
import numpy as np

from vqe_noise_aware_trimero_anello import (
    conteggio_cx, energia_rumorosa, ottimizza_vqe_noise_aware, J, Jp, b, D, MODE,
)
from trimer_ring_exact import trimer_hamiltonian_dm
from noise_model_trimero_anello import build_noise_model
from qiskit import transpile
from qiskit.quantum_info import DensityMatrix, Statevector, state_fidelity
from qiskit_aer import AerSimulator
from noise_model_trimero_anello import BASIS_GATES

data = np.load("w2q6_params_optimal.npz")
vqe_params_ideali = data["params"]

H = trimer_hamiltonian_dm(J, Jp, b, MODE, D).to_matrix()
Evals, V = np.linalg.eigh(H)
psi_exact = V[:, 0]
imax = np.argmax(np.abs(psi_exact))
psi_exact = psi_exact * np.exp(-1j * np.angle(psi_exact[imax]))

nm_ref, params_ref = build_noise_model()
Hop = trimer_hamiltonian_dm(J, Jp, b, MODE, D)

print("=" * 70)
print("1. ARTEFATTO DEL TRANSPILATORE: struttura fissa, CX deve restare 6")
print("=" * 70)
rng = np.random.default_rng(2)
for _ in range(5):
    p = rng.uniform(-np.pi, np.pi, 6)
    c0 = conteggio_cx(p, optimization_level=0)
    print(f"  theta casuale -> CX (livello 0) = {c0}")
    assert c0 == 6, "struttura fissa non ha prodotto 6 CX: verificare w_block/pma_2q_trimer_exact"
print("  -> OK")

print()
print("=" * 70)
print("2. RIPRODUCIBILITA' DEI VALORI DI RIFERIMENTO")
print("=" * 70)


def _fedelta(params, noise_model, optimization_level):
    ansatz = __import__("vqe_w2q6_trimero_anello").w2q6_circuit().assign_parameters(params)
    tqc = transpile(ansatz, basis_gates=BASIS_GATES, optimization_level=optimization_level,
                     seed_transpiler=7)
    sim = AerSimulator(method="density_matrix", noise_model=noise_model)
    tqc.save_density_matrix()
    rho = DensityMatrix(sim.run(tqc).result().data(0)["density_matrix"])
    return float(state_fidelity(rho, Statevector(psi_exact)))


E_riuso = energia_rumorosa(vqe_params_ideali, Hop, nm_ref, optimization_level=0)
F_riuso = _fedelta(vqe_params_ideali, nm_ref, optimization_level=0)
print(f"  riuso parametri ideali: E={E_riuso:.8f}  F={F_riuso:.8f}")
print(f"    (atteso: E=-5.36232432  F=0.96728547, entro 1e-3)")
assert abs(E_riuso - (-5.36232432)) < 1e-3
assert abs(F_riuso - 0.96728547) < 1e-3

params_na, E_na = ottimizza_vqe_noise_aware(nm_ref, n_start=12, seed=0, optimization_level=0)
F_na = _fedelta(params_na, nm_ref, optimization_level=0)
print(f"  VQE noise-aware:        E={E_na:.8f}  F={F_na:.8f}")
print(f"    (atteso: E=-5.36648903  F=0.95153755, entro 5e-3 -- multistart stocastico)")
assert abs(E_na - (-5.36648903)) < 5e-3
assert abs(F_na - 0.95153755) < 1e-2
print("  -> OK")

print()
print("=" * 70)
print("3. SEGNO ATTESO: l'ottimizzazione diretta non puo' peggiorare l'energia")
print("=" * 70)
print(f"  Delta_E = {E_na - E_riuso:+.6e}")
assert E_na <= E_riuso + 1e-6, "VQE noise-aware ha dato energia PEGGIORE del riuso: bug"
print("  -> OK (E_na <= E_riuso, come deve essere per costruzione)")

np.savez("vqe_noise_aware_validato.npz", params=params_na, E_na=E_na, F_na=F_na,
         E_riuso=E_riuso, F_riuso=F_riuso)
print("\nSalvato: vqe_noise_aware_validato.npz")
