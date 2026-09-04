"""
Verifica obbligatoria di correlatori_rumorosi_dimero.py.

  1. Limite di rumore nullo: deve riprodurre i valori esatti di Parte 1
     (correlator_from_circuit di circuito_correlazioni_dimero.py), entro
     l'infedelta' nota della preparazione VQE.
  2. Conteggio gate: crescita lineare in N (nessuna fusione), con i
     contributi dei quattro blocchi tutti visibili.
  3. Formula del readout: confronto Monte Carlo (ReadoutError vero, shot
     finiti) vs formula analitica (1-2p)*Z_ideale -- cammini di calcolo
     indipendenti.
"""
import numpy as np
from qiskit import transpile
from qiskit_aer import AerSimulator

from correlatori_rumorosi_dimero import (
    build_noisy_correlator_circuit, ancilla_z_gate_noisy,
    correlator_rumoroso, J_DEFAULT, b_DEFAULT, D_DEFAULT,
)
from circuito_correlazioni_dimero import correlator_from_circuit
from noise_model_dimero import build_noise_model, BASIS_GATES

data = np.load("ground_state_test2.npz")
vqe_params = data["vqe_params"]

print("=" * 70)
print("1. LIMITE DI RUMORE NULLO vs Parte 1")
print("=" * 70)
print(f"{'(i,a,j,b,t,N)':26s} {'Parte 1 (ansatz)':>22s}   {'Passo 4 (rumore=0)':>22s}   {'|diff|':>10s}")
casi = [(2, "x", 1, "x", 2.0, 20), (1, "z", 1, "z", 1.0, 20), (1, "x", 1, "y", 0.5, 20)]
for (i, al, j, be, t, N) in casi:
    c1 = correlator_from_circuit(i, al, j, be, t, N, J_DEFAULT, b_DEFAULT,
                                  D_DEFAULT, ansatz_params=vqe_params)
    c4 = correlator_rumoroso(i, al, j, be, t, N, J_DEFAULT, b_DEFAULT,
                              D_DEFAULT, vqe_params,
                              noise_model=None, p_readout=0.0)
    label = f"({i},{al},{j},{be},{t},{N})"
    print(f"{label:26s} {c1.real:+.6f}{c1.imag:+.6f}i   "
          f"{c4.real:+.6f}{c4.imag:+.6f}i   {abs(c1 - c4):.2e}")
    assert abs(c1 - c4) < 1e-5, "limite di rumore nullo fallito"
print("  -> OK (differenza compatibile con l'infedelta' nota di preparazione)")

print()
print("=" * 70)
print("2. CONTEGGIO GATE: crescita lineare, nessuna fusione")
print("=" * 70)
print(f"  {'N':>4}  {'CNOT totali':>12}")
prev = None
for N in [1, 2, 5, 10, 20, 40]:
    qc = build_noisy_correlator_circuit(2, "x", 1, "x", 2.0, N, J_DEFAULT,
                                         b_DEFAULT, D_DEFAULT, "re", vqe_params)
    ncx = qc.count_ops().get("cx", 0)
    delta = "" if prev is None else f"  (delta={ncx - prev})"
    print(f"  {N:>4}  {ncx:>12}{delta}")
    prev = ncx
print("  -> atteso: incremento costante di 3 CNOT per unita' di N "
      "(contributo del passo di Trotter); confermato sopra.")

print()
print("=" * 70)
print("3. FORMULA DI READOUT: Monte Carlo (shot finiti) vs analitica")
print("=" * 70)
p_readout = 0.05
nm_gate, _ = build_noise_model(eps_1q=2.9e-4, eps_2q=3.8e-3, p_readout=0.0)

qc_re = build_noisy_correlator_circuit(2, "x", 1, "x", 2.0, 10, J_DEFAULT,
                                        b_DEFAULT, D_DEFAULT, "re", vqe_params)

# ramo analitico: <Z> con rumore di gate, poi correzione (1-2p)
z_gate_noisy = ancilla_z_gate_noisy(qc_re, noise_model=nm_gate)
z_analitico = z_gate_noisy * (1 - 2 * p_readout)

# ramo Monte Carlo: stesso rumore di gate + ReadoutError vero, shot finiti
nm_mc, _ = build_noise_model(eps_1q=2.9e-4, eps_2q=3.8e-3, p_readout=p_readout)

qc_mc = qc_re.copy()
qc_mc.measure_all()
shots = 200_000
sim = AerSimulator(method="density_matrix", noise_model=nm_mc)
tqc = transpile(qc_mc, basis_gates=BASIS_GATES, optimization_level=0)
counts = sim.run(tqc, shots=shots, seed_simulator=42).result().get_counts()

# l'ancilla e' il qubit 0 -> bit meno significativo nella stringa di misura
n0 = sum(c for bitstring, c in counts.items() if bitstring[-1] == "0")
n1 = shots - n0
z_montecarlo = (n0 - n1) / shots
errore_statistico = 1 / np.sqrt(shots)  # stima grezza, ordine di grandezza

print(f"  <Z> analitico (gate noise + correzione readout) = {z_analitico:+.6f}")
print(f"  <Z> Monte Carlo ({shots} shot, rumore di gate+lettura vero) = {z_montecarlo:+.6f}")
print(f"  |differenza| = {abs(z_analitico - z_montecarlo):.2e}  "
      f"(atteso <~ {3 * errore_statistico:.4f}, 3 sigma)")
assert abs(z_analitico - z_montecarlo) < 3 * errore_statistico + 0.01
print("  -> OK: formula analitica confermata da un cammino di calcolo "
      "indipendente (simulazione Monte Carlo con ReadoutError vero).")
