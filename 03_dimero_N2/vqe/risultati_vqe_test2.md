# Risultati — VQE ground state al punto di lavoro del test 2

File: `vqe_test2.py`. Punto di lavoro: $b/J=0.35$, $D/J=0.80$, $J=1$
(parametri del test 2 in `relazione_test_parametri.md`).

## Metodologia (nessuna scelta nuova)

- Hamiltoniana: stessa convenzione di `dimer_exact.py` /
  `confronto_ansatz_entangler.ipynb`,
  $H=J(X_1X_2+Y_1Y_2+Z_1Z_2)+b(Z_1+Z_2)+D(X_1Z_2-Z_1X_2)$.
- Ansatz: **PMA-2q·3** (blocco RBS + $R_y$ indipendenti sui due qubit, 3
  parametri) — il riferimento canonico deciso in `confronto_ansatz_entangler.ipynb`.
- Ottimizzazione: multistart $R=6$ (COBYLA, reinizializzazione nel ciclo
  esterno) seguito da un **polish L-BFGS-B** dal miglior punto trovato.
  Il polish è un'aggiunta rispetto al notebook di confronto: lì l'obiettivo
  era il confronto qualitativo fra ansatz su tutto un range di $b/J$, qui
  serve uno stato preciso a precisione macchina perché diventerà l'input
  del circuito con l'ancilla nello stadio successivo — un residuo
  $\mathcal O(10^{-5})$ in energia (quanto lasciava COBYLA da solo)
  propagherebbe un errore sistematico non controllato nelle correlazioni.

## Risultato

| quantità | valore |
|---|---|
| $E_0$ (esatto) | $-3.57321145$ |
| $E$ (VQE) | $-3.57321145$ |
| $|E_\text{VQE}-E_0|$ | $7.75\times10^{-11}$ |
| Fidelity | $1.00000000$ (a precisione macchina) |
| $\langle M_z\rangle$ | $-0.034730$ |

Stato (base $|00\rangle,|01\rangle,|10\rangle,|11\rangle$, reale come atteso
— vedi nota di rigore in `confronto_ansatz_entangler.ipynb` sul perché il
DM in forma $XZ-ZX$ mantiene $H$ reale):

$$|\psi_0\rangle \simeq 0.2017\,|00\rangle + 0.6648\,|01\rangle - 0.6648\,|10\rangle + 0.2746\,|11\rangle$$

Parametri ottimali: $(p_0,p_1,p_2) = (3.978569,\ 1.226719,\ 1.914748)$ rad.

## Lettura fisica

- $\langle M_z\rangle\simeq-0.035$: il ground state resta vicino al settore
  $M=0$ (il campo $b/J=0.35$ è modesto rispetto a $J$), ma non è puro
  $M=0$ — la piccola componente $|11\rangle$ ($0.2746$) e l'asimmetria fra
  $|00\rangle$ e $|11\rangle$ vengono dal termine DM ($D/J=0.8$, non
  trascurabile) che mescola i settori.
- Il peso dominante è sulla combinazione antisimmetrica $|01\rangle-|10\rangle$
  (verso il singoletto $|S\rangle=(|01\rangle-|10\rangle)/\sqrt2$): coerente
  con l'aspettativa che a $D/J\lesssim1$ e campo piccolo il ground state
  resti "vicino" al singoletto del caso $D=0,b=0$, deformato dal DM.
- Il fatto che $\langle\psi_\text{exact}|\psi_\text{VQE}\rangle$ sia reale e
  positivo (non solo $|\cdot|=1$) conferma che non c'è una fase relativa
  residua da fissare a mano prima di usare questo stato come input di un
  circuito.

## Dispersione del multistart

Le 6 energie finali di COBYLA (prima del polish) hanno dispersione
$6.73\times10^{-3}$ — indica che il paesaggio a 3 parametri ha comunque
minimi locali non banali a questo punto di lavoro (diversamente da $D=0$),
motivo in più per non fidarsi del solo COBYLA e applicare il polish.

## Prossimo passo

Lo stato $|\psi_0^\text{VQE}\rangle$ (equivalentemente i 3 parametri
ottimali dell'ansatz PMA-2q·3) è salvato in `ground_state_test2.npz` ed è
pronto per essere preparato come stato iniziale nel circuito con l'ancilla
per le correlazioni dinamiche.

**Risposta del relatore ricevuta:** nessuna restrizione — sia
auto-correlazione (stesso sito) sia correlazione fra spin diversi sono di
interesse, e vale la pena provare più componenti ($S_z,S_x,S_y$); alcune
combinazioni si annulleranno per simmetria dell'Hamiltoniana (atteso, non
un errore). Prima di implementare il circuito: controllo classico di quali
combinazioni sono strutturalmente nulle a questo punto di lavoro. Vedi
`log_decisioni.md` e `domande_relatore.md` per il dettaglio.
