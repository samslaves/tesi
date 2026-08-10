# Shot, rumore statistico e la soglia $1/\sqrt{N_{\rm shots}}$

Spiegazione autosufficiente di un concetto usato più volte nei notebook
(`quantum_simulation_dimero_trotter.ipynb` e `..._semplificato.ipynb`, sezione
"Esecuzione sul circuito"): perché si confronta l'escursione di un segnale con
$1/\sqrt{N_{\rm shots}}$, e cosa significa esattamente quel numero. Nessuna
conoscenza di statistica è data per scontata.

---

## 1. Perché serve ripetere la misura

Un computer quantistico, quando misuri un qubit, non ti restituisce mai "il
valore di aspettazione" — ti restituisce **un singolo bit**, 0 oppure 1, ottenuto
in modo probabilistico. È una proprietà fisica della meccanica quantistica, non
un difetto dello strumento: se lo stato è una sovrapposizione, il risultato di
una singola misura è intrinsecamente casuale, e la teoria (la "regola di Born")
predice solo **con quale probabilità** esce ciascun risultato, non quale
risultato uscirà in una singola esecuzione.

Per stimare quella probabilità — e quindi il valore medio di un osservabile come
$\langle S_z\rangle$ — bisogna ripetere l'intero esperimento (preparare lo stato,
farlo evolvere, misurare) molte volte e guardare **la frazione di volte** in cui
esce ciascun risultato. Ogni ripetizione si chiama **shot**. "8192 shot" vuol
dire: l'intero esperimento è stato ripetuto 8192 volte, e si contano i risultati.

---

## 2. L'esempio più semplice possibile: la moneta

Dimentica per un momento i qubit. Immagina di avere una moneta e di volerne
scoprire la probabilità di uscita testa, $p$. Se la moneta è onesta, $p=0.5$; se
è truccata, magari $p=0.503$ o $p=0.9$.

**L'unico modo per scoprirlo è lanciarla molte volte e contare.** Se lanci la
moneta $N$ volte e ottieni $k$ teste, la tua **stima** di $p$ è
$$\hat p = \frac{k}{N}.$$

Il cappello $\hat{\ }$ sopra la $p$ è la notazione standard per dire "stima",
distinta dal vero valore $p$ che non conosci e stai cercando di indovinare.

**Punto chiave**: $\hat p$ non è mai esattamente $p$, tranne che per un colpo di
fortuna. Ogni volta che ripeti l'intero esperimento (altri $N$ lanci), $\hat p$
esce leggermente diverso. Questa variabilità va sotto il nome di **rumore
statistico** (o errore di campionamento): non è un errore di misura nel senso
di "lo strumento è impreciso", è un effetto del fatto che stai cercando di
dedurre una probabilità da un numero finito di prove.

---

## 3. Quanto è grande, di solito, questo rumore?

Qui arriva l'unico risultato matematico di cui abbiamo bisogno, e lo si può
capire per gradi senza calcoli avanzati.

### 3.1 Intuizione: più lanci, meno rumore, ma non linearmente

Con **pochi** lanci (es. $N=4$) è facilissimo ottenere $\hat p=0.75$ (3 teste su
4) anche se la moneta è onesta ($p=0.5$): è solo sfortuna/fortuna nel campione
piccolo. Con **molti** lanci (es. $N=1\,000\,000$) è quasi impossibile che
$\hat p$ si discosti molto da $0.5$: le fluttuazioni "in più" e "in meno" nei
singoli lanci tendono a compensarsi su un campione enorme.

Quindi: il rumore **diminuisce** all'aumentare di $N$. Ma di quanto? Qui viene
il punto meno intuitivo: il rumore **non** dimezza raddoppiando $N$. Per
dimezzare il rumore serve **quadruplicare** $N$. Il rumore scala come
$1/\sqrt{N}$, non come $1/N$.

### 3.2 Da dove viene esattamente $1/\sqrt{N}$

