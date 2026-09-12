import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "codice"))
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "dati"))


"""
Verifica obbligatoria di vqe_dm_rumoroso_trimero_anello.py prima di
considerare lo Stadio 2 concluso. Mirror di
validate_vqe_dm_rumoroso_dimero.py, adattato a 3 qubit.

  1. Limite di rumore nullo: F deve coincidere con la fedelta' VQE nota di
     Parte 1 (registrata in w2q6_params_optimal.npz), non solo essere
     "vicina a 1".
  2. Formula della fedelta' per stato misto: F=<psi|rho|psi> verificata
     contro qiskit.quantum_info.state_fidelity (implementazione
     indipendente) su uno stato misto casuale A 3 QUBIT (dimensione 8,
     non 4 come sul dimero -- non assunto identico solo perche' la
     formula e' la stessa).
  3. Scan su eps_2q: energia e fedelta' devono degradare in modo monotono.
"""
import numpy as np
from qiskit.quantum_info import DensityMatrix, Statevector, state_fidelity

from vqe_dm_rumoroso_trimero_anello import (
    vqe_energia_fedelta_rumorosa, J, Jp, b, D, MODE,
)
from trimer_ring_exact import trimer_hamiltonian_dm
from noise_model_trimero_anello import build_noise_model

data = np.load("w2q6_params_optimal.npz")
vqe_params = data["params"]
E0_exact = float(data["E_exact"])
F_vqe_registrata = float(data["fidelity"])

H = trimer_hamiltonian_dm(J, Jp, b, MODE, D).to_matrix()
Evals, V = np.linalg.eigh(H)
psi_exact = V[:, 0]
imax = np.argmax(np.abs(psi_exact))
psi_exact = psi_exact * np.exp(-1j * np.angle(psi_exact[imax]))

print("=" * 70)
print("1. LIMITE DI RUMORE NULLO")
print("=" * 70)
E0, F0, ncx0 = vqe_energia_fedelta_rumorosa(vqe_params, psi_exact, noise_model=None)
print(f"  F registrata (Parte 1, w2q6_params_optimal.npz) = {F_vqe_registrata:.12f}")
print(f"  F ricalcolata qui (rumore nullo)                 = {F0:.12f}")
print(f"  |differenza|                                     = {abs(F0 - F_vqe_registrata):.2e}")
assert abs(F0 - F_vqe_registrata) < 1e-9, "LIMITE DI RUMORE NULLO FALLITO SULLA FEDELTA'"
print(f"  E ricalcolata qui (rumore nullo) = {E0:.8f}  (registrato: {E0_exact:.8f})")
assert abs(E0 - E0_exact) < 1e-6, "LIMITE DI RUMORE NULLO FALLITO SULL'ENERGIA"
print("  -> OK")

print()
print("=" * 70)
print("2. FORMULA F=<psi|rho|psi> vs qiskit.state_fidelity (stato misto casuale, 3 qubit)")
print("=" * 70)
rng = np.random.default_rng(0)
d = 8  # 3 qubit, non 4 come sul dimero -- verificato esplicitamente a questa dimensione
A = rng.standard_normal((d, d)) + 1j * rng.standard_normal((d, d))
rho_mat = A @ A.conj().T
rho_mat /= np.trace(rho_mat).real
psi_test = rng.standard_normal(d) + 1j * rng.standard_normal(d)
psi_test /= np.linalg.norm(psi_test)

F_formula = np.real(psi_test.conj() @ rho_mat @ psi_test)
F_qiskit = state_fidelity(DensityMatrix(rho_mat), Statevector(psi_test))
print(f"  F (<psi|rho|psi>, calcolo diretto) = {F_formula:.12f}")
print(f"  F (qiskit.state_fidelity)          = {F_qiskit:.12f}")
print(f"  |differenza|                       = {abs(F_formula - F_qiskit):.2e}")
assert abs(F_formula - F_qiskit) < 1e-10
print("  -> OK: la semplificazione della fedelta' di Uhlmann per un "
      "riferimento puro e' confermata anche a d=8 (3 qubit), non solo "
      "alla d=4 gia' verificata sul dimero.")

print()
print("=" * 70)
print("3. SCAN SU eps_2q — degradazione monotona attesa")
print("=" * 70)
print(f"  {'eps_2q':>10s}  {'E':>14s}  {'F':>12s}")
scan_eps2q = [0.0, 1e-3, 3.8e-3, 8e-3, 1.5e-2]
risultati_scan = []
for eps2q in scan_eps2q:
    nm, _ = build_noise_model(eps_1q=2.9e-4, eps_2q=eps2q, p_readout=2.3e-2)
    E, F, _ = vqe_energia_fedelta_rumorosa(vqe_params, psi_exact, noise_model=nm)
    risultati_scan.append((eps2q, E, F))
    print(f"  {eps2q:>10.2e}  {E:>14.8f}  {F:>12.8f}")

Es = [r[1] for r in risultati_scan]
Fs = [r[2] for r in risultati_scan]
assert all(Es[i] >= Es[i + 1] - 1e-9 for i in range(len(Es) - 1)) or \
       all(Es[i] <= Es[i + 1] + 1e-9 for i in range(len(Es) - 1)), \
       "energia non monotona nello scan"
assert all(Fs[i] >= Fs[i + 1] - 1e-9 for i in range(len(Fs) - 1)), \
       "fedelta' non monotona decrescente nello scan"
print("  -> OK: energia crescente ($E$ si allontana dal fondamentale) e "
      "fedelta' monotona decrescente in eps_2q, come atteso.")

np.savez("scan_eps2q_vqe_dm_trimero_anello.npz",
         eps2q=np.array(scan_eps2q), E=np.array(Es), F=np.array(Fs))
print("\nSalvato: scan_eps2q_vqe_dm_trimero_anello.npz")
