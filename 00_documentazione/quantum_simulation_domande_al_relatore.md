# Domande per il relatore — quantum simulation (Trotter) sul dimero

Domande aperte sul nuovo task (simulare $e^{-iHt}$ sull'Hamiltoniana del
dimero, non su Ising), da porre a Prof. Chiesa al prossimo incontro.

---

## 1. Serve un qubit di supporto per le correlazioni nel tempo?

Nel notebook di esempio che ho usato come riferimento (quello sul modello di
Ising), oltre ai qubit che rappresentano i due spin fisici ne viene usato un
**terzo, aggiuntivo**, che non rappresenta nessuno spin reale del sistema:
serve solo come "strumento di misura indiretto" per calcolare quantità che
altrimenti non sarebbero accessibili direttamente, tipo la correlazione tra
uno spin al tempo $t$ e l'altro al tempo $0$, $\langle s_{x1}(t)s_{x2}\rangle$.

**Domanda:** per il task che mi ha chiesto (evoluzione temporale
dell'Hamiltoniana del dimero, non del modello di Ising), mi serve anche a me
questo qubit aggiuntivo, oppure per ora mi basta guardare l'evoluzione di
osservabili "semplici" (es. la magnetizzazione $M_z(t)$), senza calcolare
correlazioni a due tempi?

## 2. Includo subito il termine DM o parto dal caso più semplice?

Con il termine DM acceso ($D\neq0$) i due pezzi dell'Hamiltoniana (il campo
$b$ e lo scambio $J$) non commutano, quindi serve una decomposizione
approssimata (Trotter), con un errore che dipende dal numero di passi usati.

Se invece $D=0$, i due pezzi commutano e si può scrivere l'evoluzione in
modo **esatto**, senza approssimazioni.

**Domanda:** conviene partire dal caso $D=0$ (esatto) per validare il metodo,
e poi passare a $D\neq0$ (Trotter, con l'errore da studiare)? O vuole vedere
subito il caso completo con $D\neq0$?

## 3. Dove va collocato questo blocco nella tesi?

**Domanda:** questa simulazione temporale è una sotto-sezione della Parte 1
(sistema chiuso), oppure la immagina come una sezione a sé, magari come ponte
verso la Parte 2 (sistema aperto/rumore)?

## 4. Range di parametri e condizioni iniziali

**Domanda:** c'è un valore di riferimento per $b/J$ e $D$ da usare (es. gli
stessi usati nel resto della tesi per il dimero), e uno stato iniziale
specifico da cui far partire l'evoluzione (es. $|\!\uparrow\uparrow\rangle$,
oppure lo stato fondamentale trovato con il VQE)?
