import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "codice"))
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "dati"))


"""
"Quando la preparazione non e' esatta" (Documento 4): confronto fra
preparazione esatta (ampiezze dirette) e preparazione reale (circuito
VQE W-2q.6, parametri ottimali) sui correlatori dinamici -- gia'
parzialmente presente in 05_valida_correlatori_vqe.py (medie di errore
su 81 combinazioni a T=1.3), ma senza: il correlatore di riferimento
usato nei documenti (C_21^xx, non C_11^yy), il confronto su una curva
C(t) completa, e il controllo esplicito che lo scarto non correli con
l'ampiezza (la differenza qualitativa col dimero, dove l'ansatz meno
accurato mostra invece una struttura riconoscibile).
"""
import itertools
import numpy as np

from circuito_correlazioni_trimero_anello import ground_state, correlator_from_circuit

J, Jp, b, D = 1.0, 0.4, 2.4, 0.15
N = 60
SITI = (1, 2, 3)
COMP = ("x", "y", "z")

data = np.load("w2q6_params_optimal.npz")
vqe_params = data["params"]
psi0, _ = ground_state(J, Jp, b, D)

print("=" * 78)
print("1. CURVA C_21^xx(t): preparazione esatta vs VQE")
print("=" * 78)
ts = np.linspace(0.0, 6.0, 13)
C_esatto = np.array([correlator_from_circuit(2, "x", 1, "x", t, N, J, Jp, b, D, psi0=psi0)
                      for t in ts])
C_vqe = np.array([correlator_from_circuit(2, "x", 1, "x", t, N, J, Jp, b, D,
                                            ansatz_params=vqe_params)
                   for t in ts])
scarto_t = np.abs(C_vqe - C_esatto)
print(f"  scarto medio su {len(ts)} istanti: {scarto_t.mean():.3e}")
print(f"  scarto massimo:                  {scarto_t.max():.3e}")
assert scarto_t.max() < 1e-5, "scarto inatteso, ansatz W-2q.6 dovrebbe essere quasi esatto"
print("  -> OK")

print()
print("=" * 78)
print("2. SCAN COMPLETO (81 combinazioni, t=2): scarto vs ampiezza")
print("=" * 78)
scarti, ampiezze = [], []
righe = []
for (i, al), (j, be) in itertools.product(itertools.product(SITI, COMP),
                                            itertools.product(SITI, COMP)):
    ce = correlator_from_circuit(i, al, j, be, 2.0, N, J, Jp, b, D, psi0=psi0)
    cv = correlator_from_circuit(i, al, j, be, 2.0, N, J, Jp, b, D, ansatz_params=vqe_params)
    s = abs(cv - ce)
    scarti.append(s); ampiezze.append(abs(ce))
    righe.append((i, al, j, be, abs(ce), s))
scarti = np.array(scarti); ampiezze = np.array(ampiezze)

print(f"  scarto medio: {scarti.mean():.3e}   scarto massimo: {scarti.max():.3e}")
corr = np.corrcoef(ampiezze, scarti)[0, 1]
print(f"  correlazione scarto vs ampiezza: {corr:+.3f}  "
      f"(atteso vicino a 0: nessuna struttura riconoscibile, a differenza "
      f"del dimero con un ansatz meno accurato)")
assert abs(corr) < 0.3, "correlazione inattesa fra scarto e ampiezza"
print("  -> OK")

idx_peggiore = int(np.argmax(scarti))
i, al, j, be, amp, s = righe[idx_peggiore]
print(f"\n  combinazione con scarto massimo: C_{i}{j}^{al}{be} "
      f"(|C_esatto|={amp:.4f}, scarto={s:.2e})")

np.savez("confronto_vqe_esatto.npz",
         ts=ts, C_esatto=C_esatto, C_vqe=C_vqe,
         scarti=scarti, ampiezze=ampiezze)
print("\nSalvato: confronto_vqe_esatto.npz")
