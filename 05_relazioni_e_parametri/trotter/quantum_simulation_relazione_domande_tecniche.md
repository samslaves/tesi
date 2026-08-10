# Note tecniche sulla dinamica del dimero: criteri di scelta dei parametri

Raccolta organizzata per argomento dei concetti usati nella relazione dei test
sui parametri (`relazione_test_parametri`), utile come riferimento rapido
prima della discussione con il relatore.

---

## Criterio di non monocromaticità: il rapporto $a_2/a_1$

Un segnale è "non monocromatico" quando almeno due frequenze di oscillazione
hanno ampiezza confrontabile, non una sola frequenza dominante con le altre
trascurabili. Il rapporto fra le ampiezze dei due modi spettrali dominanti,
$a_2/a_1$, quantifica questo aspetto:

- $a_2/a_1\to0$: un solo modo domina, il segnale è di fatto monocromatico;
- $a_2/a_1\to1$: le due frequenze dominanti hanno ampiezza praticamente
  uguale — il caso più "non monocromatico" possibile con due frequenze.

Dai cinque set di parametri testati:

| test | $a_2/a_1$ |
|---|---|
| 4 | **0.96** ← il più vicino a 1 |
| 1 | 0.84 |
| 2 | 0.84 |
| 5 | 0.82 |
| 3 | 0.52 ← un modo domina nettamente sull'altro |

**Il rapporto $a_2/a_1$ da solo non basta.** Un segnale può avere $a_2/a_1$
perfetto ma ampiezza complessiva (escursione) minuscola — inosservabile in
pratica sopra il rumore statistico. Per questo la scelta del regime richiede
**due** indicatori insieme: l'escursione (deve superare la soglia del rumore
statistico, $\sim0.011$ a 8192 shot) *e* $a_2/a_1$ (deve avvicinarsi a 1). Il
test 4 risulta il migliore proprio perché soddisfa **entrambi** i criteri
insieme (escursione $1.281$, $a_2/a_1=0.96$), non solo perché ha l'$a_2/a_1$
più alto in assoluto.

---

## Numero di frequenze osservabili e livelli energetici

Con $n$ livelli energetici (autostati dell'Hamiltoniana, etichettati
$k=0,\dots,n-1$), le frequenze di oscillazione possibili in un osservabile
come $\langle S_z\rangle(t)$ sono le differenze $\Delta_{kl}=E_l-E_k$ per ogni
**coppia** di livelli distinti. Il numero di coppie distinte che si possono
formare da $n$ elementi è il coefficiente binomiale $\binom{n}{2}$; per il
caso a 4 livelli del dimero:
$$\binom{4}{2} = \frac{4\times3}{2} = 6$$

cioè le coppie $(0,1)$, $(0,2)$, $(0,3)$, $(1,2)$, $(1,3)$, $(2,3)$ — **al
massimo sei frequenze** possibili.

### Perché $\binom{n}{2}$ e non $n^2$ o $n(n-1)$

Sviluppando $\langle S_z\rangle(t)$ su tutte le coppie $(k,l)$:
- le coppie con $k=l$ ($n$ casi) non oscillano — danno solo la costante
  attorno a cui il segnale si muove, non una frequenza;
- le coppie $(k,l)$ e $(l,k)$ con $k\neq l$ sono la stessa oscillazione
  fisica contata due volte (complessi coniugati l'uno dell'altro) — si
  sommano in un'unica frequenza reale osservabile, non se ne contano due.

Da $n^2$ combinazioni totali si tolgono le $n$ con $k=l$, e si dimezzano le
restanti $n(n-1)$ (perché $(k,l)$ e $(l,k)$ coincidono fisicamente),
ottenendo $\binom n2 = n(n-1)/2$.

### Livelli disaccoppiati riducono ulteriormente il numero di frequenze osservate

