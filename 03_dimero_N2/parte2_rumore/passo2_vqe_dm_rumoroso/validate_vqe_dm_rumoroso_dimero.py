"""
Verifica obbligatoria di vqe_dm_rumoroso_dimero.py prima di considerare il
Passo 2 concluso.

  1. Limite di rumore nullo: F deve coincidere con la fedelta' VQE nota di
     Parte 1 (registrata in ground_state_test2.npz), non solo essere
     "vicina a 1".
  2. Formula della fedelta' per stato misto: F=<psi|rho|psi> verificata
     contro qiskit.quantum_info.state_fidelity (implementazione
     indipendente) su uno stato misto casuale (non solo sul caso
     particolare del VQE).
  3. Scan su eps_2q: energia e fedelta' devono degradare in modo monotono.
"""
import numpy as np
from qiskit.quantum_info import DensityMatrix, Statevector, state_fidelity

from vqe_dm_rumoroso_dimero import vqe_energia_fedelta_rumorosa
from noise_model_dimero import build_noise_model

data = np.load("ground_state_test2.npz")
vqe_params = data["vqe_params"]
psi_exact = data["psi0_exact"]
E0_exact = float(data["E0_exact"])
F_vqe_registrata = float(data["fidelity"])

print("=" * 70)
print("1. LIMITE DI RUMORE NULLO")
print("=" * 70)
E0, F0, ncx0 = vqe_energia_fedelta_rumorosa(vqe_params, psi_exact, noise_model=None)
print(f"  F registrata (Parte 1, ground_state_test2.npz) = {F_vqe_registrata:.12f}")
print(f"  F ricalcolata qui (rumore nullo)                = {F0:.12f}")
print(f"  |differenza|                                    = {abs(F0 - F_vqe_registrata):.2e}")
assert abs(F0 - F_vqe_registrata) < 1e-9, "LIMITE DI RUMORE NULLO FALLITO SULLA FEDELTA'"
print(f"  E ricalcolata qui (rumore nullo) = {E0:.8f}  (registrato: {E0_exact:.8f})")
assert abs(E0 - E0_exact) < 1e-6, "LIMITE DI RUMORE NULLO FALLITO SULL'ENERGIA"
print("  -> OK")

print()
print("=" * 70)
print("2. FORMULA F=<psi|rho|psi> vs qiskit.state_fidelity (stato misto casuale)")
print("=" * 70)
rng = np.random.default_rng(0)
A = rng.standard_normal((4, 4)) + 1j * rng.standard_normal((4, 4))
rho_mat = A @ A.conj().T
rho_mat /= np.trace(rho_mat).real
psi_test = rng.standard_normal(4) + 1j * rng.standard_normal(4)
psi_test /= np.linalg.norm(psi_test)

F_formula = np.real(psi_test.conj() @ rho_mat @ psi_test)
F_qiskit = state_fidelity(DensityMatrix(rho_mat), Statevector(psi_test))
print(f"  F (<psi|rho|psi>, calcolo diretto) = {F_formula:.12f}")
print(f"  F (qiskit.state_fidelity)          = {F_qiskit:.12f}")
print(f"  |differenza|                       = {abs(F_formula - F_qiskit):.2e}")
assert abs(F_formula - F_qiskit) < 1e-10
print("  -> OK: la semplificazione della fedelta' di Uhlmann per un "
      "riferimento puro è confermata anche su uno stato misto generico, "
      "non solo sul caso VQE (dove l'infedeltà era troppo piccola per "
      "essere un test stringente).")

print()
print("=" * 70)
print("3. SCAN SU eps_2q — degradazione monotona attesa")
print("=" * 70)
print(f"  {'eps_2q':>10s}  {'E':>14s}  {'F':>12s}")
for eps2q in [0.0, 1e-3, 3.8e-3, 8e-3, 1.5e-2]:
    nm, _ = build_noise_model(eps_1q=2.9e-4, eps_2q=eps2q, p_readout=2.3e-2)
    E, F, _ = vqe_energia_fedelta_rumorosa(vqe_params, psi_exact, noise_model=nm)
    print(f"  {eps2q:>10.2e}  {E:>14.8f}  {F:>12.8f}")
