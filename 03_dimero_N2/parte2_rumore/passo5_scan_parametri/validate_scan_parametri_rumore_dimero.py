"""
Verifica obbligatoria di scan_parametri_rumore_dimero.py.

  1. Nessuna regressione: N* al punto di riferimento (eps_1q=2.9e-4,
     eps_2q=3.8e-3) deve coincidere con quello gia' trovato al Passo 3
     (N*=8), calcolato li' con una ricerca manuale, qui con la funzione
     generale trova_N_star -- stesso risultato, cammino di codice diverso.
  2. Monotonia: N* deve essere non-crescente al crescere di eps_1q o
     eps_2q (piu' rumore -> conviene fermarsi prima), su tutto lo scan.
  3. Invarianza da p_readout: dimostrata analiticamente (la correzione di
     readout e' un fattore costante (1-2p), applicato identicamente a
     ogni N, quindi non sposta mai il massimo) e verificata numericamente
     su un correlatore con tre valori di p_readout molto diversi.
"""
import numpy as np

from scan_parametri_rumore_dimero import (
    trova_N_star, scan_eps2q, scan_eps1q,
)
from correlatori_rumorosi_dimero import correlator_rumoroso, J_DEFAULT, b_DEFAULT, D_DEFAULT
from noise_model_dimero import build_noise_model

data = np.load("ground_state_test2.npz")
vqe_params = data["vqe_params"]
psi0_exact = data["psi0_exact"]

print("=" * 70)
print("1. NESSUNA REGRESSIONE: N* al punto di riferimento")
print("=" * 70)
N_star_rif, F_star_rif, _ = trova_N_star(vqe_params, psi0_exact,
                                          eps_1q=2.9e-4, eps_2q=3.8e-3)
print(f"  N* (questo modulo)  = {N_star_rif}")
print(f"  N* (Passo 3, registrato) = 8")
assert N_star_rif == 8, "regressione: N* al riferimento non coincide col Passo 3"
print("  -> OK")

print()
print("=" * 70)
print("2. MONOTONIA: N* non-crescente al crescere del rumore")
print("=" * 70)
ris_eps2q = scan_eps2q(vqe_params, psi0_exact,
                        [1e-3, 2e-3, 3.8e-3, 6e-3, 1e-2, 1.5e-2, 2.5e-2])
Ns_2q = [r[1] for r in ris_eps2q]
print(f"  N* al crescere di eps_2q: {Ns_2q}")
assert all(Ns_2q[i] >= Ns_2q[i + 1] for i in range(len(Ns_2q) - 1)), \
    "N* non e' monotono in eps_2q"
print("  -> OK: monotono non-crescente")

ris_eps1q = scan_eps1q(vqe_params, psi0_exact,
                        [1e-4, 2.9e-4, 1e-3, 3e-3, 1e-2, 3e-2])
Ns_1q = [r[1] for r in ris_eps1q]
print(f"  N* al crescere di eps_1q: {Ns_1q}")
assert all(Ns_1q[i] >= Ns_1q[i + 1] for i in range(len(Ns_1q) - 1)), \
    "N* non e' monotono in eps_1q"
print("  -> OK: monotono non-crescente")

print()
print("=" * 70)
print("3. INVARIANZA DI N* DA p_readout")
print("=" * 70)
print("  Derivazione: <Z>_readout = (1-2p)*<Z>_ideale (Passo 4) -- un")
print("  fattore MOLTIPLICATIVO COSTANTE in N. Se g(N) ha un massimo a")
print("  N*, allora c*g(N) (c>0 costante) ha il MASSIMO ALLO STESSO N*:")
print("  moltiplicare per una costante positiva non sposta un argmax.")
print()
nm_gate, _ = build_noise_model(eps_1q=2.9e-4, eps_2q=3.8e-3, p_readout=0.0)
N_candidati = [3, 4, 5, 6, 7, 8]
for p_readout in [0.0, 0.05, 0.20]:
    vals = [abs(correlator_rumoroso(2, "x", 1, "x", 2.0, N, J_DEFAULT,
                                     b_DEFAULT, D_DEFAULT, vqe_params,
                                     noise_model=nm_gate, p_readout=p_readout))
            for N in N_candidati]
    N_star = N_candidati[int(np.argmax(vals))]
    print(f"  p_readout={p_readout:.2f}: N* = {N_star}  "
          f"(valori: {[f'{v:.4f}' for v in vals]})")
    assert N_star == 5, "N* dipende da p_readout, contro la previsione analitica"
print("  -> OK: N*=5 per tutti i valori di p_readout testati, come previsto.")