Se uno dei livelli non è popolato dallo stato iniziale, o non contribuisce
all'osservabile misurato, o non si mescola con gli altri sotto l'evoluzione,
ogni coppia che lo coinvolge dà ampiezza esattamente nulla — anche se
resterebbe matematicamente "possibile" secondo il conteggio combinatorio. Nel
caso del dimero, il livello $|t_0\rangle$ è disaccoppiato per tutte e tre
queste ragioni contemporaneamente (vedi sezione successiva): delle 6 coppie
possibili, le 3 che lo coinvolgono — $(0,2)$, $(1,2)$, $(2,3)$ — si spengono
automaticamente, e ne restano solo 3, coerentemente con quanto osservato in
tutti e cinque i test.

### Frequenze indipendenti vs frequenze osservate

Le frequenze superstiti non sono tutte indipendenti fra loro: essendo
differenze di energia, sono vincolate dall'identità
$$\Delta_{03} = \Delta_{01} + \Delta_{13}$$
(la somma di due gap consecutivi è il gap totale). Verificato numericamente
su tutti i test, ad esempio nel test 4: $0.789+1.556=2.345$. Delle 3
frequenze osservate, quindi, solo **2 sono realmente indipendenti** — è
questo, e non il numero grezzo di frequenze visibili, il vero limite
superiore alla "ricchezza spettrale" ottenibile con un sistema a 4 livelli in
questa configurazione.

---

## Stati disaccoppiati dalla dinamica: il caso di $|t_0\rangle$

Nel dimero, lo stato
$$|t_0\rangle = \frac{|01\rangle+|10\rangle}{\sqrt2}$$
(la combinazione **simmetrica** delle due configurazioni con uno spin su e
uno giù) risulta completamente isolato dalla dinamica, per tre proprietà
verificate numericamente a scarto **esattamente zero**:

