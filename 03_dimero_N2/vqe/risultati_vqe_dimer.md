# Lettura dei risultati — `vqe_dimer.py`

## Configurazione della run

Confronto incrociato **2 ansätze × 2 valori di D**, su griglia $4\times4$ pannelli
(righe = configurazioni, colonne = metriche). Output salvato in `.png` (raster) e
`.pdf` (vettoriale, zoomabile).

| riga | ansatz | $D$ | parametri |
|---|---|---|---|
| 1 | HA (hardware-efficient, `n_local` Ry+CZ, reps=2) | $0$ | 6 |
| 2 | HA | $0.2$ | 6 |
| 3 | PMA (physically motivated, Crippa et al., $K=1$) | $0$ | 1 |
| 4 | PMA | $0.2$ | 1 |

Parametri comuni: $J=1$, 20 punti $B/J\in[0,5]$, ottimizzatore L-BFGS-B, 3 restart.

> Nota: il PMA per il dimero con $K=1$ ha **1 parametro** (un solo legame, un solo
> gate $W_{01}(\theta)$), non 2. Lo stato iniziale dipende da $B/J$: singoletto locale
> sotto $B/J=2$, $|11\rangle$ sopra.

---

## Riga 1 — HA, D=0 (baseline)

- **Energia:** VQE sovrapposto all'esatto su tutto il range.
- **Errore:** $\Delta E \sim 10^{-13}$–$10^{-14}$, rumore numerico puro.
- **Fidelity:** $\mathcal{F}=1.000$ ovunque.
- **Magnetizzazione:** salto netto $0 \to -1$ in $B/J=2$, riprodotto esattamente.

L'HA con 6 parametri è espressivamente completo per il dimero isotropo.

## Riga 2 — HA, D=0.2

- **Energia e fidelity:** identiche qualità del caso $D=0$ — $\Delta E \sim 10^{-13}$,
  $\mathcal{F}=1.000$ ovunque, **anche attraverso l'anticrossing**.
- **Magnetizzazione:** crossover liscio attraverso $B/J=2$ (non più un gradino),
  VQE sovrapposto all'esatto.

L'HA, essendo generico, rappresenta senza problemi il ground state misto
dell'anticrossing. Il termine DM non lo penalizza.

## Riga 3 — PMA, D=0

- **Errore:** $\Delta E \sim 10^{-16}$ — precisione macchina, **migliore dell'HA**.
- **Fidelity:** $\mathcal{F}=1.000$ ovunque.
- **Magnetizzazione:** salto netto perfetto.

Il PMA raggiunge il ground state esatto con **1 solo parametro** contro i 6 dell'HA.
È il vantaggio centrale di Crippa et al.: imporre le simmetrie del problema
($S$, $M$ conservati) riduce drasticamente la complessità variazionale.

## Riga 4 — PMA, D=0.2 (il caso istruttivo)

- **Errore:** sale fino a $\Delta E \simeq 0.2$ in $B/J=2$, con un picco netto.
- **Fidelity:** scende a $\mathcal{F}\simeq 0.82$ in $B/J=2$, poi risale.
- **Magnetizzazione:** resta un **gradino netto** $0\to-1$, NON il crossover liscio
  dell'esatto.

Questo **non è un bug**: è la conseguenza diretta della struttura del PMA. Il PMA
costruisce per costruzione stati a $S, M$ definiti (singoletto $M=0$ sotto soglia,
$|11\rangle$ con $M=-1$ sopra). Ma con $D\neq0$ il vero ground state **non ha più $M$
definito** — è la miscela singoletto/tripletto $M=-1$ dell'anticrossing. Il PMA,
che conserva $M$, non può rappresentare quella miscela.

- La degradazione è **massima in $B/J=2$**, dove il mescolamento dei due settori è
  massimo, e svanisce lontano dalla soglia (dove il ground state torna a $M$ quasi
  definito).
- La magnetizzazione resta un gradino perché gli stati del PMA hanno $\langle M_z\rangle$
  esattamente $0$ o $-1$, mai valori intermedi.

---

## Sintesi del confronto HA vs PMA

| | HA | PMA |
|---|---|---|
| parametri (dimero) | 6 | 1 |
| accuratezza $D=0$ | $\sim10^{-13}$ | $\sim10^{-16}$ |
| accuratezza $D=0.2$ | $\sim10^{-13}$ (perfetta) | degrada a $B/J=2$ ($\mathcal{F}\simeq0.82$) |
| robustezza a rottura di simmetria | alta (generico) | bassa (vincolato a $S,M$) |

**Il trade-off è il messaggio centrale:** il PMA è enormemente più efficiente
(1 parametro vs 6, precisione macchina) **finché il modello rispetta le simmetrie
su cui è costruito**. Quando un termine come il DM rompe la conservazione di $M$,
il PMA fallisce proprio dove la rottura è massima, mentre l'HA generico resta accurato.

Questo è esattamente il punto fisico che lega:
- la derivazione del termine DM (`dimero_sintesi.pdf`),
- l'analisi delle simmetrie ($[H_D, S_z]\neq0$),
- e la scelta dell'ansatz.

## Ruolo nel progetto

Risultato completo e autocontenuto per il dimero $N=2$. Stabilisce il metodo di
confronto (HA vs PMA, $D=0$ vs $D=0.2$) che verrà replicato su $N=3$ nelle due
topologie. La lezione sul PMA — efficiente ma fragile alle rotture di simmetria —
sarà particolarmente rilevante per il triangolo frustrato.
