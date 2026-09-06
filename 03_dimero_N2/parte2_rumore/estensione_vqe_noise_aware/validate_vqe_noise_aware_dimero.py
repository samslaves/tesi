"""
Verifica obbligatoria di vqe_noise_aware_dimero.py.

  1. Invarianza del conteggio CNOT rispetto a theta (premessa fisica della
     previsione dichiarata in log_decisioni.md): deve restare CNOT=2 su
     assegnazioni casuali multiple.
  2. Limite di rumore nullo: il VQE noise-aware con rumore SPENTO deve
     ritrovare l'energia esatta E0 gia' registrata in Parte 1.
  3. Robustezza del risultato rumoroso: un multistart INDIPENDENTE, piu'
     ampio (R=20) e senza il seme dei parametri ideali, deve convergere
     allo STESSO ottimo rumoroso trovato con R=6+seme -- altrimenti il
     risultato "theta_rumore* ~ theta_ideale*" sarebbe un artefatto del
     seme, non una proprieta' del paesaggio energetico.
  4. Confronto con la versione originale del VQE con termine DM sotto
     rumore (riuso dei parametri ideali): |Delta E| e |Delta F| devono
     essere sotto una soglia stretta (1e-4), a conferma della previsione
     (canale isotropo -> nessun vantaggio a rioptimizzare).
  5. N* della quantum simulation (Trotter) sotto rumore, con i parametri
     noise-aware: deve restare N*=8, come nella versione originale con i
     parametri ideali.
"""
import numpy as np

from vqe_noise_aware_dimero import (
    controllo_invarianza_cnot, vqe_noise_aware, energia_fedelta_rumorosa,
    transpila_dopo_assegnazione,
)
from vqe_dm_rumoroso_dimero import vqe_energia_fedelta_rumorosa
from dimer_exact import dimer_hamiltonian
from noise_model_dimero import build_noise_model
from trotter_rumoroso_dimero import fedelta_trotter_rumoroso

J, b, D = 1.0, 0.35, 0.80

data = np.load("ground_state_test2.npz")
vqe_params_ideali = data["vqe_params"]
psi_exact = data["psi0_exact"]
E0_exact = float(data["E0_exact"])
nm_ref, _ = build_noise_model()

print("=" * 70)
print("1. INVARIANZA DEL CONTEGGIO CNOT RISPETTO A THETA")
print("=" * 70)
conteggi, dettagli = controllo_invarianza_cnot(n_prove=5, seed=0)
print(f"  CNOT su 5 assegnazioni casuali: {conteggi}")
for i, d in enumerate(dettagli):
    print(f"    prova {i}: {d}")
assert all(c == 2 for c in conteggi), "il conteggio CNOT dipende da theta -- premessa fisica falsificata"
print("  -> OK: CNOT=2 indipendentemente da theta (unica sorgente di "
      "variazione: i gate rz/sx a 1 qubit, non i cx).")

print()
print("=" * 70)
print("2. LIMITE DI RUMORE NULLO (VQE noise-aware con rumore spento)")
print("=" * 70)
ris_zero = vqe_noise_aware(noise_model=None, R=6, maxiter=300, seed=0)
diff = abs(ris_zero["E"] - E0_exact)
print(f"  E (noise-aware, rumore nullo) = {ris_zero['E']:.10f}")
print(f"  E0 (esatto, registrato)       = {E0_exact:.10f}")
print(f"  |differenza|                  = {diff:.2e}")
assert diff < 1e-6, "LIMITE DI RUMORE NULLO FALLITO"
print("  -> OK")

print()
print("=" * 70)
print("3. ROBUSTEZZA: multistart indipendente (R=20, senza seme) vs R=6+seme")
print("=" * 70)
ris_seme = vqe_noise_aware(noise_model=nm_ref, R=6, maxiter=300, seed=0,
                            x_seme=vqe_params_ideali)