| proprietà | risultato |
|---|---|
| $H_2\,|t_0\rangle$ (termine DM applicato) | $=0$ esatto |
| $H_1\,|t_0\rangle - \frac{J}{4}|t_0\rangle$ | $=0$ esatto ($t_0$ autostato di $H_1$) |
| $H\,|t_0\rangle - \frac{J}{4}|t_0\rangle$ | $=0$ esatto ($t_0$ autostato dell'Hamiltoniana intera) |
| $\langle t_0|00\rangle$ | $=0$ (non popolato dallo stato iniziale) |
| $\langle t_0|S_z|t_0\rangle$ | $=0$ (non contribuisce a $S_z$) |

### Origine fisica del disaccoppiamento

**Il campo e lo scambio isotropo ($H_1$) lasciano $|t_0\rangle$ fermo.** Lo
scambio isotropo $J\vec s_1\cdot\vec s_2$ tratta i due spin in modo
simmetrico (non distingue "chi" ha spin su e "chi" giù, solo la loro
relazione reciproca), quindi $|t_0\rangle$ ne è autostato, con energia
$E=J/4$. Il campo $b(s_{z1}+s_{z2})$ è diagonale nella base computazionale e
su $|01\rangle$ e $|10\rangle$ dà lo stesso contributo (uno spin su, uno giù,
in entrambi i casi) — quindi anche il campo lascia $|t_0\rangle$ come
autostato, senza mescolarlo con nient'altro.

**Il termine DM annichila $|t_0\rangle$ del tutto: $H_2|t_0\rangle=0$.** Il
motivo è legato alla simmetria del termine DM
$D(s_{x1}s_{z2}-s_{z1}s_{x2})$: applicandolo separatamente a $|01\rangle$ e a
$|10\rangle$, i due contributi risultano uguali in modulo ma di segno
opposto — un'interferenza distruttiva esatta, non un'approssimazione. Nella
combinazione simmetrica $(|01\rangle+|10\rangle)/\sqrt2$ i due contributi si
cancellano esattamente; nella combinazione antisimmetrica
$(|01\rangle-|10\rangle)/\sqrt2$ (il singoletto) si sommerebbero invece di
cancellarsi. Il termine DM, in altre parole, "vede" solo la parte
antisimmetrica dei due spin, non quella simmetrica.

### Conseguenze pratiche

Essendo autostato esatto della somma $H_1+H_2$ (non solo di un pezzo),
$|t_0\rangle$:
- non evolve mai in nient'altro — resta isolato dagli altri tre livelli per
  qualunque valore di $b$, $D$, $t$;
- non viene popolato dallo stato iniziale $|00\rangle$, dato che i due sono
  ortogonali per costruzione ($|00\rangle$ ha entrambi gli spin uguali,
  $|t_0\rangle$ è fatto solo di configurazioni con spin opposti);
- non contribuisce mai a $\langle S_z\rangle$, perché $S_z|t_0\rangle=0$
  esattamente (uno spin su e uno giù si cancellano nella somma $Z_1+Z_2$).

Tre proprietà indipendenti che puntano tutte nella stessa direzione: quel
livello resta semplicemente fuori dai giochi per tutta la dinamica studiata,
qualunque siano i parametri usati.

---

## Battimenti ed escursione del segnale

Due proprietà distinte e indipendenti di un segnale oscillante, spesso
confuse ma concettualmente separate.

### Battimenti

Quando si sommano due oscillazioni di frequenza vicina ma non identica, il
risultato non è una singola onda pulita: cresce e decresce in ampiezza nel
tempo, con un pattern che si ripete più lentamente della singola
oscillazione — lo stesso fenomeno percepibile con due corde di chitarra
quasi, ma non perfettamente, accordate: non si sentono due note separate, si
sente un'unica nota che "pulsa".

Matematicamente, con due frequenze $\Delta_1$ e $\Delta_2$ di ampiezza
simile:
$$\cos(\Delta_1 t) + \cos(\Delta_2 t) = 2\cos\!\left(\frac{\Delta_1-\Delta_2}{2}t\right)\cos\!\left(\frac{\Delta_1+\Delta_2}{2}t\right)$$

il primo fattore (lento, dipende dalla *differenza* delle frequenze) modula
in ampiezza il secondo (veloce, dipende dalla loro *media*): quell'inviluppo
lento che sale e scende è il battimento.

Se le due frequenze sono **incommensurabili** (il loro rapporto non è un
numero razionale semplice), il segnale risultante non è periodico in senso
stretto ma **quasi-periodico**: non si ripete mai esattamente, pur restando
confinato in un inviluppo regolare — è il comportamento tipico dei regimi
scelti nei test, dove i due gap energetici non hanno un rapporto commensurato
"pulito".

Perché serve $a_2/a_1$ vicino a 1 per vedere bene i battimenti: se una delle
due ampiezze è molto più piccola dell'altra, il fattore di modulazione ha un
effetto trascurabile e si osserva quasi solo la frequenza dominante — nessun
battimento visibile.

### Escursione

L'escursione è semplicemente **quanto è grande** il segnale — la differenza
fra il valore massimo e il valore minimo raggiunti da $\langle S_z\rangle(t)$
lungo tutta la simulazione:
$$\text{escursione} = \max_t \langle S_z\rangle(t) - \min_t \langle S_z\rangle(t)$$

Non ha alcuna relazione diretta con quante frequenze sono presenti o quanto
sono bilanciate fra loro — è solo l'ampiezza complessiva dell'oscillazione,
in valore assoluto.

### Le due proprietà non vanno di pari passo

Un segnale può avere la *forma* giusta (battimenti ben visibili, dovuti a
frequenze bilanciate) ma un'*ampiezza* complessiva piccola — il segnale
oscilla "nel modo giusto" ma "poco", restando comunque sotto la soglia di
rilevabilità pratica (il rumore statistico di campionamento). È per questo
che la scelta del regime di lavoro richiede di controllare entrambi gli
indicatori insieme, non uno dei due soltanto: uno risponde alla domanda "la
forma è quella cercata?", l'altro a "quella forma è abbastanza grande da
poter essere misurata?".
