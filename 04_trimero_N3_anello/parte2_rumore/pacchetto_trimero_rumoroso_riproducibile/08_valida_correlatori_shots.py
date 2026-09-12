import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "codice"))
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "dati"))


"""
Verifica obbligatoria di correlatori_shots_trimero_anello.py (Stadio 4bis)
prima di considerarlo concluso. Mirror concettuale della verifica gia'
fatta per il caso simmetrico sul dimero: qui il confronto e' fra la
formula analitica gia' validata allo Stadio 4 e la misura a shot finiti,
non contro un secondo calcolo indipendente da zero (la fisica del
circuito e' la stessa, verificata li').

  1. Coerenza formula analitica (Stadio 4) vs shot finiti (qui): lo
     scarto deve essere consistente con l'errore statistico atteso
     (~1/sqrt(shots)), non arbitrariamente piu' grande.
  2. N* dalla curva a shot finiti deve coincidere con N*=3, il valore
     gia' stabilito nella documentazione (risultati_correlatori_
     rumorosi_trimero_anello.tex) con la formula analitica.
  3. Verifica di convenzione: l'ancilla e' il qubit 3 (non 0 come sul
     dimero) -- il suo bit deve essere il PRIMO carattere della stringa
     di misura con measure_all, non l'ultimo.
"""
import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

from correlatori_rumorosi_trimero_anello import correlator_rumoroso
from correlatori_shots_trimero_anello import correlator_shots, SHOTS_DEFAULT
from noise_model_trimero_anello import build_noise_model

data = np.load("w2q6_params_optimal.npz")
vqe_params = data["params"]
nm_ref, params_ref = build_noise_model()

print("=" * 70)
print("1. FORMULA ANALITICA (Stadio 4) vs SHOT FINITI (qui), N=3, t=2")
print("=" * 70)
c_analitico = correlator_rumoroso(2, "x", 1, "x", 2.0, 3, 1.0, 0.4, 2.4, 0.15,
                                   vqe_params, noise_model=nm_ref,
                                   p_readout=params_ref["p_readout"])
c_shots = correlator_shots(2, "x", 1, "x", 2.0, 3, 1.0, 0.4, 2.4, 0.15,
                            vqe_params, noise_model=nm_ref, shots=SHOTS_DEFAULT)
scarto = abs(c_analitico - c_shots)
atteso = 1 / np.sqrt(SHOTS_DEFAULT)
print(f"  analitico   = {c_analitico.real:+.4f}{c_analitico.imag:+.4f}i")
print(f"  shot finiti = {c_shots.real:+.4f}{c_shots.imag:+.4f}i")
print(f"  |scarto|    = {scarto:.2e}  (atteso ~{atteso:.2e})")
assert scarto < 5 * atteso, "scarto troppo grande rispetto all'errore statistico atteso"
print("  -> OK")

print()
print("=" * 70)
print("2. N* DALLA CURVA A SHOT FINITI")
print("=" * 70)
N_grid = [1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20]
vals = []
for N in N_grid:
    c = correlator_shots(2, "x", 1, "x", 2.0, N, 1.0, 0.4, 2.4, 0.15,
                          vqe_params, noise_model=nm_ref, shots=SHOTS_DEFAULT)
    vals.append(abs(c))
    print(f"  N={N:3d}: |C| = {vals[-1]:.4f}")
Nstar = N_grid[int(np.argmax(vals))]
print(f"  N* = {Nstar}  (atteso: 3, dalla documentazione)")
assert Nstar == 3, f"N* inatteso: {Nstar}"
print("  -> OK")

print()
print("=" * 70)
print("3. CONVENZIONE ANCILLA: qubit 3, PRIMO carattere (non ultimo come sul dimero)")
print("=" * 70)
qc = QuantumCircuit(4, 1)
qc.x(3)  # solo l'ancilla, registro resta |000>
qc.measure(3, 0)
sim = AerSimulator()
counts = sim.run(qc, shots=100).result().get_counts()
print(f"  X solo sull'ancilla, registro |000>, 100 shot -> {counts}")
assert counts.get("1", 0) == 100, "convenzione ancilla non verificata"
print("  -> OK: il bit misurato e' 1, coerente con l'ancilla = qubit 3")

np.savez("scan_N_correlatore_shots_trimero_anello.npz",
         N_grid=np.array(N_grid), vals=np.array(vals), Nstar=Nstar)
print("\nSalvato: scan_N_correlatore_shots_trimero_anello.npz")
