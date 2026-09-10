import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "codice"))
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "dati"))


"""
Verifica obbligatoria di scan_parametri_rumore_trimero_anello.py. Mirror
di validate_scan_parametri_rumore_dimero.py, esteso a due scenari.

  1. Nessuna regressione: N* al punto di riferimento deve coincidere con
     quello ricalcolato con griglia fine (N*_A=3, N*_B=9 -- valori
     CORRETTI rispetto a quelli originariamente riportati nello Stadio 3,
     N*_A=2 e N*_B=10, trovati con una griglia troppo grezza).
  2. Monotonia: N* deve essere non-crescente al crescere di eps_1q o
     eps_2q, per ENTRAMBI gli scenari (non assunto identico solo perche'
     valeva per uno dei due).
  3. Invarianza da p_readout: dimostrata analiticamente (fattore
     moltiplicativo costante in N) e verificata numericamente sul
     correlatore (Stadio 4), come sul dimero.
"""
import numpy as np

from scan_parametri_rumore_trimero_anello import trova_N_star, scan_eps2q, scan_eps1q
from correlatori_rumorosi_trimero_anello import (
    correlator_rumoroso, J_DEFAULT, JP_DEFAULT, B_DEFAULT, D_DEFAULT,
)
from noise_model_trimero_anello import build_noise_model

data = np.load("w2q6_params_optimal.npz")
vqe_params = data["params"]

print("=" * 70)
print("1. NESSUNA REGRESSIONE: N* al punto di riferimento (griglia fine)")
print("=" * 70)
for scenario, N_atteso, F_atteso in [("A", 3, 0.700335), ("B", 9, 0.381896)]:
    N_star, F_star = trova_N_star(scenario, vqe_params, eps_1q=2.9e-4, eps_2q=3.8e-3)
    print(f"  Scenario {scenario}: N* = {N_star} (atteso {N_atteso}), "
          f"F(N*) = {F_star:.6f} (atteso {F_atteso:.6f})")
    assert N_star == N_atteso, f"regressione: N* scenario {scenario} non coincide"
    assert abs(F_star - F_atteso) < 1e-5, f"regressione: F(N*) scenario {scenario} non coincide"
print("  -> OK per entrambi gli scenari")

print()
print("=" * 70)
print("2. MONOTONIA: N* non-crescente al crescere del rumore, entrambi gli scenari")
print("=" * 70)
eps2q_vals = [1e-3, 2e-3, 3.8e-3, 6e-3, 1e-2, 1.5e-2, 2.5e-2]
eps1q_vals = [1e-4, 2.9e-4, 1e-3, 3e-3, 1e-2, 3e-2]

for scenario in ["A", "B"]:
    ris_2q = scan_eps2q(scenario, vqe_params, eps2q_vals)
    Ns_2q = [r[1] for r in ris_2q]
    print(f"  Scenario {scenario}, N* al crescere di eps_2q: {Ns_2q}")
    assert all(Ns_2q[i] >= Ns_2q[i + 1] for i in range(len(Ns_2q) - 1)), \
        f"N* non monotono in eps_2q (scenario {scenario})"

    ris_1q = scan_eps1q(scenario, vqe_params, eps1q_vals)
    Ns_1q = [r[1] for r in ris_1q]
    print(f"  Scenario {scenario}, N* al crescere di eps_1q: {Ns_1q}")
    assert all(Ns_1q[i] >= Ns_1q[i + 1] for i in range(len(Ns_1q) - 1)), \
        f"N* non monotono in eps_1q (scenario {scenario})"
print("  -> OK: monotono non-crescente in entrambi gli scenari e in entrambi i parametri")

print()
print("=" * 70)
print("3. INVARIANZA DI N* DA p_readout (verificata sul correlatore, Stadio 4)")
print("=" * 70)
print("  Stessa derivazione del dimero: <Z>_readout = (1-2p)*<Z>_ideale, un")
print("  fattore MOLTIPLICATIVO COSTANTE in N -- non sposta mai un argmax.")
print()
nm_gate, _ = build_noise_model(eps_1q=2.9e-4, eps_2q=3.8e-3, p_readout=0.0)
N_candidati = [1, 2, 3, 4, 5, 6, 8, 10]
N_star_precedente = None
for p_readout in [0.0, 0.05, 0.20]:
    vals = [abs(correlator_rumoroso(2, "x", 1, "x", 2.0, N, J_DEFAULT, JP_DEFAULT,
                                     B_DEFAULT, D_DEFAULT, vqe_params,
                                     noise_model=nm_gate, p_readout=p_readout))
            for N in N_candidati]
    N_star = N_candidati[int(np.argmax(vals))]
    print(f"  p_readout={p_readout:.2f}: N* = {N_star}  "
          f"(valori: {[f'{v:.4f}' for v in vals]})")
    if N_star_precedente is not None:
        assert N_star == N_star_precedente, "N* dipende da p_readout, contro la previsione"
    N_star_precedente = N_star
print(f"  -> OK: N*={N_star_precedente} per tutti i valori di p_readout testati, come previsto.")
