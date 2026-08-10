# Note sul notebook `confronto_ansatz_entangler.ipynb`

Il notebook confronta **quattro ansatz variazionali con entangler diversi** (A–D), tutti
costruiti con sole rotazioni $R_y$ (quindi in campo reale), più **due famiglie PMA** a rottura
di simmetria. Ogni ansatz è ottimizzato via VQE su simulatore statevector (sistema chiuso,
esatto) con la metodologia adottata: **multistart con reinizializzazione casuale
ad ogni ciclo esterno**. Poggia sullo stesso benchmark esatto (`eigh`) usato dagli altri moduli
del dimero.

Gli ansatz confrontati:

| | circuito | entangler | n. param | note |
|---|---|---|---|---|
| **A** | $R_y$–CNOT–$R_y$ | CNOT (non param.) | 4 | ridondanza 1 |
| **B** | $R_y$–CZ–$R_y$ | CZ (non param.) | 4 | ridondanza 1, ≡ A |
| **C** | $R_y$–$CR_y(\varphi)$–$R_y$ | $CR_y$ (param.) | 5 | ridondanza 2 |
| **D** | $R_y$–RBS($\varphi$)–$R_y$ | RBS (param.) | 5 | ridondanza 2 |
| **PMA-1q** | $X$–RBS–[$R_y(q_1)$–RBS]$^k$ | RBS + $R_y$ su un solo qubit | 1, 2, 4, 6 | $\mathcal F=1$ da 4 |
| **PMA-2q** | $X$–RBS–[$R_y(q_0),R_y(q_1)$]$^k$ | RBS + $R_y$ indip. su entrambi | 1, 3, 5, 7 | ★ **consigliata**, $\mathcal F=1$ da 3 |

La **ridondanza** di A–D è $n_\text{par}-3$: il ground state reale di 2 qubit vive in $S^3$, cioè
ha 3 gradi di libertà fisici (4 ampiezze reali $-1$ normalizzazione $-1$ fase globale). Ogni
parametro oltre i 3 è gauge. Per le famiglie PMA il conteggio è diverso: si parte da 1 solo
parametro (il blocco RBS di base, $M$-conservante) e si aggiungono parametri di *rottura di
simmetria*, uno alla volta (PMA-1q) o a coppie indipendenti (PMA-2q).

---

## Un solo blocco $M$-conservante in tutto il notebook: il blocco RBS

Sia l'ansatz D sia le famiglie PMA usano la **stessa, unica implementazione** del blocco
$M$-conservante — niente decomposizioni diverse per la stessa fisica, per evitare
l'ambiguità di avere due gate "equivalenti ma scritti diversamente" a spasso nel notebook.

Il blocco realizza la rotazione di Givens reale nel settore $\{|01\rangle,|10\rangle\}$,
$$G(\varphi)=\begin{pmatrix}1&&&\\&\cos\varphi&-\sin\varphi&\\&\sin\varphi&\cos\varphi&\\&&&1\end{pmatrix},$$
con soli $R_y$, Hadamard e CZ — nessuna decomposizione CX-$CR_y$-CX ad hoc:
$$\mathrm{RBS}(\varphi) = (H\otimes H)\,\mathrm{CZ}\,\big(R_y(\varphi)_{q_0}\otimes R_y(-\varphi)_{q_1}\big)\,\mathrm{CZ}\,(H\otimes H).$$
Self-test nel notebook: errore rispetto a $G(\varphi)$ target $\sim10^{-16}$, per diversi valori
di $\varphi$.

Da solo, il blocco RBS conserva $M$ (è il cuore del PMA); circondato da strati $R_y$ liberi,
come nell'ansatz D, esplora invece stati generici — è il **ponte HA↔PMA**: la stessa unità
fisica che, a seconda di cosa le sta intorno, si comporta da ansatz simmetrico o da ansatz
generico.

---

## Perché si può restare in campo reale (anche con $D\neq0$)

L'Hamiltoniana
$$H = J\,(X_1X_2+Y_1Y_2+Z_1Z_2) + b\,(Z_1+Z_2) + D\,(X_1Z_2 - Z_1X_2)$$
è una **matrice reale simmetrica**: tutti i termini, incluso $Y\otimes Y$ (i due fattori $i$ si
elidono) e il DM in forma $XZ-ZX$, hanno entrate reali. Per il teorema spettrale, **il ground
state può sempre essere scelto reale** — cercarlo tra i soli stati reali (ansatz a sole $R_y$) è
una restrizione *gratuita*, non perde generalità.

