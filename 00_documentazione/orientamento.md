# Orientamento del lavoro di tesi

## I due documenti prodotti

**`dimero_spin.pdf`** (14 pagine) è il documento **didattico-derivativo**: mi ha permesso di capire cosa c'è dietro le slide del professore. Parte dal modello di Hubbard, costruisce la seconda quantizzazione, deriva il superscambio, mostra perché $J = 4t^2/U$, e arriva all'Hamiltoniana in operatori di Pauli. È il *perché* della forma di $H$.

**`dimero_sintesi.pdf`** (8 pagine) è il documento **di orientamento e piano**: registra cosa è stato stabilito nella fase preliminare — l'inquadramento del problema, il ruolo del termine DM, l'analisi delle degenerazioni, e la roadmap di lavoro.

---

## Roadmap confermata

### Parte 1 — sistema chiuso (senza rumore)

$$N=2 \xrightarrow{\text{chiuso}} N=3\text{ (catena aperta)} \xrightarrow{\text{chiuso}} N=3\text{ (anello/triangolo)}$$

### Parte 2 — sistema aperto (con rumore)

Stessi sistemi, trattazione **dimostrativa** (non esaustiva): $T_1$, $T_2$, errori di gate e di lettura.

---

## Aggiornamento 18/07/2026 — stato di avanzamento e nuovo task

**N=2 (dimero): sostanzialmente completo.** Prodotti e validati: benchmark
esatto (`dimer_exact.py`, self-test a precisione macchina), VQE con ansatz HA
e famiglia PMA (`vqe_dimer.py`), confronto esteso con 4 ansatz reali generici
e le famiglie PMA-1q/PMA-2q (`confronto_ansatz_entangler.ipynb`), derivazione
di quali rotazioni servono per rompere la simmetria $M$
(`analisi_rotazioni_PMA.ipynb`). Ansatz raccomandato per N=3: `PMA-2q·3`.
Dettagli completi in `log_decisioni.md`.

**Nuovo task, non presente nella roadmap originale sopra:** il relatore ha
richiesto separatamente una *quantum simulation* (evoluzione temporale reale
$e^{-iHt}$ via Suzuki-Trotter) sull'Hamiltoniana del dimero, sul modello
metodologico di un notebook di esempio basato sul modello di Ising. Non è
ancora chiaro se questo task vada collocato come estensione della Parte 1
(sistema chiuso) qui sopra, o come sezione a sé/ponte verso la Parte 2 — è
una delle domande inviate al relatore, in attesa di risposta. Vedi
`log_decisioni.md` (sezioni dedicate) e `domande_relatore.md` per lo stato
completo e aggiornato.
