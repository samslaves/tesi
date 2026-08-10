# Struttura dei file — tesi VQE su sistemi di spin

## Parte 1 — sistema chiuso (senza rumore)

### N=2 — Dimero

| file | ruolo | stato |
|---|---|---|
| `dimer_exact.py` | benchmark esatto: spettro, magnetizzazione, self-test | ✅ fatto |
| `dimer_exact_spiegato.ipynb` | notebook pedagogico: `SparsePauliOp`, `eigh`, convenzione $J$ | ✅ fatto |
| `vqe_dimer.py` | implementazione VQE dimero (HA e PMA) | 🔲 prossimo |
| `vqe_dimer_spiegato.ipynb` | notebook pedagogico interattivo sul VQE dimero | 🔲 prossimo |

### N=3 — Catena aperta

| file | ruolo | stato |
|---|---|---|
| `trimer_chain_exact.py` | benchmark esatto catena aperta | 🔲 |
| `vqe_trimer_chain.py` | implementazione VQE catena aperta | 🔲 |
| `vqe_trimer_chain_spiegato.ipynb` | notebook pedagogico interattivo | 🔲 |

### N=3 — Anello / triangolo frustrato

| file | ruolo | stato |
|---|---|---|
| `trimer_ring_exact.py` | benchmark esatto anello/triangolo | 🔲 |
| `vqe_trimer_ring.py` | implementazione VQE anello/triangolo frustrato | 🔲 |
| `vqe_trimer_ring_spiegato.ipynb` | notebook pedagogico interattivo | 🔲 |

---

## Parte 2 — sistema aperto (con rumore)

### N=2 — Dimero rumoroso

| file | ruolo | stato |
|---|---|---|
| `vqe_dimer_noisy.py` | VQE dimero con modelli di rumore Qiskit ($T_1$, $T_2$, gate, readout) | 🔲 |
| `vqe_dimer_noisy_spiegato.ipynb` | notebook pedagogico interattivo | 🔲 |

### N=3 (dimostrativo)

| file | ruolo | stato |
|---|---|---|
| `vqe_trimer_noisy.py` | VQE $N=3$ con rumore (catena, dimostrativo) | 🔲 |

---

## Dipendenze tra i moduli

```
dimer_exact.py
    └── importato da: vqe_dimer.py
                      vqe_dimer_noisy.py

trimer_chain_exact.py
    └── importato da: vqe_trimer_chain.py
                      vqe_trimer_noisy.py

trimer_ring_exact.py
    └── importato da: vqe_trimer_ring.py
```

I moduli `*_exact.py` sono **sola lettura** da qui in avanti: sono il metro di misura e non vanno mai modificati.

---

## Principio generale

Per ogni step:
1. modulo `.py` funzionante e validato (self-test automatico);
2. notebook `_spiegato.ipynb` che lo spiega cella per cella con slider interattivi.