Ogni singolo lancio è una variabile che vale $1$ (testa) con probabilità $p$ e
$0$ (croce) con probabilità $1-p$. Un fatto di base della probabilità (che qui
prendiamo come dato, è uno dei risultati fondazionali della teoria — la
distribuzione binomiale) dice che, sommando $N$ lanci indipendenti di questo
tipo, la variabilità del **totale** dei successi cresce come $\sqrt{N}$, non
come $N$. Dividendo per $N$ per ottenere la frazione $\hat p=k/N$, la
variabilità di $\hat p$ diventa:
$$\text{deviazione standard di } \hat p \;=\; \sqrt{\frac{p(1-p)}{N}}.$$

Questa quantità si chiama **errore standard** della stima. "Deviazione
standard" è solo un modo preciso di dire "quanto ci si aspetta che $\hat p$
oscilli, in media, attorno al vero valore $p$, ripetendo l'esperimento più
volte".

### 3.3 Il caso peggiore: $p=0.5$

Il fattore $p(1-p)$ nella formula dice qualcosa di interessante: è **massimo**
quando $p=0.5$ (dove vale $0.25$), e **si azzera** quando $p\to0$ o $p\to1$.

Ha senso intuitivamente: se la moneta esce **sempre** testa ($p=1$), ogni lancio
ti dà la stessa informazione — non c'è incertezza su cosa succederà. Se invece
$p=0.5$, ogni lancio è "il più incerto possibile" (equivale esattamente a un
lancio equo), e l'incertezza sulla stima è massima.

A $p=0.5$:
$$\text{deviazione standard di } \hat p = \sqrt{\frac{0.25}{N}} = \frac{0.5}{\sqrt N}.$$

---

## 4. Applicazione a un qubit e a $\langle S_z\rangle$

Nel nostro caso non stimiamo una probabilità fra 0 e 1, ma un valore di
aspettazione $\langle S_z\rangle$ che va da $-1$ a $+1$ (autovalore $+1$ su
$|00\rangle$, $-1$ su $|11\rangle$). Con $n_{00}$ conteggi su $N_{\rm shots}$
shot:
$$\widehat{\langle S_z\rangle} = \frac{n_{00}-n_{11}}{N_{\rm shots}} = 2\hat p - 1, \qquad \hat p \equiv \frac{n_{00}}{N_{\rm shots}}.$$

Riscalare una stima moltiplicandola per $2$ moltiplica anche la sua deviazione
standard per $2$ (la sottrazione di $1$ non cambia la variabilità, sposta solo
il centro). Quindi:
$$\text{deviazione standard di }\widehat{\langle S_z\rangle} = 2\sqrt{\frac{p(1-p)}{N_{\rm shots}}}.$$

Nel **caso peggiore** ($p=0.5$, cioè $\langle S_z\rangle=0$):
$$2\sqrt{\frac{0.25}{N_{\rm shots}}} = 2\cdot\frac{0.5}{\sqrt{N_{\rm shots}}} = \frac{1}{\sqrt{N_{\rm shots}}}.$$

**Ecco da dove viene esattamente il numero $1/\sqrt{N_{\rm shots}}$ usato nei
notebook.** Non è un valore arbitrario né una regola empirica: è la deviazione
standard della stima di $\langle S_z\rangle$ da campionamento, calcolata nel
punto di massima incertezza possibile ($\langle S_z\rangle=0$).

Con $N_{\rm shots}=8192$:
$$\frac{1}{\sqrt{8192}} \approx 0.0110.$$

---

## 5. Perché è un caso *peggiore*, e non il valore esatto ovunque

La formula generale, $2\sqrt{p(1-p)/N_{\rm shots}}$, dipende da $p$ — cioè da
**dove** ti trovi lungo la curva di $\langle S_z\rangle(t)$, non solo da quanti
shot usi. La tabella seguente lo mostra con $N_{\rm shots}=8192$:

| $\langle S_z\rangle$ vero | $p=(\langle S_z\rangle+1)/2$ | $p(1-p)$ | deviazione standard reale |
|---|---|---|---|
| $0.000$ | $0.500$ | $0.2500$ | $0.0110$ (il caso peggiore, $=1/\sqrt{8192}$) |
| $0.500$ | $0.750$ | $0.1875$ | $0.0096$ |
| $0.900$ | $0.950$ | $0.0900$ | $0.0066$ |
| $0.994$ | $0.997$ | $0.0030$ | $0.0012$ |
| $1.000$ | $1.000$ | $0.0000$ | $0.0000$ (nessuna incertezza: esce sempre lo stesso risultato) |

