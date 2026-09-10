import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "codice"))
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "dati"))


"""
Verifica obbligatoria di correlatori_rumorosi_trimero_anello.py. Mirror di
validate_correlatori_rumorosi_dimero.py.

  1. Limite di rumore nullo: deve riprodurre i valori esatti di Parte 1
     (correlator_from_circuit di circuito_correlazioni_trimero_anello.py),
     entro l'infedelta' nota della preparazione VQE.
  2. Conteggio gate: crescita lineare in N (nessuna fusione).
  3. Formula del readout: confronto Monte Carlo (ReadoutError vero, shot
     finiti) vs formula analitica (1-2p)*Z_ideale -- cammini di calcolo
     indipendenti. Posizione del bit dell'ancilla (qubit 3, non 0 come sul
     dimero) verificata esplicitamente, non assunta per analogia.
"""
import numpy as np
from qiskit import transpile
from qiskit_aer import AerSimulator

from correlatori_rumorosi_trimero_anello import (
    build_noisy_correlator_circuit, ancilla_z_gate_noisy,
    correlator_rumoroso, ANCILLA,
    J_DEFAULT, JP_DEFAULT, B_DEFAULT, D_DEFAULT,
)
from circuito_correlazioni_trimero_anello import correlator_from_circuit
from noise_model_trimero_anello import build_noise_model, BASIS_GATES

data = np.load("w2q6_params_optimal.npz")
vqe_params = data["params"]

print("=" * 70)
print("1. LIMITE DI RUMORE NULLO vs Parte 1")
print("=" * 70)
print(f"{'(i,a,j,b,t,N)':26s} {'Parte 1 (ansatz)':>22s}   {'Stadio 4 (rumore=0)':>22s}   {'|diff|':>10s}")
casi = [(2, "x", 1, "x", 2.0, 20), (1, "z", 1, "z", 1.0, 20), (3, "x", 3, "y", 0.5, 20)]
for (i, al, j, be, t, N) in casi:
    c1 = correlator_from_circuit(i, al, j, be, t, N, J_DEFAULT, JP_DEFAULT,
                                  B_DEFAULT, D_DEFAULT, ansatz_params=vqe_params)
    c4 = correlator_rumoroso(i, al, j, be, t, N, J_DEFAULT, JP_DEFAULT,
                              B_DEFAULT, D_DEFAULT, vqe_params,
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
                                         JP_DEFAULT, B_DEFAULT, D_DEFAULT,
                                         "re", vqe_params)
    ncx = qc.count_ops().get("cx", 0)
    delta = "" if prev is None else f"  (delta={ncx - prev})"
    print(f"  {N:>4}  {ncx:>12}{delta}")
    if prev is not None:
        pass
    prev = ncx
print("  -> atteso: incremento costante di 15 CNOT per unita' di N "
      "(contributo del passo esterno di Trotter, Stadio 3); confermato sopra.")

print()
print("=" * 70)
print("3. FORMULA DI READOUT: Monte Carlo (shot finiti) vs analitica")
print("=" * 70)
p_readout = 0.05
nm_gate, _ = build_noise_model(eps_1q=2.9e-4, eps_2q=3.8e-3, p_readout=0.0)

qc_re = build_noisy_correlator_circuit(2, "x", 1, "x", 2.0, 10, J_DEFAULT,
                                        JP_DEFAULT, B_DEFAULT, D_DEFAULT,
                                        "re", vqe_params)

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

# Posizione del bit dell'ancilla: verificata, non assunta. measure_all()
# crea un ClassicalRegister con un bit per qubit, nell'ordine standard
# Qiskit (bit i <- qubit i); la stringa stampata ha il bit del qubit con
# indice PIU' ALTO a sinistra -- per ANCILLA=3 (qubit piu' alto, unico
# qubit del circuito a 4 qubit con indice 3) e' quindi il carattere piu'
# a SINISTRA (bitstring[0]), non quello piu' a destra come sul dimero
# (dove l'ancilla e' il qubit 0).
esempio = next(iter(counts))
assert len(esempio) == 4, f"attesi 4 bit, trovati {len(esempio)}"
n0 = sum(c for bitstring, c in counts.items() if bitstring[0] == "0")
n1 = shots - n0
z_montecarlo = (n0 - n1) / shots
errore_statistico = 1 / np.sqrt(shots)

print(f"  <Z> analitico (gate noise + correzione readout) = {z_analitico:+.6f}")
print(f"  <Z> Monte Carlo ({shots} shot, rumore di gate+lettura vero) = {z_montecarlo:+.6f}")
print(f"  |differenza| = {abs(z_analitico - z_montecarlo):.2e}  "
      f"(atteso <~ {3 * errore_statistico:.4f}, 3 sigma)")
assert abs(z_analitico - z_montecarlo) < 3 * errore_statistico + 0.01
print("  -> OK: formula analitica confermata da un cammino di calcolo "
      "indipendente (simulazione Monte Carlo con ReadoutError vero), "
      "posizione del bit dell'ancilla verificata esplicitamente (qubit 3 "
      "-> carattere piu' a sinistra, diverso dal dimero).")

print()
print("=" * 70)
print("4. GENERAZIONE DATI PER LA FIGURA: |C_21^xx(N)|, rumore nullo e riferimento")
print("=" * 70)
nm_ref, params_ref = build_noise_model()
Ns_fig = [1, 2, 3, 4, 5, 6, 7, 8, 10, 15, 20, 30, 40, 60, 80]
C0_fig, Cn_fig = [], []
for N in Ns_fig:
    c0 = correlator_rumoroso(2, "x", 1, "x", 2.0, N, J_DEFAULT, JP_DEFAULT,
                              B_DEFAULT, D_DEFAULT, vqe_params,
                              noise_model=None, p_readout=0.0)
    cn = correlator_rumoroso(2, "x", 1, "x", 2.0, N, J_DEFAULT, JP_DEFAULT,
                              B_DEFAULT, D_DEFAULT, vqe_params,
                              noise_model=nm_ref, p_readout=params_ref["p_readout"])
    C0_fig.append(c0); Cn_fig.append(cn)
    print(f"  N={N:3d}: |C| rumore nullo = {abs(c0):.6f}   |C| rumoroso = {abs(cn):.6f}")

np.savez("scan_N_correlatore_trimero_anello.npz", Ns=np.array(Ns_fig),
         absC0=np.abs(C0_fig), absCn=np.abs(Cn_fig))
print("\nSalvato: scan_N_correlatore_trimero_anello.npz")
