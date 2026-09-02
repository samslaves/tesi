# Risultati — circuito_correlazioni_dimero.py

Modulo estratto da `circuito_correlazioni_tutte.ipynb` (dove la stessa logica
viveva solo dentro le celle, non importabile), per colmare il gap segnalato
in una sessione precedente dedicata al rumore quantico e confermato assente
in una sessione successiva: a differenza di anello e catena, il dimero non
aveva un modulo `.py` a sé per il circuito Hadamard test delle correlazioni.

**API pubblica**, stessa firma dei moduli equivalenti per N=3:
```
ground_state(b, J=1.0, D=0.0) -> (psi0, E)
build_correlator_circuit(i, alpha, j, beta, t, N, J, b, D, part, psi0=None, measure=False, ansatz_params=None)
ancilla_z_expectation(qc) -> float
correlator_from_circuit(i, alpha, j, beta, t, N, J, b, D, psi0=None, ansatz_params=None) -> complex
```

`ansatz_params` non è ancora implementato per il dimero (solleva
`NotImplementedError` se diverso da `None`) — la preparazione dello stato
usa sempre le ampiezze esatte via `prepare_state`. Per anello e catena
questo argomento seleziona la preparazione via il circuito VQE reale al
posto delle ampiezze esatte; per il dimero resta un placeholder di firma,
non ancora chiuso il collegamento VQE→correlazioni con il circuito
effettivo (lo stand-in a ampiezze esatte è tuttora in uso).

## Convenzione sito↔qubit (verificata, non assunta)

```
ancilla  = qubit assoluto 0
sito 2   = qreg locale 0  (qubit assoluto 1)
sito 1   = qreg locale 1  (qubit assoluto 2)
```

Un errore di mapping qui è invisibile sui correlatori simmetrici rispetto
allo scambio dei siti — rischio già segnalato esplicitamente in una
sessione precedente ("con l'ancilla in mezzo un errore di mapping non è
visibile su stati simmetrici"), poi realmente trovato durante lo sviluppo
di questo modulo (vedi sotto) esattamente in quella forma.

## Due bug trovati e corretti prima di questa estrazione

Entrambi nella derivazione originale dentro `circuito_correlazioni_tutte.ipynb`,
mascherati per coincidenza sui primi due correlatori validati
($C_{2,1}^{xx}$, $C_{2,1}^{xy}$) grazie alla simmetria $U$, e diventati
visibili solo scansionando sistematicamente tutte le 36 combinazioni:

1. **Formula spettrale del riferimento classico**: mancava un coniugato
   complesso ($C(t)=\sum_k e^{i(E_0-E_k)t}\overline{a_k}b_k$, non $a_kb_k$).
   Invisibile per componenti reali ($x,z$), sbagliava il segno per $\alpha=y$.
2. **Mappatura sito→qubit invertita**: `{1:0, 2:1}` invece di `{1:1, 2:0}`.
   Invisibile per $\eta_\alpha\eta_\beta=+1$ (il caso di entrambi i
   correlatori validati per primi).

Questo modulo incorpora la versione già corretta. Cronaca completa in
`log_decisioni.md`.

## Validazione (`validate_circuito_correlazioni_dimero.py`)

Riferimento classico calcolato con un **metodo indipendente** dalla formula
spettrale (esponenziale di matrice diretto via `scipy.linalg.expm`, non
riuso della stessa formula già usata altrove — controllo più rigoroso).

Sei correlatori rappresentativi, tre valori di $t$, $N=200$: residuo
$\sim10^{-3}$–$10^{-2}$, crescente con $t$, coerente con puro errore di
Trotter (nessuna anomalia). Zeri a $t=0$ per le combinazioni attese (siti
diversi, una sola componente $y$): confermati a precisione macchina
($\sim10^{-16}$–$10^{-17}$). Convergenza in $N$ su $C_{2,1}^{xx}(t{=}2.0)$:
rapporto $\approx2$ raddoppiando $N$ da 10 a 320, coerente con Trotter al
prim'ordine ($O(1/N)$ sull'ampiezza).

## Cosa NON fa questo modulo

- Nessun rumore reale (shot finiti, errori di gate) — `ancilla_z_expectation`
  legge sempre lo statevector esatto. La stima da conteggi è materia della
  Parte 2, da aggiungere quando si apre quel blocco.
- Nessuna preparazione via VQE reale (vedi `ansatz_params` sopra).
