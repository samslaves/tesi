# Note sul notebook `vqe_dimer_spiegato.ipynb`

Il notebook spiega il modulo VQE del dimero e poggia sul benchmark esatto
(`dimer_exact.py`), che fornisce il riferimento contro cui misurare l'errore.

---

## Principio variazionale (perché il VQE funziona)

Per qualsiasi stato normalizzato $∣\psi\rangle$ vale
$$\langle\psi∣H∣\psi\rangle \;\geq\; E_0,$$
con uguaglianza solo se $∣\psi\rangle$ è il ground state. Parametrizzando una famiglia
$∣\psi(\boldsymbol\theta)\rangle$ e **minimizzando** $\langle H\rangle_{\boldsymbol\theta}$,
il VQE si avvicina a $E_0$ **da sopra**: non può mai scendere sotto. È il motivo per cui
$\Delta E = E_\text{VQE} - E_0 \geq 0$ sempre (a meno del rumore numerico). Nel notebook
questo si verifica numericamente: stati casuali hanno tutti $\langle H\rangle \geq E_0$.

## Estimator (come si calcola $\langle H\rangle$)

A ogni iterazione del ciclo quantistico-classico, `StatevectorEstimator` valuta
$\langle\psi(\boldsymbol\theta)∣H∣\psi(\boldsymbol\theta)\rangle$. Si costruisce un **PUB**
`(ansatz, hamiltonian, [params])`; il risultato sta in `result[0].data.evs`, che è un array
NumPy — serve `.item()` per ottenere uno scalare. Il notebook mostra che l'estimator dà lo
stesso valore del calcolo manuale via `Statevector`.

---

## I due ansätze

**HA — hardware-efficient** (`n_local`, Ry + CZ). Generico: non sa nulla della fisica del
problema, ma con abbastanza strati rappresenta qualunque stato. Parametri: $2(\text{reps}+1)$,
cioè **6** per `reps=2`. (`n_local` è la funzione che sostituisce la classe `TwoLocal`,
deprecata in Qiskit 2.1.)

**PMA — physically motivated** (Crippa et al. 2021). Costruito **sulle simmetrie** del
problema. Blocco fondamentale su ogni legame:
$$W_{ij}(\theta) = \text{CNOT}_{ij}\,\big(R_y(\theta)_i\otimes I_j\big)\,\text{CNOT}_{ij}.$$
Lo stato iniziale rispetta la simmetria del ground state atteso:
- $B/J < 2$ (GS = singoletto, $S=0$, $M=0$): si parte dal singoletto locale
  $(∣01\rangle-∣10\rangle)/\sqrt2$;
- $B/J \geq 2$ (GS = $∣11\rangle$, $M=-1$): si parte da $∣11\rangle$.

Per il dimero ($N=2$, un legame, $K=1$): **1 solo parametro**. Il prezzo dell'efficienza è
che il PMA **conserva $S$ e $M$**.

### Perché si sceglie il riferimento in base a $B/J$

Il ground state del dimero **cambia natura bruscamente** al livello critico $B/J=2$ (level
crossing): sotto soglia è il singoletto, sopra è $∣11\rangle$ — due stati completamente
diversi, non c'è un singolo riferimento che vada bene ovunque. L'ansatz quindi **sceglie il
ramo** in base al regime, invece di usare un unico circuito che copra continuamente tutto
l'asse $B/J$ (come si fa invece in `confronto_ansatz_entangler.ipynb` con il blocco RBS/Givens,
che è "sicuro" anche partendo da una sovrapposizione dei due settori). Le due scelte sono
entrambe legittime; qui la si vede esplicitamente passo per passo.

### Derivazione esplicita: perché $X,H,\mathrm{CX},X$ prepara il singoletto

Seguendo lo stato passo per passo, partendo da $∣00\rangle$ (convenzione $∣q_0\,q_1\rangle$):

