# Note di approfondimento — `quantum_simulation_dimero_trotter.ipynb`

Materiale a corredo del notebook, tenuto fuori dalle celle per mantenerlo snello.

---

## Cosa vuol dire "oscillazioni non monocromatiche"

Il termine viene dall'ottica: una luce monocromatica ha una sola frequenza (un solo
colore). Un'oscillazione **monocromatica** è un segnale con una sola frequenza pura:

$$f(t)=A\cos(\omega t+\phi)$$

Un'oscillazione **non monocromatica** è invece una sovrapposizione di più frequenze
diverse:

$$f(t)=A_1\cos(\omega_1 t+\phi_1)+A_2\cos(\omega_2 t+\phi_2)+\dots$$

### Applicazione al dimero

$\langle S_z\rangle(t)$ è per costruzione una somma di modi a frequenze di Bohr
$\Delta_{kl}=E_l-E_k$ (Sezione 3 del notebook):

$$\langle S_z\rangle(t)=\text{costante}+\sum_{k<l}2\,\mathrm{Re}\!\left[c_k^*c_l(S_z)_{kl}\,e^{-i\Delta_{kl}t}\right]$$

- Se **un solo** termine domina, il grafico è un coseno pulito e regolare. È il caso
  del regime R0 ($D/J=1/6$, rapporto $a_2/a_1=0.04$).
- Se **due o più** termini hanno ampiezze confrontabili e frequenze diverse, si
  sommano e producono **battimenti**: massimi e minimi irregolari, senza periodicità
  semplice. È il caso di R1 ($a_2/a_1=0.74$).

### Perché il relatore lo chiede

Un'oscillazione monocromatica equivale dinamicamente a un sistema a due livelli, e
non mette alla prova né il codice Trotter né lo sviluppo su più autostati — un
singolo coseno si ottiene anche a mano. Un regime non monocromatico costringe la
dinamica su più autostati a entrare in gioco.

**Precisazione da tenere presente** (Sezione 3.1 del notebook): poiché $|T_0\rangle$
è esattamente disaccoppiato, la dinamica è effettivamente a **3 livelli**, con solo
**2 frequenze indipendenti** (la terza è la somma delle altre due, vincolo automatico
fra gap di livelli). Il passaggio R0 $\to$ R1 è quindi da 1 a 2 frequenze
indipendenti, non da 2 a 4 livelli: da riportare con questa precisione, perché il
guadagno è reale ma più modesto di quanto suggerirebbe il conteggio dei livelli.

---

## Criterio di selezione del regime: cosa è stato usato e cosa no

Nel notebook la scelta del punto di lavoro usa due grandezze **trasparenti e
verificabili a mano**, entrambe calcolate dalla dinamica esatta:

1. **escursione** picco-picco di $\langle S_z\rangle(t)$ — il segnale deve essere
   leggibile sopra il rumore statistico $\sim1/\sqrt{N_\text{shots}}$;
2. **$a_2/a_1$** — rapporto fra le ampiezze dei due modi dominanti, $\approx0$ per un
   segnale monocromatico, $\approx1$ per due frequenze equilibrate.

Servono entrambe: un segnale grande ma monocromatico non soddisfa la richiesta del
relatore (caso della risonanza $b=-J$), e un segnale spettralmente ricco ma minuscolo
è inutilizzabile.

> **Nota storica.** In una versione precedente il criterio era un'*entropia spettrale
> pesata* $A\cdot S$ con $S=-\sum_m p_m\ln p_m$. È stata rimossa: il concetto generale
> esiste in signal processing (Kapur & Kesavan 1992, entropia di Shannon su una
> distribuzione di potenza spettrale), ma la sua applicazione a un insieme discreto di
> ampiezze di transizione fra autostati non risulta da alcuna fonte, né dal materiale
> del corso — era una proposta originale non richiesta. Inoltre risultava poco robusta:
> lo scarto di punteggio fra 1° e 5° classificato era del $4\%$, e un criterio
> alternativo rimescolava completamente la graduatoria. Il criterio a due colonne
> attuale è più semplice, altrettanto efficace e direttamente verificabile dal relatore.

---

## Nota sulla convenzione di segno delle frequenze

La convenzione standard in letteratura (Cohen-Tannoudji e affini) è

$$\omega_{kl}\equiv\frac{E_k-E_l}{\hbar}$$

cioè il primo indice porta il segno positivo. Nel notebook si usa invece

$$\Delta_{kl}\equiv E_l-E_k>0 \qquad (k<l)$$