Il notebook lo verifica in una cella: a $D=0.2$ la parte immaginaria di $H$ è esattamente $0$ e il
GS risulta reale.

### Nota di rigore — quale DM

Il termine usato qui, $D(X_1Z_2-Z_1X_2)$, è quello del notebook di partenza del progetto. Va
distinto dalla DM "canonica" $D(X_1Y_2 - Y_1X_2)$:

- $XZ-ZX$: **reale**, ma **rompe la conservazione di $M$** ($\|[H,S_z]\|\neq0$, verificato in cella).
- $XY-YX$: **immaginaria**, renderebbe $H$ complesso e il GS complesso.

La distinzione è cruciale per l'interpretazione: ciò che il DM di questo notebook rompe è la
**simmetria $M$**, non la realtà dello stato. È esattamente questo a mettere in crisi il PMA-1q,
come si vede dai risultati.

---

## Le due famiglie PMA: come rompere $M$ in modo reale

Il PMA di base ($X\cdot\mathrm{RBS}(\theta)$, 1 parametro) resta nel settore $M=0$ per
costruzione, e questo lo fa fallire in **due situazioni distinte**: già a $D=0$ per $b/J>2$ (il
ground state è $|11\rangle$, settore $M=-1$, semplicemente irraggiungibile con 1 parametro
$M$-conservante — non è un effetto del DM, è l'assenza di un meccanismo per uscire da $M=0$), e a
$D\neq0$ vicino a $b/J=2$ (dove il DM mescola i settori). Per recuperare in entrambi i casi
bisogna popolare i settori $M=\pm1$ con rotazioni $R_y$ **reali** aggiuntive. Due modi funzionano
(analisi completa, con derivazioni e casi che *falliscono*, in `analisi_rotazioni_PMA.ipynb`):

- **PMA-1q**: $R_y$ su **un solo** qubit ($q_1$) alternato a blocchi RBS. 1 parametro per
  blocco → sequenza **1, 2, 4, 6**. Funziona perché la rotazione locale agisce su uno stato
  *già entangled* dal blocco RBS precedente: basta un solo grado di libertà locale per
  redistribuire ampiezza verso $M=\pm1$. Raggiunge $\mathcal F=1$ da **4** parametri.
- **PMA-2q** ★ **(scelta consigliata)**: $R_y$ **indipendenti** su entrambi i qubit
  ($\alpha\neq\beta$). 2 parametri per coppia → sequenza **1, 3, 5, 7**. Raggiunge
  $\mathcal F=1$ già da **3** parametri — il minimo teorico ($S^3$, zero ridondanza).

**Perché non basta un parametro condiviso.** Ruotare entrambi i qubit con lo **stesso**
parametro (stesso segno o segno opposto) non funziona: i coefficienti generati nei settori
$M=\pm1$ risultano entrambi proporzionali a un'unica combinazione ($a+b$ o $a-b$) — un solo
grado di libertà reale, non due. Serve un parametro *indipendente* per settore. Derivazione
completa in `analisi_rotazioni_PMA.ipynb`.

**Scelta canonica per il seguito.** Si tengono entrambe le famiglie nel confronto (il contrasto
è istruttivo), ma **PMA-2q·3** è il riferimento che verrà usato nei prossimi notebook (N=3):
a parità di fisica, raggiunge il risultato con meno parametri totali. La variabile
`PMA_RECOMMENDED` nel codice la marca esplicitamente (★ nei titoli dei grafici).

---

## Multistart

Il paesaggio $E(\boldsymbol\theta)=\langle\psi(\boldsymbol\theta)|H|\psi(\boldsymbol\theta)\rangle$
è **non-convesso**: un ottimizzatore locale (COBYLA) converge al minimo del bacino in cui cade
il punto iniziale. Il multistart campiona $R$ punti di partenza casuali e tiene la corsa a
energia minima:
$$\boldsymbol\theta^\star = \arg\min_{k=1,\dots,R}\; E\big(\boldsymbol\theta^{*(k)}\big).$$

Due precisazioni operative:

- La reinizializzazione è nel ciclo **esterno** (una per corsa completa), **non** ad ogni
  iterazione interna di COBYLA: azzerare $\boldsymbol\theta$ ad ogni passo distruggerebbe la
  discesa. Crippa et al. usano 5 restart (fino a 10 nei casi difficili); qui $R=6$.
- La funzione registra anche la **dispersione** delle $R$ energie finali (quanto è accidentato
  il paesaggio) e il costo (`nfev` della corsa migliore). Così il notebook non solo trova il
  ground state, ma **mostra perché** il multistart serve.

**Distinzione da tenere ferma.** I restart e la scelta dell'ansatz risolvono problemi
*ortogonali*: l'**architettura** decide *cosa* è raggiungibile (l'immagine dell'ansatz), i
**restart** aiutano a *trovarlo* dentro un paesaggio con minimi locali. Se il ground state non è
raggiungibile, nessun numero di restart lo recupera. È esattamente il caso di PMA-1q·1 a
$D\neq0$: nessun restart lo salva, perché il settore $M=0$ non contiene il vero ground state.

---

## Fidelity robusta alla degenerazione

A $D=0$ e $b/J=2$ esatto, singoletto ($E=-3J$) e $|11\rangle$ ($E=J-2b=-3J$) sono **degeneri**:
`eigh` restituisce una combinazione arbitraria del sottospazio fondamentale, e la fidelity verso
*un* singolo autovettore è mal definita. Il notebook usa la fidelity verso l'**intero
sottospazio fondamentale** $\mathcal G$:
$$\mathcal F = \langle\psi|\,P_{\mathcal G}\,|\psi\rangle = \sum_{i\in\mathcal G}|\langle v_i|\psi\rangle|^2,$$
con $P_{\mathcal G}$ proiettore sugli autostati a energia $E_0$ (entro tolleranza). Fuori dalla
degenerazione si riduce alla fidelity ordinaria.

---

## Grafici interattivi (§6.2, 6.3, 6.4)

Con 11 ansatz nel confronto, un grafico statico con tutte le curve è illeggibile. Le figure di
queste tre sezioni sono **interattive**: una griglia di checkbox (una per ansatz) più due
pulsanti "Seleziona tutti"/"Deseleziona tutti", collegata al grafico tramite
`ipywidgets.interactive_output` — selezionando/deselezionando le curve, il grafico si
ridisegna automaticamente, senza rieseguire la cella. Se `ipywidgets` non è installato, la
cella lo rileva (`HAS_WIDGETS`) e mostra automaticamente un grafico statico con tutte le curve,
senza errori.

§6.1 (fidelity, un pannello per ansatz) resta invece una griglia statica: con un pannello per
ansatz non c'è affollamento da diradare.

---

## Il risultato centrale

| configurazione | esito ansatz reali (A–D) | esito PMA-1q·1 | esito PMA-2q·3 |
|---|---|---|---|
| $D=0$, $b/J<2$ | $\mathcal F=1$, $\Delta E\sim10^{-9}$ | $\mathcal F=1$ (settore $M=0$, GS=singoletto) | $\mathcal F=1$ |
| $D=0$, $b/J=2$ | energia esatta; fidelity-sottospazio necessaria | $\mathcal F=1$ (settore $M=0$) | $\mathcal F=1$ |
| $D=0$, $b/J>2$ | $\mathcal F=1$ | $\mathcal F=0$ (GS=$|11\rangle$, settore $M=-1$, irraggiungibile) | $\mathcal F=1$ |
| $D=0.2$–$1.0$, ogni $b/J$ | $\mathcal F=1$ ovunque | $\mathcal F=0$ per $b/J>2$; scende ulteriormente vicino a $b/J=2$ | $\mathcal F=1$ ovunque |

Cinque letture:

1. **A ≡ B.** Le curve di A ($R_y$-CNOT) e B ($R_y$-CZ) coincidono: per $N=2$ CNOT e CZ,
   avvolti da strati $R_y$, sono localmente equivalenti ($\mathrm{CNOT}=(I\otimes H)\,\mathrm{CZ}\,(I\otimes H)$,
   con le Hadamard assorbite dagli $R_y$). La scelta dell'entangler è qui **cosmetica** — conta
   solo per la transpilazione su hardware reale.

2. **Gli ansatz reali bastano anche a $D\neq0$.** A $D=0.2$ tutti e quattro raggiungono
   $\mathcal F=1$: il GS resta reale, quindi le sole $R_y$ sono sufficienti.

3. **PMA-1q·1 fallisce per assenza di simmetrie di rottura, non solo per il DM.** Già a $D=0$
   crolla a fidelity $0$ per $b/J>2$: parte sempre dal riferimento $|01\rangle$ ($M=0$) e il blocco
   RBS da solo non può mai raggiungere $|11\rangle$ ($M=-1$), il vero ground state sopra soglia — è
   un limite dell'assenza di branching sullo stato iniziale, non del DM. A $D=0.2$ il quadro si
   allarga con un secondo tipo di fallimento, concentrato attorno a $b/J=2$, dove il DM mescola i
   settori. Il contrasto con gli ansatz reali generici — che *non* hanno nessuno di questi due
   vincoli e restano a $\mathcal F=1$ ovunque — **isola** il messaggio: il limite del PMA-1q·1 è
   strutturale (confinamento a $M=0$), non la mancanza di fasi complesse.

4. **La rottura di simmetria reale funziona, e in due modi diversi.** PMA-1q e PMA-2q
   dimostrano che bastano rotazioni $R_y$ aggiuntive — non serve uscire dal campo reale — per
   recuperare $\mathcal F=1$ anche a $D\neq0$. PMA-2q·3 ci arriva con un parametro in meno
   perché fornisce **due gradi di libertà indipendenti in un colpo solo** (uno per settore
   $M=\pm1$), mentre PMA-1q ne fornisce uno alla volta.

5. **Espressività vs costo.** C e D (5 param., ridondanza 2) non migliorano la fidelity
   rispetto ad A/B (già a 1), ma hanno un paesaggio più accidentato: dispersione multistart
   maggiore, più valutazioni di funzione. Conferma operativa del principio "**parametri
   adeguati, non massimi**": oltre i 3 gradi di libertà fisici si aggiunge solo gauge, che
   l'ottimizzatore deve comunque navigare. Lo stesso principio, applicato alle famiglie PMA,
   è dimostrato esplicitamente in §6.6: impilare blocchi RBS aggiuntivi (tutti $M$-conservanti)
   non cambia la fidelity — restano nel settore $M=0$ qualunque sia $K$.

---

## La lezione

Questo notebook completa e rafforza per contrasto il risultato di `vqe_dimer_spiegato.ipynb`.
Là si vedeva il PMA degradare a $D\neq0$; qui si **dimostra la causa**: mettendo accanto quattro
ansatz reali generici che non degradano affatto, si esclude la complessità dello stato come
spiegazione e si isola la **rottura di simmetria $M$** come unico responsabile — e si mostra
**come ripararla** in modo economico, con due famiglie PMA estese che restano nel campo reale.

Emergono tre principi di progetto degli ansatz:

- **Raggiungibilità e minimi locali sono problemi separati**: il primo si risolve con
  l'architettura, il secondo con il multistart. Confonderli porta a "aggiungere restart" quando
  il problema è l'ansatz, o "cambiare ansatz" quando basta un restart in più.
- **La restrizione al campo reale è gratuita** finché $H$ è reale (anche con il DM $XZ-ZX$): un
  ansatz a sole $R_y$ non perde nulla, e risparmia parametri rispetto a uno con $R_z$.
- **Non tutti i parametri aggiuntivi sono uguali**: impilare parametri $M$-conservanti non
  aiuta mai (§6.6); servono parametri che aprano *nuovi* gradi di libertà verso i settori
  mancanti. È la stessa distinzione che decide tra PMA-1q e PMA-2q, e che renderà cruciale la
  scelta dell'entangler per il triangolo frustrato.

Sarà rilevante per il **triangolo frustrato** ($N=3$), dove la scelta dell'entangler smette di
essere cosmetica: sfruttare (o rompere) la simmetria di rotazione $C_3$ della topologia cambia
l'immagine raggiungibile dell'ansatz, e la distinzione HA↔PMA — di cui il blocco RBS è qui il
ponte esplicito — diventa strutturale. PMA-2q·3 è il punto di partenza naturale per quella fase.