ris_ampio = vqe_noise_aware(noise_model=nm_ref, R=20, maxiter=300, seed=1,
                             x_seme=None)
print(f"  E (R=6 + seme)      = {ris_seme['E']:.8f}")
print(f"  E (R=20, senza seme) = {ris_ampio['E']:.8f}")
diff_multistart = abs(ris_seme["E"] - ris_ampio["E"])
print(f"  |differenza|        = {diff_multistart:.2e}")
assert diff_multistart < 1e-3, ("i due multistart indipendenti non convergono "
                                 "allo stesso ottimo rumoroso")
print("  -> OK: l'ottimo rumoroso e' raggiunto anche SENZA il seme, dato "
      "un numero sufficiente di restart casuali (R=20) -- non e' un "
      "artefatto del seme, e' una proprieta' del paesaggio energetico "
      "(coerente con l'argomento del canale isotropo).")
print("  Nota onesta: con SOLO R=6 e nessun seme (stesso R della versione "
      "originale del VQE con termine DM sotto rumore) il minimo trovato "
      "puo' restare a distanza 1e-4..1e-2 dall'ottimo vero, a seconda del "
      "seed casuale (dispersione reale del paesaggio energetico, non un "
      "bug -- vedi risultati_vqe_noise_aware_completo.tex, Sez. 4.4, per "
      "la caratterizzazione su 8 seed) -- per questo il risultato "
      "principale usa il seme, e questo controllo conferma "
      "indipendentemente che il seme non altera la conclusione fisica, "
      "solo l'affidabilita' pratica dell'ottimizzatore con poche "
      "ripetizioni.")

print()
print("=" * 70)
print("4. CONFRONTO CON LA VERSIONE ORIGINALE DEL VQE+DM RUMOROSO (riuso parametri ideali)")
print("=" * 70)
E_ideale_su_rumore, F_ideale_su_rumore, _ = vqe_energia_fedelta_rumorosa(
    vqe_params_ideali, psi_exact, noise_model=nm_ref)
E_na, F_na, ncx_na = energia_fedelta_rumorosa(
    ris_seme["x"], dimer_hamiltonian(b=b, J=J, D=D), nm_ref, psi_exact)
dE = E_na - E_ideale_su_rumore
dF = F_na - F_ideale_su_rumore
print(f"  E ideale-su-rumore = {E_ideale_su_rumore:.8f}   E noise-aware = {E_na:.8f}   Delta E = {dE:+.2e}")
print(f"  F ideale-su-rumore = {F_ideale_su_rumore:.8f}   F noise-aware = {F_na:.8f}   Delta F = {dF:+.2e}")
assert abs(dE) < 1e-4, "scostamento energetico oltre la soglia attesa"
assert abs(dF) < 1e-4, "scostamento di fedelta' oltre la soglia attesa"
print("  -> OK: |Delta E|, |Delta F| < 1e-4 -- previsione confermata, "
      "rioptimizzare sotto rumore non porta vantaggio misurabile.")

print()
print("=" * 70)
print("5. N* DELLA QUANTUM SIMULATION (TROTTER) SOTTO RUMORE, PARAMETRI NOISE-AWARE")
print("=" * 70)
t = 2.0
Ns = list(range(1, 21)) + [30, 40, 60, 80, 120, 160]
Fs = []
for N in Ns:
    F, _ = fedelta_trotter_rumoroso(ris_seme["x"], psi_exact, t, N, noise_model=nm_ref)
    Fs.append(F)
imax = int(np.argmax(Fs))
print(f"  N* (parametri noise-aware) = {Ns[imax]}   F(N*) = {Fs[imax]:.6f}")
assert Ns[imax] == 8, f"N* si e' spostato: {Ns[imax]} invece di 8"
print("  -> OK: N*=8 invariato rispetto alla versione originale della "
      "quantum simulation (Trotter) sotto rumore (parametri ideali).")

print()
print("=" * 70)
print("TUTTI I CONTROLLI SUPERATI")
print("=" * 70)