con indici esplicitamente ordinati, per avere frequenze positive senza dover ricordare
la convenzione di segno a ogni passaggio: $\Delta_{kl}=\omega_{lk}$. La scelta non
incide sul risultato fisico — $\langle S_z\rangle(t)$ è reale e ogni modo entra come
$2|z|\cos(\Delta_{kl}t-\arg z)$, quindi invertire il segno di una frequenza si
riassorbe nella fase — ma va tenuta coerente nel resto della tesi.

---

## Convenzioni da dichiarare insieme

Le tre convenzioni che, prese singolarmente, sembrano innocue e che insieme producono
la maggior parte degli errori di segno difficili da diagnosticare:

1. **Endianness di Qiskit**: `Pauli('AB')` ha $B$ sul qubit 0. Con spin 1 $\to$ qubit
   0, quindi $X_1Z_2\equiv$ `Pauli('ZX')`.
2. **Segno del termine DM**: con $H_2'=-H_2$ cambiano segno *entrambi* gli angoli dei
   due $R_{ZZ}$, la struttura del circuito resta identica. Per l'osservabile $S_z$ da
   $|00\rangle$ il risultato non cambia (i due casi sono legati dallo scambio
   $1\leftrightarrow2$, che lascia invarianti sia $|00\rangle$ sia $S_z$).
3. **Fattori $1/2$ dei gate**: $R_z(\phi)=e^{-i\phi Z/2}$, $R_{ZZ}(\phi)=e^{-i\phi ZZ/2}$
   — da cui $\theta=Jt/2$ e non $Jt/4$ nei blocchi di scambio.

---

## Provenienza del punto di lavoro R1 — cronologia

Vale la pena registrarla, perché il punto è cambiato due volte e il relatore potrebbe
chiedere conto del percorso.

1. **Prima versione (scartata).** R1 $=(b/J=-0.15,\;D/J=1)$ veniva da uno scan
   automatico su 2349 punti classificati con un'*entropia spettrale pesata* $A\cdot S$.
   Criterio poco robusto (scarto 1°–5° classificato del 4%) e non riconducibile ad
   alcuna fonte: rimosso.
2. **Seconda versione (scartata).** Stessa coppia di valori, ma giustificata con una
   tabella di regimi candidati. Era una razionalizzazione *a posteriori*: la tabella
   era stata costruita con R1 già dentro, quindi non permetteva di ricostruire come ci
   si fosse arrivati.
3. **Versione attuale.** R1 $=(b/J=-0.18,\;D/J=1)$ **derivato** dalla struttura a V
   dell'Hamiltoniana (Sezioni 3.1–3.4 del notebook): due condizioni indipendenti
   (ampiezza del segnale dalla formula di Rabi; numero di frequenze dai due detuning
   $\Delta_\pm=J\pm b$) e due scan 1D. I due modi dominanti risultano bilanciati a
   $a_2/a_1=0.995$.

Il valore $-0.15$ resta comunque dentro il plateau $b/J\in[-0.22,-0.14]$: se serve
mantenerlo per coerenza con materiale già scritto, basta cambiarlo nel setup senza
invalidare la derivazione.

---

## Bibliografia: cosa è citabile e cosa no

La Sezione 8 del notebook contiene la tabella completa. In sintesi, per la derivazione
di R1 **non è stata consultata alcuna fonte esterna**: la struttura è stata ricavata e
verificata numericamente. Gli ingredienti sono però standard, e due sono già
documentati nel progetto stesso (`simmetrie_dmi_spin.pdf` §11.1, §11.2.2, §12, §13.3).

L'unico elemento senza riferimento preciso è la formula di Rabi per il trasferimento di
popolazione a due livelli: è un risultato da manuale, ma non è stata verificata una
citazione specifica e **non va inventata**. Se serve in tesi, va presa da un testo che
hai effettivamente in mano.

La combinazione dei due criteri in una procedura di selezione è costruzione originale
di questo lavoro, e va presentata come tale.

---

## Discrepanza aperta con `simmetrie_dmi_spin.pdf`

Vedi Sezione 8.1 del notebook per la verifica numerica completa. In breve: gli elementi
di matrice della DMI riportati nel documento (§11.2.1 e §11.2.2) risultano **doppi**
rispetto al calcolo diretto. Il controllo di covarianza rotazionale
($\|(\vec s_1\times\vec s_2)_a|0,0\rangle\|=1/2$ per ogni asse $a$) supporta il valore
ricavato qui. Se confermato, va corretta anche l'espressione di §13.2 per $E_\pm$.

Da chiarire con il relatore prima di portare l'una o l'altra versione in tesi.