**Vicino agli estremi ($\langle S_z\rangle\to\pm1$) il rumore vero è molto più
piccolo del valore generico $1/\sqrt{N_{\rm shots}}$.** Usare
$1/\sqrt{N_{\rm shots}}$ come soglia di riferimento è quindi una scelta
**prudenziale**: è il rumore che avresti nel punto più difficile possibile, non
necessariamente il rumore esatto nel punto che stai guardando. È una buona
regola pratica per uno screening rapido ("questo segnale è chiaramente troppo
piccolo anche nel caso più favorevole?"), non un calcolo di precisione punto per
punto.

---

## 6. Due esempi numerici concreti

### 6.1 Un segnale che si perde nel rumore (caso generico, $p$ vicino a 0.5)

Supponiamo di voler distinguere due valori veri di $\langle S_z\rangle$, molto
vicini fra loro: $0.030$ e $0.024$ (differenza reale: $0.006$ — le stesse cifre
dell'escursione del set $R_0$ discusso nel notebook). Simulando il
campionamento a 8192 shot, sei ripetizioni indipendenti dell'intero
esperimento danno:

| ripetizione | stima (vero $=0.030$) | stima (vero $=0.024$) |
|---|---|---|
| 1 | 0.0164 | 0.0229 |
| 2 | 0.0281 | 0.0288 |
| 3 | 0.0378 | 0.0225 |
| 4 | 0.0112 | 0.0210 |
| 5 | 0.0305 | 0.0259 |
| 6 | 0.0242 | 0.0134 |

Le due colonne **si mescolano completamente**: guardando solo i numeri
campionati, non è possibile dire in modo affidabile quale dei due fosse il
valore vero più grande — a volte la stima del valore "più piccolo" (0.024)
viene fuori più grande di quella del valore "più grande" (0.030) per puro
rumore (righe 2 e 3). Il rumore reale qui ($\approx0.0110$, siamo vicino a
$p=0.5$) è più grande della differenza che si vuole distinguere ($0.006$):
il segnale è, di fatto, invisibile a questo numero di shot.

### 6.2 Lo stesso segnale, ma vicino a $\langle S_z\rangle=1$ (il caso reale di $R_0$)

Nel notebook, il set $R_0$ oscilla non attorno a $0$ ma vicino a $1$ (fra
$0.994$ e $1.000$). Dalla tabella della Sezione 5, lì il rumore vero è molto
più piccolo ($\sim0.0012$ invece di $0.0110$). Questo significa che la
conclusione "il segnale è invisibile" andrebbe in linea di principio verificata
punto per punto, non con la sola soglia generica.

Ciò non cambia comunque la conclusione pratica per due motivi:

1. **La soglia generica è pensata apposta per essere conservativa**: se un
   segnale supera comodamente $1/\sqrt{N_{\rm shots}}$, è sicuramente misurabile
   ovunque lungo la curva; se invece è più piccolo (come $0.0062$ contro
   $0.0110$), serve un controllo più attento — che è proprio quello appena fatto
   nella Sezione 5, e che conferma che anche il rumore vero locale
   ($\sim0.001$–$0.002$ vicino agli estremi) resta dello stesso ordine di
   grandezza della minuscola escursione, rendendo comunque il segnale difficile
   da separare dal rumore in modo pulito su tutta la traiettoria.
2. **Il motivo per scartare $R_0$ nel notebook non è comunque solo questo**: la
   scelta del punto di lavoro richiede anche una seconda condizione (due
   frequenze di oscillazione confrontabili, non solo un'ampiezza sufficiente) —
   il controllo sul rumore statistico è solo il primo, più immediato, dei due
   filtri applicati.

---

## 7. Riepilogo in una frase

$1/\sqrt{N_{\rm shots}}$ è la fluttuazione che ci si aspetta, nel caso peggiore
possibile, stimando un valore di aspettazione da campionamento ripetuto: cresce
la precisione aumentando gli shot, ma solo con la radice quadrata, e un segnale
fisico più piccolo di questa soglia rischia di essere indistinguibile dal
rumore di misura — non perché il calcolo o l'hardware siano imprecisi, ma per la
natura statistica della misura quantistica stessa.
