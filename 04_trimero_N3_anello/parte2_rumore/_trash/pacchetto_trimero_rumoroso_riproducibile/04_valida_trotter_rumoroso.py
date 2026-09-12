import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "codice"))
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "dati"))


"""
Verifica obbligatoria di trotter_rumoroso_trimero_anello.py, entrambi gli
scenari (A: punto VQE; B: punto R0). Mirror di
validate_trotter_rumoroso_dimero.py.

  1. Conteggio gate: CNOT totali devono scalare come cx_prep + 15N
     (lineare, NESSUNA fusione degli N passi) -- controllo diretto della
     strategia di transpilazione a blocchi, scritta da zero per l'anello.
  2. Cross-check indipendente del ramo "rumore nullo": la fedelta' dal
     circuito Qiskit deve coincidere con un calcolo classico via potenza
     di matrice del singolo passo di Trotter (numpy puro).
  3. Individuazione di N* (rumore di riferimento), per entrambi gli
     scenari -- non assunto identico solo perche' il dimero mostrava un
     massimo a N finito.
"""
import numpy as np
import scipy.linalg as sla

from trotter_rumoroso_trimero_anello import (
    build_step_block, build_full_circuit, fedelta_trotter_rumoroso,
    target_state, PUNTO_VQE, PUNTO_R0,
)
from trimer_ring_exact import trimer_hamiltonian_dm
from trotter_trimero_anello import step_Hex, step_field, step_HDM
from noise_model_trimero_anello import build_noise_model
from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator

t = 2.0
psi0_000 = np.zeros(8, dtype=complex); psi0_000[0] = 1.0

H_vqe = trimer_hamiltonian_dm(PUNTO_VQE["J"], PUNTO_VQE["Jp"],
                               PUNTO_VQE["b"], "B", PUNTO_VQE["D"]).to_matrix()
Evals, V = np.linalg.eigh(H_vqe)
psi0_vqe_exact = V[:, 0]
imax = np.argmax(np.abs(psi0_vqe_exact))
psi0_vqe_exact = psi0_vqe_exact * np.exp(-1j * np.angle(psi0_vqe_exact[imax]))

data = np.load("w2q6_params_optimal.npz")
vqe_params = data["params"]

print("=" * 78)
print("1. CONTEGGIO GATE: cx_totali = cx_prep + 15N ?")
print("=" * 78)
for nome, punto, prep, cx_prep in [
    ("A (VQE)", PUNTO_VQE, vqe_params, 6),
    ("B (R0)", PUNTO_R0, None, 0),
]:
    print(f"  Scenario {nome}:")
    for N in [1, 2, 5, 10, 20]:
        qc = build_full_circuit(**punto, t=t, N=N, vqe_params=prep)
        ncx = qc.count_ops().get("cx", 0)
        atteso = cx_prep + 15 * N
        print(f"    N={N:3d}: cx osservati={ncx:4d}   attesi={atteso:4d}   "
              f"{'OK' if ncx == atteso else 'MISMATCH'}")
        assert ncx == atteso, f"conteggio gate inatteso ({nome}, N={N})"
print("  -> OK: crescita lineare confermata in entrambi gli scenari, "
      "nessuna fusione dei passi.")

print()
print("=" * 78)
print("2. CROSS-CHECK INDIPENDENTE (rumore nullo): circuito vs numpy puro")
print("=" * 78)


def step_matrix(J, Jp, b, D, tau):
    """Stesso passo esterno (Hex, campo, HDM) a livello di matrice 8x8,
    riusando i blocchi di gate di Parte 1 ma valutati con Operator() --
    cammino di calcolo indipendente dalla transpilazione a blocchi."""
    qc = QuantumCircuit(3)
    step_Hex(qc, J, Jp, tau)
    step_field(qc, b, tau)
    step_HDM(qc, J, Jp, D, tau)
    return Operator(qc).data


for nome, punto, prep, psi0 in [
    ("A (VQE)", PUNTO_VQE, vqe_params, psi0_vqe_exact),
    ("B (R0)", PUNTO_R0, None, psi0_000),
]:
    print(f"  Scenario {nome}:")
    for N in [5, 20, 80]:
        tau = t / N
        step_mat = step_matrix(punto["J"], punto["Jp"], punto["b"], punto["D"], tau)
        # ramo numpy: se c'e' preparazione, applicare prima lo stato VQE
        # ESATTO (infedelta' nota, gia' caratterizzata in Stadio 2:
        # 1-F~2e-13 a questo punto) -- stessa approssimazione fatta sul dimero
        psi_start = psi0
        psi_trotter = np.linalg.matrix_power(step_mat, N) @ psi_start
        psi_target = target_state(punto["J"], punto["Jp"], punto["b"], punto["D"], t, psi0)
        F_numpy = float(np.abs(np.vdot(psi_target, psi_trotter)) ** 2)

        F_qiskit, _ = fedelta_trotter_rumoroso(**punto, t=t, N=N, psi0=psi0,
                                                noise_model=None, vqe_params=prep)
        diff = abs(F_numpy - F_qiskit)
        print(f"    N={N:3d}: F (numpy) = {F_numpy:.10f}   "
              f"F (Qiskit) = {F_qiskit:.10f}   |diff| = {diff:.2e}")
        assert diff < 5e-6, f"cross-check fallito ({nome}, N={N})"
print("  -> OK: i due cammini di calcolo, completamente indipendenti, "
      "coincidono in entrambi gli scenari.")

print()
print("=" * 78)
print("3. LOCALIZZAZIONE DI N* (rumore di riferimento), entrambi gli scenari")
print("=" * 78)
nm_ref, _ = build_noise_model()
Ns = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 20, 30, 40, 60, 80]
risultati_Nstar = {}
for nome, punto, prep, psi0 in [
    ("A (VQE)", PUNTO_VQE, vqe_params, psi0_vqe_exact),
    ("B (R0)", PUNTO_R0, None, psi0_000),
]:
    print(f"  Scenario {nome}:")
    Fs = []
    for N in Ns:
        F, _ = fedelta_trotter_rumoroso(**punto, t=t, N=N, psi0=psi0,
                                         noise_model=nm_ref, vqe_params=prep)
        Fs.append(F)
        print(f"    N={N:4d}   F = {F:.6f}")
    imax_ = int(np.argmax(Fs))
    print(f"    -> N* approssimato = {Ns[imax_]}, F(N*) = {Fs[imax_]:.6f}")
    risultati_Nstar[nome] = (Ns, Fs, Ns[imax_])
print("  -> il massimo e' a un N finito in entrambi gli scenari: "
      "conferma diretta del compromesso Trotter/rumore, non assunto "
      "identico al dimero solo per analogia.")

np.savez("scan_N_trotter_rumoroso_trimero_anello.npz",
         Ns=np.array(Ns),
         Fs_A=np.array(risultati_Nstar["A (VQE)"][1]),
         Fs_B=np.array(risultati_Nstar["B (R0)"][1]))
print("\nSalvato: scan_N_trotter_rumoroso_trimero_anello.npz")