| gate | stato dopo |
|---|---|
| (iniziale) | $∣00\rangle$ |
| $X(q_0)$ | $∣10\rangle$ |
| $H(q_0)$ | $\frac{1}{\sqrt2}\big(∣00\rangle-∣10\rangle\big)$ |
| $\mathrm{CX}(q_0\to q_1)$ | $\frac{1}{\sqrt2}\big(∣00\rangle-∣11\rangle\big)$ (stato di Bell) |
| $X(q_0)$ | $\frac{1}{\sqrt2}\big(∣10\rangle-∣01\rangle\big) = -\frac{1}{\sqrt2}\big(∣01\rangle-∣10\rangle\big)$ |

L'ultimo stato è il **singoletto**, a meno di una fase globale $-1$ irrilevante. Quattro gate
fissi, senza parametri: non è un ansatz variazionale, è una **preparazione deterministica**. Il
notebook verifica ogni stadio intermedio con il simulatore (non solo il risultato finale), così
si vede esattamente dove nasce l'entanglement (al passo CX, che produce prima uno stato di
Bell) e dove arriva il singoletto (all'ultimo $X$).

### Perché basta 1 parametro: la struttura a blocchi di $W_{01}(\theta)$

Il blocco $W_{01}(\theta)$ **non** è semplicemente "l'identità fuori dal settore $M=0$", come
si potrebbe pensare. È qualcosa di più preciso, verificato nel notebook stampando la sua
matrice $4\times4$ esplicita: è **diagonale a blocchi**, con la **stessa** rotazione (stesso
angolo $\theta$) che agisce **sia** su $\{∣01\rangle,∣10\rangle\}$ **sia** su
$\{∣00\rangle,∣11\rangle\}$, senza mai farli comunicare:
$$W_{01}(\theta) = \begin{pmatrix} R(\theta) & 0 \\ 0 & R(\theta)\end{pmatrix}
\quad\text{nei due sottospazi } \{∣00\rangle,∣11\rangle\} \text{ e } \{∣01\rangle,∣10\rangle\}.$$

**Perché questo spiega tutto.** Il blocco non fa uscire lo stato dal sottospazio invariante in
cui lo ha messo la preparazione iniziale:
- se parti dal **singoletto** (ampiezza solo su $\{∣01\rangle,∣10\rangle\}$), il blocco fa
  scorrere lo stato dentro *quel* sottospazio (dal singoletto verso il tripletto $M=0$ e
  viceversa);
- se parti da $∣11\rangle$ (ampiezza solo su $\{∣00\rangle,∣11\rangle\}$), il blocco fa
  scorrere lo stato dentro *quell'altro* sottospazio.

I due sottospazi non si mescolano mai (la matrice è a blocchi), ma il blocco **non** è
l'identità su nessuno dei due — li ruota entrambi, con lo stesso angolo. Ecco perché **un solo
parametro $\theta$** basta per esplorare correttamente entrambi i rami: non servono due
parametri separati, perché la stessa rotazione riparametrizza correttamente qualunque dei due
sottospazi ti serva, una volta scelto il ramo dalla preparazione.

**Confronto con la rotazione di Givens/RBS "vera".** Nel notebook
`confronto_ansatz_entangler.ipynb` si usa invece un blocco che è **l'identità** su
$\{∣00\rangle,∣11\rangle\}$ (li lascia fermi del tutto), non un'altra rotazione con lo stesso
angolo. Sono due decomposizioni diverse della stessa idea — "un solo parametro per il settore
$M=0$" — con proprietà leggermente diverse: quella di questo notebook richiede di scegliere il
ramo giusto in partenza (perché ruoterebbe anche l'altro sottospazio se ci fosse ampiezza lì);
quella di Givens/RBS sarebbe "sicura" anche partendo da una sovrapposizione dei due settori.
Nessuna delle due è più corretta: sono scelte di implementazione diverse dello stesso principio
fisico, ed entrambe compaiono nel progetto per un confronto esplicito.

## Fidelity

L'energia dice quanto sei vicino in *valore*; la fidelity dice quanto sei vicino in *stato*:
$$\mathcal F = ∣\langle\psi_0∣\psi(\tilde{\boldsymbol\theta})\rangle∣,$$
con $∣\psi_0\rangle$ il ground state esatto da `eigh`. $\mathcal F=1$ significa che il VQE ha
trovato esattamente il ground state, non solo la sua energia.

---

## Il risultato centrale: HA vs PMA, $D=0$ vs $D=0.2$

| configurazione | parametri | accuratezza | fidelity |
|---|---|---|---|
| HA, $D=0$ | 6 | $\Delta E \sim 10^{-13}$ | $\mathcal F = 1$ ovunque |
| HA, $D=0.2$ | 6 | $\Delta E \sim 10^{-13}$ | $\mathcal F = 1$ ovunque |
| PMA, $D=0$ | 1 | $\Delta E \sim 10^{-16}$ | $\mathcal F = 1$ ovunque |
| PMA, $D=0.2$ | 1 | $\Delta E$ fino a $\sim 0.2$ in $B/J=2$ | $\mathcal F \simeq 0.82$ in $B/J=2$ |

Con $D=0$ il PMA **batte** l'HA: raggiunge il ground state esatto (precisione macchina) con
**1 parametro invece di 6**. È il vantaggio centrale di Crippa et al.: imporre le simmetrie
del problema riduce drasticamente la complessità variazionale.

Con $D=0.2$ il PMA **crolla** vicino a $B/J=2$. Non è un bug: è la conseguenza diretta della
sua struttura. Il PMA prepara stati con $M$ definito ($M=0$ sotto soglia, $M=-1$ sopra). Ma
con $D\neq0$ si ha $[H_D, S_z]\neq0$, e il vero ground state in $B/J=2$ è la **miscela**
$$∣\psi_0\rangle = \alpha\,∣\text{singoletto}\rangle + \beta\,∣11\rangle,$$
che il PMA — conservando $M$ — non può rappresentare. La degradazione è massima proprio dove
il mescolamento dei due settori è massimo ($B/J=2$) e svanisce lontano dalla soglia. La sua
magnetizzazione resta inoltre un gradino netto (valori di $\langle M_z\rangle$ esattamente $0$
o $-1$), mai il crossover liscio dell'esatto.

L'HA, generico, non ha questo vincolo e resta a $\mathcal F = 1$ in entrambi i casi.

**Nota di collegamento.** Il notebook `confronto_ansatz_entangler.ipynb` dimostra *perché*
esattamente questo accade, per contrasto: mettendo accanto quattro ansatz reali generici che
non degradano affatto a $D\neq0$, isola la rottura di simmetria $M$ come unica causa (non la
complessità dello stato), e mostra come ripararla — con due famiglie di PMA estesi (PMA-1q,
PMA-2q) che restano nel campo reale e recuperano $\mathcal F=1$ ovunque.

---

## Nota tecnica: warning "default.json not found"

`show_circuit` disegna i circuiti con `qc.draw("mpl", style="iqp")`, uno stile esplicito
esistente. Le versioni recenti di Qiskit non includono più il file `default.json` che il
drawer cercherebbe con lo stile implicito, generando altrimenti un `UserWarning` innocuo ma
fastidioso ad ogni disegno. Passare uno stile esistente (`iqp`, `textbook`, `clifford`) evita
il problema alla radice.

---

## La lezione

Le simmetrie nell'ansatz sono **un'arma a doppio taglio**: il PMA è enormemente più
efficiente (1 vs 6 parametri, precisione macchina) **finché il modello rispetta le simmetrie
su cui è costruito**; quando un termine come il DM le rompe, il PMA fallisce proprio dove la
rottura è massima.

Questo lega tre cose costruite separatamente:
- la derivazione del termine DM (`dimero_sintesi.pdf`),
- l'analisi delle simmetrie ($[H_D, S_z]\neq0$),
- la scelta dell'ansatz — inclusa la struttura interna del blocco $W_{ij}(\theta)$, che rivela
  *come* un solo parametro riesca a coprire entrambi i rami del level crossing.

Sarà particolarmente rilevante per il **triangolo frustrato** ($N=3$), dove la struttura
fisica dell'ansatz conta di più.
